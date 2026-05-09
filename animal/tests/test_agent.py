"""
Agent测试
"""
import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from src.agents.pet_health_agent import PetHealthAgent
from src.agents.base_agent import AgentState, AgentStatus
from src.db.crud import create_user
from src.schemas.user import UserCreate


class TestPetHealthAgent:
    """宠物健康助手Agent测试类"""

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
    def mock_llm(self):
        """创建模拟LLM"""
        llm = Mock()
        llm.invoke = Mock(return_value="这是一个模拟的响应")
        return llm

    def test_agent_initialization(self, db_session: Session, test_user, mock_llm):
        """测试Agent初始化"""
        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        assert agent.db is not None
        assert agent.llm is not None
        assert agent.user_id == test_user.user_id
        assert len(agent.tools) > 0

    def test_agent_state(self, db_session: Session, test_user, mock_llm):
        """测试Agent状态"""
        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        assert agent.state is not None
        assert isinstance(agent.state, AgentState)
        assert agent.state.status == AgentStatus.IDLE
        assert agent.state.current_task == ""
        assert len(agent.state.plan) == 0
        assert len(agent.state.results) == 0

    def test_agent_get_tool(self, db_session: Session, test_user, mock_llm):
        """测试获取工具"""
        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        tool = agent.get_tool("get_pet_info")
        assert tool is not None
        assert tool.name == "get_pet_info"

        non_existent_tool = agent.get_tool("non_existent_tool")
        assert non_existent_tool is None

    def test_agent_execute_action(self, db_session: Session, test_user, mock_llm):
        """测试执行行动"""
        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        action = {
            "tool": "get_user_pets",
            "args": {"user_id": test_user.user_id}
        }

        result = agent.execute_action(action)

        assert result is not None
        assert isinstance(result, list)

    def test_agent_execute_action_non_existent_tool(
        self,
        db_session: Session,
        test_user,
        mock_llm
    ):
        """测试执行不存在的工具"""
        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        action = {
            "tool": "non_existent_tool",
            "args": {}
        }

        result = agent.execute_action(action)

        assert "error" in result

    def test_base_agent_direct_response(self, db_session: Session, test_user, mock_llm):
        """测试BaseAgent直接响应"""
        from src.agents.base_agent import BaseAgent

        agent = BaseAgent(
            db=db_session,
            llm=mock_llm,
        )

        # plan 返回空列表时应走 _direct_response 路径
        response = agent._direct_response("你好", {})
        assert response is not None

    def test_agent_status_transitions(self, db_session: Session, test_user, mock_llm):
        """测试Agent状态转换"""
        agent = PetHealthAgent(
            db=db_session,
            llm=mock_llm,
            user_id=test_user.user_id
        )

        assert agent.state.status == AgentStatus.IDLE

        # 模拟运行过程状态变化
        agent.state.status = AgentStatus.PLANNING
        assert agent.state.status == AgentStatus.PLANNING

        agent.state.status = AgentStatus.EXECUTING
        assert agent.state.status == AgentStatus.EXECUTING

        agent.state.status = AgentStatus.IDLE
        assert agent.state.status == AgentStatus.IDLE
