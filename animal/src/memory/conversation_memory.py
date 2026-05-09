import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from src.core.vector_db import get_vector_db
from src.core.knowledge_retriever import get_knowledge_retriever
from src.repositories.mongo_repositories import (
    ConversationRepository,
    MessageRepository,
)

logger = logging.getLogger(__name__)


class ConversationMemoryManager:
    """对话历史记忆管理器"""

    def __init__(self, db=None):
        self.db = db
        self.vector_db = get_vector_db()
        self.retriever = get_knowledge_retriever()
        self._chat_history: List[BaseMessage] = []
    
    def create_new_conversation(
        self,
        user_id: str,
        pet_id: Optional[str] = None,
        title: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建新对话"""
        doc = {
            "conversation_id": str(__import__('uuid').uuid4()),
            "user_id": user_id,
            "pet_id": pet_id,
            "title": title,
            "context": context or {}
        }

        conversation_id = ConversationRepository.create(doc)
        doc["conversation_id"] = conversation_id

        return doc
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        store_in_vector_db: bool = True
    ) -> Dict[str, Any]:
        """添加消息到对话历史

        Args:
            conversation_id: 对话ID
            role: 消息角色(user/assistant/system)
            content: 消息内容
            metadata: 消息元数据
            store_in_vector_db: 是否存储到向量数据库

        Returns:
            创建的消息字典
        """
        vector_id = None
        if store_in_vector_db and self.vector_db.is_available:
            vector_id = self._store_message_to_vector_db(
                conversation_id=conversation_id,
                role=role,
                content=content,
                metadata=metadata
            )
        elif store_in_vector_db and not self.vector_db.is_available:
            logger.warning("嵌入模型不可用，跳过消息向量存储")

        message_doc = {
            "message_id": str(__import__('uuid').uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "metadata": metadata,
            "vector_id": vector_id
        }

        message_id = MessageRepository.create(message_doc)
        message_doc["message_id"] = message_id

        self._update_langchain_memory(role, content)

        return message_doc
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[BaseMessage]:
        """获取对话历史(LangChain格式)

        Args:
            conversation_id: 对话ID
            limit: 返回的消息数量限制

        Returns:
            LangChain消息列表
        """
        messages = MessageRepository.list_by_conversation(
            conversation_id=conversation_id,
            limit=limit
        )

        langchain_messages = []
        for msg in messages:
            if msg.get("role") == "user":
                langchain_messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                langchain_messages.append(AIMessage(content=msg.get("content", "")))
            elif msg.get("role") == "system":
                langchain_messages.append(SystemMessage(content=msg.get("content", "")))

        return langchain_messages
    
    def retrieve_relevant_context(
        self,
        query: str,
        n_results: int = 5,
        conversation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """检索相关上下文（通过统一检索入口）
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            conversation_id: 对话ID(可选,用于过滤)
            
        Returns:
            相关上下文列表
        """
        return self.retriever.search_for_conversation_context(
            query=query,
            conversation_id=conversation_id,
            n_results=n_results
        )
    
    def _store_message_to_vector_db(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """将消息存储到向量数据库
        
        Args:
            conversation_id: 对话ID
            role: 消息角色
            content: 消息内容
            metadata: 消息元数据
            
        Returns:
            向量文档ID，存储失败返回None
        """
        try:
            vector_metadata = {
                "conversation_id": conversation_id,
                "role": role,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if metadata:
                vector_metadata.update(metadata)
            
            doc_id = f"{conversation_id}_{datetime.utcnow().timestamp()}"
            
            self.vector_db.add_documents(
                documents=[content],
                metadatas=[vector_metadata],
                ids=[doc_id]
            )
            
            return doc_id
        except RuntimeError as e:
            logger.error(f"消息向量存储失败（嵌入模型不可用）: {e}")
            return None
        except Exception as e:
            logger.error(f"消息向量存储失败: {e}")
            return None
    
    def _update_langchain_memory(self, role: str, content: str):
        """更新内存中的对话历史"""
        if role == "user":
            self._chat_history.append(HumanMessage(content=content))
        elif role == "assistant":
            self._chat_history.append(AIMessage(content=content))
    
    def get_chat_history(self) -> List[BaseMessage]:
        """获取内存中的对话历史（LangChain 消息格式）"""
        return self._chat_history
    
    def clear_memory(self):
        """清空内存"""
        self._chat_history.clear()
