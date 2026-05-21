'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { deviceApi, type DeviceCreateRequest } from '@/api/devices';

const DEVICE_TYPES = [
  { value: 'collar', label: '智能项圈' },
  { value: 'positioning_tag', label: '定位牌' },
  { value: 'feeder', label: '智能喂食器' },
  { value: 'litter_box', label: '智能猫砂盆' },
  { value: 'camera', label: '监控摄像头' },
  { value: 'other', label: '其他设备' },
];

export default function NewDevicePage() {
  const router = useRouter();
  const [form, setForm] = useState<DeviceCreateRequest>({
    pet_id: '',
    device_name: '',
    device_type: 'collar',
    brand: 'generic',
    model: '',
    serial_number: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.pet_id.trim() || !form.device_name.trim()) {
      setError('请填写宠物ID和设备名称');
      return;
    }
    try {
      setSubmitting(true);
      await deviceApi.bind(form);
      router.push('/devices');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '绑定失败');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50 p-4 sm:p-6 md:p-8">
      <div className="mx-auto max-w-lg">
        <Link href="/devices" className="mb-4 inline-flex items-center text-sm text-neutral-500 hover:text-primary-600">
          ← 返回设备列表
        </Link>

        <h1 className="mb-6 text-2xl font-bold text-neutral-900">绑定新设备</h1>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-600">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm space-y-4">
          {/* 宠物ID */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">宠物ID *</label>
            <input
              type="text"
              value={form.pet_id}
              onChange={(e) => setForm({ ...form, pet_id: e.target.value })}
              placeholder="输入已注册的宠物ID"
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
              required
            />
          </div>

          {/* 设备名称 */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">设备名称 *</label>
            <input
              type="text"
              value={form.device_name}
              onChange={(e) => setForm({ ...form, device_name: e.target.value })}
              placeholder="例如：豆豆的智能项圈"
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
              required
            />
          </div>

          {/* 设备类型 */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">设备类型</label>
            <select
              value={form.device_type}
              onChange={(e) => setForm({ ...form, device_type: e.target.value })}
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
            >
              {DEVICE_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          {/* 品牌 */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">品牌</label>
            <select
              value={form.brand}
              onChange={(e) => setForm({ ...form, brand: e.target.value })}
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
            >
              <option value="xiaomi">小米 (Xiaomi)</option>
              <option value="huawei">华为 (Huawei)</option>
              <option value="apple">苹果 (Apple)</option>
              <option value="generic">通用/其他</option>
            </select>
          </div>

          {/* 型号 */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">型号</label>
            <input
              type="text"
              value={form.model || ''}
              onChange={(e) => setForm({ ...form, model: e.target.value })}
              placeholder="设备型号（选填）"
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
            />
          </div>

          {/* 序列号 */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">序列号</label>
            <input
              type="text"
              value={form.serial_number || ''}
              onChange={(e) => setForm({ ...form, serial_number: e.target.value })}
              placeholder="设备序列号/SN（选填）"
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
            />
          </div>

          {/* 备注 */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">备注</label>
            <textarea
              value={form.notes || ''}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              placeholder="备注信息（选填）"
              rows={2}
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-primary-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {submitting ? '绑定中...' : '绑定设备'}
          </button>
        </form>
      </div>
    </div>
  );
}