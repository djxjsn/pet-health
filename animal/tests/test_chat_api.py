"""
DEV-003 Agent编排 集成测试

测试对话API、WebSocket、Agent编排的核心流程
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.db.crud import create_user
from src.schemas.user import UserCreate


class TestChatAPI:
    """对话 API 集成测试"""

    @pytest.fixture
    def auth_client(self, client: TestClient, auth_headers: dict) -> TestClient:
        return client

    def test_create_conversation(self, client: TestClient, auth_headers: dict):
        """测试创建对话"""
        response = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"title": "测试对话"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "conversation_id" in data
        assert data["title"] == "测试对话"

    def test_list_conversations(self, client: TestClient, auth_headers: dict):
        """测试获取对话列表"""
        # 先创建一个对话
        client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"title": "列表测试对话"},
        )

        response = client.get(
            "/api/v1/conversations",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_conversation_detail(self, client: TestClient, auth_headers: dict):
        """测试获取对话详情"""
        # 创建对话
        create_resp = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"title": "详情测试对话"},
        )
        conversation_id = create_resp.json()["conversation_id"]

        response = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert data["title"] == "详情测试对话"
        assert "messages" in data

    def test_delete_conversation(self, client: TestClient, auth_headers: dict):
        """测试删除对话"""
        create_resp = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"title": "待删除对话"},
        )
        conversation_id = create_resp.json()["conversation_id"]

        response = client.delete(
            f"/api/v1/conversations/{conversation_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # 验证已删除
        get_resp = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 404

    def test_conversation_isolation(self, client: TestClient, auth_headers: dict, second_auth_headers: dict):
        """测试对话数据隔离 - 用户不能访问其他用户的对话"""
        create_resp = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"title": "私有对话"},
        )
        conversation_id = create_resp.json()["conversation_id"]

        # 第二个用户尝试访问
        response = client.get(
            f"/api/v1/conversations/{conversation_id}",
            headers=second_auth_headers,
        )
        assert response.status_code == 403

    def test_unauthorized_access(self, client: TestClient):
        """测试未认证访问"""
        response = client.get("/api/v1/conversations")
        assert response.status_code == 401

    @patch("src.agents.pet_health_agent.PetHealthAgent.chat")
    def test_chat_endpoint(self, mock_chat, client: TestClient, auth_headers: dict):
        """测试对话端点（mock Agent）"""
        mock_chat.return_value = {
            "conversation_id": "test-conv-id",
            "response": "这是AI的回复",
            "relevant_context": [],
        }

        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "你好"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response" in data

    @patch("src.agents.pet_health_agent.PetHealthAgent.chat")
    def test_chat_with_pet_context(self, mock_chat, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试指定宠物上下文的对话"""
        mock_chat.return_value = {
            "conversation_id": "test-conv-id",
            "response": "关于旺财的健康建议...",
            "relevant_context": [],
        }

        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={
                "message": "我的狗最近不爱吃饭",
                "pet_id": created_pet["pet_id"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    @patch("src.agents.pet_health_agent.PetHealthAgent.chat")
    def test_chat_with_conversation_id(self, mock_chat, client: TestClient, auth_headers: dict):
        """测试多轮对话（指定 conversation_id）"""
        mock_chat.return_value = {
            "conversation_id": "existing-conv-id",
            "response": "继续之前的对话...",
            "relevant_context": [],
        }

        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={
                "message": "还有其他建议吗？",
                "conversation_id": "existing-conv-id",
            },
        )
        assert response.status_code == 200


class TestAgentOrchestration:
    """Agent编排核心流程测试"""

    @pytest.fixture
    def test_user(self, db_session: Session):
        user_data = UserCreate(
            phone="13800000001",
            email="test@example.com",
            password="test1234"
        )
        user = create_user(db_session, user_data)
        return user

    @pytest.fixture
    def mock_llm(self):
        """创建模拟LLM，支持不同场景"""
        llm = Mock()

        def mock_invoke(messages):
            msg_str = str(messages)
            if "规划" in msg_str or "plan" in msg_str.lower():
                return '[]'
            return "这是一个模拟的宠物健康建议"

        llm.invoke = Mock(side_effect=mock_invoke)
        return llm

    def test_agent_run_without_tools(self, db_session: Session, test_user, mock_llm):
        """测试Agent无工具时直接响应"""
        from src.agents.pet_health_agent import PetHealthAgent

        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        # plan返回空列表时走直接响应路径
        response = agent.run("你好", {})
        assert response is not None

    def test_agent_execute_get_user_pets(self, db_session: Session, test_user, mock_llm):
        """测试Agent执行获取用户宠物工具"""
        from src.agents.pet_health_agent import PetHealthAgent

        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        action = {"tool": "get_user_pets", "args": {"user_id": test_user.user_id}}
        result = agent.execute_action(action)
        assert isinstance(result, list)

    def test_agent_chat_creates_conversation(self, db_session: Session, test_user, mock_llm):
        """测试Agent对话自动创建会话"""
        from src.agents.pet_health_agent import PetHealthAgent

        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        result = agent.chat(user_input="你好")
        assert "conversation_id" in result
        assert "response" in result

    def test_agent_chat_continues_conversation(self, db_session: Session, test_user, mock_llm):
        """测试Agent多轮对话"""
        from src.agents.pet_health_agent import PetHealthAgent

        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        result1 = agent.chat(user_input="你好")
        conv_id = result1["conversation_id"]

        result2 = agent.chat(
            user_input="还有其他建议吗",
            conversation_id=conv_id
        )

        assert result2["conversation_id"] == conv_id

    def test_agent_error_handling(self, db_session: Session, test_user):
        """测试Agent错误处理"""
        from src.agents.pet_health_agent import PetHealthAgent
        from src.agents.base_agent import AgentStatus

        # 使用会抛出异常的LLM
        bad_llm = Mock()
        bad_llm.invoke = Mock(side_effect=Exception("LLM调用失败"))

        agent = PetHealthAgent(
            db=db_session,
            llm=bad_llm,
            user_id=test_user.user_id
        )

        response = agent.run("测试错误", {})
        assert "错误" in response or "error" in response.lower() or agent.state.status == AgentStatus.ERROR
