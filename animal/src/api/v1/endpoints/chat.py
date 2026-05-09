"""
对话管理端点

提供AI助手对话、历史查询等功能

架构变更(v2.0): conversations/messages 从 MySQL 迁移到 MongoDB
"""
import asyncio
import logging
from typing import Any, Optional
from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessagesResponse,
    MessageResponse,
)
from src.agents.pet_health_agent import PetHealthAgent
from src.repositories.mongo_repositories import (
    ConversationRepository,
    MessageRepository,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_ai(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_request: ChatRequest,
) -> Any:
    """与AI宠物健康助手对话
    
    - 支持多轮对话，自动维护上下文
    - 可选指定宠物ID获取个性化建议
    - 返回相关上下文和响应内容
    """
    try:
        agent = PetHealthAgent(
            db=db,
            user_id=current_user.user_id
        )
        
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                agent.chat,
                chat_request.message,
                chat_request.conversation_id,
                chat_request.pet_id
            ),
            timeout=150.0
        )
        
        return result
        
    except asyncio.TimeoutError:
        logger.error(f"Chat request timed out for user {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="请求处理超时，请稍后重试或简化您的问题"
        )
    except Exception as e:
        logger.error(f"Chat request failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理请求时出错: {str(e)}"
        )


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """查询用户的对话列表
    
    - 支持分页查询
    - 按更新时间倒序排列
    - 返回对话基本信息和消息数量
    """
    conversations = ConversationRepository.list_by_user(
        user_id=current_user.user_id,
        skip=skip,
        limit=limit
    )
    
    return [
        ConversationResponse(
            conversation_id=c["conversation_id"],
            user_id=c["user_id"],
            pet_id=c.get("pet_id"),
            title=c.get("title"),
            message_count=c.get("message_count", 0),
            created_at=c["created_at"],
            updated_at=c["updated_at"],
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation_detail(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: str,
) -> Any:
    """获取对话详情（包含消息记录）
    
    - 验证对话归属权限
    - 返回完整的对话历史
    - 包含所有消息内容和元数据
    """
    conversation = ConversationRepository.get_by_id(conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    if conversation["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此对话"
        )
    
    messages = MessageRepository.list_by_conversation(
        conversation_id=conversation_id,
        limit=100
    )
    
    return {
        "conversation_id": conversation["conversation_id"],
        "user_id": conversation["user_id"],
        "pet_id": conversation.get("pet_id"),
        "title": conversation.get("title"),
        "message_count": conversation.get("message_count", 0),
        "messages": [
            {
                "message_id": msg["message_id"],
                "conversation_id": msg["conversation_id"],
                "role": msg["role"],
                "content": msg["content"],
                "metadata": msg.get("metadata"),
                "created_at": msg["created_at"]
            }
            for msg in messages
        ],
        "created_at": conversation["created_at"],
        "updated_at": conversation["updated_at"]
    }


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: str,
) -> None:
    """删除指定对话
    
    - 验证对话归属权限
    - 级联删除所有关联消息
    """
    conversation = ConversationRepository.get_by_id(conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    if conversation["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此对话"
        )
    
    success = ConversationRepository.delete(conversation_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除失败"
        )


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_conversation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_data: Optional[ConversationCreate] = None,
) -> Any:
    """创建新对话
    
    - 自动绑定当前用户
    - 可选指定关联的宠物
    - 初始化对话上下文
    """
    if not conversation_data:
        conversation_data = ConversationCreate()
    
    conversation_id = str(uuid.uuid4())
    doc = {
        "conversation_id": conversation_id,
        "user_id": current_user.user_id,
        "pet_id": conversation_data.pet_id,
        "title": conversation_data.title,
    }
    
    ConversationRepository.create(doc)
    
    return ConversationResponse(
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        pet_id=conversation_data.pet_id,
        title=conversation_data.title,
        message_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: str,
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """获取对话的消息列表
    
    - 验证对话归属权限
    - 支持分页查询
    - 按时间正序返回
    """
    conversation = ConversationRepository.get_by_id(conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在"
        )
    
    if conversation["user_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此对话"
        )
    
    messages = MessageRepository.list_by_conversation(
        conversation_id=conversation_id,
        skip=skip,
        limit=limit
    )
    
    return [
        MessageResponse(
            message_id=msg["message_id"],
            conversation_id=msg["conversation_id"],
            role=msg["role"],
            content=msg["content"],
            metadata=msg.get("metadata"),
            created_at=msg["created_at"],
        )
        for msg in messages
    ]
