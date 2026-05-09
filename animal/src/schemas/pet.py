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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PetListResponse(BaseModel):
    items: List[PetResponse]
    total: int
    page: int
    page_size: int
