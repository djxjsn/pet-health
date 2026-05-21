import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Text, Integer, Date, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from src.core.database import Base


class HealthRecord(Base):
    """宠物健康档案模型"""
    __tablename__ = "health_records"

    record_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="记录ID，UUID主键"
    )
    pet_id = Column(
        CHAR(36),
        ForeignKey("pets.pet_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="宠物ID，外键"
    )
    record_type = Column(
        SAEnum("checkup", "vaccine", "illness", "allergy", "surgery", name="record_type_enum"),
        nullable=False,
        comment="记录类型: checkup/vaccine/illness/allergy/surgery"
    )
    symptoms = Column(
        JSON,
        nullable=True,
        comment="症状列表(简版，字符串数组)"
    )
    structured_symptoms = Column(
        JSON,
        nullable=True,
        comment="结构化症状列表(新版，含name/duration/severity/onset等)"
    )
    diagnosis = Column(
        Text,
        nullable=True,
        comment="诊断结果(简版，纯文本)"
    )
    structured_diagnosis = Column(
        JSON,
        nullable=True,
        comment="结构化诊断结果(新版，含primary/icd_code/differential/confidence等)"
    )
    prescription = Column(
        Text,
        nullable=True,
        comment="处方/用药"
    )
    vet_name = Column(
        String(50),
        nullable=True,
        comment="兽医姓名"
    )
    hospital = Column(
        String(100),
        nullable=True,
        comment="医院/诊所名称"
    )
    record_date = Column(
        Date,
        nullable=True,
        comment="就诊日期"
    )
    next_checkup_date = Column(
        Date,
        nullable=True,
        comment="下次检查日期"
    )
    notes = Column(
        Text,
        nullable=True,
        comment="备注"
    )
    # 软删除
    is_deleted = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="是否已删除(0=否,1=是)"
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="删除时间"
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

    pet = relationship("Pet", backref="health_records")

    def __repr__(self):
        return f"<HealthRecord(record_id={self.record_id}, pet_id={self.pet_id}, type={self.record_type})>"


class Consultation(Base):
    """AI健康咨询记录模型"""
    __tablename__ = "consultations"

    consultation_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="咨询ID，UUID主键"
    )
    user_id = Column(
        CHAR(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID，外键"
    )
    pet_id = Column(
        CHAR(36),
        ForeignKey("pets.pet_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="宠物ID，外键"
    )
    symptoms = Column(
        JSON,
        nullable=True,
        comment="症状列表"
    )
    description = Column(
        Text,
        nullable=True,
        comment="用户描述"
    )
    image_urls = Column(
        JSON,
        nullable=True,
        comment="上传图片URL列表"
    )
    diagnosis_result = Column(
        JSON,
        nullable=True,
        comment="AI诊断结果"
    )
    recommendations = Column(
        JSON,
        nullable=True,
        comment="AI建议列表"
    )
    urgency_level = Column(
        Integer,
        default=1,
        nullable=False,
        comment="紧急程度(1-5, 5为最紧急)"
    )
    status = Column(
        SAEnum("pending", "completed", "cancelled", name="consultation_status_enum"),
        default="pending",
        nullable=False,
        comment="状态: pending/completed/cancelled"
    )
    conversation_id = Column(
        CHAR(36),
        ForeignKey("conversations.conversation_id", ondelete="SET NULL"),
        nullable=True,
        comment="关联对话ID"
    )
    # 软删除
    is_deleted = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="是否已删除(0=否,1=是)"
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="删除时间"
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

    user = relationship("User", backref="consultations")
    pet = relationship("Pet", backref="consultations")
    conversation = relationship("Conversation", backref="consultations")

    def __repr__(self):
        return f"<Consultation(consultation_id={self.consultation_id}, urgency={self.urgency_level})>"
