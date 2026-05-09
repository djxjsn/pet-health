"""
API 依赖注入

提供常用的依赖项，如数据库会话、当前用户等
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.core.security import decode_token
from src.db.crud.user import get_user_by_id
from src.models.user import User
from src.core.config import get_settings

settings = get_settings()

# OAuth2 密码流配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class TokenPayload(BaseModel):
    """JWT 令牌负载"""
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前登录用户
    
    Args:
        db: 数据库会话
        token: JWT 访问令牌
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 令牌无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码 JWT 令牌
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
            
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # 验证令牌类型
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    return user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前超级管理员用户
    
    Args:
        current_user: 当前用户（通过依赖注入）
        
    Returns:
        User: 超级管理员用户对象
        
    Raises:
        HTTPException: 当前用户不是超级管理员
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户没有超级管理员权限"
        )
    return current_user
