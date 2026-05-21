"""
LLM驱动的查询改写器

用LLM替代纯规则引擎进行查询改写和意图识别，
支持多查询变体生成，提升检索召回率。
LLM不可用时自动回退到规则引擎。
"""
import json
import re
import logging
from typing import List, Optional, Dict, Any

from src.core.config import get_settings

logger = logging.getLogger(__name__)

QUERY_REWRITE_PROMPT = """你是宠物健康领域的查询优化专家。将用户口语化查询改写为更精确的检索查询。

用户查询：{query}
宠物上下文：{context}

输出JSON格式：
{{
  "rewritten": "改写后的核心检索查询（添加专业术语和领域关键词）",
  "intent": "意图分类（symptom_diagnosis/medication_info/nutrition_advice/first_aid/behavior_training/prevention/general_knowledge）",
  "entities": ["提取的关键实体列表"],
  "category": "最相关的知识分类（disease/medication/nutrition/first_aid/behavior）"
}}

改写要求：
1. 保留原始意图，添加专业术语（如"拉肚子"→"腹泻 排便异常"）
2. 如有物种信息，添加到查询中
3. 去除口语化冗余（如"请问""我想知道"）
4. rewritten字段只返回查询文本，不加解释"""

MULTI_QUERY_PROMPT = """生成同一问题的3个不同角度的检索查询变体。

用户查询：{query}
改写查询：{rewritten}

输出JSON格式：
{{
  "variants": ["变体1", "变体2", "变体3"]
}}

要求：
1. 每个变体从不同角度切入（症状角度、治疗角度、预防角度）
2. 变体应包含不同但相关的关键词
3. 只返回JSON，不加解释"""


class LLMQueryRewriter:
    """LLM驱动的查询改写器（支持规则引擎兜底）"""

    def __init__(self):
        self.settings = get_settings()
        self._llm = None
        self._rule_rewriter = None
        self._llm_available = False
        self._init_llm()

    def _init_llm(self):
        try:
            from src.core.llm import get_llm
            self._llm = get_llm()
            self._llm_available = True
            logger.info("LLM查询改写器初始化成功")
        except Exception as e:
            logger.warning(f"LLM查询改写器初始化失败，使用规则引擎兜底: {e}")
            self._llm_available = False

    def _get_rule_rewriter(self):
        if self._rule_rewriter is None:
            from src.core.query_rewriter import get_query_rewriter
            self._rule_rewriter = get_query_rewriter()
        return self._rule_rewriter

    def rewrite(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """LLM驱动的查询改写

        Returns:
            {
                "original": 原始查询,
                "rewritten": 改写查询,
                "intent": 意图分类,
                "entities": 实体列表,
                "category": 知识分类,
                "strategy": "llm" | "rule",
            }
        """
        if self._llm_available and self._llm:
            return self._llm_rewrite(query, context)
        return self._rule_rewrite(query, context)

    def _llm_rewrite(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        ctx_str = self._format_context(context)

        try:
            prompt = QUERY_REWRITE_PROMPT.format(query=query, context=ctx_str)
            response = self._llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            text = self._extract_json(text)

            result = json.loads(text)
            return {
                "original": query,
                "rewritten": result.get("rewritten", query),
                "intent": result.get("intent", "general_knowledge"),
                "entities": result.get("entities", []),
                "category": result.get("category"),
                "strategy": "llm",
            }
        except Exception as e:
            logger.warning(f"LLM改写失败，回退到规则引擎: {e}")
            return self._rule_rewrite(query, context)

    def _rule_rewrite(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        rule_rw = self._get_rule_rewriter()
        rewritten = rule_rw.rewrite(query, context)
        intent = rule_rw._detect_intent(query) or "general_knowledge"

        entities = []
        for word, synonyms in rule_rw.synonyms.items():
            if word in query:
                entities.append(word)

        domain = None
        for cat, keywords in rule_rw.domain_keywords.items():
            if any(kw in query for kw in keywords):
                domain = cat
                break

        return {
            "original": query,
            "rewritten": rewritten,
            "intent": intent,
            "entities": entities,
            "category": domain,
            "strategy": "rule",
        }

    def generate_multi_queries(
        self,
        query: str,
        rewritten: str,
        num_variants: int = 3
    ) -> List[str]:
        """生成多查询变体"""
        if self._llm_available and self._llm:
            try:
                prompt = MULTI_QUERY_PROMPT.format(query=query, rewritten=rewritten)
                response = self._llm.invoke(prompt)
                text = response.content if hasattr(response, "content") else str(response)
                text = self._extract_json(text)

                result = json.loads(text)
                variants = result.get("variants", [])
                valid = [v for v in variants if v and v != query and v != rewritten]
                return valid[:num_variants]
            except Exception as e:
                logger.warning(f"LLM多查询生成失败: {e}")

        rule_rw = self._get_rule_rewriter()
        return rule_rw.generate_multi_queries(query, num_variants)

    def extract_intent_and_category(self, query: str) -> Dict[str, str]:
        """快速意图和分类提取（供RetrievalRouter使用）"""
        rewrite_result = self.rewrite(query)
        return {
            "intent": rewrite_result.get("intent", "general_knowledge"),
            "category": rewrite_result.get("category"),
            "strategy": rewrite_result.get("strategy", "rule"),
        }

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

    def _format_context(self, context: Optional[Dict[str, Any]]) -> str:
        if not context:
            return "无"
        parts = []
        for k, v in context.items():
            parts.append(f"{k}: {v}")
        return ", ".join(parts)


_llm_query_rewriter: Optional[LLMQueryRewriter] = None


def get_llm_query_rewriter() -> LLMQueryRewriter:
    global _llm_query_rewriter
    if _llm_query_rewriter is None:
        _llm_query_rewriter = LLMQueryRewriter()
    return _llm_query_rewriter