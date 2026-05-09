"""
[DEPRECATED] SQLAlchemy CRUD Operations for Conversations and Messages

⚠️  WARNING: This module is DEPRECATED and no longer in use!

Migration completed on: 2026-04-19
New storage system: MongoDB (via src.repositories.mongo_repositories)

These functions were used with MySQL but have been replaced by MongoDB Repository methods:
  - create_conversation() → ConversationRepository.create()
  - get_conversation_by_id() → ConversationRepository.get_by_id()
  - get_user_conversations() → ConversationRepository.list_by_user()
  - update_conversation() → ConversationRepository.update()
  - delete_conversation() → ConversationRepository.delete()
  - create_message() → MessageRepository.create()
  - get_message_by_id() → MessageRepository.get_by_id()
  - get_conversation_messages() → MessageRepository.list_by_conversation()
  - update_message_vector_id() → (use MessageRepository.create() with vector_id)
  - get_recent_messages() → MessageRepository.list_by_conversation()

If you see any code importing from this file, please update it to use:
  - src.repositories.mongo_repositories.ConversationRepository
  - src.repositories.mongo_repositories.MessageRepository

This file is kept for reference only. It can be safely deleted after confirming
no other code depends on these functions.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from warnings import warn

# Import deprecated models for backward compatibility
from src.models.conversation import Conversation, Message
from src.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
)


def _deprecated_warning(func_name, replacement):
    """Emit deprecation warning"""
    warn(
        f"{func_name} is deprecated! Use {replacement} instead.",
        DeprecationWarning,
        stacklevel=3
    )


def get_conversation_by_id(db: Session, conversation_id: str) -> Optional[Conversation]:
    """[DEPRECATED] 根据ID获取对话 - Use ConversationRepository.get_by_id()"""
    _deprecated_warning("get_conversation_by_id()", "ConversationRepository.get_by_id()")
    return db.query(Conversation).filter(
        Conversation.conversation_id == conversation_id
    ).first()


def get_user_conversations(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 20
) -> List[Conversation]:
    """[DEPRECATED] 获取用户的对话列表 - Use ConversationRepository.list_by_user()"""
    _deprecated_warning("get_user_conversations()", "ConversationRepository.list_by_user()")
    return db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()


def create_conversation(
    db: Session,
    user_id: str,
    conversation_data: ConversationCreate
) -> Conversation:
    """[DEPRECATED] 创建新对话 - Use ConversationRepository.create()"""
    _deprecated_warning("create_conversation()", "ConversationRepository.create()")
    conversation = Conversation(
        user_id=user_id,
        pet_id=conversation_data.pet_id,
        title=conversation_data.title,
        context=conversation_data.context,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def update_conversation(
    db: Session,
    conversation_id: str,
    conversation_data: ConversationUpdate
) -> Optional[Conversation]:
    """[DEPRECATED] 更新对话 - Use ConversationRepository.update()"""
    _deprecated_warning("update_conversation()", "ConversationRepository.update()")
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        return None
    
    update_data = conversation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)
    
    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, conversation_id: str) -> bool:
    """[DEPRECATED] 删除对话 - Use ConversationRepository.delete()"""
    _deprecated_warning("delete_conversation()", "ConversationRepository.delete()")
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        return False
    
    db.delete(conversation)
    db.commit()
    return True


def get_message_by_id(db: Session, message_id: str) -> Optional[Message]:
    """[DEPRECATED] 根据ID获取消息 - Use MessageRepository.get_by_id()"""
    _deprecated_warning("get_message_by_id()", "MessageRepository.get_by_id()")
    return db.query(Message).filter(Message.message_id == message_id).first()


def get_conversation_messages(
    db: Session,
    conversation_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Message]:
    """[DEPRECATED] 获取对话的消息列表 - Use MessageRepository.list_by_conversation()"""
    _deprecated_warning(
        "get_conversation_messages()",
        "MessageRepository.list_by_conversation()"
    )
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).offset(skip).limit(limit).all()


def create_message(
    db: Session,
    conversation_id: str,
    message_data: MessageCreate,
    vector_id: Optional[str] = None
) -> Message:
    """[DEPRECATED] 创建新消息 - Use MessageRepository.create()"""
    _deprecated_warning("create_message()", "MessageRepository.create()")
    message = Message(
        conversation_id=conversation_id,
        role=message_data.role,
        content=message_data.content,
        message_metadata=message_data.metadata,
        vector_id=vector_id,
    )
    db.add(message)
    
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation:
        conversation.message_count += 1
    
    db.commit()
    db.refresh(message)
    return message


def update_message_vector_id(
    db: Session,
    message_id: str,
    vector_id: str
) -> Optional[Message]:
    """[DEPRECATED] 更新消息的向量ID - Include in MessageRepository.create()"""
    _deprecated_warning(
        "update_message_vector_id()",
        "Pass vector_id to MessageRepository.create()"
    )
    message = get_message_by_id(db, message_id)
    if not message:
        return None
    
    message.vector_id = vector_id
    db.commit()
    db.refresh(message)
    return message


def get_recent_messages(
    db: Session,
    conversation_id: str,
    limit: int = 10
) -> List[Message]:
    """[DEPRECATED] 获取对话的最近消息 - Use MessageRepository.list_by_conversation()"""
    _deprecated_warning(
        "get_recent_messages()",
        "MessageRepository.list_by_conversation()"
    )
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(desc(Message.created_at)).limit(limit).all()[::-1]
