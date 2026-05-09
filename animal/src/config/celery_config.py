"""
Celery 异步任务配置

配置 Celery 任务队列和调度器。
"""
from celery import Celery
from celery.schedules import crontab
import logging

from src.config.third_party_config import get_third_party_config

logger = logging.getLogger(__name__)

# 创建 Celery 应用
celery_app = Celery(
    'pet_health_agent',
    broker=None,
    backend=None,
    include=[
        'src.services.tool_services.celery_tasks'
    ]
)

# 加载配置
def configure_celery():
    """配置 Celery"""
    config = get_third_party_config()
    
    # 设置 broker 和 backend
    broker_url = config.celery_broker_url or config.redis_url
    result_backend = config.celery_result_backend or config.redis_url
    
    celery_app.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        
        # 任务序列化
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        
        # 时区
        timezone='Asia/Shanghai',
        enable_utc=True,
        
        # 任务路由
        task_routes={
            'src.services.tool_services.celery_tasks.process_image_task': {
                'queue': 'image_processing'
            },
            'src.services.tool_services.celery_tasks.analyze_ingredients_task': {
                'queue': 'analysis'
            },
            'src.services.tool_services.celery_tasks.web_search_task': {
                'queue': 'search'
            }
        },
        
        # 速率限制
        task_default_rate_limit='100/m',
        
        # 结果过期时间（秒）
        result_expires=3600,
        
        # 定时任务
        beat_schedule={
            # 每天凌晨 2 点清理过期任务结果
            'cleanup-results': {
                'task': 'src.services.tool_services.celery_tasks.cleanup_results',
                'schedule': crontab(hour=2, minute=0),
            },
            # 每小时检查一次系统健康
            'health-check': {
                'task': 'src.services.tool_services.celery_tasks.system_health_check',
                'schedule': crontab(minute=0),
            }
        }
    )
    
    logger.info(f"Celery 配置完成：broker={broker_url}, backend={result_backend}")


# 初始化 Celery
configure_celery()


def get_celery_app() -> Celery:
    """获取 Celery 应用实例"""
    return celery_app
