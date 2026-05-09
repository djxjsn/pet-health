"""
工具集成基础服务接口

定义所有工具服务的抽象基类。
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """基础服务抽象类"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化服务"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查服务是否可用"""
        pass


class ImageRecognitionService(BaseService):
    """图像识别服务抽象基类"""
    
    @abstractmethod
    def recognize_image(self, image_path: str) -> Dict[str, Any]:
        """识别图像内容"""
        pass
    
    @abstractmethod
    def detect_skin_disease(self, image_path: str) -> Dict[str, Any]:
        """检测皮肤病"""
        pass
    
    @abstractmethod
    def analyze_pet_health(self, image_path: str, pet_type: str) -> Dict[str, Any]:
        """分析宠物健康状况"""
        pass


class FileStorageService(BaseService):
    """文件存储服务抽象基类"""
    
    @abstractmethod
    def upload_file(self, file_path: str, folder: Optional[str] = None) -> str:
        """上传文件，返回访问 URL"""
        pass
    
    @abstractmethod
    def upload_image(self, image_path: str, folder: Optional[str] = None) -> str:
        """上传图片，返回访问 URL"""
        pass
    
    @abstractmethod
    def download_file(self, file_url: str, save_path: str) -> bool:
        """下载文件"""
        pass
    
    @abstractmethod
    def delete_file(self, file_url: str) -> bool:
        """删除文件"""
        pass
    
    @abstractmethod
    def get_file_url(self, file_key: str) -> str:
        """获取文件访问 URL"""
        pass


class WebSearchService(BaseService):
    """联网搜索服务抽象基类"""
    
    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """搜索网络信息"""
        pass
    
    @abstractmethod
    def search_with_content(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """搜索并返回完整内容"""
        pass
    
    @abstractmethod
    def get_news(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """搜索新闻"""
        pass


class AsyncTaskService(BaseService):
    """异步任务服务抽象基类"""
    
    @abstractmethod
    def submit_task(self, task_func: callable, *args, **kwargs) -> str:
        """提交异步任务，返回任务 ID"""
        pass
    
    @abstractmethod
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        pass
    
    @abstractmethod
    def is_task_completed(self, task_id: str) -> bool:
        """检查任务是否完成"""
        pass
    
    @abstractmethod
    def schedule_task(self, task_func: callable, schedule: str, *args, **kwargs) -> str:
        """调度定时任务"""
        pass
