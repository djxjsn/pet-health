"""
AI 宠物健康助手 - FastAPI 应用入口

版本：v2.0.0
日期：2026-04-16
混合架构：MySQL (users/user_profiles/pets) + MongoDB (conversations/messages/health_records/consultations/behavior_analyses)
"""
import os

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.database import engine, MySQLBase
from src.core.mongodb import MongoDBClient
from src.api.v1.router import api_router

settings = get_settings()

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## AI 宠物健康助手 API

基于 LangChain 框架的 AI 宠物健康助手智能体项目，提供宠物健康咨询、疾病诊断、营养建议等功能。

### 数据存储架构

**MySQL（关系型数据）**
- `users` - 用户账户
- `user_profiles` - 用户档案
- `pets` - 宠物档案

**MongoDB（文档型数据）**
- `conversations` - 对话记录
- `messages` - 消息记录
- `health_records` - 健康档案
- `consultations` - AI咨询记录
- `behavior_analyses` - 行为分析记录

### 主要功能模块

**用户认证模块**
- 用户注册
- 用户登录
- JWT 令牌管理

**宠物档案管理**
- 宠物信息录入
- 多宠物管理
- 档案维护

**健康咨询**
- 症状分析
- 健康建议
- 多模态识别

**智能购物**
- 商品推荐
- 成分分析
- 对比报告
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 配置 CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["根路径"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# 健康检查端点
@app.get("/health", tags=["健康检查"])
async def health_check():
    """
    检查服务健康状态
    
    返回:
        dict: 包含服务状态信息
    """
    # 检查 MongoDB 连接
    mongo_status = "unknown"
    try:
        mongo_client = MongoDBClient()
        if mongo_client.check_connection():
            mongo_status = "connected"
        else:
            mongo_status = "disconnected"
    except Exception:
        mongo_status = "error"
    
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "databases": {
            "mysql": "connected",
            "mongodb": mongo_status,
        }
    }


# 应用生命周期事件
@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行
    - 创建 MySQL 数据库表（仅 users, user_profiles, pets）
    - 初始化 MongoDB 连接
    - 预加载 LLM 和嵌入模型
    - 初始化连接池
    - 加载配置
    """
    import os
    import logging
    logger = logging.getLogger(__name__)
    
    if os.getenv("TESTING", "False").lower() == "true":
        return
    
    MySQLBase.metadata.create_all(bind=engine)
    
    try:
        mongo_client = MongoDBClient()
        mongo_client.connect()
    except Exception as e:
        logger.warning(f"MongoDB 连接初始化失败，将使用降级方案: {e}")
    
    try:
        from src.core.llm import get_llm
        llm = get_llm()
        logger.info("LLM 模型预加载完成")
    except Exception as e:
        logger.warning(f"LLM 预加载失败（首次请求时将重试）: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时执行
    - 关闭 MySQL 数据库连接
    - 关闭 MongoDB 连接
    - 清理资源
    """
    try:
        mongo_client = MongoDBClient()
        mongo_client.close()
    except Exception:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
