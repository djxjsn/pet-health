from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class UserCreate(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20, description="手机号码")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    password: str = Field(..., min_length=8, max_length=128, description="密码")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("密码长度不能少于8位")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    phone: str = Field(..., description="手机号码")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    user_id: str
    phone: str
    email: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileCreate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    gender: Optional[str] = Field("unspecified", description="性别")
    date_of_birth: Optional[date] = Field(None, description="出生日期")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    address: Optional[str] = Field(None, max_length=500, description="联系地址")
    bio: Optional[str] = Field(None, description="个人简介")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v not in ("male", "female", "other", "unspecified"):
            raise ValueError("性别值不合法")
        return v


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None


class UserProfileResponse(BaseModel):
    profile_id: str
    user_id: str
    full_name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None
    pet_count: int = 0
    address: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserFullResponse(BaseModel):
    user: UserResponse
    profile: Optional[UserProfileResponse] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str
