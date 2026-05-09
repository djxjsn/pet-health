"""
Celery 异步任务定义

定义各种耗时的异步任务。
"""
from celery import shared_task
from celery.result import AsyncResult
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_task(
    self,
    image_path: str,
    task_type: str = "recognize",
    pet_type: str = "dog"
) -> Dict[str, Any]:
    """
    异步处理图片任务
    
    Args:
        image_path: 图片路径
        task_type: 任务类型（recognize/detect_skin/analyze_health）
        pet_type: 宠物类型
    
    Returns:
        处理结果字典
    """
    try:
        logger.info(f"开始处理图片：{image_path}, 类型：{task_type}")
        
        from src.services.tool_services.baidu_image_recognition import (
            get_baidu_image_recognition
        )
        
        service = get_baidu_image_recognition()
        
        if not service.is_available():
            return {
                "success": False,
                "error": "图像识别服务不可用"
            }
        
        if task_type == "recognize":
            result = service.recognize_image(image_path)
        elif task_type == "detect_skin":
            result = service.detect_skin_disease(image_path)
        elif task_type == "analyze_health":
            result = service.analyze_pet_health(image_path, pet_type)
        else:
            result = {
                "success": False,
                "error": f"未知的任务类型：{task_type}"
            }
        
        logger.info(f"图片处理完成：{image_path}")
        return result
        
    except Exception as e:
        logger.error(f"图片处理失败：{e}")
        # 重试逻辑
        try:
            self.retry(exc=e, countdown=60)
        except Exception:
            return {
                "success": False,
                "error": str(e)
            }


@shared_task(bind=True)
def analyze_ingredients_task(
    self,
    ingredients_text: str,
    pet_type: str,
    breed: Optional[str] = None,
    age_group: Optional[str] = None,
    health_conditions: Optional[list] = None
) -> Dict[str, Any]:
    """
    异步分析成分任务
    
    Args:
        ingredients_text: 成分文本
        pet_type: 宠物类型
        breed: 品种
        age_group: 年龄阶段
        health_conditions: 健康问题列表
    
    Returns:
        分析结果字典
    """
    try:
        from src.core.ingredient_analyzer import get_ingredient_analyzer
        
        analyzer = get_ingredient_analyzer()
        
        result = analyzer.analyze(
            ingredients_text=ingredients_text,
            pet_type=pet_type,
            breed=breed,
            age_group=age_group,
            health_conditions=health_conditions or []
        )
        
        logger.info(f"成分分析完成")
        return result
        
    except Exception as e:
        logger.error(f"成分分析失败：{e}")
        return {
            "success": False,
            "error": str(e)
        }


@shared_task(bind=True)
def web_search_task(
    self,
    query: str,
    search_type: str = "basic",
    max_results: int = 5
) -> Dict[str, Any]:
    """
    异步联网搜索任务
    
    Args:
        query: 搜索关键词
        search_type: 搜索类型（basic/advanced/news）
        max_results: 最大结果数
    
    Returns:
        搜索结果字典
    """
    try:
        from src.services.tool_services.tavily_search import get_tavily_web_search
        
        service = get_tavily_web_search()
        
        if not service.is_available():
            return {
                "success": False,
                "error": "联网搜索服务不可用"
            }
        
        if search_type == "basic":
            results = service.search(query, max_results=max_results)
        elif search_type == "advanced":
            results = service.search_with_content(query, max_results=max_results)
        elif search_type == "news":
            results = service.get_news(query, max_results=max_results)
        else:
            results = service.search(query, max_results=max_results)
        
        logger.info(f"联网搜索完成：{query}，返回{len(results)}条结果")
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "total": len(results)
        }
        
    except Exception as e:
        logger.error(f"联网搜索失败：{e}")
        return {
            "success": False,
            "error": str(e)
        }


@shared_task
def cleanup_results():
    """清理过期的任务结果（定时任务）"""
    try:
        logger.info("开始清理过期任务结果")
        # TODO: 实现清理逻辑
        logger.info("任务结果清理完成")
        return {"success": True, "message": "清理完成"}
    except Exception as e:
        logger.error(f"清理任务结果失败：{e}")
        return {"success": False, "error": str(e)}


@shared_task
def system_health_check():
    """系统健康检查（定时任务）"""
    try:
        logger.info("开始系统健康检查")
        
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # 检查图像识别服务
        try:
            from src.services.tool_services.baidu_image_recognition import (
                get_baidu_image_recognition
            )
            service = get_baidu_image_recognition()
            health_status["services"]["image_recognition"] = service.is_available()
        except Exception as e:
            health_status["services"]["image_recognition"] = False
            health_status["services"]["image_recognition_error"] = str(e)
        
        # 检查联网搜索服务
        try:
            from src.services.tool_services.tavily_search import get_tavily_web_search
            service = get_tavily_web_search()
            health_status["services"]["web_search"] = service.is_available()
        except Exception as e:
            health_status["services"]["web_search"] = False
            health_status["services"]["web_search_error"] = str(e)
        
        # 检查文件存储服务
        try:
            from src.services.tool_services.factory import get_file_storage
            service = get_file_storage()
            health_status["services"]["file_storage"] = service.is_available()
        except Exception as e:
            health_status["services"]["file_storage"] = False
            health_status["services"]["file_storage_error"] = str(e)
        
        logger.info(f"系统健康检查完成：{health_status}")
        return health_status
        
    except Exception as e:
        logger.error(f"系统健康检查失败：{e}")
        return {"success": False, "error": str(e)}


def submit_image_processing(
    image_path: str,
    task_type: str = "recognize",
    pet_type: str = "dog"
) -> str:
    """提交图片处理任务（便捷函数）
    
    Returns:
        任务 ID
    """
    result = process_image_task.delay(image_path, task_type, pet_type)
    return result.id


def submit_ingredient_analysis(
    ingredients_text: str,
    pet_type: str,
    breed: Optional[str] = None,
    age_group: Optional[str] = None,
    health_conditions: Optional[list] = None
) -> str:
    """提交成分分析任务（便捷函数）
    
    Returns:
        任务 ID
    """
    result = analyze_ingredients_task.delay(
        ingredients_text,
        pet_type,
        breed,
        age_group,
        health_conditions
    )
    return result.id


def submit_web_search(
    query: str,
    search_type: str = "basic",
    max_results: int = 5
) -> str:
    """提交联网搜索任务（便捷函数）
    
    Returns:
        任务 ID
    """
    result = web_search_task.delay(query, search_type, max_results)
    return result.id


def get_task_result(task_id: str) -> Optional[AsyncResult]:
    """获取任务结果（便捷函数）
    
    Returns:
        Celery AsyncResult 对象
    """
    return AsyncResult(task_id, app=process_image_task.app)
