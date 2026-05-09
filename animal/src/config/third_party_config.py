"""
工具集成配置管理

集中管理所有第三方服务的配置信息。
"""
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()


class ThirdPartyConfig(BaseModel):
    """第三方服务配置"""
    
    # 图像识别服务配置
    image_recognition_provider: str = Field(default="baidu", description="图像识别服务商：baidu/tencent")
    baidu_api_key: Optional[str] = Field(default=None)
    baidu_secret_key: Optional[str] = Field(default=None)
    baidu_app_id: Optional[str] = Field(default=None)
    
    tencent_secret_id: Optional[str] = Field(default=None)
    tencent_secret_key: Optional[str] = Field(default=None)
    
    # 文件存储配置
    storage_provider: Literal["local", "minio", "oss"] = Field(default="local", description="存储服务商：local/minio/oss")
    local_storage_path: str = Field(default="./uploads", description="本地存储路径")
    
    minio_endpoint: Optional[str] = Field(default=None)
    minio_access_key: Optional[str] = Field(default=None)
    minio_secret_key: Optional[str] = Field(default=None)
    minio_bucket: Optional[str] = Field(default="pet-health")
    
    oss_endpoint: Optional[str] = Field(default=None)
    oss_access_key_id: Optional[str] = Field(default=None)
    oss_access_key_secret: Optional[str] = Field(default=None)
    oss_bucket_name: Optional[str] = Field(default=None)
    
    # 联网搜索配置
    tavily_api_key: Optional[str] = Field(default=None)
    
    # 异步任务配置
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis 连接 URL")
    celery_broker_url: Optional[str] = Field(default=None)
    celery_result_backend: Optional[str] = Field(default=None)
    
    # 通用配置
    max_upload_size: int = Field(default=10 * 1024 * 1024, description="最大上传大小（字节）")
    allowed_image_extensions: list = Field(default=[".jpg", ".jpeg", ".png", ".gif", ".webp"])
    allowed_file_extensions: list = Field(default=[".pdf", ".doc", ".docx", ".txt"])
    
    class Config:
        arbitrary_types_allowed = True


def load_third_party_config() -> ThirdPartyConfig:
    """从环境变量加载第三方服务配置"""
    return ThirdPartyConfig(
        # 图像识别
        image_recognition_provider=os.getenv("IMAGE_RECOGNITION_PROVIDER", "baidu"),
        baidu_api_key=os.getenv("BAIDU_API_KEY"),
        baidu_secret_key=os.getenv("BAIDU_SECRET_KEY"),
        baidu_app_id=os.getenv("BAIDU_APP_ID"),
        tencent_secret_id=os.getenv("TENCENT_SECRET_ID"),
        tencent_secret_key=os.getenv("TENCENT_SECRET_KEY"),
        
        # 文件存储
        storage_provider=os.getenv("STORAGE_PROVIDER", "local"),
        local_storage_path=os.getenv("LOCAL_STORAGE_PATH", "./uploads"),
        minio_endpoint=os.getenv("MINIO_ENDPOINT"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY"),
        minio_bucket=os.getenv("MINIO_BUCKET", "pet-health"),
        oss_endpoint=os.getenv("OSS_ENDPOINT"),
        oss_access_key_id=os.getenv("OSS_ACCESS_KEY_ID"),
        oss_access_key_secret=os.getenv("OSS_ACCESS_KEY_SECRET"),
        oss_bucket_name=os.getenv("OSS_BUCKET_NAME"),
        
        # 联网搜索
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        
        # 异步任务
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        celery_broker_url=os.getenv("CELERY_BROKER_URL"),
        celery_result_backend=os.getenv("CELERY_RESULT_BACKEND"),
        
        # 通用配置
        max_upload_size=int(os.getenv("MAX_UPLOAD_SIZE", "10485760")),
        allowed_image_extensions=os.getenv(
            "ALLOWED_IMAGE_EXTENSIONS", 
            ".jpg,.jpeg,.png,.gif,.webp"
        ).split(","),
        allowed_file_extensions=os.getenv(
            "ALLOWED_FILE_EXTENSIONS",
            ".pdf,.doc,.docx,.txt"
        ).split(",")
    )


# 全局配置实例
_config: Optional[ThirdPartyConfig] = None


def get_third_party_config() -> ThirdPartyConfig:
    """获取第三方服务配置（单例模式）"""
    global _config
    if _config is None:
        _config = load_third_party_config()
    return _config


def reload_config() -> ThirdPartyConfig:
    """重新加载配置"""
    global _config
    _config = load_third_party_config()
    return _config
