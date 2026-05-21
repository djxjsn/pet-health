"""
设备与健康数据 Pydantic 校验模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 设备管理 Schemas ====================

class DeviceCreate(BaseModel):
    """创建/绑定设备请求"""
    pet_id: str = Field(..., description="绑定的宠物ID")
    device_name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    device_type: str = Field(default="collar", description="设备类型: collar/positioning_tag/feeder/litter_box/camera/other")
    brand: str = Field(..., min_length=1, max_length=50, description="品牌")
    model: Optional[str] = Field(None, max_length=50, description="型号")
    serial_number: Optional[str] = Field(None, max_length=100, description="序列号")
    notes: Optional[str] = Field(None, description="备注")


class DeviceUpdate(BaseModel):
    """更新设备信息"""
    device_name: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, description="设备状态: online/offline/maintenance/unbound")
    battery_level: Optional[str] = Field(None)
    firmware_version: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None)


class DeviceResponse(BaseModel):
    """设备信息响应"""
    device_id: str
    pet_id: str
    device_name: str
    device_type: str
    brand: str
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    status: str
    last_online_at: Optional[datetime] = None
    battery_level: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== 健康数据 Schemas ====================

class HealthMetricPoint(BaseModel):
    """单条健康指标数据点"""
    metric_name: str = Field(..., description="指标名称: heart_rate/steps/temperature/activity_level/sleep_hours/calories")
    value: float = Field(..., description="指标数值")
    timestamp: Optional[datetime] = Field(None, description="数据时间戳，默认当前时间")
    unit: Optional[str] = Field(None, description="单位: bpm/步/°C/级别/小时/kcal")


class DeviceDataReport(BaseModel):
    """设备数据上报请求（批量）"""
    device_id: str = Field(..., description="设备ID")
    metrics: List[HealthMetricPoint] = Field(..., min_length=1, max_length=50, description="健康指标数据点列表")


class HealthMetricQuery(BaseModel):
    """健康数据查询请求"""
    device_id: str = Field(..., description="设备ID")
    metric_name: Optional[str] = Field(None, description="指标名称，不传则查全部")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    interval: Optional[str] = Field(default="1h", description="聚合间隔: 1m/5m/15m/1h/1d")


class HealthMetricResponse(BaseModel):
    """健康数据查询响应"""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime


class HealthAggregationResponse(BaseModel):
    """健康数据聚合统计响应"""
    metric_name: str
    unit: str
    avg: float
    min: float
    max: float
    latest: float
    count: int


# ==================== 日报 Schemas ====================

class DailyReportRequest(BaseModel):
    """日报生成请求"""
    pet_id: str = Field(..., description="宠物ID")
    date: str = Field(..., description="报告日期 YYYY-MM-DD")


class DailyReportResponse(BaseModel):
    """日报响应"""
    report_id: str
    pet_id: str
    pet_name: str
    date: str
    summary: str = Field(description="健康总结")
    metrics_summary: dict = Field(description="各指标统计摘要")
    alerts: List[dict] = Field(default_factory=list, description="预警列表")
    suggestions: List[str] = Field(default_factory=list, description="健康建议")
    generated_at: datetime


# ==================== 预警 Schemas ====================

class AlertRule(BaseModel):
    """预警规则"""
    rule_id: str
    metric_name: str
    condition: str = Field(description="条件: gt/lt/outside")
    threshold_low: Optional[float] = None
    threshold_high: Optional[float] = None
    enabled: bool = True


class AlertEvent(BaseModel):
    """预警事件"""
    device_id: str
    pet_id: str
    rule_id: str
    metric_name: str
    value: float
    threshold: float
    message: str
    severity: str = Field(description="严重程度: warning/critical")
    triggered_at: datetime