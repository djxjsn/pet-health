"""
多轮对话与向量检索专项测试

测试上下文保持、向量数据库检索等功能
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session


class TestMultiTurnConversation:
    """多轮对话上下文保持测试"""
    
    @pytest.fixture
    def test_user(self, db_session: Session):
        """创建测试用户"""
        from src.db.crud.user import create_user
        from src.schemas.user import UserCreate
        
        user_data = UserCreate(
            phone="13800000002",
            email="multi_turn@example.com",
            password="test1234"
        )
        return create_user(db_session, user_data)
    
    def test_conversation_context_persistence(
        self,
        db_session: Session,
        test_user
    ):
        """测试对话上下文持久化"""
        from src.memory.conversation_memory import ConversationMemoryManager
        
        memory = ConversationMemoryManager(db_session)
        
        # 创建对话
        conv = memory.create_new_conversation(
            user_id=test_user.user_id,
            title="多轮对话测试"
        )
        
        conversation_id = conv.conversation_id
        
        # 第一轮：添加消息
        msg1 = memory.add_message(
            conversation_id=conversation_id,
            role="user",
            content="我的狗叫旺财"
        )
        
        # 第二轮：添加回复
        msg2 = memory.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content="您好！旺财是一只很可爱的名字。请问它多大了？"
        )
        
        # 第三轮：继续对话
        msg3 = memory.add_message(
            conversation_id=conversation_id,
            role="user",
            content="它今年2岁了"
        )
        
        # 验证消息数量
        assert conv.message_count == 3
        
        # 获取历史记录
        history = memory.get_conversation_history(
            conversation_id=conversation_id
        )
        
        # 验证历史记录完整性
        assert len(history) == 3
        contents = [h.content for h in history]
        assert "我的狗叫旺财" in contents
        assert "它今年2岁了" in contents
    
    def test_context_retrieval_for_followup(
        self,
        db_session: Session,
        test_user
    ):
        """测试后续问题的上下文检索"""
        from src.memory.conversation_memory import ConversationMemoryManager
        
        memory = ConversationMemoryManager(db_session)
        
        # 创建对话并添加历史
        conv = memory.create_new_conversation(user_id=test_user.user_id)
        
        memory.add_message(
            conversation_id=conv.conversation_id,
            role="user",
            content="我有一只金毛寻回犬",
            store_in_vector_db=True
        )
        
        memory.add_message(
            conversation_id=conv.conversation_id,
            role="assistant",
            content="金毛是非常优秀的家庭伴侣犬，性格温顺友好。",
            store_in_vector_db=True
        )
        
        # 检索相关上下文
        context = memory.retrieve_relevant_context(
            query="金毛的饮食建议",
            n_results=2
        )
        
        # 验证检索结果
        assert context is not None
        assert len(context) > 0
    
    def test_separate_conversations_isolation(
        self,
        db_session: Session,
        test_user
    ):
        """测试不同对话之间的隔离性"""
        from src.memory.conversation_memory import ConversationMemoryManager
        
        memory = ConversationMemoryManager(db_session)
        
        # 创建两个独立对话
        conv1 = memory.create_new_conversation(
            user_id=test_user.user_id,
            title="对话1"
        )
        
        conv2 = memory.create_new_conversation(
            user_id=test_user.user_id,
            title="对话2"
        )
        
        # 向对话1添加消息
        memory.add_message(
            conversation_id=conv1.conversation_id,
            role="user",
            content="这是对话1的内容"
        )
        
        # 向对话2添加消息
        memory.add_message(
            conversation_id=conv2.conversation_id,
            role="user",
            content="这是对话2的内容"
        )
        
        # 获取各自的历史记录
        history1 = memory.get_conversation_history(conv1.conversation_id)
        history2 = memory.get_conversation_history(conv2.conversation_id)
        
        # 验证隔离性
        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0].content != history2[0].content


class TestVectorDatabaseRetrieval:
    """向量数据库检索功能测试"""
    
    @pytest.fixture
    def setup_test_data(self):
        """设置测试数据"""
        from src.core.vector_db import VectorDatabase
        
        VectorDatabase._instance = None
        db = VectorDatabase()
        
        # 添加测试文档
        test_docs = [
            {
                "content": "狗需要定期接种疫苗,包括犬瘟热、细小病毒等疫苗",
                "metadata": {"category": "vaccination", "species": "dog"},
                "id": "test_vac_1"
            },
            {
                "content": "猫的常见疾病包括猫瘟、猫鼻支、猫传腹等",
                "metadata": {"category": "disease", "species": "cat"},
                "id": "test_dis_1"
            },
            {
                "content": "宠物饮食应该营养均衡,包含蛋白质、脂肪、碳水化合物等",
                "metadata": {"category": "nutrition", "type": "general"},
                "id": "test_nut_1"
            }
        ]
        
        for doc in test_docs:
            db.add_documents(
                documents=[doc["content"]],
                metadatas=[doc["metadata"]],
                ids=[doc["id"]]
            )
        
        return db
    
    def test_basic_similarity_search(self, setup_test_data):
        """测试基础相似度搜索"""
        results = setup_test_data.query(
            query_texts=["狗的疫苗接种"],
            n_results=2
        )
        
        assert results is not None
        assert 'documents' in results
        assert len(results['documents'][0]) > 0
    
    def test_filtered_search(self, setup_test_data):
        """测试带过滤条件的搜索"""
        results = setup_test_data.query(
            query_texts=["疾病"],
            n_results=5,
            where={"species": "cat"}
        )
        
        assert results is not None
        if results.get('documents') and len(results['documents'][0]) > 0:
            for meta in results.get('metadatas', [[]])[0]:
                assert meta.get('species') == 'cat'
    
    def test_multiple_queries_batch(self, setup_test_data):
        """测试批量查询"""
        queries = ["狗的疫苗", "猫的疾病", "宠物饮食"]
        
        results = setup_test_data.query(
            query_texts=queries,
            n_results=1
        )
        
        assert results is not None
        assert len(results['documents']) == len(queries)
    
    def test_document_update_and_requery(self, setup_test_data):
        """测试文档更新后重新查询"""
        original_id = "test_update_requery"
        
        # 添加原始文档
        setup_test_data.add_documents(
            documents=["原始内容"],
            ids=[original_id]
        )
        
        # 更新文档
        setup_test_data.update_documents(
            ids=[original_id],
            documents=["更新后的新内容"]
        )
        
        # 查询新内容
        results = setup_test_data.query(
            query_texts=["新内容"],
            n_results=1
        )
        
        assert results is not None
    
    def test_empty_result_handling(self, setup_test_data):
        """测试空结果处理"""
        results = setup_test_data.query(
            query_texts=["完全不相关的内容xyz123"],
            n_results=3
        )
        
        assert results is not None
        # 即使没有精确匹配也应该返回结果（基于向量相似度）
    
    def test_large_document_count(self):
        """测试大量文档处理"""
        from src.core.vector_db import VectorDatabase
        
        VectorDatabase._instance = None
        db = VectorDatabase()
        
        # 批量添加100个文档
        docs = [f"测试文档{i}: 宠物健康知识" for i in range(100)]
        ids = [f"bulk_doc_{i}" for i in range(100)]
        
        db.add_documents(documents=docs, ids=ids)
        
        count = db.get_document_count()
        assert count >= 100


class TestAgentContextManagement:
    """Agent上下文管理测试"""
    
    @pytest.fixture
    def mock_agent(self, db_session: Session):
        with patch('src.core.llm.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = "模拟回复"
            mock_get_llm.return_value = mock_llm
            
            from src.agents.pet_health_agent import PetHealthAgent
            agent = PetHealthAgent(
                db=db_session,
                user_id="test_user_123"
            )
            
            return agent
    
    def test_state_initialization(self, mock_agent):
        assert mock_agent.state.current_task == ""
        assert len(mock_agent.state.plan) == 0
        assert len(mock_agent.state.results) == 0
    
    def test_state_clearing(self, mock_agent):
        mock_agent.state.current_task = "测试任务"
        mock_agent.state.plan = [{"tool": "test"}]
        mock_agent.state.results = ["result1"]
        
        from src.agents.base_agent import AgentState, AgentStatus
        mock_agent.state = AgentState()
        
        assert mock_agent.state.current_task == ""
        assert len(mock_agent.state.plan) == 0
        assert len(mock_agent.state.results) == 0
    
    def test_tool_registration(self, mock_agent):
        initial_count = len(mock_agent.tools)
        
        from src.tools.pet_health_tools import HealthKnowledgeTool
        new_tool = HealthKnowledgeTool()
        mock_agent.tools.append(new_tool)
        
        assert len(mock_agent.tools) == initial_count + 1
        assert "search_health_knowledge" in [t.name for t in mock_agent.tools]


class TestEdgeCases:
    """边界情况测试"""
    
    def test_very_long_message(self, db_session: Session):
        """测试超长消息处理"""
        from src.memory.conversation_memory import ConversationMemoryManager
        from src.db.crud.user import create_user
        from src.schemas.user import UserCreate
        
        user = create_user(db_session, UserCreate(
            phone="13800000003",
            email="long_msg@test.com",
            password="test1234"
        ))
        
        memory = ConversationMemoryManager(db_session)
        conv = memory.create_new_conversation(user_id=user.user_id)
        
        long_message = "测试" * 10000  # 20000字符的消息
        
        try:
            message = memory.add_message(
                conversation_id=conv.conversation_id,
                role="user",
                content=long_message
            )
            
            assert message.content == long_message
        except Exception as e:
            pytest.fail(f"长消息处理失败: {e}")
    
    def test_special_characters_in_message(self, db_session: Session):
        """测试特殊字符处理"""
        from src.memory.conversation_memory import ConversationMemoryManager
        from src.db.crud.user import create_user
        from src.schemas.user import UserCreate
        
        user = create_user(db_session, UserCreate(
            phone="13800000004",
            email="special@test.com",
            password="test1234"
        ))
        
        memory = ConversationMemoryManager(db_session)
        conv = memory.create_new_conversation(user_id=user.user_id)
        
        special_messages = [
            "Hello! <script>alert('xss')</script>",
            "中文测试 🎉🐕",
            "Emoji: 😊👍💖",
            "Special: \n\t\r\n",
            "Unicode: 你好世界🌍"
        ]
        
        for msg in special_messages:
            result = memory.add_message(
                conversation_id=conv.conversation_id,
                role="user",
                content=msg
            )
            assert result.content == msg
    
    def test_rapid_successive_requests(self, db_session: Session):
        """测试快速连续请求"""
        from src.memory.conversation_memory import ConversationMemoryManager
        from src.db.crud.user import create_user
        from src.schemas.user import UserCreate
        
        user = create_user(db_session, UserCreate(
            phone="13800000005",
            email="rapid@test.com",
            password="test1234"
        ))
        
        memory = ConversationMemoryManager(db_session)
        conv = memory.create_new_conversation(user_id=user.user_id)
        
        messages = []
        for i in range(10):
            msg = memory.add_message(
                conversation_id=conv.conversation_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"快速请求 {i}"
            )
            messages.append(msg)
        
        assert len(messages) == 10
        assert conv.message_count == 10
