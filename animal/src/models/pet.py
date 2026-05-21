import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Date, Boolean, CHAR, ForeignKey, Enum, Numeric, Text
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
    # ===== P1 扩展字段 =====
    microchip_id = Column(
        String(30),
        nullable=True,
        unique=True,
        comment="芯片号，宠物唯一标识"
    )
    blood_type = Column(
        String(10),
        nullable=True,
        comment="血型: 犬DEA1.1+/DEA1.1-等, 猫A/B/AB"
    )
    current_status = Column(
        Enum("healthy", "ill", "recovering", "chronic", "deceased",
             name="pet_status_enum"),
        default="healthy",
        nullable=False,
        comment="当前健康状态"
    )
    diet_type = Column(
        String(30),
        nullable=True,
        comment="饮食类型: dry_food/wet_food/raw/prescription/mixed"
    )
    spay_neuter_date = Column(
        Date,
        nullable=True,
        comment="绝育日期"
    )
    emergency_contact = Column(
        String(200),
        nullable=True,
        comment="紧急联系人信息"
    )
    source = Column(
        String(20),
        nullable=True,
        comment="来源: purchase/adoption/rescue/gift/other"
    )
    # ===== P0 软删除 =====
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="是否已删除(软删除)"
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

    user = relationship("User", back_populates="pets", lazy="joined")

    def __repr__(self):
        return f"<Pet(pet_id={self.pet_id}, name={self.name}, species={self.species})>"


class PetAllergy(Base):
    """宠物过敏源记录"""
    __tablename__ = "pet_allergies"

    allergy_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="过敏源ID，UUID主键"
    )
    pet_id = Column(
        CHAR(36),
        ForeignKey("pets.pet_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="宠物ID，外键"
    )
    allergen_name = Column(
        String(100),
        nullable=False,
        comment="过敏源名称: 鸡肉/青霉素/尘螨等"
    )
    allergen_type = Column(
        Enum("food", "medication", "environmental", "contact", name="allergen_type_enum"),
        default="food",
        nullable=False,
        comment="过敏源类型: food/medication/environmental/contact"
    )
    severity = Column(
        Enum("mild", "moderate", "severe", "anaphylaxis", name="allergy_severity_enum"),
        default="mild",
        nullable=False,
        comment="严重程度: mild/moderate/severe/anaphylaxis"
    )
    confirmed_by = Column(
        Enum("self", "vet", "test", name="allergy_confirmed_by_enum"),
        default="self",
        nullable=False,
        comment="确认方式: self(自述)/vet(兽医)/test(检测)"
    )
    reaction_desc = Column(
        String(500),
        nullable=True,
        comment="过敏反应描述: 皮肤红疹/呕吐/呼吸困难等"
    )
    first_observed = Column(
        Date,
        nullable=True,
        comment="首次发现日期"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否仍然过敏(可能脱敏)"
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

    pet = relationship("Pet", backref="allergies")

    def __repr__(self):
        return f"<PetAllergy(allergy_id={self.allergy_id}, pet_id={self.pet_id}, allergen={self.allergen_name})>"


class PetVaccination(Base):
    """宠物疫苗接种记录"""
    __tablename__ = "pet_vaccinations"

    vaccination_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="接种记录ID，UUID主键"
    )
    pet_id = Column(
        CHAR(36),
        ForeignKey("pets.pet_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="宠物ID，外键"
    )
    vaccine_name = Column(
        String(100),
        nullable=False,
        comment="疫苗名称: 狂犬疫苗/犬六联/猫三联等"
    )
    vaccine_type = Column(
        Enum("core", "non_core", name="vaccine_type_enum"),
        default="core",
        nullable=False,
        comment="疫苗类型: core(核心)/non_core(非核心)"
    )
    dose_number = Column(
        String(10),
        nullable=True,
        comment="针次: 1/2/3/加强针"
    )
    administered_date = Column(
        Date,
        nullable=False,
        comment="接种日期"
    )
    next_due_date = Column(
        Date,
        nullable=True,
        comment="下次接种到期日期"
    )
    vet_name = Column(
        String(50),
        nullable=True,
        comment="接种兽医姓名"
    )
    hospital = Column(
        String(100),
        nullable=True,
        comment="接种医院/诊所"
    )
    batch_number = Column(
        String(50),
        nullable=True,
        comment="疫苗批号(溯源)"
    )
    manufacturer = Column(
        String(100),
        nullable=True,
        comment="疫苗生产厂商"
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

    pet = relationship("Pet", backref="vaccinations")

    def __repr__(self):
        return f"<PetVaccination(vaccination_id={self.vaccination_id}, vaccine={self.vaccine_name})>"
