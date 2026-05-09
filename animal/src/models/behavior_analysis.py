import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from src.core.database import Base


class BehaviorAnalysis(Base):
    """宠物行为分析记录模型"""
    __tablename__ = "behavior_analyses"

    analysis_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="分析ID，UUID主键"
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
    behavior_description = Column(
        Text,
        nullable=True,
        comment="行为描述"
    )
    behavior_category = Column(
        SAEnum(
            "destructive", "howling", "aggression",
            "food_refusal", "excessive_licking", "other",
            name="behavior_category_enum"
        ),
        nullable=True,
        comment="行为类别: destructive/howling/aggression/food_refusal/excessive_licking/other"
    )
    possible_causes = Column(
        JSON,
        nullable=True,
        comment='可能原因列表 [{"cause":"...", "probability":0.8, "category":"breed/age/environment"}]'
    )
    breed_analysis = Column(
        JSON,
        nullable=True,
        comment="品种特性分析结果"
    )
    recommendations = Column(
        JSON,
        nullable=True,
        comment="训练建议列表"
    )
    severity_level = Column(
        Integer,
        default=1,
        nullable=False,
        comment="严重程度(1-5, 5为最严重)"
    )
    status = Column(
        SAEnum("pending", "completed", name="behavior_analysis_status_enum"),
        default="pending",
        nullable=False,
        comment="状态: pending/completed"
    )
    conversation_id = Column(
        CHAR(36),
        ForeignKey("conversations.conversation_id", ondelete="SET NULL"),
        nullable=True,
        comment="关联对话ID"
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

    user = relationship("User", backref="behavior_analyses")
    pet = relationship("Pet", backref="behavior_analyses")
    conversation = relationship("Conversation", backref="behavior_analyses")

    def __repr__(self):
        return f"<BehaviorAnalysis(analysis_id={self.analysis_id}, severity={self.severity_level})>"
