from fastapi import APIRouter

from src.api.v1.endpoints import auth, users, pets, chat, ws_chat, health, behavior, knowledge, shopping, files, security, ecommerce, encyclopedia, devices

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["用户认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(pets.router, prefix="/pets", tags=["宠物档案"])
api_router.include_router(devices.router, prefix="/devices", tags=["设备管理"])
api_router.include_router(health.router, prefix="/health", tags=["健康咨询"])
api_router.include_router(behavior.router, prefix="/behavior", tags=["行为分析"])
api_router.include_router(knowledge.router, prefix="", tags=["知识管理"])
api_router.include_router(shopping.router, prefix="", tags=["购物助手"])
api_router.include_router(ecommerce.router, prefix="", tags=["电商模块"])
api_router.include_router(files.router, prefix="", tags=["文件管理"])
api_router.include_router(chat.router, prefix="", tags=["AI 对话"])
api_router.include_router(ws_chat.router, prefix="", tags=["WebSocket 对话"])
api_router.include_router(security.router, prefix="/security", tags=["数据安全"])
api_router.include_router(encyclopedia.router, prefix="", tags=["宠物知识科普"])
