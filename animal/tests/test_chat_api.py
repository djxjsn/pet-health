"""
DEV-003 Agent编排 集成测试

测试对话API、WebSocket、Agent编排的核心流程
"""
import pytest
from datetime import datetime
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
            "orchestration": {"engine": "v2", "fallback": False, "emergency_hit": None},
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
        assert "orchestration" in data
        assert data["orchestration"]["engine"] == "v2"
        assert data["orchestration"]["fallback"] is False

    @patch("src.agents.pet_health_agent.PetHealthAgent.chat")
    def test_chat_with_pet_context(self, mock_chat, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试指定宠物上下文的对话"""
        mock_chat.return_value = {
            "conversation_id": "test-conv-id",
            "response": "关于旺财的健康建议...",
            "relevant_context": [],
            "orchestration": {"engine": "v2", "fallback": False, "emergency_hit": None},
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
            "orchestration": {"engine": "v2", "fallback": False, "emergency_hit": None},
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

    @patch("src.agents.pet_health_agent.PetHealthAgent.chat")
    def test_chat_endpoint_emergency_orchestration(self, mock_chat, client: TestClient, auth_headers: dict):
        """测试紧急场景编排字段透传"""
        mock_chat.return_value = {
            "conversation_id": "test-conv-id",
            "response": "请立即送医",
            "relevant_context": [],
            "orchestration": {"engine": "emergency_gate", "fallback": False, "emergency_hit": "抽搐"},
        }

        response = client.post(
            "/api/v1/chat",
            headers=auth_headers,
            json={"message": "突然抽搐怎么办"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["orchestration"]["engine"] == "emergency_gate"
        assert data["orchestration"]["fallback"] is False
        assert data["orchestration"]["emergency_hit"] == "抽搐"

    def test_chat_orchestration_stats_endpoint(self, client: TestClient, auth_headers: dict):
        """测试编排统计接口返回结构与计数"""
        from src.core.mongodb import get_mongo_collection

        conv_resp = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"title": "orchestration stats test"},
        )
        assert conv_resp.status_code == 201
        conv_data = conv_resp.json()
        conversation_id = conv_data["conversation_id"]

        messages = get_mongo_collection("messages")
        messages.insert_one({
            "message_id": "msg-stat-1",
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": "v2 response",
            "metadata": {"orchestration": {"engine": "v2", "fallback": False, "emergency_hit": None, "quality_action": "accept"}},
            "created_at": datetime.utcnow(),
        })
        messages.insert_one({
            "message_id": "msg-stat-2",
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": "fallback response",
            "metadata": {"orchestration": {"engine": "v1", "fallback": True, "emergency_hit": None, "quality_action": "revise"}},
            "created_at": datetime.utcnow(),
        })
        messages.insert_one({
            "message_id": "msg-stat-3",
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": "emergency response",
            "metadata": {"orchestration": {"engine": "emergency_gate", "fallback": False, "emergency_hit": "抽搐", "quality_action": "refuse"}},
            "created_at": datetime.utcnow(),
        })

        stats_resp = client.get("/api/v1/chat/orchestration/stats?limit=100", headers=auth_headers)
        assert stats_resp.status_code == 200
        data = stats_resp.json()

        assert "counters" in data
        assert "rates" in data
        assert data["counters"]["with_orchestration"] >= 3
        assert data["counters"]["by_engine"]["v2"] >= 1
        assert data["counters"]["by_engine"]["v1"] >= 1
        assert data["counters"]["by_engine"]["emergency_gate"] >= 1
        assert data["counters"]["by_quality_action"]["accept"] >= 1
        assert data["counters"]["by_quality_action"]["revise"] >= 1
        assert data["counters"]["by_quality_action"]["refuse"] >= 1
        assert "quality_accept_rate" in data["rates"]
        assert "quality_revise_rate" in data["rates"]
        assert "quality_refuse_rate" in data["rates"]

    def test_message_repository_create_increments_message_count(self, client: TestClient, auth_headers: dict):
        """测试MessageRepository.create会正确累加会话message_count"""
        from src.repositories.mongo_repositories import ConversationRepository, MessageRepository

        conv_resp = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"title": "message_count increment test"},
        )
        assert conv_resp.status_code == 201
        conversation_id = conv_resp.json()["conversation_id"]

        before = ConversationRepository.get_by_id(conversation_id)
        before_count = before.get("message_count", 0)

        MessageRepository.create({
            "message_id": "msg-inc-1",
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": "first assistant message",
            "metadata": {"from_test": True},
        })

        after = ConversationRepository.get_by_id(conversation_id)
        after_count = after.get("message_count", 0)
        assert after_count == before_count + 1


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

    def test_chat_emergency_gate(self, db_session: Session, test_user, mock_llm):
        """测试紧急关键词命中时走紧急前置策略"""
        from src.agents.pet_health_agent import PetHealthAgent

        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        result = agent.chat("我的猫突然抽搐并呼吸困难，怎么办")

        assert "conversation_id" in result
        assert result["orchestration"]["engine"] == "emergency_gate"
        assert result["orchestration"]["fallback"] is False
        assert "紧急" in result["response"] or "急诊" in result["response"]

    def test_chat_fallback_to_v1_when_v2_fails(self, db_session: Session, test_user, mock_llm):
        """测试V2异常时自动回退V1"""
        from src.agents.pet_health_agent import PetHealthAgent

        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        with patch.object(agent.agent_v2, "run_v2", side_effect=Exception("v2 failed")):
            with patch.object(agent, "run", return_value="v1 fallback response") as mock_run:
                result = agent.chat("普通咨询问题")

        assert mock_run.called
        assert result["response"] == "v1 fallback response"
        assert result["orchestration"]["engine"] == "v1"
        assert result["orchestration"]["fallback"] is True
