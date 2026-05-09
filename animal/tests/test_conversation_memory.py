"""
对话记忆测试
"""
import pytest
from sqlalchemy.orm import Session
from src.memory.conversation_memory import ConversationMemoryManager
from src.db.crud import create_user
from src.schemas.user import UserCreate
from src.core.security import hash_password


class TestConversationMemory:
    """对话记忆测试类"""
    
    @pytest.fixture
    def test_user(self, db_session: Session):
        """创建测试用户"""
        user_data = UserCreate(
            phone="13800000001",
            email="test@example.com",
            password="test1234"
        )
        user = create_user(db_session, user_data)
        return user
    
    def test_create_conversation(self, db_session: Session, test_user):
        """测试创建对话"""
        memory_manager = ConversationMemoryManager(db_session)
        
        conversation = memory_manager.create_new_conversation(
            user_id=test_user.user_id,
            title="测试对话"
        )
        
        assert conversation is not None
        assert conversation.user_id == test_user.user_id
        assert conversation.title == "测试对话"
    
    def test_add_message(self, db_session: Session, test_user):
        """测试添加消息"""
        memory_manager = ConversationMemoryManager(db_session)
        
        conversation = memory_manager.create_new_conversation(
            user_id=test_user.user_id
        )
        
        message = memory_manager.add_message(
            conversation_id=conversation.conversation_id,
            role="user",
            content="你好"
        )
        
        assert message is not None
        assert message.role == "user"
        assert message.content == "你好"
    
    def test_get_conversation_history(self, db_session: Session, test_user):
        """测试获取对话历史"""
        memory_manager = ConversationMemoryManager(db_session)
        
        conversation = memory_manager.create_new_conversation(
            user_id=test_user.user_id
        )
        
        memory_manager.add_message(
            conversation_id=conversation.conversation_id,
            role="user",
            content="你好"
        )
        
        memory_manager.add_message(
            conversation_id=conversation.conversation_id,
            role="assistant",
            content="你好!有什么可以帮助你的吗?"
        )
        
        history = memory_manager.get_conversation_history(
            conversation_id=conversation.conversation_id
        )
        
        assert len(history) == 2
        assert history[0].content == "你好"
        assert history[1].content == "你好!有什么可以帮助你的吗?"
    
    def test_retrieve_relevant_context(self, db_session: Session, test_user):
        """测试检索相关上下文"""
        memory_manager = ConversationMemoryManager(db_session)
        
        conversation = memory_manager.create_new_conversation(
            user_id=test_user.user_id
        )
        
        memory_manager.add_message(
            conversation_id=conversation.conversation_id,
            role="user",
            content="狗的常见疾病有哪些?",
            store_in_vector_db=True
        )
        
        memory_manager.add_message(
            conversation_id=conversation.conversation_id,
            role="assistant",
            content="狗的常见疾病包括犬瘟热、细小病毒等",
            store_in_vector_db=True
        )
        
        relevant_context = memory_manager.retrieve_relevant_context(
            query="狗的疾病",
            n_results=2
        )
        
        assert relevant_context is not None
        assert len(relevant_context) > 0
