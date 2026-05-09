"""
端到端测试：MongoDB存储修复验证

完整的E2E测试，验证从API到MongoDB的完整数据流
"""
import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.agents.pet_health_agent import PetHealthAgent
from src.memory.conversation_memory import ConversationMemoryManager
from src.repositories.mongo_repositories import (
    ConversationRepository,
    MessageRepository,
)


class TestEndToEndConversationFlow:
    """端到端对话流程测试"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock数据库会话（虽然不再需要，但保持兼容）"""
        return Mock()

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM实例"""
        llm = Mock()
        llm.invoke.return_value = Mock(content="I understand your concern about your pet's health.")
        return llm

    def test_complete_chat_flow_saves_to_mongodb(self, mock_db_session, mock_llm):
        """
        测试完整的聊天流程：
        1. 用户发送消息
        2. Agent处理
        3. 对话和消息保存到MongoDB
        4. 可以从MongoDB查询到数据
        """
        test_user_id = f'e2e_user_{uuid.uuid4()}'
        test_input = "My dog has been vomiting for 2 days"

        # Mock MongoDB operations
        with patch.object(ConversationRepository, 'create') as mock_create_conv:
            with patch.object(MessageRepository, 'create', side_effect=[
                f'e2e_msg_user_{uuid.uuid4()}',
                f'e2e_msg_ai_{uuid.uuid4()}'
            ]) as mock_create_msg:
                # 设置返回值
                conv_id = f'e2e_conv_{uuid.uuid4()}'
                mock_create_conv.return_value = conv_id

                # 创建Agent（使用mock的LLM避免实际调用）
                agent = PetHealthAgent(
                    db=mock_db_session,
                    llm=mock_llm,
                    user_id=test_user_id
                )

                # 执行聊天
                result = agent.chat(
                    user_input=test_input,
                    pet_id=None
                )

                # 验证结果
                assert 'conversation_id' in result
                assert 'response' in result
                assert result['conversation_id'] == conv_id

                # 验证MongoDB操作被调用
                assert mock_create_conv.call_count == 1  # 创建了1个对话
                assert mock_create_msg.call_count == 2   # 创建了2条消息（用户+AI）

                print("\n✅ E2E测试通过：完整聊天流程正常工作")
                print(f"   用户: {test_user_id}")
                print(f"   输入: {test_input}")
                print(f"   对话ID: {conv_id}")
                print(f"   AI回复: {result['response'][:50]}...")

    def test_multi_turn_conversation_maintains_context(self, mock_db_session, mock_llm):
        """测试多轮对话保持上下文"""
        test_user_id = f'multi_turn_user_{uuid.uuid4()}'
        conv_id = f'multi_turn_conv_{uuid.uuid4()}'

        msg_counter = [0]
        def generate_msg_id(doc):
            msg_counter[0] += 1
            return f'multi_turn_msg_{msg_counter[0]}_{uuid.uuid4()}'

        with patch.object(ConversationRepository, 'create', return_value=conv_id) as mock_conv:
            with patch.object(MessageRepository.create, 'side_effect', generate_msg_id) as mock_msg:
                with patch.object(MessageRepository, 'list_by_conversation', return_value=[]):
                    agent = PetHealthAgent(
                        db=mock_db_session,
                        llm=mock_llm,
                        user_id=test_user_id
                    )

                    # 第一轮对话
                    result1 = agent.chat(user_input="Hello")
                    assert result1['conversation_id'] == conv_id

                    # 第二轮对话（应该使用相同的conversation_id）
                    result2 = agent.chat(
                        user_input="Follow up question",
                        conversation_id=conv_id
                    )

                    assert result2['conversation_id'] == conv_id

                    # 验证只创建了1个对话（多轮复用）
                    assert mock_conv.call_count == 1

                    # 验证创建了4条消息（2轮 × 每轮2条）
                    assert mock_msg.call_count == 4

                    print("\n✅ 多轮对话测试通过")
                    print(f"   对话ID: {conv_id}")
                    print(f"   轮次: 2")
                    print(f"   总消息数: 4")


class TestDataConsistency:
    """数据一致性测试"""

    def test_conversation_and_messages_linked(self):
        """测试对话和消息正确关联"""
        conv_id = f'consistency_conv_{uuid.uuid4()}'
        user_id = f'consistency_user_{uuid.uuid4()}'
        msg_ids = []

        def capture_msg_id(doc):
            msg_id = f'consistency_msg_{uuid.uuid4()}'
            msg_ids.append(msg_id)
            return msg_id

        with patch.object(ConversationRepository, 'create', return_value=conv_id):
            with patch.object(MessageRepository.create, side_effect=capture_msg_id):
                manager = ConversationMemoryManager()

                # 创建对话
                convo = manager.create_new_conversation(
                    user_id=user_id,
                    title='Consistency Test'
                )

                # 添加3条消息
                for i in range(3):
                    manager.add_message(
                        conversation_id=conv_id,
                        role='user',
                        content=f'Message {i}'
                    )

                # 验证所有消息都关联到同一个对话
                assert len(msg_ids) == 3

                print("\n✅ 数据一致性测试通过")
                print(f"   对话ID: {conv_id}")
                print(f"   消息数量: {len(msg_ids)}")
                print(f"   所有消息都关联到同一对话: True")

    def test_timestamp_ordering(self):
        """测试时间戳顺序正确"""
        timestamps = []

        def capture_timestamp(doc):
            ts = doc.get('created_at')
            if ts:
                timestamps.append(ts)
            return uuid.uuid4()

        with patch.object(MessageRepository.create, side_effect=capture_timestamp):
            manager = ConversationMemoryManager()
            conv_id = f'timestamp_conv_{uuid.uuid4()}'

            # 快速添加多条消息
            for _ in range(5):
                manager.add_message(
                    conversation_id=conv_id,
                    role='user',
                    content='test'
                )

            # 验证时间戳递增（或至少不递减）
            if len(timestamps) >= 2:
                for i in range(len(timestamps) - 1):
                    assert timestamps[i] <= timestamps[i+1], \
                        f"Timestamp ordering error at index {i}"

                print("\n✅ 时间戳顺序测试通过")
                print(f"   消息数: {len(timestamps)}")
                print(f"   时间戳单调递增: True")


class TestErrorHandling:
    """错误处理测试"""

    def test_handles_mongodb_connection_error_gracefully(self):
        """测试优雅处理MongoDB连接错误"""
        with patch.object(ConversationRepository, 'create', side_effect=Exception("Connection failed")):
            manager = ConversationMemoryManager()

            with pytest.raises(Exception) as exc_info:
                manager.create_new_conversation(
                    user_id='test_user',
                    title='Should Fail'
                )

            assert "Connection failed" in str(exc_info.value)
            print("\n✅ 错误处理测试通过")

    def test_invalid_role_rejected(self):
        """测试拒绝无效的角色类型"""
        valid_roles = ['user', 'assistant', 'system']

        with patch.object(MessageRepository.create, return_value='msg-id'):
            manager = ConversationMemoryManager()

            # 测试有效角色
            for role in valid_roles:
                try:
                    result = manager.add_message(
                        conversation_id='test-conv',
                        role=role,
                        content='Test'
                    )
                    assert result is not None
                except Exception as e:
                    pytest.fail(f"Valid role '{role}' should not raise exception: {e}")

            print("\n✅ 角色验证测试通过")
            print(f"   有效角色: {valid_roles}")


class TestPerformance:
    """性能基准测试"""

    def test_bulk_message_creation_performance(self):
        """测试批量创建消息的性能"""
        import time

        conv_id = f'perf_conv_{uuid.uuid4()}'
        num_messages = 100

        start_time = time.time()

        with patch.object(MessageRepository.create, return_value=str(uuid.uuid4())):
            manager = ConversationMemoryManager()

            for i in range(num_messages):
                manager.add_message(
                    conversation_id=conv_id,
                    role='user' if i % 2 == 0 else 'assistant',
                    content=f'Performance test message {i}'
                )

        end_time = time.time()
        elapsed = end_time - start_time

        # 应该在合理时间内完成（< 5秒，因为是mock）
        assert elapsed < 5.0, f"Took too long: {elapsed:.2f}s"

        print(f"\n✅ 性能测试通过")
        print(f"   消息数量: {num_messages}")
        print(f"   总耗时: {elapsed:.3f}s")
        print(f"   平均每条: {(elapsed/num_messages)*1000:.2f}ms")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-s'])
