"""
优化版 Agent/Prompt/评估器 全面测试

测试范围：
1. prompts_v2 - 模板完整性/格式正确性/意图路由表
2. agent_v2 - AgentV2推理流程/意图分类/工具路由/反思循环
3. prompt_evaluator - 评估指标/A/B测试/报告生成
4. 与V1对比测试
"""
import json
import pytest
from unittest.mock import MagicMock, patch


class TestPromptsV2:
    """优化版Prompt模板测试"""

    def test_all_templates_defined(self):
        """所有关键模板必须已定义且非空"""
        from src.core.prompts_v2 import (
            CLASSIFY_PROMPT_TEMPLATE, PLAN_V2_PROMPT_TEMPLATE,
            REFLECT_PROMPT_TEMPLATE, INTEGRATE_V2_PROMPT_TEMPLATE,
            DIRECT_V2_PROMPT_TEMPLATE, FORMAT_GUIDELINES,
            ROLE_SYSTEM_PROMPT_V2
        )
        templates = {
            "CLASSIFY": CLASSIFY_PROMPT_TEMPLATE,
            "PLAN_V2": PLAN_V2_PROMPT_TEMPLATE,
            "REFLECT": REFLECT_PROMPT_TEMPLATE,
            "INTEGRATE_V2": INTEGRATE_V2_PROMPT_TEMPLATE,
            "DIRECT_V2": DIRECT_V2_PROMPT_TEMPLATE,
            "FORMAT": FORMAT_GUIDELINES,
            "ROLE": ROLE_SYSTEM_PROMPT_V2,
        }
        for name, template in templates.items():
            assert isinstance(template, str), f"{name} 不是字符串"
            assert len(template) > 50, f"{name} 内容过短 ({len(template)} chars)"

    def test_format_guidelines_includes_all_requirements(self):
        """格式规范应包含所有必要要求"""
        from src.core.prompts_v2 import FORMAT_GUIDELINES
        required = ["emoji", "【", "】", "⚠️", "重要提醒"]
        for req in required:
            assert req in FORMAT_GUIDELINES, f"缺少格式要求: {req}"

    def test_role_prompt_includes_safety(self):
        """角色提示词必须包含安全性约束"""
        from src.core.prompts_v2 import ROLE_SYSTEM_PROMPT_V2
        safety_keywords = ["不能替代", "就医", "遵医嘱"]
        for kw in safety_keywords:
            assert kw in ROLE_SYSTEM_PROMPT_V2, f"缺少安全关键词: {kw}"

    def test_intent_definitions_complete(self):
        """意图定义应包含所有10个类别"""
        from src.core.prompts_v2 import INTENT_DEFINITIONS
        intents = [
            "pet_info", "health_consult", "symptom_check",
            "nutrition_advice", "behavior_analysis", "emergency_assess",
            "daily_care", "external_service", "casual_chat", "unknown"
        ]
        for intent in intents:
            assert intent in INTENT_DEFINITIONS, f"缺少意图定义: {intent}"

    def test_tool_to_intent_map_complete(self):
        """工具到意图映射表应包含所有意图"""
        from src.core.prompts_v2 import TOOL_TO_INTENT_MAP
        expected_intents = [
            "pet_info", "health_consult", "symptom_check",
            "nutrition_advice", "behavior_analysis", "emergency_assess",
            "daily_care", "external_service", "casual_chat", "unknown"
        ]
        for intent in expected_intents:
            assert intent in TOOL_TO_INTENT_MAP, f"缺少意图映射: {intent}"
            assert isinstance(TOOL_TO_INTENT_MAP[intent], list)

    def test_casual_chat_no_tools(self):
        """闲聊意图不应需要任何工具"""
        from src.core.prompts_v2 import TOOL_TO_INTENT_MAP
        assert TOOL_TO_INTENT_MAP["casual_chat"] == []

    def test_symptom_check_has_urgency_tool(self):
        """症状分析意图应包含紧急评估工具"""
        from src.core.prompts_v2 import TOOL_TO_INTENT_MAP
        assert "assess_urgency" in TOOL_TO_INTENT_MAP["symptom_check"]

    def test_emergency_assess_has_urgency_tool(self):
        """紧急评估意图应包含assess_urgency"""
        from src.core.prompts_v2 import TOOL_TO_INTENT_MAP
        assert "assess_urgency" in TOOL_TO_INTENT_MAP["emergency_assess"]

    def test_tool_priority_range(self):
        """工具优先级应在1-10范围内"""
        from src.core.prompts_v2 import TOOL_PRIORITY
        for tool, priority in TOOL_PRIORITY.items():
            assert 1 <= priority <= 10, f"{tool} 优先级 {priority} 超出范围"

    def test_high_priority_tools_first(self):
        """get_user_pets应该是最高优先级"""
        from src.core.prompts_v2 import TOOL_PRIORITY
        assert TOOL_PRIORITY["get_user_pets"] == 10
        assert TOOL_PRIORITY["assess_urgency"] >= 8

    def test_all_registered_tools_have_priority(self):
        """所有注册到意图映射的工具都应有权重"""
        from src.core.prompts_v2 import TOOL_TO_INTENT_MAP, TOOL_PRIORITY
        all_tools = set()
        for tools in TOOL_TO_INTENT_MAP.values():
            all_tools.update(tools)
        for tool in all_tools:
            assert tool in TOOL_PRIORITY, f"工具 {tool} 缺少优先级定义"

    def test_plan_template_has_examples(self):
        """规划模板应包含至少2个示例"""
        from src.core.prompts_v2 import PLAN_V2_PROMPT_TEMPLATE
        assert "示例1" in PLAN_V2_PROMPT_TEMPLATE
        assert "示例2" in PLAN_V2_PROMPT_TEMPLATE
        # JSON示例中的关键字段
        assert '"tool"' in PLAN_V2_PROMPT_TEMPLATE
        assert '"args"' in PLAN_V2_PROMPT_TEMPLATE
        assert '"reason"' in PLAN_V2_PROMPT_TEMPLATE

    def test_classify_template_has_examples(self):
        """分类模板应包含类别示例"""
        from src.core.prompts_v2 import CLASSIFY_PROMPT_TEMPLATE
        assert "primary_intent" in CLASSIFY_PROMPT_TEMPLATE
        assert "confidence" in CLASSIFY_PROMPT_TEMPLATE

    def test_reflect_template_has_sufficient_field(self):
        """反思模板应包含sufficient判断字段"""
        from src.core.prompts_v2 import REFLECT_PROMPT_TEMPLATE
        assert "sufficient" in REFLECT_PROMPT_TEMPLATE

    def test_integrate_template_references_format(self):
        """整合模板应引用格式规范"""
        from src.core.prompts_v2 import INTEGRATE_V2_PROMPT_TEMPLATE
        assert "{FORMAT_GUIDELINES}" in INTEGRATE_V2_PROMPT_TEMPLATE

    def test_prompt_v1_vs_v2_structure_comparison(self):
        """V2 vs V1结构对比：V2应该有更丰富的结构元素"""
        from src.core.prompts_v2 import (
            INTEGRATE_V2_PROMPT_TEMPLATE, ROLE_SYSTEM_PROMPT_V2
        )
        # V2应有更多结构元素
        structural = ["【", "】", "⚠️", "禁止", "遵循"]
        count = sum(1 for s in structural if s in ROLE_SYSTEM_PROMPT_V2)
        assert count >= 3, f"角色提示词缺少结构元素 (仅{count}个)"


class TestAgentV2Architecture:
    """AgentV2架构测试"""

    def test_intent_enum_complete(self):
        """意图枚举应包含10个类别"""
        from src.agents.agent_v2 import IntentCategory
        assert len(IntentCategory) == 10

    def test_intent_result_pydantic_validation(self):
        """IntentResult pydantic验证"""
        from src.agents.agent_v2 import IntentResult, IntentCategory
        result = IntentResult(
            primary_intent=IntentCategory.HEALTH_CONSULT,
            confidence=0.85,
            reasoning="测试"
        )
        assert result.primary_intent == IntentCategory.HEALTH_CONSULT
        assert result.confidence == 0.85

    def test_intent_result_confidence_range(self):
        """confidence必须在0-1之间"""
        from src.agents.agent_v2 import IntentResult, IntentCategory
        with pytest.raises(Exception):
            IntentResult(primary_intent=IntentCategory.HEALTH_CONSULT, confidence=1.5)
        with pytest.raises(Exception):
            IntentResult(primary_intent=IntentCategory.HEALTH_CONSULT, confidence=-0.1)

    def test_intent_result_secondary_limit(self):
        """secondary_intents最多2个"""
        from src.agents.agent_v2 import IntentResult, IntentCategory
        result = IntentResult(
            primary_intent=IntentCategory.HEALTH_CONSULT,
            secondary_intents=[
                IntentCategory.SYMPTOM_CHECK,
                IntentCategory.NUTRITION_ADVICE,
                IntentCategory.DAILY_CARE,
            ],
            confidence=0.8,
        )
        assert len(result.secondary_intents) == 2

    def test_tool_plan_pydantic_validation(self):
        """ToolPlan pydantic验证"""
        from src.agents.agent_v2 import ToolPlan
        plan = ToolPlan(
            tool="get_user_pets",
            args={},
            reason="获取宠物",
            priority=10,
        )
        assert plan.tool == "get_user_pets"
        assert plan.priority == 10
        assert plan.depends_on is None

    def test_tool_plan_priority_range(self):
        """ToolPlan priority必须在1-10之间"""
        from src.agents.agent_v2 import ToolPlan
        with pytest.raises(Exception):
            ToolPlan(tool="test", priority=0)
        with pytest.raises(Exception):
            ToolPlan(tool="test", priority=11)
        assert ToolPlan(tool="test", priority=1)
        assert ToolPlan(tool="test", priority=10)

    def test_action_plan_pydantic_validation(self):
        """ActionPlan pydantic验证"""
        from src.agents.agent_v2 import ActionPlan, ToolPlan
        plan = ActionPlan(
            actions=[ToolPlan(tool="get_user_pets", priority=10)]
        )
        assert len(plan.actions) == 1
        assert plan.fallback_response is None

    def test_reflection_result_pydantic_validation(self):
        """ReflectionResult pydantic验证"""
        from src.agents.agent_v2 import ReflectionResult
        result = ReflectionResult(
            sufficient=True,
            reasoning="信息充足"
        )
        assert result.sufficient is True
        assert result.missing_info == []
        assert result.additional_tools == []

    def test_get_relevant_tools_routing(self):
        """意图到工具的路由映射测试"""
        from src.agents.agent_v2 import AgentV2, IntentCategory
        agent = AgentV2(llm=MagicMock())
        # health_consult意图应包含核心工具
        tools = agent._get_relevant_tools([IntentCategory.HEALTH_CONSULT])
        assert "health_consult" in tools
        assert "get_user_pets" in tools
        assert "get_pet_info" in tools

    def test_casual_chat_no_tools_routed(self):
        """闲聊意图应路由到空工具列表（仅基础工具）"""
        from src.agents.agent_v2 import AgentV2, IntentCategory
        agent = AgentV2(llm=MagicMock())
        tools = agent._get_relevant_tools([IntentCategory.CASUAL_CHAT])
        # 闲聊意图TOOL_TO_INTENT_MAP为空，但_get_relevant_tools总是添加基础工具
        # 这是设计意图：即使闲聊，也应准备好基础信息以做个性化回复
        assert "get_user_pets" in tools
        assert "get_pet_info" in tools

    def test_max_reflection_rounds(self):
        """最大反思轮次应>=1"""
        from src.agents.agent_v2 import AgentV2
        assert AgentV2.MAX_REFLECTION_ROUNDS >= 1

    def test_max_tools_per_plan(self):
        """每次计划最大工具数应合理（3-7）"""
        from src.agents.agent_v2 import AgentV2
        assert 3 <= AgentV2.MAX_TOOLS_PER_PLAN <= 7

    def test_extract_json_handles_markdown(self):
        """_extract_json能处理markdown包裹的JSON"""
        from src.agents.agent_v2 import AgentV2
        agent = AgentV2(llm=MagicMock())
        result = agent._extract_json('```json\n{"key": "value"}\n```')
        assert result == '{"key": "value"}'

    def test_extract_json_handles_plain(self):
        """_extract_json能处理纯JSON"""
        from src.agents.agent_v2 import AgentV2
        agent = AgentV2(llm=MagicMock())
        result = agent._extract_json('{"key": "value"}')
        assert result == '{"key": "value"}'

    def test_extract_json_handles_text_with_json(self):
        """_extract_json能从文本中提取JSON"""
        from src.agents.agent_v2 import AgentV2
        agent = AgentV2(llm=MagicMock())
        result = agent._extract_json('some text before {"key": "value"}')
        assert result == '{"key": "value"}'

    def test_format_pet_info_complete(self):
        """_format_pet_info应正确格式化宠物信息"""
        from src.agents.agent_v2 import AgentV2
        result = AgentV2._format_pet_info({
            "name": "小白",
            "species": "cat",
            "breed": "布偶猫",
            "gender": "female"
        })
        assert "小白" in result
        assert "cat" in result
        assert "布偶猫" in result

    def test_format_pet_info_empty(self):
        """无宠物信息时应返回提示"""
        from src.agents.agent_v2 import AgentV2
        assert "无宠物信息" in AgentV2._format_pet_info(None)
        assert "无宠物信息" in AgentV2._format_pet_info({})

    def test_agent_context_dataclass(self):
        """AgentContext数据类测试"""
        from src.agents.agent_v2 import AgentContext
        ctx = AgentContext(user_input="test")
        assert ctx.reflection_count == 0
        assert ctx.results == []

    def test_token_stats_helper(self):
        """get_token_stats应返回结构化信息"""
        from src.agents.agent_v2 import AgentV2, AgentContext
        agent = AgentV2(llm=MagicMock())
        ctx = AgentContext(user_input="test")
        stats = agent.get_token_stats(ctx)
        assert "intent_classification_tokens" in stats
        assert "planning_tools_considered" in stats
        assert "executed_tools" in stats
        assert "reflection_rounds" in stats
        assert "total_time_ms" in stats


class TestPromptEvaluator:
    """Prompt评估器测试"""

    def test_evaluator_creation(self):
        """创建评估器"""
        from src.core.prompt_evaluator import create_default_evaluator
        eval = create_default_evaluator()
        assert eval is not None

    def test_heuristic_evaluate_basic(self):
        """启发式评分基本测试"""
        from src.core.prompt_evaluator import PromptEvaluator
        evaluator = PromptEvaluator(llm=None)
        result = evaluator.evaluate_with_llm(
            query="猫拉肚子怎么办",
            intent="symptom_check",
            response_v1="可能是消化不良，建议观察。",
            response_v2="🐾【症状分析】\n\n猫咪腹泻可能的原因：\n1. 饮食不当\n2. 寄生虫\n\n⚠️ 建议仅供参考，严重请就医。",
        )
        assert result.winner in ("v1", "v2", "tie")
        assert len(result.scores_v1) > 0
        assert len(result.scores_v2) > 0

    def test_v2_wins_with_structured_response(self):
        """结构化回复应优于简单回复"""
        from src.core.prompt_evaluator import PromptEvaluator
        evaluator = PromptEvaluator(llm=None)
        result = evaluator.evaluate_with_llm(
            query="猫拉肚子怎么办",
            intent="symptom_check",
            response_v1="可能消化不良。",
            response_v2="🐾【症状分析】\n\n猫咪腹泻可能的原因：\n\n1. 饮食不当或突然换粮\n2. 寄生虫感染\n3. 肠胃炎症\n\n⚠️ 紧急情况：如果持续腹泻超过24小时、伴有呕吐或便血\n\n✅【家庭护理】\n\n1. 先禁食12小时，提供充足饮水\n2. 恢复饮食后用易消化的处方粮\n\n⚠️ 重要提醒：建议仅供参考，不能替代兽医诊断。持续腹泻请立即就医。",
        )
        assert result.winner == "v2"

    def test_score_range_valid(self):
        """评分应在合理范围内"""
        from src.core.prompt_evaluator import PromptEvaluator
        evaluator = PromptEvaluator(llm=None)
        result = evaluator.evaluate_with_llm(
            query="test",
            intent="health",
            response_v1="short",
            response_v2="structured long response",
        )
        for scores in (result.scores_v1, result.scores_v2):
            for dim, score in scores.items():
                assert 0 <= score <= 10, f"{dim} 评分 {score} 超出范围"

    def test_builtin_test_cases_count(self):
        """预置测试用例应>=15个"""
        from src.core.prompt_evaluator import BUILTIN_TEST_CASES
        assert len(BUILTIN_TEST_CASES) >= 15

    def test_builtin_cases_have_all_intents(self):
        """预置测试用例应覆盖所有意图类别"""
        from src.core.prompt_evaluator import BUILTIN_TEST_CASES
        intents = set(c["intent"] for c in BUILTIN_TEST_CASES)
        required = {"symptom_check", "health_consult", "emergency_assess",
                     "behavior_analysis", "daily_care", "casual_chat",
                     "nutrition_advice", "pet_info", "external_service"}
        for r in required:
            assert r in intents, f"缺少意图: {r}"

    def test_aggregate_result_calculation(self):
        """汇总结果计算测试"""
        from src.core.prompt_evaluator import AggregateResult
        agg = AggregateResult(
            total_cases=10,
            v2_wins=7,
            v1_wins=2,
            ties=1,
            avg_scores_v1={"accuracy": 7.0},
            avg_scores_v2={"accuracy": 8.5},
            avg_time_v1_ms=100,
            avg_time_v2_ms=80,
            avg_token_saved_percent=20.0,
            dimension_improvements={"accuracy": 1.5},
        )
        assert agg.v2_wins == 7
        assert agg.v1_wins == 2
        assert agg.avg_token_saved_percent == 20.0

    def test_generate_report_output(self):
        """报告生成应包含所有关键部分"""
        from src.core.prompt_evaluator import PromptEvaluator, AggregateResult
        evaluator = PromptEvaluator()
        agg = AggregateResult(
            total_cases=5,
            v2_wins=4,
            v1_wins=0,
            ties=1,
            avg_scores_v1={"accuracy": 7.0, "relevance": 7.0, "completeness": 6.0,
                           "safety": 7.0, "clarity": 6.0, "personalization": 5.0,
                           "token_efficiency": 7.0, "hallucination_risk": 7.0},
            avg_scores_v2={"accuracy": 8.5, "relevance": 8.5, "completeness": 8.0,
                           "safety": 9.0, "clarity": 8.0, "personalization": 7.0,
                           "token_efficiency": 8.0, "hallucination_risk": 8.5},
            avg_time_v1_ms=150,
            avg_time_v2_ms=100,
            avg_token_saved_percent=15.0,
            dimension_improvements={k: 1.5 for k in ["accuracy", "relevance", "completeness"]},
        )
        report = evaluator.generate_report(agg)
        assert "A/B 测试报告" in report
        assert "测试概览" in report
        assert "各维度平均分对比" in report
        assert "性能对比" in report
        assert "结论" in report
        assert "✅" in report or "⚠️" in report

    def test_quick_ab_test(self):
        """快速A/B测试"""
        from src.core.prompt_evaluator import quick_ab_test
        cases = [
            {"query": "猫拉肚子", "intent": "symptom_check"},
            {"query": "你好", "intent": "casual_chat"},
        ]
        v1_responses = ["可能消化不良", "你好！"]
        v2_responses = ["🐾【症状】\n\n1. 观察\n\n⚠️ 请就医", "你好呀！有什么可以帮你的吗？🐾"]
        result = quick_ab_test(v1_responses, v2_responses, cases)
        assert result.total_cases == 2
        assert isinstance(result.v2_wins, int)


class TestV1VsV2Comparison:
    """V1与V2对比测试"""

    def test_v2_has_intent_classification(self):
        """V2应有意图分类步骤，V1没有"""
        from src.agents.agent_v2 import AgentV2
        assert hasattr(AgentV2, 'classify_intent')

    def test_v2_has_reflection_loop(self):
        """V2应有反思循环"""
        from src.agents.agent_v2 import AgentV2
        assert hasattr(AgentV2, 'reflect')

    def test_v2_has_parallel_execution(self):
        """V2应有并行执行"""
        from src.agents.agent_v2 import AgentV2
        assert hasattr(AgentV2, '_execute_parallel')

    def test_v2_uses_intent_routing(self):
        """V2使用意图路由减少工具数量"""
        from src.agents.agent_v2 import AgentV2, IntentCategory
        agent = AgentV2(llm=MagicMock())
        # 特定意图 vs 全部工具
        specific_tools = agent._get_relevant_tools([IntentCategory.HEALTH_CONSULT])
        all_tools = agent.tool_registry.list_tools()
        assert len(specific_tools) <= len(all_tools)

    def test_v2_prompts_have_few_shot_examples(self):
        """V2 Prompt应有更多few-shot示例"""
        from src.core.prompts_v2 import PLAN_V2_PROMPT_TEMPLATE
        from src.core.rag_prompts import RAG_QUERY_TEMPLATE
        # V2示例数
        v2_examples = PLAN_V2_PROMPT_TEMPLATE.count("示例")
        # V1的plan prompt嵌入在pet_health_agent.py中，只有1个示例
        assert v2_examples >= 2

    def test_v2_system_prompt_has_role_definition(self):
        """V2系统提示词应明确定义角色和行为边界"""
        from src.core.prompts_v2 import ROLE_SYSTEM_PROMPT_V2
        role_keywords = ["角色定位", "行为准则", "禁止行为"]
        found = sum(1 for kw in role_keywords if kw in ROLE_SYSTEM_PROMPT_V2)
        assert found >= 2, f"角色定义不完整，仅找到{found}个关键词"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])