import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Date, Text, CHAR, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship

from src.core.database import MySQLBase as Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="档案ID，UUID主键"
    )
    user_id = Column(
        CHAR(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="关联用户ID，外键+唯一约束实现一对一"
    )
    full_name = Column(
        String(100),
        nullable=True,
        comment="用户真实姓名"
    )
    gender = Column(
        Enum("male", "female", "other", "unspecified", name="gender_enum"),
        default="unspecified",
        nullable=False,
        comment="性别"
    )
    date_of_birth = Column(
        Date,
        nullable=True,
        comment="出生日期"
    )
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="头像URL地址"
    )
    pet_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="宠物数量"
    )
    address = Column(
        String(500),
        nullable=True,
        comment="联系地址"
    )
    bio = Column(
        Text,
        nullable=True,
        comment="个人简介"
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

    user = relationship(
        "User",
        back_populates="profile",
        lazy="joined"
    )

    def __repr__(self):
        return f"<UserProfile(profile_id={self.profile_id}, user_id={self.user_id}, full_name={self.full_name})>"
