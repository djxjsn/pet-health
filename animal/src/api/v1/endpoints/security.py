"""
数据安全 API 端点

提供数据安全相关的管理接口，包括：
- 加密/解密操作
- 数据脱敏预览
- RBAC 角色权限查询
- 审计日志查询
- 安全事件监控
"""
import logging
from typing import Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from src.core.encryption import get_encryption_service, EncryptionService
from src.core.data_masker import get_data_masker, DataMasker, MaskStrategy
from src.core.rbac import (
    get_role_service, RoleService, Role, Permission,
    require_permission, require_role, SecurityContext,
)
from src.core.audit import (
    get_audit_service, AuditLogService, AuditAction, AuditLogLevel,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== Schemas ==========

class EncryptRequest(BaseModel):
    plaintext: str = Field(..., description="待加密的明文")
    field_name: Optional[str] = Field(None, description="字段名（用于关联数据认证）")


class DecryptRequest(BaseModel):
    encrypted_text: str = Field(..., description="待解密的密文")
    field_name: Optional[str] = Field(None, description="字段名")


class MaskRequest(BaseModel):
    value: str = Field(..., description="待脱敏的值")
    strategy: str = Field(..., description="脱敏策略: phone/email/id_card/name/address/bank_card/password/ip_address/custom")
    visible_prefix: int = Field(2, description="自定义策略-可见前缀长度")
    visible_suffix: int = Field(2, description="自定义策略-可见后缀长度")


class AuditLogQuery(BaseModel):
    user_id: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    level: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=200)


# ========== 加密/解密端点 ==========

@router.post("/encrypt")
def encrypt_data(request: EncryptRequest):
    """加密数据"""
    try:
        service = get_encryption_service()
        
        if request.field_name:
            encrypted = service.encrypt_field(request.plaintext, request.field_name)
        else:
            encrypted = service.encrypt(request.plaintext)
        
        return {
            "encrypted": encrypted,
            "field_name": request.field_name,
            "algorithm": "AES-256-GCM"
        }
    except Exception as e:
        logger.error(f"加密失败: {e}")
        raise HTTPException(status_code=500, detail=f"加密失败: {str(e)}")


@router.post("/decrypt")
def decrypt_data(request: DecryptRequest):
    """解密数据"""
    try:
        service = get_encryption_service()
        
        if request.field_name:
            decrypted = service.decrypt_field(request.encrypted_text, request.field_name)
        else:
            decrypted = service.decrypt(request.encrypted_text)
        
        return {
            "decrypted": decrypted,
            "field_name": request.field_name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"解密失败: {e}")
        raise HTTPException(status_code=500, detail=f"解密失败: {str(e)}")


# ========== 脱敏端点 ==========

@router.post("/mask")
def mask_data(request: MaskRequest):
    """数据脱敏预览"""
    try:
        masker = get_data_masker()
        
        strategy_map = {
            "phone": MaskStrategy.PHONE,
            "email": MaskStrategy.EMAIL,
            "id_card": MaskStrategy.ID_CARD,
            "name": MaskStrategy.NAME,
            "address": MaskStrategy.ADDRESS,
            "bank_card": MaskStrategy.BANK_CARD,
            "password": MaskStrategy.PASSWORD,
            "ip_address": MaskStrategy.IP_ADDRESS,
            "custom": MaskStrategy.CUSTOM,
        }
        
        strategy = strategy_map.get(request.strategy)
        if not strategy:
            raise HTTPException(status_code=400, detail=f"不支持的脱敏策略: {request.strategy}")
        
        if strategy == MaskStrategy.CUSTOM:
            masked = masker.mask_custom(
                request.value,
                visible_prefix=request.visible_prefix,
                visible_suffix=request.visible_suffix
            )
        else:
            masked = masker.mask(request.value, strategy)
        
        return {
            "original_length": len(request.value),
            "masked": masked,
            "strategy": request.strategy
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"脱敏失败: {e}")
        raise HTTPException(status_code=500, detail=f"脱敏失败: {str(e)}")


# ========== RBAC 端点 ==========

@router.get("/roles")
def list_roles():
    """列出所有角色及其权限"""
    service = get_role_service()
    return {
        "roles": service.list_roles(),
        "total": len(Role)
    }


@router.get("/permissions")
def list_permissions():
    """列出所有可用权限"""
    permissions = [
        {
            "code": p.value,
            "category": p.value.split(":")[0],
            "name": p.value.split(":")[1]
        }
        for p in Permission
    ]
    
    categories = {}
    for p in permissions:
        cat = p["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p)
    
    return {
        "permissions": permissions,
        "categories": categories,
        "total": len(permissions)
    }


@router.get("/role/{role_name}/permissions")
def get_role_permissions(role_name: str):
    """获取指定角色的权限列表"""
    try:
        role = Role(role_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的角色名: {role_name}")
    
    service = get_role_service()
    perms = service.get_role_permissions(role)
    
    return {
        "role": role_name,
        "permissions": [p.value for p in sorted(perms, key=lambda x: x.value)],
        "permission_count": len(perms)
    }


# ========== 审计日志端点 ==========

@router.get("/audit/logs")
def query_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """查询审计日志"""
    try:
        service = get_audit_service()
        result = service.query_logs(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            level=level,
            skip=skip,
            limit=limit,
        )
        return result
    except Exception as e:
        logger.error(f"查询审计日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/audit/security-events")
def get_security_events(hours: int = Query(24, ge=1, le=168)):
    """获取最近的安全事件"""
    try:
        service = get_audit_service()
        events = service.get_security_events(hours=hours)
        return {
            "events": events,
            "total": len(events),
            "hours": hours
        }
    except Exception as e:
        logger.error(f"获取安全事件失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/audit/user-activity/{user_id}")
def get_user_activity(user_id: str, days: int = Query(30, ge=1, le=365)):
    """获取用户活动摘要"""
    try:
        service = get_audit_service()
        return service.get_user_activity_summary(user_id, days)
    except Exception as e:
        logger.error(f"获取用户活动摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# ========== 安全概览端点 ==========

@router.get("/overview")
def security_overview():
    """安全模块概览"""
    return {
        "module": "M7 数据安全与隐私",
        "version": "1.0.0",
        "features": {
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_derivation": "PBKDF2-SHA256",
                "iterations": 100000,
                "status": "active"
            },
            "data_masking": {
                "strategies": ["phone", "email", "id_card", "name", "address", "bank_card", "password", "ip_address", "custom"],
                "status": "active"
            },
            "rbac": {
                "roles": len(Role),
                "permissions": len(Permission),
                "status": "active"
            },
            "audit": {
                "storage": "MongoDB",
                "immutable": True,
                "status": "active"
            }
        },
        "token_security": {
            "access_token_ttl_minutes": 120,
            "refresh_token_ttl_days": 7,
            "algorithm": "HS256"
        }
    }
