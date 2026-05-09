import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship

from src.core.database import MySQLBase as Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="用户ID，UUID主键"
    )
    phone = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="手机号码，唯一约束"
    )
    email = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="电子邮箱，唯一约束"
    )
    password_hash = Column(
        String(255),
        nullable=False,
        comment="加密后的密码"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="账户是否激活"
    )
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为超级管理员"
    )
    last_login_at = Column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
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

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined"
    )

    pets = relationship(
        "Pet",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, phone={self.phone})>"
