"""
Agentic RAG 核心引擎

基于 ReAct (Reasoning + Acting) 模式的自主智能体：
1. 思考 (Think) - 分析用户问题，制定检索计划
2. 行动 (Act) - 调用工具执行检索计划
3. 观察 (Observe) - 分析工具返回结果
4. 反思 (Reflect) - 评估结果质量，决定是否补充检索
5. 回答 (Answer) - 整合所有信息生成最终回答

支持 Plan-and-Execute 模式用于复杂多步查询。
"""
import json
import re
import time
import logging
from typing import List, Dict, Any, Optional, Callable

from src.core.config import get_settings

logger = logging.getLogger(__name__)

AGENT_SYSTEM_PROMPT = """你是宠物健康领域的智能助手，具备自主检索和推理能力。

核心能力：
1. 分析用户问题，识别需要哪些信息
2. 规划检索策略（向量检索、图谱推理、症状分析等）
3. 调用合适的工具获取信息
4. 评估信息是否足够，决定是否需要补充检索
5. 整合多源信息生成专业回答

检索工具：
- knowledge_search: 向量语义检索，适合模糊/概念性问题
- graph_search: 知识图谱多跳推理，适合关联性问题
- symptom_analysis: 症状→疾病推理分析
- breed_info: 品种百科查询
- nutrition_advice: 营养建议查询

回答原则：
1. 基于检索到的参考资料回答，不编造信息
2. 多工具结果互相印证，优先级：图谱路径 > 向量检索 > 通用知识
3. 信息不足时诚实告知，建议咨询兽医
4. 回答格式遵循回复规范"""

REACT_THOUGHT_PROMPT = """当前对话：
{history}

用户最新问题：{query}
已知上下文：{context}

请分析：
1. 用户的核心意图是什么？
2. 需要哪些信息来回答？
3. 应该使用哪些检索工具？按什么顺序？

输出JSON：
{{
  "intent": "symptom_diagnosis/medication_info/nutrition_advice/first_aid/behavior_training/breed_info/general_knowledge",
  "required_info": ["信息需求列表"],
  "plan": [{{"tool": "工具名", "query": "检索查询", "reason": "使用理由"}}],
  "confidence": 0.0-1.0
}}"""

REACT_OBSERVE_PROMPT = """已执行的检索计划：
{execution_log}

检索到的信息：
{observations}

请分析：
1. 当前信息是否足够回答用户问题？
2. 是否需要补充检索？如需，建议使用什么工具和查询？
3. 各信息来源的可靠性如何？

输出JSON：
{{
  "sufficient": true/false,
  "gap_analysis": "信息缺口分析",
  "supplement_plan": [{{"tool": "工具名", "query": "补充查询"}}]（如不需要则为空数组）,
  "confidence": 0.0-1.0
}}"""

REACT_ANSWER_PROMPT = """用户问题：{query}
宠物信息：{pet_info}

检索到的参考信息：
{observations}

请基于以上信息生成专业回答。遵循回复格式规范：
1. 开头emoji + 友好开场
2. 按场景拆分模块，emoji + 标题
3. 操作步骤数字序号，注意事项用-列出
4. ❌标注风险禁忌
5. 结尾重要提醒

信息不足时明确说"该问题需要专业兽医面诊"。
禁止编造未在参考资料中出现的事实性信息。"""

MAX_ITERATIONS = 5
MIN_CONFIDENCE = 0.7


class AgentState:
    """Agent状态"""
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    ANSWERING = "answering"
    DONE = "done"
    REFUSED = "refused"


class AgenticRAG:
    """Agentic RAG 核心引擎"""

    def __init__(self):
        self.settings = get_settings()
        self._llm = None
        self._available = False
        self._tools: Dict[str, Callable] = {}
        self._state = AgentState.THINKING
        self._history: List[Dict[str, Any]] = []
        self._observations: List[Dict[str, Any]] = []
        self._execution_log: List[Dict[str, Any]] = []
        self._iterations = 0
        self._init_llm()

    def _init_llm(self):
        try:
            from src.core.llm import get_llm
            self._llm = get_llm()
            self._available = True
            logger.info("AgenticRAG LLM初始化成功")
        except Exception as e:
            logger.warning(f"AgenticRAG LLM初始化失败: {e}")

    @property
    def is_available(self) -> bool:
        return self._available and self._llm is not None

    def register_tool(self, name: str, func: Callable):
        """注册工具"""
        self._tools[name] = func
        logger.info(f"工具已注册: {name}")

    def run(
        self,
        query: str,
        pet_info: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        max_iterations: int = MAX_ITERATIONS
    ) -> Dict[str, Any]:
        """执行Agentic RAG主循环

        Returns:
            {
                "answer": 最终回答,
                "execution_trace": 执行轨迹,
                "iterations": 迭代次数,
                "state": 最终状态,
                "confidence": 置信度,
            }
        """
        self._state = AgentState.THINKING
        self._observations = []
        self._execution_log = []
        self._iterations = 0
        start_time = time.time()

        try:
            thought = self._think(query, context)
            self._iterations += 1

            plan = thought.get("plan", [])
            if not plan and thought.get("confidence", 0) < 0.3:
                return self._refuse(query, "无法理解问题意图")

            self._state = AgentState.ACTING
            observations = self._execute_plan(plan)

            self._state = AgentState.OBSERVING
            sufficient = self._observe(query, observations, thought)

            while not sufficient and self._iterations < max_iterations:
                supplement_plan = self._observations[-1].get("supplement_plan", []) if self._observations else []
                if not supplement_plan:
                    break

                self._state = AgentState.ACTING
                more_obs = self._execute_plan(supplement_plan)
                observations.extend(more_obs)

                self._state = AgentState.OBSERVING
                sufficient = self._observe(query, observations, thought)
                self._iterations += 1

            self._state = AgentState.ANSWERING
            answer = self._answer(query, observations, pet_info)

            final_confidence = self._compute_final_confidence(observations, thought)

            self._state = AgentState.DONE
            elapsed = time.time() - start_time

            return {
                "answer": answer,
                "execution_trace": self._execution_log,
                "iterations": self._iterations,
                "state": self._state,
                "confidence": final_confidence,
                "elapsed_seconds": elapsed,
            }

        except Exception as e:
            logger.error(f"AgenticRAG执行失败: {e}")
            return {
                "answer": "抱歉，处理您的问题时遇到了技术问题，请稍后重试或咨询专业兽医。",
                "execution_trace": self._execution_log,
                "iterations": self._iterations,
                "state": "error",
                "confidence": 0.0,
                "error": str(e),
            }

    def _think(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """思考阶段：分析问题，制定计划"""
        history_str = self._format_history()
        ctx_str = json.dumps(context or {}, ensure_ascii=False)

        try:
            prompt = REACT_THOUGHT_PROMPT.format(
                history=history_str,
                query=query,
                context=ctx_str
            )
            response = self._llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            text = self._extract_json(text)
            result = json.loads(text)

            self._execution_log.append({
                "phase": "think",
                "intent": result.get("intent"),
                "required_info": result.get("required_info", []),
                "plan": result.get("plan", []),
                "confidence": result.get("confidence", 0.5),
            })
            return result
        except Exception as e:
            logger.warning(f"Agent思考失败: {e}")
            return self._default_think(query)

    def _execute_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行检索计划"""
        observations = []

        for step in plan:
            tool_name = step.get("tool", "")
            query_text = step.get("query", "")
            reason = step.get("reason", "")

            if not tool_name or tool_name not in self._tools:
                logger.warning(f"工具不可用: {tool_name}")
                continue

            try:
                result = self._tools[tool_name](query_text)
                observations.append({
                    "tool": tool_name,
                    "query": query_text,
                    "reason": reason,
                    "result": result,
                    "timestamp": time.time(),
                })
                self._execution_log.append({
                    "phase": "act",
                    "tool": tool_name,
                    "query": query_text,
                    "success": True,
                })
            except Exception as e:
                logger.error(f"工具执行失败 [{tool_name}]: {e}")
                self._execution_log.append({
                    "phase": "act",
                    "tool": tool_name,
                    "query": query_text,
                    "success": False,
                    "error": str(e),
                })

        return observations

    def _observe(
        self, query: str, observations: List[Dict[str, Any]], thought: Dict[str, Any]
    ) -> bool:
        """观察阶段：评估结果是否足够"""
        observations_text = self._format_observations(observations)
        execution_text = json.dumps(self._execution_log, ensure_ascii=False)

        try:
            prompt = REACT_OBSERVE_PROMPT.format(
                execution_log=execution_text,
                observations=observations_text
            )
            response = self._llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            text = self._extract_json(text)
            result = json.loads(text)

            self._observations.append(result)
            self._execution_log.append({
                "phase": "observe",
                "sufficient": result.get("sufficient", False),
                "gap_analysis": result.get("gap_analysis", ""),
                "confidence": result.get("confidence", 0.5),
            })

            return result.get("sufficient", True)
        except Exception as e:
            logger.warning(f"Agent观察失败: {e}")
            return True

    def _answer(
        self, query: str, observations: List[Dict[str, Any]], pet_info: Optional[Dict[str, Any]]
    ) -> str:
        """回答阶段：整合信息生成回答"""
        observations_text = self._format_observations(observations)
        pet_info_str = self._format_pet_info(pet_info)

        try:
            prompt = REACT_ANSWER_PROMPT.format(
                query=query,
                pet_info=pet_info_str,
                observations=observations_text
            )
            response = self._llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            return text.strip()
        except Exception as e:
            logger.error(f"Agent回答生成失败: {e}")
            return "抱歉，处理您的问题时遇到了技术问题。建议您咨询专业兽医获取帮助。"

    def _refuse(self, query: str, reason: str) -> Dict[str, Any]:
        self._state = AgentState.REFUSED
        return {
            "answer": "抱歉，该问题比较复杂，建议尽快咨询专业兽医进行面诊。",
            "execution_trace": self._execution_log,
            "iterations": self._iterations,
            "state": self._state,
            "confidence": 0.0,
            "refuse_reason": reason,
        }

    def _default_think(self, query: str) -> Dict[str, Any]:
        """当LLM不可用时的默认思考"""
        plan = []
        if any(kw in query for kw in ["病", "症状", "痛", "肿", "红", "吐", "拉"]):
            plan.append({"tool": "knowledge_search", "query": query, "reason": "症状相关问题"})
            plan.append({"tool": "symptom_analysis", "query": query, "reason": "分析症状可能对应疾病"})
        elif any(kw in query for kw in ["品种", "金毛", "布偶", "柯基", "泰迪"]):
            plan.append({"tool": "breed_info", "query": query, "reason": "品种信息查询"})
        elif any(kw in query for kw in ["营养", "吃什么", "喂食", "鱼油", "维生素"]):
            plan.append({"tool": "nutrition_advice", "query": query, "reason": "营养建议查询"})
        else:
            plan.append({"tool": "knowledge_search", "query": query, "reason": "通用知识检索"})

        return {
            "intent": "general_knowledge",
            "required_info": [query],
            "plan": plan,
            "confidence": 0.5,
        }

    def _compute_final_confidence(
        self, observations: List[Dict[str, Any]], thought: Dict[str, Any]
    ) -> float:
        scores = [thought.get("confidence", 0.5)]
        for obs in self._observations:
            scores.append(obs.get("confidence", 0.5))
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    def _format_history(self) -> str:
        if not self._history:
            return "（无历史对话）"
        parts = []
        for h in self._history[-3:]:
            parts.append(f"用户: {h.get('query', '')}")
            parts.append(f"助手: {h.get('answer', '')[:100]}")
        return "\n".join(parts)

    def _format_observations(self, observations: List[Dict[str, Any]]) -> str:
        if not observations:
            return "（无检索结果）"
        parts = []
        for i, obs in enumerate(observations[-10:], 1):
            tool = obs.get("tool", "unknown")
            query_text = obs.get("query", "")
            result = obs.get("result", {})

            if isinstance(result, dict) and "results" in result:
                results_list = result["results"]
                if isinstance(results_list, list):
                    contents = [r.get("content", str(r))[:200] for r in results_list[:3]]
                    parts.append(f"[{i}] 工具={tool}, 查询={query_text}\n" + "\n".join(contents))
                else:
                    parts.append(f"[{i}] 工具={tool}: {str(results_list)[:300]}")
            elif isinstance(result, str):
                parts.append(f"[{i}] 工具={tool}: {result[:300]}")
            else:
                parts.append(f"[{i}] 工具={tool}: {json.dumps(result, ensure_ascii=False)[:300]}")
        return "\n\n".join(parts)

    def _format_pet_info(self, pet_info: Optional[Dict[str, Any]]) -> str:
        if not pet_info:
            return "（无宠物信息）"
        parts = []
        for k, v in pet_info.items():
            parts.append(f"{k}: {v}")
        return ", ".join(parts)

    @staticmethod
    def _extract_json(text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group()
        return text


_agentic_rag: Optional[AgenticRAG] = None


def get_agentic_rag() -> AgenticRAG:
    global _agentic_rag
    if _agentic_rag is None:
        _agentic_rag = AgenticRAG()
    return _agentic_rag