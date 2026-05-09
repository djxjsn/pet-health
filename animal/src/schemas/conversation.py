from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    role: str = Field(..., description="消息角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="消息元数据")


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    pet_id: Optional[str] = Field(None, description="宠物ID")
    title: Optional[str] = Field(None, max_length=255, description="对话标题")
    context: Optional[Dict[str, Any]] = Field(None, description="对话上下文")


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    context: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: str
    pet_id: Optional[str] = None
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    message_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationWithMessagesResponse(BaseModel):
    conversation_id: str
    user_id: str
    pet_id: Optional[str] = None
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    message_count: int
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(None, description="对话ID(可选,不提供则创建新对话)")
    pet_id: Optional[str] = Field(None, description="宠物ID")
    message: str = Field(..., description="用户消息")


class ChatResponse(BaseModel):
    conversation_id: str
    response: str = Field(..., description="AI助手响应内容")
    relevant_context: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="从向量数据库检索的相关上下文"
    )
