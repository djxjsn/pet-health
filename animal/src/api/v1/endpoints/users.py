"""
用户管理端点

提供用户信息查询、更新等功能
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.db.crud.user import get_user_by_id, get_user_by_phone, get_user_by_email
from src.models.user import User
from src.schemas.user import (
    UserResponse,
    UserUpdate,
    UserFullResponse,
    UserProfileUpdate,
    UserProfileResponse,
)
from src.api.deps import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserFullResponse)
def get_current_user_info(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取当前登录用户信息
    
    需要认证
    
    返回:
        UserFullResponse: 用户基本信息和档案信息
    """
    return {
        "user": current_user,
        "profile": current_user.profile if current_user.profile else None,
    }


@router.put("/me", response_model=UserResponse)
def update_current_user(
    *,
    db: Session = Depends(get_db),
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新当前用户信息
    
    - **phone**: 新手机号（可选）
    - **email**: 新邮箱（可选）
    
    需要认证
    
    返回:
        UserResponse: 更新后的用户信息
    """
    # 更新手机号
    if user_data.phone is not None and user_data.phone != current_user.phone:
        # 检查新手机号是否已被使用
        existing_user = get_user_by_phone(db, phone=user_data.phone)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被其他用户使用"
            )
        current_user.phone = user_data.phone
    
    # 更新邮箱
    if user_data.email is not None and user_data.email != current_user.email:
        # 检查新邮箱是否已被使用
        existing_email = get_user_by_email(db, email=user_data.email)
        if existing_email and existing_email.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被其他用户使用"
            )
        current_user.email = user_data.email
    
    # 提交更改
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.put("/me/profile", response_model=UserProfileResponse)
def update_current_user_profile(
    *,
    db: Session = Depends(get_db),
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    更新当前用户档案信息
    
    - **full_name**: 真实姓名
    - **gender**: 性别
    - **date_of_birth**: 出生日期
    - **avatar_url**: 头像 URL
    - **address**: 联系地址
    - **bio**: 个人简介
    
    需要认证
    
    返回:
        UserProfileResponse: 更新后的档案信息
    """
    from src.models.user_profile import UserProfile
    
    # 获取或创建用户档案
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()
    
    if profile is None:
        # 如果档案不存在，创建一个新的
        profile = UserProfile(
            user_id=current_user.user_id,
            **profile_data.model_dump(exclude_unset=True)
        )
        db.add(profile)
    else:
        # 更新现有档案
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile
