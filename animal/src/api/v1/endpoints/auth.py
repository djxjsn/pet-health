"""
用户认证端点

提供用户注册、登录、令牌刷新等认证功能
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.core.config import get_settings
from src.db.crud.user import (
    get_user_by_id,
    get_user_by_phone,
    get_user_by_email,
    create_user,
    create_user_profile,
    update_user_login_time,
)
from src.models.user import User
from src.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserFullResponse,
    TokenResponse,
    RefreshTokenRequest,
    UserProfileCreate,
)

settings = get_settings()

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_data: UserCreate,
) -> Any:
    """
    用户注册
    
    - **phone**: 手机号码（必填，11 位）
    - **email**: 电子邮箱（可选）
    - **password**: 密码（必填，至少 8 位，包含字母和数字）
    
    返回:
        UserResponse: 创建的用户信息（不包含密码）
    """
    # 检查手机号是否已存在
    existing_user = get_user_by_phone(db, phone=user_data.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已被注册"
        )
    
    # 检查邮箱是否已存在（如果提供）
    if user_data.email:
        existing_email = get_user_by_email(db, email=user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )
    
    # 创建用户
    user = create_user(db, user_data=user_data)
    
    # 创建用户档案
    profile_data = UserProfileCreate()
    create_user_profile(db, user_id=user.user_id, profile_data=profile_data)
    
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(
    *,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    用户登录（OAuth2 密码流）
    
    - **username**: 手机号或邮箱
    - **password**: 密码
    
    返回:
        TokenResponse: 包含访问令牌和刷新令牌
    """
    # 尝试用手机号查找用户
    user = get_user_by_phone(db, phone=form_data.username)
    
    # 如果手机号未找到，尝试用邮箱查找
    if user is None:
        user = get_user_by_email(db, email=form_data.username)
    
    # 用户不存在或密码错误
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号/邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    # 更新最后登录时间
    update_user_login_time(db, user_id=user.user_id)
    
    # 生成访问令牌和刷新令牌
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    refresh_token = create_refresh_token(data={"sub": user.user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    *,
    db: Session = Depends(get_db),
    token_data: RefreshTokenRequest,
) -> Any:
    """
    刷新访问令牌
    
    使用刷新令牌获取新的访问令牌
    
    返回:
        TokenResponse: 新的访问令牌和刷新令牌
    """
    # 验证刷新令牌
    payload = decode_token(token_data.refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    # 验证令牌类型
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌类型错误"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌中缺少用户 ID"
        )
    
    # 获取用户
    user = get_user_by_id(db, user_id=user_id)
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 生成新的访问令牌和刷新令牌
    access_token = create_access_token(
        data={"sub": user.user_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    new_refresh_token = create_refresh_token(data={"sub": user.user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    *,
    db: Session = Depends(get_db),
    phone: str,
) -> Any:
    """
    忘记密码 - 请求重置密码
    
    - **phone**: 注册手机号
    
    返回:
        dict: 提示信息
    """
    # 查找用户
    user = get_user_by_phone(db, phone=phone)
    
    if user is None or not user.is_active:
        # 为了安全，不提示具体错误
        return {
            "message": "如果该手机号已注册，重置密码链接将发送到您的邮箱"
        }
    
    # TODO: 实现密码重置邮件发送逻辑
    # 这里仅返回成功消息，实际项目中需要：
    # 1. 生成重置令牌
    # 2. 发送邮件到用户邮箱
    # 3. 用户点击链接设置新密码
    
    return {
        "message": "如果该手机号已注册，重置密码链接将发送到您的邮箱"
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    *,
    db: Session = Depends(get_db),
    token: str,
    new_password: str,
) -> Any:
    """
    重置密码
    
    - **token**: 密码重置令牌（从邮件中获取）
    - **new_password**: 新密码
    
    返回:
        dict: 提示信息
    """
    # TODO: 实现密码重置逻辑
    # 1. 验证重置令牌
    # 2. 更新用户密码
    # 3. 使其他令牌失效
    
    return {
        "message": "密码重置成功，请使用新密码登录"
    }
