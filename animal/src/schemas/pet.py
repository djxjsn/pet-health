from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


VALID_SPECIES = {"dog", "cat", "bird", "rabbit", "hamster", "fish", "other"}


class PetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="宠物名称")
    species: str = Field(..., min_length=1, max_length=20, description="物种: dog, cat, bird, rabbit, hamster, fish, other")
    breed: Optional[str] = Field(None, max_length=50, description="品种")
    gender: Optional[str] = Field("unknown", description="性别: male, female, unknown")
    birth_date: Optional[date] = Field(None, description="出生日期")
    weight: Optional[Decimal] = Field(None, gt=0, le=999.99, description="体重(kg)")
    photo_url: Optional[str] = Field(None, max_length=500, description="宠物照片URL")
    is_vaccinated: Optional[bool] = Field(False, description="是否已接种疫苗")
    is_neutered: Optional[bool] = Field(False, description="是否已绝育")
    # P1 扩展字段
    microchip_id: Optional[str] = Field(None, max_length=30, description="芯片号")
    blood_type: Optional[str] = Field(None, max_length=10, description="血型")
    current_status: Optional[str] = Field("healthy", description="健康状态: healthy/ill/recovering/chronic/deceased")
    diet_type: Optional[str] = Field(None, max_length=30, description="饮食类型: dry_food/wet_food/raw/prescription/mixed")
    spay_neuter_date: Optional[date] = Field(None, description="绝育日期")
    emergency_contact: Optional[str] = Field(None, max_length=200, description="紧急联系人")
    source: Optional[str] = Field(None, max_length=20, description="来源: purchase/adoption/rescue/gift/other")

    @field_validator("species")
    @classmethod
    def validate_species(cls, v):
        if v.lower() not in VALID_SPECIES:
            raise ValueError(f"物种类型不合法，可选值: {', '.join(sorted(VALID_SPECIES))}")
        return v.lower()

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v not in ("male", "female", "unknown"):
            raise ValueError("性别值不合法，可选值: male, female, unknown")
        return v


class PetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="宠物名称")
    species: Optional[str] = Field(None, min_length=1, max_length=20, description="物种")
    breed: Optional[str] = Field(None, max_length=50, description="品种")
    gender: Optional[str] = Field(None, description="性别: male, female, unknown")
    birth_date: Optional[date] = Field(None, description="出生日期")
    weight: Optional[Decimal] = Field(None, gt=0, le=999.99, description="体重(kg)")
    photo_url: Optional[str] = Field(None, max_length=500, description="宠物照片URL")
    is_vaccinated: Optional[bool] = Field(None, description="是否已接种疫苗")
    is_neutered: Optional[bool] = Field(None, description="是否已绝育")
    # P1 扩展字段
    microchip_id: Optional[str] = Field(None, max_length=30, description="芯片号")
    blood_type: Optional[str] = Field(None, max_length=10, description="血型")
    current_status: Optional[str] = Field(None, description="健康状态")
    diet_type: Optional[str] = Field(None, max_length=30, description="饮食类型")
    spay_neuter_date: Optional[date] = Field(None, description="绝育日期")
    emergency_contact: Optional[str] = Field(None, max_length=200, description="紧急联系人")
    source: Optional[str] = Field(None, max_length=20, description="来源")

    @field_validator("species")
    @classmethod
    def validate_species(cls, v):
        if v is not None and v.lower() not in VALID_SPECIES:
            raise ValueError(f"物种类型不合法，可选值: {', '.join(sorted(VALID_SPECIES))}")
        return v.lower() if v is not None else v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ("male", "female", "unknown"):
            raise ValueError("性别值不合法，可选值: male, female, unknown")
        return v


class PetResponse(BaseModel):
    pet_id: str
    user_id: str
    name: str
    species: str
    breed: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    weight: Optional[Decimal] = None
    photo_url: Optional[str] = None
    is_vaccinated: bool = False
    is_neutered: bool = False
    # P1 扩展字段
    microchip_id: Optional[str] = None
    blood_type: Optional[str] = None
    current_status: str = "healthy"
    diet_type: Optional[str] = None
    spay_neuter_date: Optional[date] = None
    emergency_contact: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PetListResponse(BaseModel):
    items: List[PetResponse]
    total: int
    page: int
    page_size: int


# ==================== 过敏源 Schemas ====================

class AllergyCreate(BaseModel):
    allergen_name: str = Field(..., min_length=1, max_length=100, description="过敏源名称")
    allergen_type: str = Field("food", description="类型: food/medication/environmental/contact")
    severity: str = Field("mild", description="严重程度: mild/moderate/severe/anaphylaxis")
    confirmed_by: str = Field("self", description="确认方式: self/vet/test")
    reaction_desc: Optional[str] = Field(None, max_length=500, description="过敏反应描述")
    first_observed: Optional[date] = Field(None, description="首次发现日期")
    is_active: Optional[bool] = Field(True, description="是否仍然过敏")


class AllergyUpdate(BaseModel):
    allergen_name: Optional[str] = Field(None, max_length=100)
    allergen_type: Optional[str] = Field(None)
    severity: Optional[str] = Field(None)
    confirmed_by: Optional[str] = Field(None)
    reaction_desc: Optional[str] = Field(None, max_length=500)
    first_observed: Optional[date] = Field(None)
    is_active: Optional[bool] = Field(None)


class AllergyResponse(BaseModel):
    allergy_id: str
    pet_id: str
    allergen_name: str
    allergen_type: str
    severity: str
    confirmed_by: str
    reaction_desc: Optional[str] = None
    first_observed: Optional[date] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== 疫苗 Schemas ====================

class VaccinationCreate(BaseModel):
    vaccine_name: str = Field(..., min_length=1, max_length=100, description="疫苗名称")
    vaccine_type: str = Field("core", description="类型: core/non_core")
    dose_number: Optional[str] = Field(None, max_length=10, description="针次: 1/2/3/加强针")
    administered_date: date = Field(..., description="接种日期")
    next_due_date: Optional[date] = Field(None, description="下次接种到期日期")
    vet_name: Optional[str] = Field(None, max_length=50, description="接种兽医")
    hospital: Optional[str] = Field(None, max_length=100, description="接种医院")
    batch_number: Optional[str] = Field(None, max_length=50, description="疫苗批号")
    manufacturer: Optional[str] = Field(None, max_length=100, description="生产厂商")
    notes: Optional[str] = Field(None, description="备注")


class VaccinationUpdate(BaseModel):
    vaccine_name: Optional[str] = Field(None, max_length=100)
    vaccine_type: Optional[str] = Field(None)
    dose_number: Optional[str] = Field(None, max_length=10)
    administered_date: Optional[date] = Field(None)
    next_due_date: Optional[date] = Field(None)
    vet_name: Optional[str] = Field(None, max_length=50)
    hospital: Optional[str] = Field(None, max_length=100)
    batch_number: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None)


class VaccinationResponse(BaseModel):
    vaccination_id: str
    pet_id: str
    vaccine_name: str
    vaccine_type: str
    dose_number: Optional[str] = None
    administered_date: date
    next_due_date: Optional[date] = None
    vet_name: Optional[str] = None
    hospital: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturer: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ==================== 体重追踪 Schema ====================

class WeightRecordCreate(BaseModel):
    weight: Decimal = Field(..., gt=0, le=999.99, description="体重(kg)")
    recorded_at: Optional[datetime] = Field(None, description="记录时间，默认当前时间")


class WeightRecordResponse(BaseModel):
    pet_id: str
    weight: float
    unit: str = "kg"
    timestamp: datetime


# ==================== 宠物共享 Schemas ====================

class PetOwnerCreate(BaseModel):
    pet_id: str = Field(..., description="宠物ID")
    user_id: str = Field(..., description="被授权用户ID")
    role: str = Field("family", description="角色: owner/family/vet/sitter")
    permission: str = Field("view", description="权限: view/edit/full")
    expires_at: Optional[datetime] = Field(None, description="过期时间(临时授权)")


class PetOwnerUpdate(BaseModel):
    role: Optional[str] = Field(None)
    permission: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    expires_at: Optional[datetime] = Field(None)


class PetOwnerResponse(BaseModel):
    id: str
    pet_id: str
    user_id: str
    role: str
    permission: str
    granted_by: Optional[str] = None
    granted_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}