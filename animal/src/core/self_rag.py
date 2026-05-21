"""
Self-RAG 自评估模块

对RAG的检索和生成阶段进行自评估：
1. 检索质量评估 - 判断检索结果是否足以回答问题
2. 生成质量评估 - 判断生成内容是否与上下文一致（反幻觉）
3. 置信度评分 - 综合评分决定是否需要补充检索或拒答
"""
import json
import re
import logging
from typing import List, Dict, Any, Optional

from src.core.config import get_settings

logger = logging.getLogger(__name__)

RETRIEVAL_EVAL_PROMPT = """评估以下检索结果是否能充分回答用户问题。

用户问题：{query}
检索结果：
{results}

输出JSON格式：
{{
  "is_relevant": true/false,
  "sufficiency": 0.0-1.0,
  "relevance_reason": "判断理由",
  "need_more_retrieval": true/false,
  "suggested_query": "如果需要补充检索，建议的查询文本"
}}

判断标准：
- sufficiency >= 0.7: 检索结果足够
- sufficiency 0.4-0.7: 基本足够但可能遗漏
- sufficiency < 0.4: 检索结果不足，需要补充检索或拒答"""

GENERATION_EVAL_PROMPT = """评估以下回答是否与提供的参考资料一致。

参考资料：{context}

生成的回答：{answer}

输出JSON格式：
{{
  "is_faithful": true/false,
  "hallucination_parts": ["与参考资料不一致的具体内容"],
  "confidence": 0.0-1.0,
  "hallucination_reason": "判断理由"
}}

判断标准：
- 回答中的所有事实性陈述必须在参考资料中找到依据
- 合理的推理和总结不算幻觉
- 安全提醒和建议不算幻觉
- confidence < 0.6: 可能存在严重幻觉"""

SAFETY_DISCLAIMER = "建议仅供参考，不能替代兽医诊断。如症状持续或加重，请立即咨询专业兽医。"


class SelfRAG:
    """Self-RAG：检索和生成的自我评估与纠正"""

    def __init__(self):
        self.settings = get_settings()
        self._llm = None
        self._available = False
        self._init_llm()

    def _init_llm(self):
        try:
            from src.core.llm import get_llm
            self._llm = get_llm()
            self._available = True
        except Exception as e:
            logger.warning(f"Self-RAG LLM初始化失败: {e}")
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available and self._llm is not None

    def evaluate_retrieval(
        self, query: str, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """评估检索结果质量"""
        if not self.is_available or not results:
            return self._default_retrieval_eval(results)

        results_text = self._format_retrieval_results(results)

        try:
            prompt = RETRIEVAL_EVAL_PROMPT.format(
                query=query,
                results=results_text
            )
            response = self._llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            text = self._extract_json(text)

            eval_result = json.loads(text)
            eval_result["strategy"] = "llm"
            return eval_result
        except Exception as e:
            logger.warning(f"Self-RAG检索评估失败: {e}")
            return self._default_retrieval_eval(results)

    def evaluate_generation(
        self, context_blocks: List[Dict[str, Any]], answer: str
    ) -> Dict[str, Any]:
        """评估生成结果的事实一致性"""
        if not self.is_available or not context_blocks:
            return self._default_generation_eval(context_blocks)

        context_text = self._format_context(context_blocks)

        try:
            prompt = GENERATION_EVAL_PROMPT.format(
                context=context_text,
                answer=answer
            )
            response = self._llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            text = self._extract_json(text)

            eval_result = json.loads(text)
            eval_result["strategy"] = "llm"
            return eval_result
        except Exception as e:
            logger.warning(f"Self-RAG生成评估失败: {e}")
            return self._default_generation_eval(context_blocks)

    def should_refuse_or_correct(
        self,
        retrieval_eval: Dict[str, Any],
        generation_eval: Dict[str, Any]
    ) -> Dict[str, Any]:
        """综合判断是否需要拒答、纠正或补充检索"""
        sufficiency = retrieval_eval.get("sufficiency", 0)
        confidence = generation_eval.get("confidence", 1.0)
        is_faithful = generation_eval.get("is_faithful", True)
        is_relevant = retrieval_eval.get("is_relevant", True)

        if not is_relevant or sufficiency < 0.2:
            return {
                "action": "refuse",
                "reason": "检索结果与问题不相关或严重不足",
                "supplement": None,
            }

        if not is_faithful and confidence < 0.4:
            return {
                "action": "refuse",
                "reason": f"生成内容存在严重幻觉: {generation_eval.get('hallucination_reason', '')}",
                "supplement": None,
            }

        if sufficiency < 0.4:
            return {
                "action": "supplement",
                "reason": "检索结果不足，需要补充检索",
                "supplement": retrieval_eval.get("suggested_query"),
            }

        if not is_faithful:
            return {
                "action": "correct",
                "reason": f"生成内容部分不一致: {generation_eval.get('hallucination_reason', '')}",
                "hallucination_parts": generation_eval.get("hallucination_parts", []),
                "supplement": None,
            }

        return {
            "action": "accept",
            "reason": "检索和生成质量可接受",
            "supplement": None,
        }

    def add_safety_disclaimer(self, answer: str) -> str:
        """确保回答包含安全声明"""
        if SAFETY_DISCLAIMER in answer:
            return answer
        return f"{answer}\n\n{SAFETY_DISCLAIMER}"

    def _default_retrieval_eval(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not results:
            return {
                "is_relevant": False,
                "sufficiency": 0.0,
                "relevance_reason": "无检索结果",
                "need_more_retrieval": True,
                "suggested_query": None,
                "strategy": "default",
            }

        distances = [r.get("distance", 0.5) for r in results if r.get("distance") is not None]
        scores = [1.0 - d for d in distances] if distances else [0.5]
        avg_score = sum(scores) / len(scores) if scores else 0.5

        return {
            "is_relevant": avg_score > 0.4,
            "sufficiency": min(avg_score, 0.7),
            "relevance_reason": f"基于相似度评估，平均得分{avg_score:.2f}",
            "need_more_retrieval": avg_score < 0.4,
            "suggested_query": None,
            "strategy": "default",
        }

    def _default_generation_eval(self, context_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "is_faithful": bool(context_blocks),
            "hallucination_parts": [],
            "confidence": 0.7 if context_blocks else 0.3,
            "hallucination_reason": "",
            "strategy": "default",
        }

    def _format_retrieval_results(self, results: List[Dict[str, Any]]) -> str:
        parts = []
        for i, r in enumerate(results[:5]):
            content = r.get("content", "")[:300]
            score = r.get("distance")
            relevance = f"[相似度: {1 - score:.2f}]" if score is not None else ""
            parts.append(f"[结果{i + 1}] {relevance}\n{content}")
        return "\n\n".join(parts)

    def _format_context(self, context_blocks: List[Dict[str, Any]]) -> str:
        parts = []
        for i, r in enumerate(context_blocks[:5]):
            content = r.get("content", "")[:500]
            parts.append(f"[参考资料{i + 1}]\n{content}")
        return "\n\n".join(parts)

    def _extract_json(self, text: str) -> str:
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


_self_rag: Optional[SelfRAG] = None


def get_self_rag() -> SelfRAG:
    global _self_rag
    if _self_rag is None:
        _self_rag = SelfRAG()
    return _self_rag