"""
审计日志服务

提供完整的操作审计追踪，包括：
- 用户操作记录
- 数据变更追踪
- 安全事件记录
- 日志查询与统计
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

from pymongo import MongoClient
from pymongo.collection import Collection

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class AuditAction(Enum):
    """审计操作类型"""
    # 认证相关
    LOGIN = "auth:login"
    LOGOUT = "auth:logout"
    LOGIN_FAILED = "auth:login_failed"
    TOKEN_REFRESH = "auth:token_refresh"
    PASSWORD_CHANGE = "auth:password_change"
    PASSWORD_RESET = "auth:password_reset"
    
    # 用户管理
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_READ = "user:read"
    
    # 宠物管理
    PET_CREATE = "pet:create"
    PET_UPDATE = "pet:update"
    PET_DELETE = "pet:delete"
    
    # 健康数据
    HEALTH_CONSULT = "health:consult"
    HEALTH_RECORD_CREATE = "health_record:create"
    HEALTH_RECORD_UPDATE = "health_record:update"
    
    # 购物相关
    SHOP_SEARCH = "shop:search"
    SHOP_PURCHASE = "shop:purchase"
    
    # 数据安全
    DATA_EXPORT = "data:export"
    DATA_ENCRYPT = "data:encrypt"
    DATA_DECRYPT = "data:decrypt"
    PERMISSION_CHANGE = "security:permission_change"
    ROLE_CHANGE = "security:role_change"
    
    # 系统操作
    SYSTEM_CONFIG = "system:config"
    SYSTEM_ERROR = "system:error"


class AuditLogLevel(Enum):
    """审计日志级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AuditLogService:
    """
    审计日志服务
    
    特性：
    - 不可变日志（仅追加，不修改不删除）
    - 自动记录操作上下文
    - 支持按时间/用户/操作类型查询
    - 安全事件自动升级
    """

    COLLECTION_NAME = "audit_logs"

    def __init__(self):
        settings = get_settings()
        self._client = MongoClient(settings.MONGODB_URL)
        self._db = self._client[settings.MONGODB_DATABASE]
        self._collection: Collection = self._db[self.COLLECTION_NAME]
        self._ensure_indexes()

    def _ensure_indexes(self):
        """确保必要的索引存在"""
        try:
            self._collection.create_index([("timestamp", -1)])
            self._collection.create_index([("user_id", 1)])
            self._collection.create_index([("action", 1)])
            self._collection.create_index([("level", 1)])
            self._collection.create_index([("resource_type", 1), ("resource_id", 1)])
        except Exception as e:
            logger.warning(f"创建审计日志索引失败: {e}")

    def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        level: AuditLogLevel = AuditLogLevel.INFO,
    ) -> Dict[str, Any]:
        """
        记录审计日志
        
        Args:
            action: 操作类型
            user_id: 操作用户ID
            resource_type: 资源类型
            resource_id: 资源ID
            details: 操作详情
            old_value: 变更前值
            new_value: 变更后值
            ip_address: 请求IP
            user_agent: 用户代理
            level: 日志级别
            
        Returns:
            创建的审计日志记录
        """
        log_entry = {
            "log_id": f"audit_{uuid.uuid4().hex[:12]}",
            "action": action.value,
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "old_value": old_value,
            "new_value": new_value,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "level": level.value,
            "timestamp": datetime.utcnow(),
        }
        
        try:
            self._collection.insert_one(log_entry)
            log_entry.pop("_id", None)
            
            if level == AuditLogLevel.CRITICAL:
                logger.critical(f"安全事件: {action.value} by {user_id}")
            elif level == AuditLogLevel.WARNING:
                logger.warning(f"审计告警: {action.value} by {user_id}")
            
        except Exception as e:
            logger.error(f"审计日志写入失败: {e}")
        
        return log_entry

    def log_auth_event(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        details: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """记录认证事件"""
        level = AuditLogLevel.INFO if success else AuditLogLevel.WARNING
        
        if action == AuditAction.LOGIN_FAILED:
            level = AuditLogLevel.WARNING
        
        return self.log(
            action=action,
            user_id=user_id,
            resource_type="auth",
            details={
                "success": success,
                **(details or {})
            },
            ip_address=ip_address,
            level=level,
        )

    def log_data_change(
        self,
        action: AuditAction,
        user_id: str,
        resource_type: str,
        resource_id: str,
        old_value: Optional[Dict] = None,
        new_value: Optional[Dict] = None,
        ip_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """记录数据变更"""
        return self.log(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
        )

    def log_security_event(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """记录安全事件（自动升级为CRITICAL）"""
        return self.log(
            action=action,
            user_id=user_id,
            resource_type="security",
            details=details,
            ip_address=ip_address,
            level=AuditLogLevel.CRITICAL,
        )

    def query_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """查询审计日志"""
        query_filter = {}
        
        if user_id:
            query_filter["user_id"] = user_id
        if action:
            query_filter["action"] = action
        if resource_type:
            query_filter["resource_type"] = resource_type
        if level:
            query_filter["level"] = level
        if start_time or end_time:
            time_filter = {}
            if start_time:
                time_filter["$gte"] = start_time
            if end_time:
                time_filter["$lte"] = end_time
            query_filter["timestamp"] = time_filter
        
        try:
            total = self._collection.count_documents(query_filter)
            cursor = self._collection.find(query_filter).sort("timestamp", -1).skip(skip).limit(limit)
            
            logs = []
            for doc in cursor:
                doc.pop("_id", None)
                if isinstance(doc.get("timestamp"), datetime):
                    doc["timestamp"] = doc["timestamp"].isoformat()
                logs.append(doc)
            
            return {
                "logs": logs,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        except Exception as e:
            logger.error(f"查询审计日志失败: {e}")
            return {"logs": [], "total": 0, "skip": skip, "limit": limit}

    def get_user_activity_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取用户活动摘要"""
        from datetime import timedelta
        
        start_time = datetime.utcnow() - timedelta(days=days)
        
        try:
            pipeline = [
                {"$match": {"user_id": user_id, "timestamp": {"$gte": start_time}}},
                {"$group": {
                    "_id": "$action",
                    "count": {"$sum": 1},
                    "last_occurrence": {"$max": "$timestamp"}
                }},
                {"$sort": {"count": -1}}
            ]
            
            results = list(self._collection.aggregate(pipeline))
            
            return {
                "user_id": user_id,
                "period_days": days,
                "actions": [
                    {
                        "action": r["_id"],
                        "count": r["count"],
                        "last_occurrence": r["last_occurrence"].isoformat() if isinstance(r["last_occurrence"], datetime) else str(r["last_occurrence"])
                    }
                    for r in results
                ],
                "total_actions": sum(r["count"] for r in results)
            }
        except Exception as e:
            logger.error(f"获取用户活动摘要失败: {e}")
            return {"user_id": user_id, "actions": [], "total_actions": 0}

    def get_security_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取最近的安全事件"""
        from datetime import timedelta
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        try:
            cursor = self._collection.find({
                "level": {"$in": [AuditLogLevel.WARNING.value, AuditLogLevel.CRITICAL.value]},
                "timestamp": {"$gte": start_time}
            }).sort("timestamp", -1).limit(100)
            
            events = []
            for doc in cursor:
                doc.pop("_id", None)
                if isinstance(doc.get("timestamp"), datetime):
                    doc["timestamp"] = doc["timestamp"].isoformat()
                events.append(doc)
            
            return events
        except Exception as e:
            logger.error(f"获取安全事件失败: {e}")
            return []


def get_audit_service() -> AuditLogService:
    """获取审计日志服务实例"""
    return AuditLogService()
