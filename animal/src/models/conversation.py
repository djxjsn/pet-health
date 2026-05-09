"""
[DEPRECATED] SQLAlchemy ORM Models for Conversations and Messages

⚠️  WARNING: This module is DEPRECATED and no longer in use!

Migration completed on: 2026-04-19
New storage system: MongoDB (via src.repositories.mongo_repositories)

These models were used with MySQL but have been replaced by MongoDB collections:
  - conversations → MongoDB 'conversations' collection (ConversationRepository)
  - messages → MongoDB 'messages' collection (MessageRepository)

If you see any code importing from this file, please update it to use:
  - src.repositories.mongo_repositories.ConversationRepository
  - src.repositories.mongo_repositories.MessageRepository
  - src.memory.conversation_manager.ConversationMemoryManager

This file is kept for reference only. It can be safely deleted after confirming
no other code depends on these models.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, JSON
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from warnings import warn

from src.core.database import Base


class Conversation(Base):
    """[DEPRECATED] 对话会话模型 - Use ConversationRepository instead"""
    __tablename__ = "conversations"

    conversation_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="对话ID，UUID主键"
    )
    user_id = Column(
        CHAR(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID，外键"
    )
    pet_id = Column(
        CHAR(36),
        ForeignKey("pets.pet_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="宠物ID，外键(可选)"
    )
    title = Column(
        String(255),
        nullable=True,
        comment="对话标题"
    )
    context = Column(
        JSON,
        nullable=True,
        comment="对话上下文信息"
    )
    message_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="消息数量"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间"
    )

    user = relationship("User", backref="conversations")
    pet = relationship("Pet", backref="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __init__(self, *args, **kwargs):
        warn(
            "Conversation model is deprecated! Use ConversationRepository from "
            "src.repositories.mongo_repositories instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Conversation(conversation_id={self.conversation_id}, user_id={self.user_id})>"


class Message(Base):
    """[DEPRECATED] 对话消息模型 - Use MessageRepository instead"""
    __tablename__ = "messages"

    message_id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="消息ID，UUID主键"
    )
    conversation_id = Column(
        CHAR(36),
        ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="对话ID，外键"
    )
    role = Column(
        String(20),
        nullable=False,
        comment="消息角色: user/assistant/system"
    )
    content = Column(
        Text,
        nullable=False,
        comment="消息内容"
    )
    message_metadata = Column(
        "metadata",
        JSON,
        nullable=True,
        comment="消息元数据"
    )
    vector_id = Column(
        String(255),
        nullable=True,
        comment="向量数据库中的文档ID"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )

    conversation = relationship("Conversation", back_populates="messages")

    def __init__(self, *args, **kwargs):
        warn(
            "Message model is deprecated! Use MessageRepository from "
            "src.repositories.mongo_repositories instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Message(message_id={self.message_id}, role={self.role})>"
