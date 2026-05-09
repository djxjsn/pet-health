"""
本地文件存储服务

提供本地文件系统上传功能。
"""
import os
import shutil
from pathlib import Path
from typing import Optional
import logging
import uuid

from src.services.tool_services.base import FileStorageService

logger = logging.getLogger(__name__)


class LocalFileStorage(FileStorageService):
    """本地文件存储服务"""
    
    def __init__(self, base_path: str = "./uploads"):
        """初始化本地存储
        
        Args:
            base_path: 基础存储路径
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化服务"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            self._initialized = True
            logger.info(f"本地文件存储初始化成功：{self.base_path}")
            return True
        except Exception as e:
            logger.error(f"本地文件存储初始化失败：{e}")
            return False
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self._initialized and self.base_path.exists()
    
    def upload_file(self, file_path: str, folder: Optional[str] = None) -> str:
        """上传文件
        
        Args:
            file_path: 文件路径
            folder: 目标文件夹
        
        Returns:
            文件访问 URL（本地路径）
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                raise FileNotFoundError(f"文件不存在：{file_path}")
            
            # 生成目标路径
            target_folder = self.base_path / (folder or "files")
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # 生成唯一文件名
            file_name = f"{uuid.uuid4().hex[:8]}_{source_path.name}"
            target_path = target_folder / file_name
            
            # 复制文件
            shutil.copy2(source_path, target_path)
            
            # 返回访问 URL（相对路径）
            return f"/uploads/{folder or 'files'}/{file_name}"
            
        except Exception as e:
            logger.error(f"上传文件失败：{e}")
            raise
    
    def upload_image(self, image_path: str, folder: Optional[str] = None) -> str:
        """上传图片"""
        return self.upload_file(image_path, folder=folder or "images")
    
    def download_file(self, file_url: str, save_path: str) -> bool:
        """下载文件"""
        try:
            # 从 URL 提取文件路径
            file_key = file_url.replace("/uploads/", "")
            source_path = self.base_path / file_key
            
            if not source_path.exists():
                return False
            
            shutil.copy2(source_path, save_path)
            return True
            
        except Exception as e:
            logger.error(f"下载文件失败：{e}")
            return False
    
    def delete_file(self, file_url: str) -> bool:
        """删除文件"""
        try:
            file_key = file_url.replace("/uploads/", "")
            file_path = self.base_path / file_key
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已删除文件：{file_url}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"删除文件失败：{e}")
            return False
    
    def get_file_url(self, file_key: str) -> str:
        """获取文件访问 URL"""
        return f"/uploads/{file_key}"
    
    def get_file_path(self, file_url: str) -> Path:
        """获取文件实际路径"""
        file_key = file_url.replace("/uploads/", "")
        return self.base_path / file_key


def get_local_file_storage(base_path: str = "./uploads") -> LocalFileStorage:
    """获取本地文件存储实例"""
    return LocalFileStorage(base_path)
