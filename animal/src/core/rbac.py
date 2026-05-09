"""
RBAC 权限控制服务

提供基于角色的访问控制，包括：
- 角色定义与权限管理
- 权限检查装饰器
- FastAPI 依赖注入
"""
import logging
from typing import List, Optional, Set, Dict, Any
from enum import Enum
from functools import wraps
from datetime import datetime

from fastapi import HTTPException, status, Depends
from pydantic import BaseModel, Field

from src.core.security import decode_token
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class Permission(Enum):
    """权限枚举"""
    # 用户管理
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # 宠物管理
    PET_READ = "pet:read"
    PET_WRITE = "pet:write"
    PET_DELETE = "pet:delete"
    
    # 健康咨询
    HEALTH_READ = "health:read"
    HEALTH_WRITE = "health:write"
    
    # 购物
    SHOP_READ = "shop:read"
    SHOP_WRITE = "shop:write"
    
    # 知识库
    KNOWLEDGE_READ = "knowledge:read"
    KNOWLEDGE_WRITE = "knowledge:write"
    
    # 系统管理
    ADMIN_PANEL = "admin:panel"
    AUDIT_LOG_READ = "audit:read"
    SECURITY_CONFIG = "security:config"
    
    # 数据安全
    DATA_EXPORT = "data:export"
    DATA_ENCRYPTION = "data:encryption"


class Role(Enum):
    """角色枚举"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    VETERINARIAN = "veterinarian"
    USER = "user"
    GUEST = "guest"


ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),
    
    Role.ADMIN: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.PET_READ,
        Permission.PET_WRITE,
        Permission.PET_DELETE,
        Permission.HEALTH_READ,
        Permission.HEALTH_WRITE,
        Permission.SHOP_READ,
        Permission.SHOP_WRITE,
        Permission.KNOWLEDGE_READ,
        Permission.KNOWLEDGE_WRITE,
        Permission.ADMIN_PANEL,
        Permission.AUDIT_LOG_READ,
        Permission.DATA_EXPORT,
    },
    
    Role.VETERINARIAN: {
        Permission.USER_READ,
        Permission.PET_READ,
        Permission.PET_WRITE,
        Permission.HEALTH_READ,
        Permission.HEALTH_WRITE,
        Permission.SHOP_READ,
        Permission.KNOWLEDGE_READ,
        Permission.KNOWLEDGE_WRITE,
    },
    
    Role.USER: {
        Permission.USER_READ,
        Permission.PET_READ,
        Permission.PET_WRITE,
        Permission.HEALTH_READ,
        Permission.SHOP_READ,
        Permission.KNOWLEDGE_READ,
    },
    
    Role.GUEST: {
        Permission.HEALTH_READ,
        Permission.SHOP_READ,
        Permission.KNOWLEDGE_READ,
    },
}


class RoleService:
    """角色权限服务"""

    @staticmethod
    def get_role_permissions(role: Role) -> Set[Permission]:
        """获取角色的所有权限"""
        return ROLE_PERMISSIONS.get(role, set())

    @staticmethod
    def has_permission(role: Role, permission: Permission) -> bool:
        """检查角色是否拥有指定权限"""
        return permission in ROLE_PERMISSIONS.get(role, set())

    @staticmethod
    def has_any_permission(role: Role, permissions: List[Permission]) -> bool:
        """检查角色是否拥有任一权限"""
        role_perms = ROLE_PERMISSIONS.get(role, set())
        return bool(role_perms.intersection(set(permissions)))

    @staticmethod
    def has_all_permissions(role: Role, permissions: List[Permission]) -> bool:
        """检查角色是否拥有全部权限"""
        role_perms = ROLE_PERMISSIONS.get(role, set())
        return set(permissions).issubset(role_perms)

    @staticmethod
    def get_role_from_user(user: Dict[str, Any]) -> Role:
        """从用户数据中提取角色"""
        if user.get("is_superuser"):
            return Role.SUPER_ADMIN
        
        role_str = user.get("role", "user")
        try:
            return Role(role_str)
        except ValueError:
            return Role.USER

    @staticmethod
    def list_roles() -> List[Dict[str, Any]]:
        """列出所有角色及其权限"""
        result = []
        for role in Role:
            perms = ROLE_PERMISSIONS.get(role, set())
            result.append({
                "role": role.value,
                "permissions": [p.value for p in sorted(perms, key=lambda x: x.value)],
                "permission_count": len(perms)
            })
        return result


class SecurityContext:
    """安全上下文"""

    def __init__(
        self,
        user_id: str,
        role: Role,
        permissions: Set[Permission],
        token: Optional[str] = None
    ):
        self.user_id = user_id
        self.role = role
        self.permissions = permissions
        self.token = token
        self.created_at = datetime.utcnow()

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

    def has_any_permission(self, permissions: List[Permission]) -> bool:
        return bool(self.permissions.intersection(set(permissions)))

    def is_admin(self) -> bool:
        return self.role in (Role.SUPER_ADMIN, Role.ADMIN)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "is_admin": self.is_admin()
        }


def create_security_context(user: Dict[str, Any], token: Optional[str] = None) -> SecurityContext:
    """从用户数据创建安全上下文"""
    role = RoleService.get_role_from_user(user)
    permissions = RoleService.get_role_permissions(role)
    return SecurityContext(
        user_id=user.get("user_id", ""),
        role=role,
        permissions=permissions,
        token=token
    )


def require_permission(*required_permissions: Permission):
    """
    权限检查依赖注入
    
    用法:
        @router.get("/admin/users", dependencies=[Depends(require_permission(Permission.USER_READ))])
    """
    async def _check_permission(token: str = "") -> SecurityContext:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证令牌"
            )
        
        payload = decode_token(token.replace("Bearer ", ""))
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌中缺少用户标识"
            )
        
        is_superuser = payload.get("is_superuser", False)
        role = Role.SUPER_ADMIN if is_superuser else Role(payload.get("role", "user"))
        permissions = RoleService.get_role_permissions(role)
        
        ctx = SecurityContext(
            user_id=user_id,
            role=role,
            permissions=permissions,
            token=token
        )
        
        for perm in required_permissions:
            if not ctx.has_permission(perm):
                logger.warning(f"用户 {user_id} 缺少权限: {perm.value}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足: 需要 {perm.value}"
                )
        
        return ctx
    
    return _check_permission


def require_role(*required_roles: Role):
    """
    角色检查依赖注入
    """
    async def _check_role(token: str = "") -> SecurityContext:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证令牌"
            )
        
        payload = decode_token(token.replace("Bearer ", ""))
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌"
            )
        
        user_id = payload.get("sub")
        is_superuser = payload.get("is_superuser", False)
        role = Role.SUPER_ADMIN if is_superuser else Role(payload.get("role", "user"))
        
        if role not in required_roles:
            logger.warning(f"用户 {user_id} 角色不符: 需要 {[r.value for r in required_roles]}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"角色不足: 需要 {[r.value for r in required_roles]}"
            )
        
        permissions = RoleService.get_role_permissions(role)
        return SecurityContext(
            user_id=user_id,
            role=role,
            permissions=permissions,
            token=token
        )
    
    return _check_role


def get_role_service() -> RoleService:
    """获取角色服务实例"""
    return RoleService()
