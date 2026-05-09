import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Date, Boolean, CHAR, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship

from src.core.database import MySQLBase as Base


class Pet(Base):
    __tablename__ = "pets"

    pet_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="宠物ID，UUID主键"
    )
    user_id = Column(
        CHAR(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联用户ID，外键"
    )
    name = Column(
        String(50),
        nullable=False,
        comment="宠物名称"
    )
    species = Column(
        String(20),
        nullable=False,
        comment="物种: dog, cat, bird, rabbit, hamster, fish, other"
    )
    breed = Column(
        String(50),
        nullable=True,
        comment="品种"
    )
    gender = Column(
        Enum("male", "female", "unknown", name="pet_gender_enum"),
        default="unknown",
        nullable=False,
        comment="性别"
    )
    birth_date = Column(
        Date,
        nullable=True,
        comment="出生日期"
    )
    weight = Column(
        Numeric(5, 2),
        nullable=True,
        comment="体重(kg)"
    )
    photo_url = Column(
        String(500),
        nullable=True,
        comment="宠物照片URL"
    )
    is_vaccinated = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已接种疫苗"
    )
    is_neutered = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已绝育"
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

    user = relationship("User", back_populates="pets", lazy="joined")

    def __repr__(self):
        return f"<Pet(pet_id={self.pet_id}, name={self.name}, species={self.species})>"
