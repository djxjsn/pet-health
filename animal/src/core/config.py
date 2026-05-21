from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    APP_NAME: str = "AI Pet Health Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/ai_pet_health"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # LLM 配置
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 向量数据库配置（ChromaDB - 旧版，保留兼容）
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "pet_health_knowledge"

    # Qdrant 向量数据库配置（新版）
    VECTOR_DB_BACKEND: str = "qdrant"
    QDRANT_LOCAL_PATH: str = "./data/qdrant_local"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_GRPC_PORT: int = 6334
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "pet_health_knowledge"
    QDRANT_PREFER_GRPC: bool = False
    QDRANT_HNSW_M: int = 16
    QDRANT_HNSW_EF_CONSTRUCT: int = 128
    QDRANT_ENABLE_QUANTIZATION: bool = True

    # 嵌入模型配置
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    EMBEDDING_DIMENSION: int = 512
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_PRELOAD: bool = True

    # 检索配置
    SIMILARITY_THRESHOLD: float = 0.5
    SEARCH_TOP_K: int = 5
    SEARCH_OVERRETRIEVAL_FACTOR: int = 2
    HYBRID_SEARCH_DENSE_WEIGHT: float = 0.7
    HYBRID_SEARCH_SPARSE_WEIGHT: float = 0.3
    
    # MongoDB 配置
    MONGODB_URL: str = "mongodb://localhost:27017/"
    MONGODB_DATABASE: str = "ai_pet_health"

    # InfluxDB 时序数据库配置（设备健康数据存储）
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = "my-super-secret-token"
    INFLUXDB_ORG: str = "pei-health"
    INFLUXDB_BUCKET: str = "pet_health_metrics"
    INFLUXDB_TIMEOUT_MS: int = 10000

    # 预警规则配置
    ALERT_HEART_RATE_HIGH: float = 140.0   # 心率过高阈值 (bpm)
    ALERT_HEART_RATE_LOW: float = 40.0     # 心率过低阈值 (bpm)
    ALERT_TEMPERATURE_HIGH: float = 39.5   # 体温过高阈值 (°C)
    ALERT_TEMPERATURE_LOW: float = 36.0    # 体温过低阈值 (°C)
    ALERT_INACTIVE_HOURS: int = 6          # 连续不活跃小时数触发预警
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",  # 忽略额外的环境变量
    }


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例）"""
    return Settings()
