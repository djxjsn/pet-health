"""
单元测试：ConversationMemoryManager (MongoDB版本)

验证修复后的对话记忆管理器是否正确使用MongoDB Repository
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.memory.conversation_memory import ConversationMemoryManager
from src.repositories.mongo_repositories import (
    ConversationRepository,
    MessageRepository,
)


class TestConversationMemoryManagerInit:
    """测试ConversationMemoryManager初始化"""

    def test_init_without_db(self):
        """测试不需要db参数即可初始化（MongoDB版本）"""
        # 不应该抛出异常
        manager = ConversationMemoryManager()
        assert manager is not None
        assert manager.db is None  # MongoDB版本不需要db session

    def test_init_with_db_none(self):
        """测试db=None时正常初始化"""
        manager = ConversationMemoryManager(db=None)
        assert manager is not None


class TestCreateNewConversation:
    """测试创建新对话"""

    @pytest.fixture
    def mock_memory_manager(self):
        """创建Mock的MemoryManager实例"""
        with patch.object(ConversationRepository, 'create') as mock_create:
            yield ConversationMemoryManager()

    def test_create_conversation_returns_dict(self, mock_memory_manager):
        """测试创建对话返回字典类型"""
        with patch.object(ConversationRepository, 'create', return_value='test-conv-id') as mock_create:
            manager = ConversationMemoryManager()
            result = manager.create_new_conversation(
                user_id='test-user-123',
                title='Test Conversation'
            )

            assert isinstance(result, dict)
            assert 'conversation_id' in result
            assert result['conversation_id'] == 'test-conv-id'
            mock_create.assert_called_once()

    def test_create_conversation_with_all_params(self, mock_memory_manager):
        """测试创建对话包含所有参数"""
        test_uuid = str(uuid.uuid4())

        with patch.object(ConversationRepository, 'create', return_value=test_uuid) as mock_create:
            manager = ConversationMemoryManager()
            result = manager.create_new_conversation(
                user_id='user-456',
                pet_id='pet-789',
                title='My Pet Health Question',
                context={'source': 'web'}
            )

            # 验证调用参数
            call_args = mock_create.call_args[0][0]
            assert call_args['user_id'] == 'user-456'
            assert call_args['pet_id'] == 'pet-789'
            assert call_args['title'] == 'My Pet Health Question'
            assert call_args['context']['source'] == 'web'

    def test_create_conversation_generates_uuid(self):
        """测试自动生成UUID格式的conversation_id"""
        with patch.object(ConversationRepository, 'create') as mock_create:
            def capture_and_return(doc):
                assert 'conversation_id' in doc
                assert isinstance(doc['conversation_id'], str)
                try:
                    uuid.UUID(doc['conversation_id'])
                except ValueError:
                    pytest.fail("conversation_id should be a valid UUID")
                return doc['conversation_id']

            mock_create.side_effect = capture_and_return

            manager = ConversationMemoryManager()
            result = manager.create_new_conversation(user_id='test-user')

            assert result is not None


class TestAddMessage:
    """测试添加消息"""

    def test_add_user_message(self):
        """测试添加用户消息"""
        test_msg_id = str(uuid.uuid4())
        test_conv_id = str(uuid.uuid4())

        with patch.object(MessageRepository, 'create', return_value=test_msg_id) as mock_create:
            manager = ConversationMemoryManager()
            result = manager.add_message(
                conversation_id=test_conv_id,
                role='user',
                content='Hello, my dog is sick'
            )

            assert isinstance(result, dict)
            assert result['role'] == 'user'
            assert result['content'] == 'Hello, my dog is sick'
            assert result['message_id'] == test_msg_id
            assert result['conversation_id'] == test_conv_id

            # 验证调用参数
            call_args = mock_create.call_args[0][0]
            assert call_args['role'] == 'user'
            assert call_args['content'] == 'Hello, my dog is sick'

    def test_add_assistant_message(self):
        """测试添加助手回复消息"""
        test_msg_id = str(uuid.uuid4())

        with patch.object(MessageRepository, 'create', return_value=test_msg_id) as mock_create:
            manager = ConversationMemoryManager()
            result = manager.add_message(
                conversation_id='conv-123',
                role='assistant',
                content='I can help you with that. What symptoms does your dog have?'
            )

            assert result['role'] == 'assistant'
            assert 'help you' in result['content']

    def test_add_message_with_metadata(self):
        """测试带元数据的消息"""
        test_msg_id = str(uuid.uuid4())
        metadata = {'model': 'deepseek-chat', 'tokens': 150}

        with patch.object(MessageRepository, 'create', return_value=test_msg_id) as mock_create:
            manager = ConversationMemoryManager()
            result = manager.add_message(
                conversation_id='conv-123',
                role='assistant',
                content='Response here',
                metadata=metadata
            )

            call_args = mock_create.call_args[0][0]
            assert call_args['metadata'] == metadata

    def test_add_message_updates_langchain_memory(self):
        """测试消息会更新LangChain内存"""
        with patch.object(MessageRepository, 'create', return_value='msg-123'):
            manager = ConversationMemoryManager()

            # 添加用户消息
            manager.add_message(conversation_id='conv-1', role='user', content='User says hi')
            # 添加助手消息
            manager.add_message(conversation_id='conv-1', role='assistant', content='AI responds')

            # 验证LangChain内存已更新
            assert len(manager.langchain_memory.chat_memory.messages) == 2

    def test_add_message_without_vector_db(self):
        """测试向量数据库不可用时仍能保存消息"""
        with patch.object(MessageRepository, 'create', return_value='msg-123') as mock_create:
            with patch.object(ConversationMemoryManager, 'vector_db', None):  # 模拟vector_db不可用
                manager = ConversationMemoryManager()

                result = manager.add_message(
                    conversation_id='conv-1',
                    role='user',
                    content='Test message',
                    store_in_vector_db=True
                )

                # 即使vector_db不可用，也应该成功创建消息
                assert result is not None
                mock_create.assert_called_once()


class TestGetConversationHistory:
    """测试获取对话历史"""

    def test_get_empty_history(self):
        """测试获取空对话历史"""
        with patch.object(MessageRepository, 'list_by_conversation', return_value=[]):
            manager = ConversationMemoryManager()
            history = manager.get_conversation_history('nonexistent-conv')

            assert history == []
            assert isinstance(history, list)

    def test_get_history_returns_langchain_format(self):
        """测试返回LangChain格式的历史记录"""
        mock_messages = [
            {
                'message_id': 'msg-1',
                'conversation_id': 'conv-1',
                'role': 'user',
                'content': 'Hello'
            },
            {
                'message_id': 'msg-2',
                'conversation_id': 'conv-1',
                'role': 'assistant',
                'content': 'Hi there!'
            }
        ]

        with patch.object(MessageRepository, 'list_by_conversation', return_value=mock_messages):
            manager = ConversationMemoryManager()
            history = manager.get_conversation_history('conv-1')

            assert len(history) == 2
            from langchain_core.messages import HumanMessage, AIMessage
            assert isinstance(history[0], HumanMessage)
            assert isinstance(history[1], AIMessage)
            assert history[0].content == 'Hello'
            assert history[1].content == 'Hi there!'

    def test_get_history_respects_limit(self):
        """测试limit参数生效"""
        mock_messages = [{'message_id': f'msg-{i}', 'role': 'user', 'content': f'Msg {i}'}
                        for i in range(10)]

        with patch.object(MessageRepository, 'list_by_conversation', return_value=mock_messages) as mock_list:
            manager = ConversationMemoryManager()

            # 请求5条
            history = manager.get_conversation_history('conv-1', limit=5)

            # 验证传递了正确的limit参数
            call_kwargs = mock_list.call_args[1]
            assert call_kwargs['limit'] == 5

    def test_get_history_handles_system_role(self):
        """测试处理system角色的消息"""
        mock_messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'}
        ]

        with patch.object(MessageRepository, 'list_by_conversation', return_value=mock_messages):
            manager = ConversationMemoryManager()
            history = manager.get_conversation_history('conv-1')

            from langchain_core.messages import SystemMessage
            assert len(history) == 1
            assert isinstance(history[0], SystemMessage)


class TestRetrieveRelevantContext:
    """测试检索相关上下文"""

    def test_retrieve_context_calls_retriever(self):
        """测试调用检索器"""
        mock_results = [
            {'content': 'Dog health info', 'score': 0.9},
            {'content': 'Pet care tips', 'score': 0.8}
        ]

        with patch.object(ConversationMemoryManager, 'retriever') as mock_retriever:
            mock_retriever.search_for_conversation_context.return_value = mock_results

            manager = ConversationMemoryManager()
            results = manager.retrieve_relevant_context(query="dog health", n_results=3)

            mock_retriever.search_for_conversation_context.assert_called_once_with(
                query="dog health",
                conversation_id=None,
                n_results=3
            )
            assert results == mock_results

    def test_retrieve_context_with_conversation_filter(self):
        """测试使用对话ID过滤"""
        with patch.object(ConversationMemoryManager, 'retriever') as mock_retriever:
            mock_retriever.search_for_conversation_context.return_value = []

            manager = ConversationMemoryManager()
            manager.retrieve_relevant_context(
                query="test",
                conversation_id='conv-123',
                n_results=5
            )

            call_kwargs = mock_retriever.search_for_conversation_context.call_args[1]
            assert call_kwargs['conversation_id'] == 'conv-123'


class TestClearMemory:
    """测试清空内存"""

    def test_clear_memory_resets_langchain(self):
        """测试清空LangChain内存"""
        with patch.object(MessageRepository, 'create', return_value='msg-1'):
            manager = ConversationMemoryManager()

            # 添加一些消息
            manager.add_message('conv-1', 'user', 'hello')
            manager.add_message('conv-1', 'assistant', 'hi')

            assert len(manager.langchain_memory.chat_memory.messages) > 0

            # 清空
            manager.clear_memory()

            assert len(manager.langchain_memory.chat_memory.messages) == 0


class TestIntegrationWorkflow:
    """集成测试：完整的工作流程"""

    def test_full_conversation_workflow(self):
        """测试完整的对话工作流：创建→添加消息→查询历史"""
        conv_id = str(uuid.uuid4())
        msg_ids = [str(uuid.uuid4()), str(uuid.uuid4())]

        with patch.object(ConversationRepository, 'create', return_value=conv_id) as mock_conv_create:
            with patch.object(MessageRepository, 'create', side_effect=msg_ids) as msg_create_side_effect:
                with patch.object(MessageRepository, 'list_by_conversation', return_value=[
                    {'message_id': msg_ids[0], 'role': 'user', 'content': 'My cat wont eat'},
                    {'message_id': msg_ids[1], 'role': 'assistant', 'content': 'Let me help...'}
                ]):
                    manager = ConversationMemoryManager()

                    # Step 1: 创建对话
                    convo = manager.create_new_conversation(
                        user_id='user-1',
                        title='Cat not eating'
                    )
                    assert convo['conversation_id'] == conv_id

                    # Step 2: 添加用户消息
                    user_msg = manager.add_message(
                        conversation_id=conv_id,
                        role='user',
                        content='My cat wont eat'
                    )
                    assert user_msg['message_id'] == msg_ids[0]

                    # Step 3: 添加助手回复
                    ai_msg = manager.add_message(
                        conversation_id=conv_id,
                        role='assistant',
                        content='Let me help you with that'
                    )
                    assert ai_msg['message_id'] == msg_ids[1]

                    # Step 4: 获取历史
                    history = manager.get_conversation_history(conv_id)
                    assert len(history) == 2

                    print("\n✅ 完整工作流测试通过！")
                    print(f"   对话ID: {conv_id}")
                    print(f"   用户消息: {history[0].content}")
                    print(f"   AI回复: {history[1].content}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
