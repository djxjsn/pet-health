"""设备管理 CRUD 操作"""
import logging
from typing import Optional, List
from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from src.models.device import Device

logger = logging.getLogger(__name__)


def create_device(db: Session, **kwargs) -> Device:
    """创建/绑定新设备"""
    device = Device(
        device_id=str(uuid4()),
        device_name=kwargs["device_name"],
        device_type=kwargs.get("device_type", "collar"),
        brand=kwargs["brand"],
        model=kwargs.get("model"),
        serial_number=kwargs.get("serial_number"),
        pet_id=kwargs["pet_id"],
        notes=kwargs.get("notes"),
        status="online",
        last_online_at=datetime.utcnow(),
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def get_device(db: Session, device_id: str) -> Optional[Device]:
    """获取单个设备信息"""
    return db.query(Device).filter(Device.device_id == device_id).first()


def get_device_by_serial(db: Session, serial_number: str) -> Optional[Device]:
    """通过序列号查找设备"""
    return db.query(Device).filter(Device.serial_number == serial_number).first()


def get_devices_by_pet(db: Session, pet_id: str) -> List[Device]:
    """获取某宠物的所有设备"""
    return db.query(Device).filter(Device.pet_id == pet_id).all()


def get_devices_by_user(db: Session, user_id: str) -> List[Device]:
    """获取某用户所有宠物的设备（通过 Pet 表关联）"""
    from src.models.pet import Pet
    pet_ids = db.query(Pet.pet_id).filter(Pet.user_id == user_id).all()
    pet_ids = [p[0] for p in pet_ids]
    if not pet_ids:
        return []
    return db.query(Device).filter(Device.pet_id.in_(pet_ids)).all()


def update_device(db: Session, device_id: str, **kwargs) -> Optional[Device]:
    """更新设备信息"""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        return None

    updatable_fields = [
        "device_name", "status", "battery_level",
        "firmware_version", "notes"
    ]
    for field in updatable_fields:
        if field in kwargs and kwargs[field] is not None:
            setattr(device, field, kwargs[field])

    if kwargs.get("status") == "online":
        device.last_online_at = datetime.utcnow()

    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: str) -> bool:
    """删除/解绑设备"""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        return False
    db.delete(device)
    db.commit()
    return True


def heartbeat(db: Session, device_id: str) -> Optional[Device]:
    """设备心跳上报，更新在线时间"""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        return None
    device.status = "online"
    device.last_online_at = datetime.utcnow()
    db.commit()
    db.refresh(device)
    return device