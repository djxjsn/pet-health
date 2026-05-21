"""
设备与设备健康数据模型
- Device: MySQL 存储设备元数据（品牌、型号、绑定宠物等）
- 时序健康数据存储在 InfluxDB 中
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, CHAR, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from src.core.database import MySQLBase as Base


class Device(Base):
    """可穿戴健康设备模型"""
    __tablename__ = "devices"

    device_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="设备ID，UUID主键"
    )
    pet_id = Column(
        CHAR(36),
        ForeignKey("pets.pet_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="绑定的宠物ID，外键"
    )
    device_name = Column(
        String(100),
        nullable=False,
        comment="设备名称"
    )
    device_type = Column(
        Enum("collar", "positioning_tag", "feeder", "litter_box", "camera", "other",
             name="device_type_enum"),
        default="collar",
        nullable=False,
        comment="设备类型: collar/positioning_tag/feeder/litter_box/camera/other"
    )
    brand = Column(
        String(50),
        nullable=False,
        comment="品牌: xiaomi/huawei/apple/generic"
    )
    model = Column(
        String(50),
        nullable=True,
        comment="设备型号"
    )
    serial_number = Column(
        String(100),
        nullable=True,
        unique=True,
        comment="设备序列号"
    )
    firmware_version = Column(
        String(20),
        nullable=True,
        comment="固件版本"
    )
    status = Column(
        Enum("online", "offline", "maintenance", "unbound",
             name="device_status_enum"),
        default="offline",
        nullable=False,
        comment="设备状态: online/offline/maintenance/unbound"
    )
    last_online_at = Column(
        DateTime,
        nullable=True,
        comment="最后在线时间"
    )
    battery_level = Column(
        String(10),
        nullable=True,
        comment="电量百分比"
    )
    notes = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )

    pet = relationship("Pet", backref="devices")

    def __repr__(self):
        return f"<Device(device_id={self.device_id}, name={self.device_name}, type={self.device_type})>"