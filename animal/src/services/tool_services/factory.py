"""
文件存储服务工厂

根据配置创建合适的文件存储服务实例。
"""
import logging
from typing import Optional

from src.services.tool_services.base import FileStorageService
from src.services.tool_services.local_storage import LocalFileStorage
from src.services.tool_services.minio_storage import MinIOFileStorage
from src.config.third_party_config import get_third_party_config

logger = logging.getLogger(__name__)


class FileStorageFactory:
    """文件存储服务工厂"""
    
    _instance: Optional[FileStorageService] = None
    
    @classmethod
    def get_storage(cls) -> FileStorageService:
        """获取文件存储服务实例"""
        if cls._instance is None:
            config = get_third_party_config()
            
            provider = config.storage_provider.lower()
            
            if provider == "minio":
                cls._instance = MinIOFileStorage()
            elif provider == "oss":
                # TODO: 实现 OSS 存储
                logger.warning("OSS 存储尚未实现，使用本地存储作为降级方案")
                cls._instance = LocalFileStorage()
            else:
                # 默认使用本地存储
                cls._instance = LocalFileStorage(base_path=config.local_storage_path)
            
            # 初始化服务
            if not cls._instance.initialize():
                logger.error("文件存储服务初始化失败")
                raise RuntimeError("文件存储服务初始化失败")
        
        return cls._instance
    
    @classmethod
    def reset(cls):
        """重置服务实例（用于测试）"""
        cls._instance = None


def get_file_storage() -> FileStorageService:
    """获取文件存储服务（便捷函数）"""
    return FileStorageFactory.get_storage()
