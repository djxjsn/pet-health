"""
CRAG（Corrective RAG）- 纠正性检索增强生成

在检索质量不足时，自动触发补充检索机制：
1. 置信度评估 - 结合Self-RAG的评估结果
2. Web搜索回退 - 知识库不足时搜索外部信息（Tavily）
3. 拒答机制 - 内外部信息均不足时明确拒答

纯规则驱动的CRAG（评估为轻量级，不额外调用LLM）。
Self-RAG提供LLM评估，CRAG整合结果做决策。
"""
import logging
from typing import List, Dict, Any, Optional

from src.core.config import get_settings

logger = logging.getLogger(__name__)

RETRIEVAL_CONFIDENCE_THRESHOLD = 0.5
GENERATION_CONFIDENCE_THRESHOLD = 0.6
WEB_SEARCH_CONFIDENCE_THRESHOLD = 0.4
REFUSE_CONFIDENCE_THRESHOLD = 0.2

REFUSE_MESSAGE = "抱歉，该问题比较复杂，建议尽快咨询专业兽医进行面诊。"


class CorrectiveRAG:
    """CRAG：纠正性检索增强"""

    def __init__(self):
        self.settings = get_settings()
        self._web_search = None
        self._web_available = False
        self._init_web_search()

    def _init_web_search(self):
        try:
            from tavily import TavilyClient
            import os
            api_key = os.environ.get("TAVILY_API_KEY") or getattr(self.settings, "TAVILY_API_KEY", None)
            if api_key:
                self._web_search = TavilyClient(api_key=api_key)
                self._web_available = True
                logger.info("Tavily Web搜索已启用")
            else:
                logger.info("Tavily API Key未配置，Web搜索不可用")
        except ImportError:
            logger.info("tavily-python未安装，Web搜索不可用")
        except Exception as e:
            logger.warning(f"Web搜索初始化失败: {e}")

    @property
    def web_search_available(self) -> bool:
        return self._web_available and self._web_search is not None

    def evaluate_and_correct(
        self,
        query: str,
        retrieval_results: List[Dict[str, Any]],
        retrieval_eval: Optional[Dict[str, Any]] = None,
        generation_eval: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """综合评估检索和生成质量，决定纠正策略

        Returns:
            {
                "action": "accept" | "supplement" | "web_search" | "refuse",
                "confidence": 综合置信度 0.0-1.0,
                "reason": 决策理由,
                "supplement_results": 补充检索结果,
                "web_results": Web搜索结果,
                "refuse_message": 拒答消息,
            }
        """
        conf = self._compute_comprehensive_confidence(
            retrieval_results, retrieval_eval, generation_eval
        )

        if conf < REFUSE_CONFIDENCE_THRESHOLD:
            return {
                "action": "refuse",
                "confidence": conf,
                "reason": "检索和生成质量均严重不足",
                "refuse_message": REFUSE_MESSAGE,
            }

        if conf < WEB_SEARCH_CONFIDENCE_THRESHOLD and self.web_search_available:
            try:
                web_results = self._web_search.search(query, search_depth="basic", max_results=3)
                return {
                    "action": "web_search",
                    "confidence": conf,
                    "reason": "知识库检索不足，已补充Web搜索",
                    "web_results": self._format_web_results(web_results),
                }
            except Exception as e:
                logger.warning(f"Web搜索失败: {e}")

        if conf < RETRIEVAL_CONFIDENCE_THRESHOLD:
            return {
                "action": "supplement",
                "confidence": conf,
                "reason": "检索置信度不足，建议补充检索",
                "supplement_query": retrieval_eval.get("suggested_query") if retrieval_eval else None,
            }

        return {
            "action": "accept",
            "confidence": conf,
            "reason": "检索和生成质量可接受",
        }

    def _compute_comprehensive_confidence(
        self,
        retrieval_results: List[Dict[str, Any]],
        retrieval_eval: Optional[Dict[str, Any]] = None,
        generation_eval: Optional[Dict[str, Any]] = None,
    ) -> float:
        """计算综合置信度"""
        scores = []

        if retrieval_eval:
            if retrieval_eval.get("strategy") == "llm":
                scores.append(retrieval_eval.get("sufficiency", 0.5) * 0.6)
                rel_bonus = 0.15 if retrieval_eval.get("is_relevant") else 0
                scores.append(rel_bonus)
            else:
                scores.append(retrieval_eval.get("sufficiency", 0.5) * 0.4)
        elif retrieval_results:
            distances = [r.get("distance", 0.5) for r in retrieval_results[:3] if r.get("distance") is not None]
            if distances:
                avg_similarity = 1.0 - sum(distances) / len(distances)
                scores.append(avg_similarity * 0.4)

        if generation_eval:
            if generation_eval.get("strategy") == "llm":
                scores.append(generation_eval.get("confidence", 0.5) * 0.4)
                if not generation_eval.get("is_faithful"):
                    scores.append(-0.2)
            else:
                scores.append(generation_eval.get("confidence", 0.5) * 0.2)

        if retrieval_results:
            result_count = min(len(retrieval_results), 5)
            scores.append(min(result_count / 5.0, 1.0) * 0.1)

        if not scores:
            return 0.0

        conf = sum(scores)
        return max(0.0, min(1.0, conf))

    def _format_web_results(self, web_results) -> List[Dict[str, Any]]:
        results = []
        if hasattr(web_results, "get"):
            items = web_results.get("results", [])
        else:
            items = getattr(web_results, "results", [])

        for item in items[:3]:
            results.append({
                "content": item.get("content") or item.get("snippet", ""),
                "metadata": {
                    "source": item.get("url", "web"),
                    "title": item.get("title", ""),
                    "type": "web_search",
                },
                "distance": 0.5,
            })
        return results

    def should_refuse(
        self,
        retrieval_results: List[Dict[str, Any]],
        retrieval_eval: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """快速判断是否应该拒答（轻量级，不调用LLM）"""
        if not retrieval_results:
            return True

        if retrieval_eval:
            if retrieval_eval.get("sufficiency", 0) < REFUSE_CONFIDENCE_THRESHOLD + 0.1:
                return True

        return False


_crag: Optional[CorrectiveRAG] = None


def get_corrective_rag() -> CorrectiveRAG:
    global _crag
    if _crag is None:
        _crag = CorrectiveRAG()
    return _crag