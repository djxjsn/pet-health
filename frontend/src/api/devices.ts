'use client';

import { apiClient } from './client';

export interface DeviceItem {
  device_id: string;
  pet_id: string;
  device_name: string;
  device_type: string;
  brand: string;
  model?: string;
  serial_number?: string;
  firmware_version?: string;
  status: string;
  last_online_at?: string;
  battery_level?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface DeviceCreateRequest {
  pet_id: string;
  device_name: string;
  device_type?: string;
  brand: string;
  model?: string;
  serial_number?: string;
  notes?: string;
}

export interface DeviceUpdateRequest {
  device_name?: string;
  status?: string;
  battery_level?: string;
  firmware_version?: string;
  notes?: string;
}

export interface HealthMetricPoint {
  metric_name: string;
  value: number;
  timestamp?: string;
  unit?: string;
}

export interface DeviceDataReportRequest {
  device_id: string;
  metrics: HealthMetricPoint[];
}

export interface HealthMetricResponse {
  metric_name: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface HealthAggregationResponse {
  metric_name: string;
  unit: string;
  avg: number;
  min: number;
  max: number;
  latest: number;
  count: number;
}

export interface DailyReportRequest {
  pet_id: string;
  date: string;
}

export interface DailyReportResponse {
  report_id: string;
  pet_id: string;
  pet_name: string;
  date: string;
  summary: string;
  metrics_summary: Record<string, unknown>;
  alerts: Array<Record<string, unknown>>;
  suggestions: string[];
  generated_at: string;
}

export interface SimulateRequest {
  pet_id: string;
  species: string;
  days: number;
  interval_minutes: number;
}

export const deviceApi = {
  /** 绑定设备 */
  async bind(data: DeviceCreateRequest): Promise<DeviceItem> {
    return apiClient.post<DeviceItem>('/devices', data);
  },

  /** 获取设备列表 */
  async list(petId?: string): Promise<DeviceItem[]> {
    const params = petId ? { pet_id: petId } : undefined;
    return apiClient.get<DeviceItem[]>('/devices', params);
  },

  /** 获取设备详情 */
  async getById(deviceId: string): Promise<DeviceItem> {
    return apiClient.get<DeviceItem>(`/devices/${deviceId}`);
  },

  /** 更新设备 */
  async update(deviceId: string, data: DeviceUpdateRequest): Promise<DeviceItem> {
    return apiClient.put<DeviceItem>(`/devices/${deviceId}`, data);
  },

  /** 解绑设备 */
  async unbind(deviceId: string): Promise<void> {
    return apiClient.delete(`/devices/${deviceId}`);
  },

  /** 设备心跳 */
  async heartbeat(deviceId: string): Promise<DeviceItem> {
    return apiClient.post<DeviceItem>(`/devices/${deviceId}/heartbeat`);
  },

  /** 上报健康数据 */
  async reportData(data: DeviceDataReportRequest): Promise<{ status: string; count: number }> {
    return apiClient.post<{ status: string; count: number }>('/devices/data/report', data);
  },

  /** 查询健康数据 */
  async queryData(
    deviceId: string,
    metricName: string | null,
    startTime: string,
    endTime: string,
    interval = '1h'
  ): Promise<HealthMetricResponse[]> {
    const params: Record<string, string> = {
      device_id: deviceId,
      start_time: startTime,
      end_time: endTime,
      interval,
    };
    if (metricName) params.metric_name = metricName;
    return apiClient.get<HealthMetricResponse[]>('/devices/data/query', params);
  },

  /** 获取最新数据 */
  async getLatest(deviceId: string): Promise<HealthMetricResponse[]> {
    return apiClient.get<HealthMetricResponse[]>(`/devices/${deviceId}/data/latest`);
  },

  /** 生成模拟数据 */
  async simulate(params: SimulateRequest): Promise<{ status: string; total_data_points: number }> {
    return apiClient.post<{ status: string; total_data_points: number }>(
      '/devices/data/simulate',
      undefined,
      { params }
    );
  },

  /** 生成日报 */
  async generateDailyReport(petId: string, date: string): Promise<DailyReportResponse> {
    return apiClient.post<DailyReportResponse>('/devices/reports/daily', {
      pet_id: petId,
      date,
    });
  },
};