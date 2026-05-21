"""
优化版 Agent 推理架构 V2

核心改进：
1. 意图分类与工具路由 - 避免所有15个工具一次性塞入prompt
2. 并行工具执行 - 独立工具真正并行调用
3. 带反思的重规划循环 - 基于中间结果决定是否追加工具调用
4. 结构化输出解析 - 使用Pydantic严格验证LLM输出

与传统架构对比：
- V1: plan(全部15工具) -> execute(串行) -> integrate
- V2: classify_intent -> route_tools(3-5个) -> execute(并行) -> reflect -> integrate
"""
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from langchain_core.language_models import BaseLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field, field_validator

from src.agents.base_agent import BaseAgent, AgentStatus
from src.tools.tool_registry import get_tool_registry
from src.core.prompts_v2 import (
    CLASSIFY_PROMPT_TEMPLATE,
    PLAN_V2_PROMPT_TEMPLATE,
    REFLECT_PROMPT_TEMPLATE,
    INTEGRATE_V2_PROMPT_TEMPLATE,
    DIRECT_V2_PROMPT_TEMPLATE,
    INTENT_DEFINITIONS,
    TOOL_TO_INTENT_MAP,
    TOOL_PRIORITY,
)

logger = logging.getLogger(__name__)


class IntentCategory(str, Enum):
    """意图分类"""
    PET_INFO = "pet_info"
    HEALTH_CONSULT = "health_consult"
    SYMPTOM_CHECK = "symptom_check"
    NUTRITION_ADVICE = "nutrition_advice"
    BEHAVIOR_ANALYSIS = "behavior_analysis"
    EMERGENCY_ASSESS = "emergency_assess"
    DAILY_CARE = "daily_care"
    EXTERNAL_SERVICE = "external_service"
    CASUAL_CHAT = "casual_chat"
    UNKNOWN = "unknown"


class IntentResult(BaseModel):
    """意图分类结果"""
    primary_intent: IntentCategory = Field(description="主要意图类别")
    secondary_intents: List[IntentCategory] = Field(
        default_factory=list,
        description="次要意图列表，最多2个"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0, le=1.0,
        description="分类置信度 0.0-1.0"
    )
    reasoning: str = Field(default="", description="分类理由简述")

    @field_validator("secondary_intents")
    @classmethod
    def limit_secondary(cls, v: List[IntentCategory]) -> List[IntentCategory]:
        return v[:2]


class ToolPlan(BaseModel):
    """工具调用计划条目"""
    tool: str = Field(description="工具名称")
    args: Dict[str, Any] = Field(default_factory=dict, description="工具参数")
    reason: str = Field(default="", description="调用理由")
    priority: int = Field(default=5, ge=1, le=10, description="优先级 1-10")
    depends_on: Optional[str] = Field(default=None, description="依赖的前置工具名称")


class ActionPlan(BaseModel):
    """行动规划输出"""
    actions: List[ToolPlan] = Field(description="工具调用列表，按优先级排序")
    fallback_response: Optional[str] = Field(
        default=None,
        description="当无需工具时的直接回复"
    )


class ReflectionResult(BaseModel):
    """反思结果"""
    sufficient: bool = Field(description="当前信息是否足够回答用户")
    missing_info: List[str] = Field(default_factory=list, description="仍缺失的信息")
    additional_tools: List[ToolPlan] = Field(
        default_factory=list,
        description="建议追加的工具调用"
    )
    reasoning: str = Field(default="", description="反思理由")


@dataclass
class AgentContext:
    """Agent执行上下文"""
    user_input: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    pet_id: Optional[str] = None
    pet_info: Optional[Dict[str, Any]] = None
    relevant_context: List[Dict[str, Any]] = field(default_factory=list)
    intent_result: Optional[IntentResult] = None
    plan: List[ToolPlan] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)
    reflection_count: int = 0
    start_time: float = 0.0


class AgentV2:
    """
    优化版Agent推理引擎

    改进点:
    1. 意图分类减少token消耗（15工具 -> 3-5个相关工具）
    2. 独立工具并行执行
    3. 反思机制确保信息充分
    4. 结构化输出严格验证
    5. 工具调用优先级排序
    """

    MAX_REFLECTION_ROUNDS = 2
    MAX_TOOLS_PER_PLAN = 5
    MAX_PARALLEL_TOOLS = 5

    def __init__(
        self,
        llm: BaseLLM,
        user_id: Optional[str] = None,
        db: Any = None,
    ):
        self.llm = llm
        self.user_id = user_id
        self.db = db
        self.tool_registry = get_tool_registry()
        self._tools_cache: Optional[Dict[str, Any]] = None

    def _get_relevant_tools(self, intents: List[IntentCategory]) -> List[str]:
        """根据意图获取相关工具名称"""
        tool_names = set()
        for intent in intents:
            names = TOOL_TO_INTENT_MAP.get(intent, [])
            tool_names.update(names)
        # 始终包含基础工具
        tool_names.add("get_user_pets")
        tool_names.add("get_pet_info")
        return list(tool_names)

    def _get_tools_description(self, tool_names: List[str]) -> str:
        """获取指定工具的格式化描述"""
        descriptions = []
        for name in tool_names:
            tool = self.tool_registry.get_tool(name, db=self.db)
            if tool:
                priority = TOOL_PRIORITY.get(name, 5)
                descriptions.append(
                    f"- **{name}** (优先级{priority}): {tool.description}"
                )
        return "\n".join(descriptions)

    def classify_intent(self, user_input: str, pet_info: Optional[Dict] = None) -> IntentResult:
        """第一步：意图分类

        将用户输入分类到预定义的意图类别，减少后续规划阶段需要参考的工具数量
        （从15个减少到3-5个），降低token消耗并提高规划准确性。
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            ("human", "{user_input}")
        ])

        pet_info_text = self._format_pet_info(pet_info)
        system_message = CLASSIFY_PROMPT_TEMPLATE.format(
            intent_definitions=INTENT_DEFINITIONS,
            pet_info=pet_info_text,
        )

        chain = prompt | self.llm | StrOutputParser()

        try:
            result_text = chain.invoke({
                "system_message": system_message,
                "user_input": user_input,
            })
            result_text = self._extract_json(result_text)
            result = IntentResult.model_validate_json(result_text)
            logger.info(f"意图分类: {result.primary_intent} (置信度: {result.confidence})")
            return result
        except Exception as e:
            logger.warning(f"意图分类失败，默认使用通用路由: {e}")
            return IntentResult(
                primary_intent=IntentCategory.HEALTH_CONSULT,
                confidence=0.3,
                reasoning=f"分类失败自动降级: {e}"
            )

    def plan_v2(self, user_input: str, context: AgentContext) -> ActionPlan:
        """第二步：工具规划

        仅使用意图分类筛选后的工具列表进行规划，大幅减少prompt长度。
        输出结构化JSON，通过Pydantic严格验证。
        """
        relevant_tools = self._get_relevant_tools(
            [context.intent_result.primary_intent] + context.intent_result.secondary_intents
        )
        tools_description = self._get_tools_description(relevant_tools)

        prompt_template = PLAN_V2_PROMPT_TEMPLATE.format(
            tools_description=tools_description,
            user_input=user_input,
            primary_intent=context.intent_result.primary_intent.value,
            confidence=context.intent_result.confidence,
            pet_info=self._format_pet_info(context.pet_info),
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            ("human", "{user_input}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        try:
            result_text = chain.invoke({
                "system_message": prompt_template,
                "user_input": user_input,
            })
            result_text = self._extract_json(result_text)
            plan = ActionPlan.model_validate_json(result_text)
            logger.info(f"规划完成: {len(plan.actions)}个工具调用")

            # 如果提示不需要工具，直接生成回复
            if plan.fallback_response:
                logger.info("规划结果：无需工具调用，直接回复")

            return plan
        except Exception as e:
            logger.warning(f"规划失败: {e}")
            return ActionPlan(
                actions=[],
                fallback_response="抱歉，我暂时无法处理这个请求，请稍后再试或换个方式描述您的问题。"
            )

    def execute_plan(self, plan: ActionPlan) -> List[Dict[str, Any]]:
        """第三步：执行工具调用

        改进：独立工具并行执行，依赖工具串行执行
        """
        if not plan.actions:
            return []

        # 按依赖关系分组：独立工具并行，依赖工具串行
        independent = [a for a in plan.actions if not a.depends_on]
        dependent = [a for a in plan.actions if a.depends_on]

        results = []

        # 并行执行独立工具
        if independent:
            parallel_results = self._execute_parallel(independent[:self.MAX_PARALLEL_TOOLS])
            results.extend(parallel_results)

        # 串行执行有依赖关系的工具
        for action in dependent:
            # 先找到前置结果
            dep_result = next(
                (r for r in results if r.get("_tool_name") == action.depends_on),
                None
            )
            if dep_result:
                # 将前置结果注入到参数中
                action.args["_previous_result"] = dep_result

            result = self._execute_single(action)
            results.append(result)

        return results

    def _execute_parallel(self, actions: List[ToolPlan]) -> List[Dict[str, Any]]:
        """并行执行多个工具"""
        import concurrent.futures

        results = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(len(actions), self.MAX_PARALLEL_TOOLS)
        ) as executor:
            future_map = {
                executor.submit(self._execute_single, action): action
                for action in actions
            }
            for future in concurrent.futures.as_completed(future_map):
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    action = future_map[future]
                    results.append({
                        "_tool_name": action.tool,
                        "_error": str(e),
                        "_status": "failed"
                    })
        return results

    def _execute_single(self, action: ToolPlan) -> Dict[str, Any]:
        """执行单个工具调用"""
        tool = self.tool_registry.get_tool(action.tool, db=self.db)
        if not tool:
            return {
                "_tool_name": action.tool,
                "_error": f"工具 {action.tool} 不存在",
                "_status": "not_found"
            }

        try:
            # 移除内部标记字段
            clean_args = {
                k: v for k, v in action.args.items()
                if not k.startswith("_")
            }
            result = tool._run(**clean_args)
            if isinstance(result, dict):
                result["_tool_name"] = action.tool
                result["_status"] = "success"
            else:
                result = {
                    "_tool_name": action.tool,
                    "_result": result,
                    "_status": "success"
                }
            return result
        except Exception as e:
            logger.error(f"工具 {action.tool} 执行失败: {e}")
            return {
                "_tool_name": action.tool,
                "_error": str(e),
                "_status": "failed",
                "_args": action.args
            }

    def reflect(self, context: AgentContext) -> ReflectionResult:
        """第四步：反思检查

        判断当前信息是否足够回答用户问题，如果不够，建议追加工具调用。
        """
        if context.reflection_count >= self.MAX_REFLECTION_ROUNDS:
            return ReflectionResult(sufficient=True, reasoning="达到最大反思轮次")

        results_summary = json.dumps(
            [{
                "tool": r.get("_tool_name", "unknown"),
                "status": r.get("_status", "unknown"),
                "has_data": len(r) > 3,  # 除了元数据外有实际数据
            } for r in context.results],
            ensure_ascii=False
        )

        prompt_template = REFLECT_PROMPT_TEMPLATE.format(
            user_input=context.user_input,
            primary_intent=context.intent_result.primary_intent.value,
            results_summary=results_summary,
            tools_used=[r.get("_tool_name", "unknown") for r in context.results],
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            ("human", "请评估当前结果是否足够。")
        ])

        chain = prompt | self.llm | StrOutputParser()

        try:
            result_text = chain.invoke({"system_message": prompt_template})
            result_text = self._extract_json(result_text)
            reflection = ReflectionResult.model_validate_json(result_text)
            logger.info(
                f"反思结果: sufficient={reflection.sufficient}, "
                f"追加工具={len(reflection.additional_tools)}"
            )
            return reflection
        except Exception as e:
            logger.warning(f"反思失败，默认不充分并保守收敛: {e}")
            return ReflectionResult(
                sufficient=False,
                missing_info=["反思模块异常，进入保守收敛模式"],
                additional_tools=[],
                reasoning=f"反思模块异常: {e}"
            )

    def integrate_v2(self, context: AgentContext) -> str:
        """第五步：结果整合

        将所有工具结果、反思结论整合为最终回复。
        使用优化后的RAG提示词模板，确保输出质量。
        """
        results_text = json.dumps(
            [{k: v for k, v in r.items() if k != "_tool_name"} for r in context.results],
            ensure_ascii=False,
            indent=2
        )

        intent_label = {
            IntentCategory.PET_INFO: "宠物信息查询",
            IntentCategory.HEALTH_CONSULT: "健康咨询",
            IntentCategory.SYMPTOM_CHECK: "症状分析",
            IntentCategory.NUTRITION_ADVICE: "营养建议",
            IntentCategory.BEHAVIOR_ANALYSIS: "行为分析",
            IntentCategory.EMERGENCY_ASSESS: "紧急评估",
            IntentCategory.DAILY_CARE: "日常护理",
            IntentCategory.EXTERNAL_SERVICE: "外部服务",
            IntentCategory.CASUAL_CHAT: "闲聊",
            IntentCategory.UNKNOWN: "通用咨询",
        }.get(context.intent_result.primary_intent, "通用咨询")

        system_message = INTEGRATE_V2_PROMPT_TEMPLATE.format(
            user_input=context.user_input,
            intent_label=intent_label,
            results_text=results_text,
            pet_info=self._format_pet_info(context.pet_info),
            has_results=bool(context.results),
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            ("human", "请根据以上信息，整合生成最终回复。")
        ])

        chain = prompt | self.llm | StrOutputParser()

        try:
            response = chain.invoke({"system_message": system_message})
            return response
        except Exception as e:
            return f"抱歉，处理您的请求时出现错误。建议稍后重试或换个方式描述您的问题。错误详情: {str(e)[:100]}"

    def run_v2(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Agent V2 主执行循环

        完整流程:
        1. classify_intent  -> 意图分类,筛选相关工具
        2. plan_v2          -> 基于相关工具规划调用
        3. execute_plan     -> 并行执行工具
        4. reflect          -> 检查信息充分性
        5. [可选] plan+execute 追加工具
        6. integrate_v2     -> 整合最终回复
        """
        ctx = AgentContext(
            user_input=user_input,
            start_time=time.time(),
        )

        if context:
            ctx.pet_info = context.get("pet_info")
            ctx.relevant_context = context.get("relevant_context", [])
            ctx.conversation_id = context.get("conversation_id")
            ctx.pet_id = context.get("pet_id")
            ctx.user_id = context.get("user_id") or self.user_id

        try:
            # Step 1: 意图分类
            ctx.intent_result = self.classify_intent(user_input, ctx.pet_info)

            # 闲聊直接回复，不走工具流程
            if ctx.intent_result.primary_intent == IntentCategory.CASUAL_CHAT:
                return self._casual_response(user_input, ctx)

            # Step 2: 工具规划
            plan = self.plan_v2(user_input, ctx)
            ctx.plan = plan.actions

            if plan.fallback_response:
                return plan.fallback_response

            # Step 3: 执行工具
            if plan.actions:
                ctx.results = self.execute_plan(plan)

            # Step 4-5: 反思循环
            for _ in range(self.MAX_REFLECTION_ROUNDS):
                reflection = self.reflect(ctx)
                ctx.reflection_count += 1

                if reflection.sufficient:
                    break

                if reflection.additional_tools:
                    additional_results = self._execute_parallel(
                        reflection.additional_tools
                    )
                    ctx.results.extend(additional_results)
                else:
                    # 无追加工具时主动退出，避免无效反思循环
                    break

            # Step 6: 整合结果
            response = self.integrate_v2(ctx)

            elapsed = time.time() - ctx.start_time
            logger.info(
                f"Agent V2 执行完成: {elapsed:.2f}s"
                f" | 意图={ctx.intent_result.primary_intent}"
                f" | 工具调用={len(ctx.results)}"
                f" | 反思轮次={ctx.reflection_count}"
            )

            return response

        except Exception as e:
            logger.error(f"Agent V2 执行异常: {e}", exc_info=True)
            return (
                "抱歉，处理您的请求时遇到了问题。\n\n"
                "建议您：\n"
                "1. 换个方式描述您的问题\n"
                "2. 提供更多关于宠物症状的细节\n"
                "3. 如果是紧急情况，请立即联系兽医"
            )

    def _casual_response(self, user_input: str, ctx: AgentContext) -> str:
        """处理闲聊，不需要工具调用"""
        system_message = DIRECT_V2_PROMPT_TEMPLATE.format(
            user_input=user_input,
            pet_info=self._format_pet_info(ctx.pet_info),
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            ("human", "{user_input}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        try:
            return chain.invoke({
                "system_message": system_message,
                "user_input": user_input,
            })
        except Exception as e:
            return "你好呀！有什么可以帮你的吗？🐾"

    def _extract_json(self, text: str) -> str:
        """从LLM输出中提取JSON

        处理LLM可能包裹markdown代码块的情况
        """
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        # 找到第一个 { 或 [
        for i, char in enumerate(text):
            if char in ('{', '['):
                return text[i:].strip()
        return text.strip()

    @staticmethod
    def _format_pet_info(pet_info: Optional[Dict]) -> str:
        """格式化宠物信息"""
        if not pet_info:
            return "无宠物信息"
        parts = []
        if pet_info.get("name"):
            parts.append(f"名字: {pet_info['name']}")
        if pet_info.get("species"):
            parts.append(f"物种: {pet_info['species']}")
        if pet_info.get("breed"):
            parts.append(f"品种: {pet_info['breed']}")
        if pet_info.get("gender"):
            parts.append(f"性别: {pet_info['gender']}")
        return "、".join(parts) if parts else "无宠物信息"

    def get_token_stats(self, context: AgentContext) -> Dict[str, Any]:
        """获取token消耗统计（估算）"""
        intent_tools = len(self._get_relevant_tools(
            [context.intent_result.primary_intent] if context.intent_result else []
        ))
        return {
            "intent_classification_tokens": "~500",
            "planning_tools_considered": intent_tools,
            "planning_tokens_saved_vs_v1": f"~{(15 - intent_tools) * 150}",
            "executed_tools": len(context.results),
            "reflection_rounds": context.reflection_count,
            "total_time_ms": round((time.time() - context.start_time) * 1000, 1),
        }