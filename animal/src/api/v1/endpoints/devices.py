"""
设备管理 + 健康数据 API 端点

端点列表：
  POST   /api/v1/devices                  - 绑定设备
  GET    /api/v1/devices                   - 获取用户设备列表
  GET    /api/v1/devices/{device_id}       - 获取设备详情
  PUT    /api/v1/devices/{device_id}       - 更新设备信息
  DELETE /api/v1/devices/{device_id}       - 解绑设备
  POST   /api/v1/devices/{device_id}/heartbeat  - 设备心跳
  POST   /api/v1/devices/data/report      - 上报健康数据
  GET    /api/v1/devices/data/query       - 查询健康数据
  GET    /api/v1/devices/{device_id}/data/latest  - 获取最新数据
  POST   /api/v1/reports/daily             - 生成日报
  GET    /api/v1/devices/data/simulate     - 生成模拟数据(POC)
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.influxdb import get_influxdb, InfluxDBManager
from src.db.crud import device as device_crud
from src.schemas.device import (
    DeviceCreate, DeviceUpdate, DeviceResponse,
    DeviceDataReport, HealthMetricQuery, HealthMetricResponse,
    HealthAggregationResponse, DailyReportRequest, DailyReportResponse,
)
from src.services.report_service import get_report_service, ReportService
from src.services.device_simulator import create_simulator_for_pet
from src.models.pet import Pet
from src.models.device import Device

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== 设备管理 API ====================

@router.post("/", response_model=DeviceResponse, status_code=201)
def bind_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    """绑定新设备"""
    # 检查序列号是否已绑定
    if payload.serial_number:
        existing = device_crud.get_device_by_serial(db, payload.serial_number)
        if existing:
            raise HTTPException(status_code=409, detail="该设备已被绑定")

    # 检查宠物是否存在
    pet = db.query(Pet).filter(Pet.pet_id == payload.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")

    device = device_crud.create_device(
        db,
        pet_id=payload.pet_id,
        device_name=payload.device_name,
        device_type=payload.device_type,
        brand=payload.brand,
        model=payload.model,
        serial_number=payload.serial_number,
        notes=payload.notes,
    )
    return device


@router.get("/", response_model=List[DeviceResponse])
def list_devices(
    pet_id: Optional[str] = Query(None, description="按宠物ID筛选"),
    db: Session = Depends(get_db),
):
    """获取设备列表"""
    if pet_id:
        return device_crud.get_devices_by_pet(db, pet_id)
    # 返回所有设备（生产环境应按用户过滤）
    return db.query(Device).all()


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device_detail(device_id: str, db: Session = Depends(get_db)):
    """获取设备详情"""
    device = device_crud.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device_info(
    device_id: str,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
):
    """更新设备信息"""
    device = device_crud.update_device(db, device_id, **payload.model_dump(exclude_none=True))
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device


@router.delete("/{device_id}", status_code=204)
def unbind_device(device_id: str, db: Session = Depends(get_db)):
    """解绑设备"""
    success = device_crud.delete_device(db, device_id)
    if not success:
        raise HTTPException(status_code=404, detail="设备不存在")


@router.post("/{device_id}/heartbeat", response_model=DeviceResponse)
def device_heartbeat(device_id: str, db: Session = Depends(get_db)):
    """设备心跳上报"""
    device = device_crud.heartbeat(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    return device


# ==================== 健康数据 API ====================

@router.post("/data/report", status_code=201)
def report_health_data(
    payload: DeviceDataReport,
    influxdb: InfluxDBManager = Depends(get_influxdb),
    db: Session = Depends(get_db),
):
    """设备上报健康数据（批量）"""
    # 验证设备存在
    device = device_crud.get_device(db, payload.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    # 写入 InfluxDB
    metrics = []
    for m in payload.metrics:
        metrics.append({
            "metric_name": m.metric_name,
            "value": m.value,
            "timestamp": m.timestamp or datetime.utcnow(),
        })

    influxdb.write_batch(
        device_id=payload.device_id,
        pet_id=device.pet_id,
        metrics=metrics,
    )

    # 更新设备最后在线时间
    device_crud.heartbeat(db, payload.device_id)

    return {"status": "ok", "count": len(metrics)}


@router.get("/data/query", response_model=List[HealthMetricResponse])
def query_health_data(
    device_id: str = Query(..., description="设备ID"),
    metric_name: Optional[str] = Query(None, description="指标名称"),
    start_time: str = Query(..., description="开始时间 ISO格式"),
    end_time: str = Query(..., description="结束时间 ISO格式"),
    interval: str = Query("1h", description="聚合间隔"),
    influxdb: InfluxDBManager = Depends(get_influxdb),
):
    """查询设备健康时序数据"""
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="时间格式错误，需要 ISO 格式 (YYYY-MM-DDTHH:MM:SS)")

    records = influxdb.query_metrics(
        device_id=device_id,
        metric_name=metric_name,
        start_time=start,
        end_time=end,
        interval=interval,
    )

    # 附加单位信息
    units = {
        "heart_rate": "bpm", "steps": "步", "temperature": "°C",
        "activity_level": "级", "sleep_hours": "小时", "calories": "kcal",
    }
    return [
        HealthMetricResponse(
            metric_name=r["metric_name"],
            value=r["value"],
            unit=units.get(r["metric_name"], ""),
            timestamp=r["timestamp"],
        )
        for r in records
    ]


@router.get("/{device_id}/data/latest", response_model=List[HealthMetricResponse])
def get_latest_data(
    device_id: str,
    influxdb: InfluxDBManager = Depends(get_influxdb),
):
    """获取设备所有指标的最新值"""
    metrics = influxdb.get_all_latest(device_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="暂无数据")

    units = {
        "heart_rate": "bpm", "steps": "步", "temperature": "°C",
        "activity_level": "级", "sleep_hours": "小时", "calories": "kcal",
    }
    return [
        HealthMetricResponse(
            metric_name=m["metric_name"],
            value=m["value"],
            unit=units.get(m["metric_name"], ""),
            timestamp=m["timestamp"],
        )
        for m in metrics
    ]


# ==================== 日报 API ====================

@router.post("/reports/daily", response_model=DailyReportResponse)
def generate_daily_report(
    payload: DailyReportRequest,
    db: Session = Depends(get_db),
):
    """生成宠物健康日报"""
    # 获取宠物信息
    pet = db.query(Pet).filter(Pet.pet_id == payload.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")

    # 获取宠物关联的设备
    devices = device_crud.get_devices_by_pet(db, payload.pet_id)
    if not devices:
        raise HTTPException(status_code=404, detail="该宠物没有绑定设备，无法生成日报")

    # 使用第一个设备生成报告
    device = devices[0]
    report_service = get_report_service()

    collected = report_service.collect_daily_metrics(device.device_id, payload.date)

    if not collected["data_available"]:
        raise HTTPException(status_code=404, detail=f"日期 {payload.date} 暂无健康数据")

    # 使用模板生成（POC阶段，后续可切换到 LLM）
    summary = report_service.generate_template_report(pet.name, collected)

    return DailyReportResponse(
        report_id=str(datetime.utcnow().timestamp()),
        pet_id=payload.pet_id,
        pet_name=pet.name,
        date=payload.date,
        summary=summary,
        metrics_summary=collected["metrics"],
        alerts=collected["alerts"],
        suggestions=report_service._generate_suggestions(
            collected["metrics"], collected["alerts"]
        ),
        generated_at=datetime.utcnow(),
    )


# ==================== POC 模拟数据 API ====================

@router.post("/data/simulate", status_code=201)
def generate_simulated_data(
    pet_id: str = Query(..., description="宠物ID"),
    species: str = Query("dog", description="物种: dog/cat/rabbit"),
    days: int = Query(7, ge=1, le=30, description="模拟天数"),
    interval_minutes: int = Query(15, ge=5, le=60, description="采样间隔(分钟)"),
    db: Session = Depends(get_db),
    influxdb: InfluxDBManager = Depends(get_influxdb),
):
    """
    POC 专用：为指定宠物生成模拟设备数据

    1. 如果宠物没有设备，自动创建一个虚拟设备
    2. 生成指定天数的模拟健康数据写入 InfluxDB
    """
    pet = db.query(Pet).filter(Pet.pet_id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")

    # 查找或创建设备
    devices = device_crud.get_devices_by_pet(db, pet_id)
    if not devices:
        device = device_crud.create_device(
            db,
            pet_id=pet_id,
            device_name=f"{pet.name}的智能项圈",
            device_type="collar",
            brand="generic",
            model="poc-simulator",
        )
    else:
        device = devices[0]

    # 生成模拟数据
    from src.services.device_simulator import generate_poc_data
    all_data = generate_poc_data(
        device_id=device.device_id,
        pet_id=pet_id,
        species=species,
        days=days,
        interval_minutes=interval_minutes,
    )

    # 分批写入 InfluxDB（每批 500 条）
    batch_size = 500
    total_written = 0
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i:i + batch_size]
        influxdb.write_batch(device.device_id, pet_id, batch)
        total_written += len(batch)

    # 更新设备状态
    device_crud.heartbeat(db, device.device_id)

    return {
        "status": "ok",
        "device_id": device.device_id,
        "pet_id": pet_id,
        "days": days,
        "interval_minutes": interval_minutes,
        "total_data_points": total_written,
        "message": f"成功生成 {days} 天模拟数据，共 {total_written} 条数据点",
    }