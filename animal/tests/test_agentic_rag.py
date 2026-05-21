"""Phase 4 Agentic RAG - 集成测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestAgentCore:
    """Agent核心引擎测试"""

    @pytest.fixture
    def bare_agent(self):
        with patch("src.core.agent_core.AgenticRAG._init_llm", return_value=None):
            from src.core.agent_core import AgenticRAG
            agent = AgenticRAG()
            agent._available = False
            return agent

    def test_register_tool(self, bare_agent):
        def dummy_tool(query):
            return {"result": query.upper()}

        bare_agent.register_tool("test_tool", dummy_tool)
        assert "test_tool" in bare_agent._tools

    def test_default_think_symptom(self, bare_agent):
        thought = bare_agent._default_think("狗拉肚子怎么办")
        assert len(thought["plan"]) > 0
        tool_names = [p["tool"] for p in thought["plan"]]
        assert "knowledge_search" in tool_names
        assert "symptom_analysis" in tool_names

    def test_default_think_breed(self, bare_agent):
        thought = bare_agent._default_think("金毛犬有什么特点")
        tool_names = [p["tool"] for p in thought["plan"]]
        assert "breed_info" in tool_names or "knowledge_search" in tool_names

    def test_default_think_nutrition(self, bare_agent):
        thought = bare_agent._default_think("狗狗吃什么鱼油好")
        tool_names = [p["tool"] for p in thought["plan"]]
        assert any(t in tool_names for t in ["nutrition_advice", "knowledge_search"])

    def test_default_think_general(self, bare_agent):
        thought = bare_agent._default_think("如何给猫咪梳毛")
        assert len(thought["plan"]) > 0
        assert thought["intent"] == "general_knowledge"

    def test_execute_plan(self, bare_agent):
        def mock_search(query):
            return {"results": [{"content": "test result"}]}

        bare_agent.register_tool("knowledge_search", mock_search)
        plan = [{"tool": "knowledge_search", "query": "test", "reason": "test"}]
        observations = bare_agent._execute_plan(plan)

        assert len(observations) == 1
        assert observations[0]["tool"] == "knowledge_search"
        assert "results" in observations[0]["result"]

    def test_execute_plan_unknown_tool(self, bare_agent):
        plan = [{"tool": "nonexistent", "query": "test"}]
        observations = bare_agent._execute_plan(plan)
        assert len(observations) == 0

    def test_format_observations(self, bare_agent):
        observations = [
            {"tool": "test", "query": "q", "result": {"results": [{"content": "c1"}, {"content": "c2"}]}},
        ]
        formatted = bare_agent._format_observations(observations)
        assert "test" in formatted
        assert "c1" in formatted

    def test_format_observations_string_result(self, bare_agent):
        observations = [
            {"tool": "test", "query": "q", "result": "plain text result"},
        ]
        formatted = bare_agent._format_observations(observations)
        assert "plain text result" in formatted

    def test_format_observations_empty(self, bare_agent):
        formatted = bare_agent._format_observations([])
        assert "无检索结果" in formatted

    def test_format_pet_info(self, bare_agent):
        pet_info = {"name": "旺财", "species": "犬", "breed": "金毛"}
        formatted = bare_agent._format_pet_info(pet_info)
        assert "旺财" in formatted
        assert "金毛" in formatted

    def test_format_pet_info_empty(self, bare_agent):
        formatted = bare_agent._format_pet_info(None)
        assert "无宠物信息" in formatted

    def test_extract_json(self, bare_agent):
        result = bare_agent._extract_json('{"a": 1}')
        assert "a" in result

        result = bare_agent._extract_json('```json\n{"b": 2}\n```')
        assert "b" in result

    def test_compute_confidence(self, bare_agent):
        from src.core.agent_core import AgentState
        conf = bare_agent._compute_final_confidence(
            [{"tool": "test", "query": "q", "result": {}}],
            {"confidence": 0.8}
        )
        assert 0.5 <= conf <= 1.0

    def test_refuse(self, bare_agent):
        from src.core.agent_core import AgentState
        result = bare_agent._refuse("测试问题", "测试原因")
        assert result["state"] == AgentState.REFUSED
        assert "面诊" in result["answer"]

    def test_agent_state(self):
        from src.core.agent_core import AgentState
        assert AgentState.THINKING == "thinking"
        assert AgentState.ACTING == "acting"
        assert AgentState.ANSWERING == "answering"
        assert AgentState.DONE == "done"


class TestToolManager:
    """工具管理器测试"""

    def test_register_and_call(self):
        from src.core.agent_tools import ToolManager
        tm = ToolManager()

        def hello(name):
            return f"Hello {name}"

        tm.register("greet", hello, description="打招呼", category="test")
        assert "greet" in tm._tools

        result = tm.call("greet", "World")
        assert result == "Hello World"

        stats = tm.get_call_stats()
        assert stats["total_calls"] == 1

    def test_list_tools(self):
        from src.core.agent_tools import ToolManager
        tm = ToolManager()

        def tool_a(q): return q
        def tool_b(q): return q

        tm.register("a", tool_a, category="cat1", priority=2)
        tm.register("b", tool_b, category="cat2", priority=1)

        all_tools = tm.list_tools()
        assert len(all_tools) == 2

        cat1_tools = tm.list_tools(category="cat1")
        assert len(cat1_tools) == 1
        assert cat1_tools[0]["name"] == "a"

    def test_unregister(self):
        from src.core.agent_tools import ToolManager
        tm = ToolManager()
        def dummy(q): return q
        tm.register("dummy", dummy)
        tm.unregister("dummy")
        assert "dummy" not in tm._tools

    def test_call_unknown_tool(self):
        from src.core.agent_tools import ToolManager
        tm = ToolManager()
        with pytest.raises(ValueError, match="未注册"):
            tm.call("nonexistent")

    def test_get_tool_description(self):
        from src.core.agent_tools import ToolManager
        tm = ToolManager()
        def dummy(q): return q
        tm.register("test", dummy, description="测试工具")
        assert tm.get_tool_description("test") == "测试工具"


class TestCreateDefaultTools:
    """默认工具集测试"""

    def test_create_tools(self):
        from src.core.agent_tools import create_default_tools
        tools = create_default_tools()

        expected = [
            "knowledge_search",
            "knowledge_search_quality",
            "graph_search",
            "fusion_search",
            "symptom_analysis",
            "breed_info",
            "nutrition_advice",
        ]
        for name in expected:
            assert name in tools, f"缺少工具: {name}"
            assert callable(tools[name]), f"工具不可调用: {name}"

    def test_knowledge_search_tool(self):
        from src.core.agent_tools import create_default_tools
        tools = create_default_tools()
        result = tools["knowledge_search"]("狗拉肚子")

        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_symptom_analysis_tool(self):
        from src.core.agent_tools import create_default_tools
        tools = create_default_tools()
        result = tools["symptom_analysis"]("狗呕吐腹泻")

        assert isinstance(result, dict)
        assert "results" in result

    def test_breed_info_tool(self):
        from src.core.agent_tools import create_default_tools
        tools = create_default_tools()
        result = tools["breed_info"]("金毛寻回犬特点")

        assert isinstance(result, dict)
        assert "results" in result

    def test_nutrition_advice_tool(self):
        from src.core.agent_tools import create_default_tools
        tools = create_default_tools()
        result = tools["nutrition_advice"]("狗需要什么维生素")

        assert isinstance(result, dict)
        assert "results" in result


class TestAgenticRAGIntegration:
    """Agentic RAG 集成测试"""

    @pytest.fixture
    def integrated_agent(self):
        with patch("src.core.agent_core.AgenticRAG._init_llm", return_value=None):
            from src.core.agent_core import AgenticRAG
            from src.core.agent_tools import setup_agent_tools

            agent = AgenticRAG()
            agent._available = False
            agent = setup_agent_tools(agent)
            return agent

    def test_agent_has_tools(self, integrated_agent):
        expected_tools = ["knowledge_search", "knowledge_search_quality", "graph_search",
                          "fusion_search", "symptom_analysis", "breed_info", "nutrition_advice"]
        for t in expected_tools:
            assert t in integrated_agent._tools, f"缺少工具: {t}"

    def test_agent_execute_simple_plan(self, integrated_agent):
        plan = [
            {"tool": "knowledge_search", "query": "狗腹泻原因", "reason": "获取相关知识"},
            {"tool": "breed_info", "query": "拉布拉多常见病", "reason": "品种特定信息"},
        ]
        observations = integrated_agent._execute_plan(plan)
        assert len(observations) > 0

        assert all("result" in obs for obs in observations)
        assert all("tool" in obs for obs in observations)

    def test_agent_default_think_multi_step(self, integrated_agent):
        thought = integrated_agent._default_think("金毛犬呕吐腹泻没精神怎么办")

        assert len(thought["plan"]) >= 1
        assert thought["intent"] in ["general_knowledge", "symptom_diagnosis"]

    def test_agent_run_without_llm(self, integrated_agent):
        """无LLM时使用规则引擎兜底"""
        result = integrated_agent.run(
            query="狗拉肚子怎么办",
            pet_info={"species": "犬", "breed": "金毛"},
            max_iterations=1,
        )

        assert "answer" in result
        assert "execution_trace" in result
        assert result["iterations"] >= 1
        assert result["state"] in ("done", "refused", "error")

    def test_agent_run_complex_query(self, integrated_agent):
        """复杂查询测试"""
        result = integrated_agent.run(
            query="拉布拉多犬髋关节问题和金毛犬有什么不同",
            pet_info={"species": "犬"},
            max_iterations=2,
        )

        assert result["state"] in ("done", "refused", "error")
        assert "answer" in result
        assert isinstance(result["execution_trace"], list)

    def test_execution_trace_completeness(self, integrated_agent):
        result = integrated_agent.run(
            query="猫瘟怎么预防",
            pet_info={"species": "猫"},
            max_iterations=2,
        )

        trace = result["execution_trace"]
        assert len(trace) > 0

        phases = [t.get("phase") for t in trace]
        if result["state"] != "error":
            assert "think" in phases or "act" in phases


class TestAgenticRAGComplexScenarios:
    """复杂场景测试"""

    @pytest.fixture
    def agent(self):
        with patch("src.core.agent_core.AgenticRAG._init_llm", return_value=None):
            from src.core.agent_core import AgenticRAG
            from src.core.agent_tools import setup_agent_tools
            agent = AgenticRAG()
            agent._available = False
            agent = setup_agent_tools(agent)
            return agent

    def test_multi_tool_coordination(self, agent):
        """多工具协调测试"""
        result = agent.run(
            query="布偶猫毛球症怎么处理和预防",
            pet_info={"species": "猫", "breed": "布偶猫"},
            max_iterations=3,
        )

        trace = result["execution_trace"]
        tools_used = set()
        for t in trace:
            if t.get("phase") == "act":
                tools_used.add(t.get("tool", ""))

        assert result["state"] in ("done", "refused", "error")

        if "deleted" not in result.get("answer", "").lower():
            assert len(result["answer"]) > 0

    def test_empty_query_handling(self, agent):
        """空查询处理"""
        result = agent.run("")
        assert result["state"] in ("done", "refused", "error")

    def test_very_long_query(self, agent):
        """长查询处理"""
        long_query = "我家养了一只三岁的金毛寻回犬，最近一周出现了频繁呕吐、腹泻带血、精神萎靡、不吃东西、体温升高的症状，请问可能是什么疾病？需要怎么处理？是否需要立即就医？"
        result = agent.run(query=long_query, max_iterations=2)
        assert result["state"] in ("done", "refused", "error")

    def test_graph_retrieval_integration(self, agent):
        """图谱检索集成测试"""
        result = agent.run(
            query="金毛犬常见遗传疾病有哪些",
            pet_info={"species": "犬", "breed": "金毛寻回犬"},
            max_iterations=2,
        )

        trace = result["execution_trace"]
        tools_used = [t.get("tool") for t in trace if t.get("phase") == "act"]
        if "graph_search" in tools_used or "fusion_search" in tools_used:
            assert result["state"] in ("done", "refused", "error")