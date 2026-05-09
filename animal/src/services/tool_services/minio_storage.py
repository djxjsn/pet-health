"""
MinIO 对象存储服务

提供 MinIO 兼容的对象存储功能。
"""
from typing import Optional
import logging
import uuid
from pathlib import Path

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    Minio = None
    S3Error = Exception

from src.services.tool_services.base import FileStorageService
from src.config.third_party_config import get_third_party_config

logger = logging.getLogger(__name__)


class MinIOFileStorage(FileStorageService):
    """MinIO 文件存储服务"""
    
    def __init__(self):
        """初始化 MinIO 存储"""
        self.config = get_third_party_config()
        self.client: Optional[Minio] = None
        self.bucket_name = self.config.minio_bucket
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化 MinIO 客户端"""
        if not MINIO_AVAILABLE:
            logger.error("MinIO 客户端未安装，请安装：pip install minio")
            return False
        
        try:
            self.client = Minio(
                self.config.minio_endpoint or "localhost:9000",
                access_key=self.config.minio_access_key or "minioadmin",
                secret_key=self.config.minio_secret_key or "minioadmin",
                secure=False
            )
            
            # 创建 bucket（如果不存在）
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"创建 MinIO bucket: {self.bucket_name}")
            
            self._initialized = True
            logger.info(f"MinIO 存储初始化成功：{self.config.minio_endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"MinIO 存储初始化失败：{e}")
            return False
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self._initialized and self.client is not None
    
    def upload_file(self, file_path: str, folder: Optional[str] = None) -> str:
        """上传文件到 MinIO
        
        Args:
            file_path: 文件路径
            folder: 目标文件夹
        
        Returns:
            文件访问 URL
        """
        if not self.is_available():
            raise RuntimeError("MinIO 服务未初始化")
        
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                raise FileNotFoundError(f"文件不存在：{file_path}")
            
            # 生成对象键
            file_name = f"{uuid.uuid4().hex[:8]}_{source_path.name}"
            object_name = f"{folder}/{file_name}" if folder else f"files/{file_name}"
            
            # 上传文件
            self.client.fput_object(
                self.bucket_name,
                object_name,
                str(source_path)
            )
            
            # 返回访问 URL
            return f"minio://{self.bucket_name}/{object_name}"
            
        except Exception as e:
            logger.error(f"MinIO 上传文件失败：{e}")
            raise
    
    def upload_image(self, image_path: str, folder: Optional[str] = None) -> str:
        """上传图片"""
        return self.upload_file(image_path, folder=folder or "images")
    
    def download_file(self, file_url: str, save_path: str) -> bool:
        """从 MinIO 下载文件"""
        if not self.is_available():
            return False
        
        try:
            # 解析 MinIO URL
            object_name = file_url.replace(f"minio://{self.bucket_name}/", "")
            
            # 下载文件
            self.client.fget_object(
                self.bucket_name,
                object_name,
                save_path
            )
            
            return True
            
        except Exception as e:
            logger.error(f"MinIO 下载文件失败：{e}")
            return False
    
    def delete_file(self, file_url: str) -> bool:
        """删除 MinIO 中的文件"""
        if not self.is_available():
            return False
        
        try:
            object_name = file_url.replace(f"minio://{self.bucket_name}/", "")
            
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"已删除 MinIO 文件：{file_url}")
            return True
            
        except Exception as e:
            logger.error(f"MinIO 删除文件失败：{e}")
            return False
    
    def get_file_url(self, file_key: str) -> str:
        """获取文件访问 URL"""
        return f"minio://{self.bucket_name}/{file_key}"
    
    def get_presigned_url(
        self,
        object_name: str,
        expires: int = 3600,
        response_headers: Optional[dict] = None
    ) -> str:
        """获取预签名 URL（用于临时访问）
        
        Args:
            object_name: 对象名称
            expires: 过期时间（秒）
            response_headers: 响应头
        
        Returns:
            预签名 URL
        """
        if not self.is_available():
            raise RuntimeError("MinIO 服务未初始化")
        
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=expires,
                response_headers=response_headers
            )
            return url
            
        except Exception as e:
            logger.error(f"生成预签名 URL 失败：{e}")
            raise


def get_minio_file_storage() -> MinIOFileStorage:
    """获取 MinIO 文件存储实例"""
    return MinIOFileStorage()
