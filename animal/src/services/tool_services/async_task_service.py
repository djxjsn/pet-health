"""
异步任务服务封装

提供统一的异步任务提交和管理接口。
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from src.services.tool_services.celery_tasks import (
    process_image_task,
    analyze_ingredients_task,
    web_search_task,
    get_task_result
)
from src.services.tool_services.base import AsyncTaskService

logger = logging.getLogger(__name__)


class CeleryAsyncTaskService(AsyncTaskService):
    """基于 Celery 的异步任务服务"""
    
    def __init__(self):
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化服务"""
        try:
            # 检查 Celery 配置
            from src.config.celery_config import get_celery_app
            app = get_celery_app()
            
            # 测试连接
            inspect = app.control.inspect()
            active_workers = inspect.active()
            
            if active_workers:
                logger.info(f"Celery 异步任务服务初始化成功，活跃 worker 数：{len(active_workers)}")
                self._initialized = True
                return True
            else:
                logger.warning("未检测到活跃的 Celery worker，异步任务可能无法执行")
                self._initialized = True  # 仍然允许初始化，但记录警告
                return True
                
        except Exception as e:
            logger.error(f"Celery 异步任务服务初始化失败：{e}")
            self._initialized = False
            return False
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self._initialized
    
    def submit_task(self, task_func: callable, *args, **kwargs) -> str:
        """提交异步任务
        
        Args:
            task_func: Celery 任务函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            任务 ID
        """
        try:
            result = task_func.delay(*args, **kwargs)
            logger.info(f"提交异步任务：{task_func.name}, ID: {result.id}")
            return result.id
        except Exception as e:
            logger.error(f"提交异步任务失败：{e}")
            raise
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果
        
        Args:
            task_id: 任务 ID
        
        Returns:
            任务结果字典，如果任务不存在则返回 None
        """
        try:
            result = get_task_result(task_id)
            
            if result is None:
                return None
            
            task_result = {
                "task_id": task_id,
                "state": result.state,
                "ready": result.ready(),
                "successful": result.successful() if result.ready() else None,
                "result": result.result if result.ready() else None,
                "info": result.info if hasattr(result, 'info') else None
            }
            
            return task_result
            
        except Exception as e:
            logger.error(f"获取任务结果失败：{e}")
            return None
    
    def is_task_completed(self, task_id: str) -> bool:
        """检查任务是否完成
        
        Args:
            task_id: 任务 ID
        
        Returns:
            是否完成
        """
        try:
            result = get_task_result(task_id)
            return result.ready() if result else False
        except Exception as e:
            logger.error(f"检查任务状态失败：{e}")
            return False
    
    def schedule_task(self, task_func: callable, schedule: str, *args, **kwargs) -> str:
        """调度定时任务（需要 Celery Beat）
        
        Args:
            task_func: Celery 任务函数
            schedule: Cron 表达式或时间间隔
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            调度 ID
        """
        # TODO: 实现定时任务调度
        logger.warning("定时任务调度功能尚未实现")
        raise NotImplementedError("定时任务调度功能尚未实现")
    
    # 便捷方法
    
    def submit_image_processing(
        self,
        image_path: str,
        task_type: str = "recognize",
        pet_type: str = "dog"
    ) -> str:
        """提交图片处理任务"""
        return self.submit_task(
            process_image_task,
            image_path,
            task_type,
            pet_type
        )
    
    def submit_ingredient_analysis(
        self,
        ingredients_text: str,
        pet_type: str,
        breed: Optional[str] = None,
        age_group: Optional[str] = None,
        health_conditions: Optional[List[str]] = None
    ) -> str:
        """提交成分分析任务"""
        return self.submit_task(
            analyze_ingredients_task,
            ingredients_text,
            pet_type,
            breed,
            age_group,
            health_conditions or []
        )
    
    def submit_web_search(
        self,
        query: str,
        search_type: str = "basic",
        max_results: int = 5
    ) -> str:
        """提交联网搜索任务"""
        return self.submit_task(
            web_search_task,
            query,
            search_type,
            max_results
        )


def get_async_task_service() -> CeleryAsyncTaskService:
    """获取异步任务服务实例"""
    return CeleryAsyncTaskService()
