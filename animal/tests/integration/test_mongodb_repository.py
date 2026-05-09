"""
集成测试：MongoDB Repository 操作

验证MongoDB Repository的CRUD操作是否正常工作
"""
import pytest
import uuid
from datetime import datetime
from bson import ObjectId

from src.repositories.mongo_repositories import (
    ConversationRepository,
    MessageRepository,
)
from src.core.mongodb import get_mongo_collection


@pytest.fixture(scope='module')
def test_db():
    """获取MongoDB测试数据库连接"""
    from src.core.mongodb import get_mongodb
    db = get_mongodb()
    yield db


@pytest.fixture
def cleanup_conversations(test_db):
    """清理测试对话数据的fixture"""
    conv_collection = test_db['conversations']
    msg_collection = test_db['messages']

    yield

    # 测试完成后清理
    conv_collection.delete_many({'user_id': {'$regex': '^test_'}})
    msg_collection.delete_many({'conversation_id': {'$regex': '^test_'}})


class TestConversationRepository:
    """ConversationRepository 集成测试"""

    def test_create_conversation(self, test_db, cleanup_conversations):
        """测试创建对话"""
        test_data = {
            'conversation_id': f'test_conv_{uuid.uuid4()}',
            'user_id': f'test_user_{uuid.uuid4()}',
            'title': 'Test Conversation',
            'pet_id': None,
            'context': {}
        }

        result = ConversationRepository.create(test_data)

        assert result is not None
        assert isinstance(result, str)

        # 验证数据已保存
        saved = ConversationRepository.get_by_id(result)
        assert saved is not None
        assert saved['title'] == 'Test Conversation'
        assert saved['user_id'] == test_data['user_id']

    def test_get_by_id_not_found(self, test_db):
        """测试查询不存在的对话"""
        result = ConversationRepository.get_by_id('nonexistent-id')
        assert result is None

    def test_list_by_user(self, test_db, cleanup_conversations):
        """测试按用户查询对话列表"""
        user_id = f'test_user_list_{uuid.uuid4()}'

        # 创建多个对话
        for i in range(3):
            ConversationRepository.create({
                'conversation_id': f'test_conv_{uuid.uuid4()}',
                'user_id': user_id,
                'title': f'Conversation {i}',
                'pet_id': None,
                'context': {}
            })

        conversations = ConversationRepository.list_by_user(user_id=user_id)

        assert len(conversations) >= 3
        for convo in conversations:
            assert convo['user_id'] == user_id

    def test_update_conversation(self, test_db, cleanup_conversations):
        """测试更新对话"""
        conv_id = f'test_conv_update_{uuid.uuid4()}'
        user_id = f'test_user_update_{uuid.uuid4()}'

        # 创建对话
        ConversationRepository.create({
            'conversation_id': conv_id,
            'user_id': user_id,
            'title': 'Original Title',
            'pet_id': None,
            'context': {}
        })

        # 更新标题
        success = ConversationRepository.update(conv_id, {'title': 'Updated Title'})

        assert success is True

        # 验证更新
        updated = ConversationRepository.get_by_id(conv_id)
        assert updated['title'] == 'Updated Title'

    def test_delete_conversation_cascades_messages(self, test_db, cleanup_conversations):
        """测试删除对话时级联删除消息"""
        conv_id = f'test_conv_delete_{uuid.uuid4()}'
        user_id = f'test_user_del_{uuid.uuid4()}'

        # 创建对话
        ConversationRepository.create({
            'conversation_id': conv_id,
            'user_id': user_id,
            'title': 'To Delete',
            'pet_id': None,
            'context': {}
        })

        # 添加消息
        MessageRepository.create({
            'message_id': f'test_msg_{uuid.uuid4()}',
            'conversation_id': conv_id,
            'role': 'user',
            'content': 'This will be deleted'
        })

        # 删除对话
        success = ConversationRepository.delete(conv_id)

        assert success is True

        # 验证对话和消息都被删除
        assert ConversationRepository.get_by_id(conv_id) is None
        messages = MessageRepository.list_by_conversation(conv_id)
        assert len(messages) == 0


class TestMessageRepository:
    """MessageRepository 集成测试"""

    def test_create_message(self, test_db, cleanup_conversations):
        """测试创建消息"""
        conv_id = f'test_conv_msg_{uuid.uuid4()}'
        msg_id = f'test_msg_{uuid.uuid4()}'

        # 先创建对话（外键约束）
        ConversationRepository.create({
            'conversation_id': conv_id,
            'user_id': f'test_user_msg_{uuid.uuid4()}',
            'title': 'Test for Messages',
            'pet_id': None,
            'context': {}
        })

        # 创建消息
        message_data = {
            'message_id': msg_id,
            'conversation_id': conv_id,
            'role': 'user',
            'content': 'Hello, this is a test message',
            'metadata': {'source': 'test'},
            'vector_id': None
        }

        result = MessageRepository.create(message_data)

        assert result is not None
        assert isinstance(result, str)

        # 验证保存
        saved = MessageRepository.get_by_id(msg_id)
        assert saved is not None
        assert saved['role'] == 'user'
        assert saved['content'] == 'Hello, this is a test message'

    def test_get_message_by_id_not_found(self, test_db):
        """测试查询不存在的消息"""
        result = MessageRepository.get_by_id('nonexistent-msg')
        assert result is None

    def test_list_messages_by_conversation(self, test_db, cleanup_conversations):
        """测试按对话ID查询消息列表"""
        conv_id = f'test_conv_listmsg_{uuid.uuid4()}'
        user_id = f'test_user_listmsg_{uuid.uuid4()}'

        # 创建对话
        ConversationRepository.create({
            'conversation_id': conv_id,
            'user_id': user_id,
            'title': 'Multiple Messages',
            'pet_id': None,
            'context': {}
        })

        # 创建多条消息
        for i in range(5):
            MessageRepository.create({
                'message_id': f'test_msg_multi_{uuid.uuid4()}',
                'conversation_id': conv_id,
                'role': 'user' if i % 2 == 0 else 'assistant',
                'content': f'Message number {i}'
            })

        messages = MessageRepository.list_by_conversation(conv_id)

        assert len(messages) == 5
        # 验证按时间排序
        for i in range(len(messages) - 1):
            assert messages[i]['created_at'] <= messages[i+1]['created_at']

    def test_message_auto_updates_conversation_count(self, test_db, cleanup_conversations):
        """测试添加消息时自动更新对话的消息计数"""
        conv_id = f'test_conv_count_{uuid.uuid4()}'
        user_id = f'test_user_count_{uuid.uuid4()}'

        # 创建对话
        ConversationRepository.create({
            'conversation_id': conv_id,
            'user_id': user_id,
            'title': 'Count Test',
            'pet_id': None,
            'context': {}
        })

        # 添加3条消息
        for _ in range(3):
            MessageRepository.create({
                'message_id': f'test_msg_cnt_{uuid.uuid4()}',
                'conversation_id': conv_id,
                'role': 'user',
                'content': 'Counting message'
            })

        # 验证计数更新
        conversation = ConversationRepository.get_by_id(conv_id)
        assert conversation['message_count'] == 3


class TestDataIntegrity:
    """数据完整性测试"""

    def test_conversation_timestamps_auto_generated(self, test_db, cleanup_conversations):
        """测试时间戳自动生成"""
        before_create = datetime.utcnow()

        conv_id = f'test_conv_ts_{uuid.uuid4()}'
        ConversationRepository.create({
            'conversation_id': conv_id,
            'user_id': f'test_user_ts_{uuid.uuid4()}',
            'title': 'Timestamp Test',
            'pet_id': None,
            'context': {}
        })

        conversation = ConversationRepository.get_by_id(conv_id)

        assert conversation['created_at'] is not None
        assert conversation['updated_at'] is not None
        # 允许1秒的时间误差
        assert (conversation['created_at'] - before_create).total_seconds() < 2

    def test_message_content_preserved_exactly(self, test_db, cleanup_conversations):
        """测试消息内容精确保留（包括特殊字符）"""
        conv_id = f'test_conv_special_{uuid.uuid4()}'
        ConversationRepository.create({
            'conversation_id': conv_id,
            'user_id': f'test_user_special_{uuid.uuid4()}',
            'title': 'Special Chars Test',
            'pet_id': None,
            'context': {}
        })

        special_content = """
        特殊字符测试: 中文!@#$%^&*()
        多行文本
        JSON: {"key": "value", "num": 123}
        Emoji: 🐕🐈⚕️
        """

        msg_id = f'test_msg_special_{uuid.uuid4()}'
        MessageRepository.create({
            'message_id': msg_id,
            'conversation_id': conv_id,
            'role': 'user',
            'content': special_content,
            'metadata': None,
            'vector_id': None
        })

        saved = MessageRepository.get_by_id(msg_id)
        assert saved['content'] == special_content


class TestEdgeCases:
    """边界情况测试"""

    def test_empty_title_allowed(self, test_db, cleanup_conversations):
        """测试允许空标题"""
        conv_id = f'test_conv_empty_{uuid.uuid4()}'
        ConversationRepository.create({
            'conversation_id': conv_id,
            'user_id': f'test_user_empty_{uuid.uuid4()}',
            'title': None,
            'pet_id': None,
            'context': {}
        })

        conversation = ConversationRepository.get_by_id(conv_id)
        assert conversation is not None
        assert conversation.get('title') is None

    def test_long_content_storage(self, test_db, cleanup_conversations):
        """测试长内容存储"""
        conv_id = f'test_conv_long_{uuid.uuid4()}'
        ConversationRepository.create({
            'conversation_id': conv_id,
            'user_id': f'test_user_long_{uuid.uuid4()}',
            'title': 'Long Content Test',
            'pet_id': None,
            'context': {}
        })

        long_content = "A" * 10000  # 10KB的内容

        msg_id = f'test_msg_long_{uuid.uuid4()}'
        MessageRepository.create({
            'message_id': msg_id,
            'conversation_id': conv_id,
            'role': 'assistant',
            'content': long_content,
            'metadata': None,
            'vector_id': None
        })

        saved = MessageRepository.get_by_id(msg_id)
        assert len(saved['content']) == 10000


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
