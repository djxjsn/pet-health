"""
集成测试 - 端到端流程测试
"""
import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from src.agents.pet_health_agent import PetHealthAgent
from src.memory.conversation_memory import ConversationMemoryManager
from src.core.vector_db import get_vector_db
from src.db.crud import create_user, create_pet
from src.schemas.user import UserCreate
from src.schemas.pet import PetCreate


class TestEndToEndIntegration:
    """端到端集成测试类"""
    
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
    
    @pytest.fixture
    def test_pet(self, db_session: Session, test_user):
        """创建测试宠物"""
        pet_data = PetCreate(
            name="旺财",
            species="dog",
            breed="金毛",
            gender="male"
        )
        pet = create_pet(db_session, test_user.user_id, pet_data)
        return pet
    
    @pytest.fixture
    def mock_llm(self):
        """创建模拟LLM"""
        llm = Mock()
        
        def mock_invoke(messages):
            if "规划" in str(messages) or "plan" in str(messages).lower():
                return '[{"tool": "get_user_pets", "args": {"user_id": "test"}, "reason": "获取用户宠物"}]'
            else:
                return "这是一个关于宠物健康的模拟响应"
        
        llm.invoke = Mock(side_effect=mock_invoke)
        return llm
    
    def test_full_conversation_flow(
        self,
        db_session: Session,
        test_user,
        test_pet,
        mock_llm
    ):
        """测试完整对话流程"""
        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )
        
        result = agent.chat(
            user_input="我的宠物有哪些?",
            pet_id=test_pet.pet_id
        )
        
        assert result is not None
        assert "conversation_id" in result
        assert "response" in result
        assert result["conversation_id"] is not None
    
    def test_memory_integration(
        self,
        db_session: Session,
        test_user,
        mock_llm
    ):
        """测试记忆系统集成"""
        memory_manager = ConversationMemoryManager(db_session)
        
        conversation = memory_manager.create_new_conversation(
            user_id=test_user.user_id,
            title="测试对话"
        )
        
        memory_manager.add_message(
            conversation_id=conversation.conversation_id,
            role="user",
            content="你好",
            store_in_vector_db=True
        )
        
        memory_manager.add_message(
            conversation_id=conversation.conversation_id,
            role="assistant",
            content="你好!我是宠物健康助手",
            store_in_vector_db=True
        )
        
        history = memory_manager.get_conversation_history(
            conversation_id=conversation.conversation_id
        )
        
        assert len(history) == 2
        
        relevant_context = memory_manager.retrieve_relevant_context(
            query="你好",
            n_results=1
        )
        
        assert relevant_context is not None
    
    def test_vector_db_integration(self):
        """测试向量数据库集成"""
        vector_db = get_vector_db()
        
        test_documents = [
            "狗需要定期接种疫苗",
            "猫的饮食需要注意营养均衡",
            "宠物生病时需要及时就医"
        ]
        
        vector_db.add_documents(
            documents=test_documents,
            ids=["integration_test_1", "integration_test_2", "integration_test_3"]
        )
        
        results = vector_db.query(
            query_texts=["狗的疫苗"],
            n_results=2
        )
        
        assert results is not None
        assert len(results['documents'][0]) > 0
        
        vector_db.delete_documents(
            ids=["integration_test_1", "integration_test_2", "integration_test_3"]
        )
    
    def test_tool_execution_integration(
        self,
        db_session: Session,
        test_user,
        test_pet,
        mock_llm
    ):
        """测试工具执行集成"""
        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )
        
        action = {
            "tool": "get_pet_info",
            "args": {"pet_id": test_pet.pet_id}
        }
        
        result = agent.execute_action(action)
        
        assert result is not None
        assert "pet_id" in result
        assert result["name"] == "旺财"
    
    def test_multi_turn_conversation(
        self,
        db_session: Session,
        test_user,
        test_pet,
        mock_llm
    ):
        """测试多轮对话"""
        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )
        
        result1 = agent.chat(
            user_input="你好",
            pet_id=test_pet.pet_id
        )
        
        conversation_id = result1["conversation_id"]
        
        result2 = agent.chat(
            user_input="我的宠物叫什么?",
            conversation_id=conversation_id
        )
        
        assert result2["conversation_id"] == conversation_id
        
        history = agent.memory_manager.get_conversation_history(
            conversation_id=conversation_id
        )
        
        assert len(history) >= 4
