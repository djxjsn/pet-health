"""
MongoDB 连接管理类

用于管理 MongoDB 数据库连接，支持单例模式。
"""
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from .config import get_settings
import logging

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB 客户端管理类（单例）"""
    
    _instance: Optional['MongoDBClient'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        settings = get_settings()
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._url = settings.MONGODB_URL
        self._database_name = settings.MONGODB_DATABASE
        
        self._initialized = True
    
    def connect(self) -> Database:
        """建立 MongoDB 连接并返回数据库实例"""
        if self._db is not None:
            return self._db
        
        try:
            self._client = MongoClient(
                self._url,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=30000,
            )
            # 测试连接
            self._client.admin.command('ping')
            self._db = self._client[self._database_name]
            logger.info(f"MongoDB 连接成功: {self._url}{self._database_name}")
            return self._db
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"MongoDB 连接失败: {e}，将使用降级方案")
            raise
    
    @property
    def db(self) -> Database:
        """获取数据库实例（懒加载）"""
        if self._db is None:
            return self.connect()
        return self._db
    
    def get_collection(self, name: str):
        """获取集合"""
        return self.db[name]
    
    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB 连接已关闭")
    
    def check_connection(self) -> bool:
        """检查连接状态"""
        try:
            if self._client is None:
                self.connect()
            self._client.admin.command('ping')
            return True
        except Exception:
            return False


def get_mongodb() -> Database:
    """获取 MongoDB 数据库实例（依赖注入用）"""
    client = MongoDBClient()
    return client.db


def get_mongo_collection(name: str):
    """获取 MongoDB 集合（依赖注入用）"""
    client = MongoDBClient()
    return client.get_collection(name)
