'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  deviceApi,
  type DeviceItem,
  type HealthMetricResponse,
  type DailyReportResponse,
} from '@/api/devices';

const METRIC_LABELS: Record<string, { name: string; unit: string; icon: string }> = {
  heart_rate: { name: '心率', unit: 'bpm', icon: '❤️' },
  steps: { name: '步数', unit: '步', icon: '👣' },
  temperature: { name: '体温', unit: '°C', icon: '🌡️' },
  activity_level: { name: '活动级别', unit: '级', icon: '🏃' },
  sleep_hours: { name: '睡眠', unit: '小时', icon: '😴' },
  calories: { name: '卡路里', unit: 'kcal', icon: '🔥' },
};

function getTodayRange() {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
  const end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
  return { start, end };
}

function formatISO(d: Date): string {
  return d.toISOString().replace('Z', '');
}

function toLocalTime(isoStr: string): string {
  const d = new Date(isoStr);
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

export default function DeviceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [device, setDevice] = useState<DeviceItem | null>(null);
  const [latestData, setLatestData] = useState<HealthMetricResponse[]>([]);
  const [report, setReport] = useState<DailyReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reportDate, setReportDate] = useState(
    new Date().toISOString().split('T')[0]
  );

  const fetchAll = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      const [deviceData, latest] = await Promise.all([
        deviceApi.getById(id),
        deviceApi.getLatest(id).catch(() => []),
      ]);
      setDevice(deviceData);
      setLatestData(latest);
      setError(null);
    } catch {
      setError('加载设备信息失败');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const handleGenerateReport = async () => {
    if (!device) return;
    try {
      const result = await deviceApi.generateDailyReport(
        device.pet_id,
        reportDate
      );
      setReport(result);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : '生成日报失败';
      alert(msg);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !device) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-red-600">{error || '设备不存在'}</p>
          <Link href="/devices" className="mt-4 inline-block text-primary-600 hover:underline">
            返回设备列表
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-4 sm:p-6 md:p-8">
      <div className="mx-auto max-w-4xl">
        {/* 返回导航 */}
        <Link href="/devices" className="mb-4 inline-flex items-center text-sm text-neutral-500 hover:text-primary-600">
          ← 返回设备列表
        </Link>

        {/* 设备信息卡片 */}
        <div className="mb-6 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-neutral-900">{device.device_name}</h1>
              <p className="mt-1 text-sm text-neutral-500">
                {device.brand} · {device.model || '未知型号'}
                {device.serial_number ? ` · SN: ${device.serial_number}` : ''}
              </p>
            </div>
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${
                device.status === 'online'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-neutral-100 text-neutral-600'
              }`}
            >
              {device.status === 'online' ? '🟢 在线' : '⚫ 离线'}
            </span>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            <div className="rounded-md bg-neutral-50 p-3">
              <span className="text-neutral-500">类型</span>
              <p className="font-medium text-neutral-900">{device.device_type}</p>
            </div>
            <div className="rounded-md bg-neutral-50 p-3">
              <span className="text-neutral-500">电量</span>
              <p className="font-medium text-neutral-900">{device.battery_level || '--'}%</p>
            </div>
            <div className="rounded-md bg-neutral-50 p-3">
              <span className="text-neutral-500">固件</span>
              <p className="font-medium text-neutral-900">{device.firmware_version || '--'}</p>
            </div>
            <div className="rounded-md bg-neutral-50 p-3">
              <span className="text-neutral-500">最后在线</span>
              <p className="font-medium text-neutral-900">
                {device.last_online_at
                  ? new Date(device.last_online_at).toLocaleString('zh-CN')
                  : '--'}
              </p>
            </div>
          </div>
        </div>

        {/* 实时指标卡片 */}
        <h2 className="mb-4 text-lg font-semibold text-neutral-900">实时健康指标</h2>
        {latestData.length === 0 ? (
          <div className="rounded-lg border border-neutral-200 bg-white p-8 text-center text-neutral-500">
            暂无实时数据，请先<a href="#" className="text-primary-600 hover:underline" onClick={() => {/* trigger simulate */}}>生成模拟数据</a>
          </div>
        ) : (
          <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-6">
            {latestData.map((item) => {
              const info = METRIC_LABELS[item.metric_name] || {
                name: item.metric_name,
                unit: item.unit,
                icon: '📊',
              };
              return (
                <div
                  key={item.metric_name}
                  className="rounded-lg border border-neutral-200 bg-white p-4 text-center shadow-sm"
                >
                  <div className="text-xl">{info.icon}</div>
                  <p className="mt-1 text-2xl font-bold text-neutral-900">
                    {item.value}
                  </p>
                  <p className="text-xs text-neutral-500">
                    {info.name} ({info.unit})
                  </p>
                </div>
              );
            })}
          </div>
        )}

        {/* 日报生成 */}
        <div className="mb-6 rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-neutral-900">健康日报</h2>
          <div className="flex items-center space-x-3">
            <input
              type="date"
              value={reportDate}
              onChange={(e) => setReportDate(e.target.value)}
              className="rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
            />
            <button
              onClick={handleGenerateReport}
              className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
            >
              生成日报
            </button>
          </div>

          {report && (
            <div className="mt-4 rounded-lg bg-neutral-50 p-4">
              <div className="prose prose-sm max-w-none whitespace-pre-wrap text-neutral-700">
                {report.summary}
              </div>
            </div>
          )}
        </div>

        {/* 时序图表占位 - 后续可用 Chart.js 实现 */}
        <div className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-neutral-900">24小时趋势</h2>
          <p className="text-sm text-neutral-500">
            时序图表将在 Phase 1 中使用 Chart.js / ECharts 实现。当前可调用{' '}
            <code className="rounded bg-neutral-100 px-1 py-0.5 text-xs">GET /api/v1/devices/data/query</code>{' '}
            获取时序数据。
          </p>
        </div>
      </div>
    </div>
  );
}