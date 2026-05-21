'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { deviceApi, type DeviceItem } from '@/api/devices';

const DEVICE_TYPE_LABELS: Record<string, string> = {
  collar: '智能项圈',
  positioning_tag: '定位牌',
  feeder: '智能喂食器',
  litter_box: '智能猫砂盆',
  camera: '监控摄像头',
  other: '其他设备',
};

const STATUS_COLORS: Record<string, string> = {
  online: 'bg-green-500',
  offline: 'bg-neutral-400',
  maintenance: 'bg-yellow-500',
  unbound: 'bg-red-500',
};

const STATUS_LABELS: Record<string, string> = {
  online: '在线',
  offline: '离线',
  maintenance: '维护中',
  unbound: '未绑定',
};

export default function DevicesPage() {
  const [devices, setDevices] = useState<DeviceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDevices = useCallback(async () => {
    try {
      setLoading(true);
      const data = await deviceApi.list();
      setDevices(data);
      setError(null);
    } catch (err) {
      setError('加载设备列表失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  const handleUnbind = async (deviceId: string, deviceName: string) => {
    if (!confirm(`确定要解绑设备「${deviceName}」吗？`)) return;
    try {
      await deviceApi.unbind(deviceId);
      setDevices((prev) => prev.filter((d) => d.device_id !== deviceId));
    } catch {
      alert('解绑失败');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-4 sm:p-6 md:p-8">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-neutral-900">设备管理</h1>
          <Link
            href="/devices/new"
            className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            + 绑定新设备
          </Link>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4 text-sm text-red-600">{error}</div>
        )}

        {devices.length === 0 ? (
          <div className="rounded-lg border border-neutral-200 bg-white p-12 text-center">
            <div className="text-4xl mb-4">📡</div>
            <p className="text-lg font-medium text-neutral-700">暂无绑定设备</p>
            <p className="mt-2 text-sm text-neutral-500">
              绑定一个智能穿戴设备，开始追踪宠物的健康数据
            </p>
            <Link
              href="/devices/new"
              className="mt-4 inline-block rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
            >
              绑定设备
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {devices.map((device) => (
              <div
                key={device.device_id}
                className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">
                      {device.device_type === 'collar' ? '🔗' :
                       device.device_type === 'positioning_tag' ? '📍' :
                       device.device_type === 'feeder' ? '🍖' :
                       device.device_type === 'litter_box' ? '📦' :
                       device.device_type === 'camera' ? '📹' : '📡'}
                    </span>
                    <div>
                      <h3 className="font-semibold text-neutral-900">{device.device_name}</h3>
                      <p className="text-xs text-neutral-500">
                        {DEVICE_TYPE_LABELS[device.device_type] || device.device_type}
                        {device.brand ? ` · ${device.brand}` : ''}
                        {device.model ? ` · ${device.model}` : ''}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                      device.status === 'online'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-neutral-100 text-neutral-600'
                    }`}
                  >
                    <span
                      className={`mr-1 h-2 w-2 rounded-full ${STATUS_COLORS[device.status] || 'bg-neutral-400'}`}
                    />
                    {STATUS_LABELS[device.status] || device.status}
                  </span>
                </div>

                {device.battery_level && (
                  <div className="mt-3 flex items-center text-xs text-neutral-500">
                    <span className="mr-2">🔋 电量: {device.battery_level}%</span>
                  </div>
                )}

                <div className="mt-4 flex space-x-2">
                  <Link
                    href={`/devices/${device.device_id}`}
                    className="flex-1 rounded-md bg-primary-50 px-3 py-1.5 text-center text-sm font-medium text-primary-700 hover:bg-primary-100"
                  >
                    查看数据
                  </Link>
                  <button
                    onClick={() => handleUnbind(device.device_id, device.device_name)}
                    className="rounded-md bg-neutral-100 px-3 py-1.5 text-sm font-medium text-neutral-600 hover:bg-neutral-200"
                  >
                    解绑
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}