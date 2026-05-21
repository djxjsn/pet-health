"""
融合检索器

整合向量语义检索和图谱推理检索，实现双路融合：
1. 双路并行检索 - 同时执行向量检索和图谱推理
2. 结果混合排序 - 基于语义相关度和图谱结构重要性混合排序
3. 信息互补 - 图谱填补向量检索的结构化知识空白
4. 统一输出 - 标准化检索结果，供LLM直接使用
"""
import logging
from typing import List, Dict, Any, Optional

from src.core.knowledge_retriever import get_knowledge_retriever
from src.core.graph_retriever import get_graph_retriever
from src.core.llm_query_rewriter import get_llm_query_rewriter

logger = logging.getLogger(__name__)

VECTOR_WEIGHT = 0.55
GRAPH_WEIGHT = 0.45
HYBRID_MIN_SCORE = 0.3


class FusionRetriever:
    """融合检索器 - 向量 + 图谱双路融合"""

    def __init__(self):
        self.vector_retriever = get_knowledge_retriever()
        self.graph_retriever = get_graph_retriever()
        self.query_rewriter = get_llm_query_rewriter()
        self._available = self.vector_retriever.is_available

    @property
    def is_available(self) -> bool:
        return self._available

    def search(
        self,
        query: str,
        top_k: int = 5,
        enable_quality_eval: bool = True,
        enable_graph: bool = True,
        fusion_strategy: str = "weighted_reciprocal"
    ) -> Dict[str, Any]:
        """融合检索主入口

        Args:
            query: 用户查询
            top_k: 最终返回结果数
            enable_quality_eval: 是否启用Self-RAG+CRAG质量评估
            enable_graph: 是否启用图谱检索
            fusion_strategy: 融合策略 (weighted_reciprocal / rrf / linear)

        Returns:
            {
                "results": 融合后的检索结果,
                "vector_results": 向量检索原始结果,
                "graph_results": 图谱检索原始结果,
                "quality": 质量评估结果,
                "rewrite": 查询改写结果,
                "fusion": 融合元信息,
            }
        """
        rewrite_result = self.query_rewriter.rewrite(query)

        vector_query = rewrite_result["rewritten"]
        entities = [{"type": "Entity", "name": e, "aliases": [e], "properties": {}}
                     for e in rewrite_result.get("entities", [])]

        if enable_quality_eval:
            quality_result = self.vector_retriever.search_with_quality(
                query=vector_query,
                top_k=top_k * 3,
                enable_self_rag=True,
                enable_crag=True,
            )
            vector_results = quality_result
        else:
            vector_results_raw = self.vector_retriever.search(
                query=vector_query, top_k=top_k * 3
            )
            vector_results = {
                "results": vector_results_raw,
                "action": "accept",
                "confidence": 0.7,
            }

        graph_results = None
        if enable_graph and self.graph_retriever.graph_db.is_available:
            try:
                graph_results = self.graph_retriever.search(
                    query=query,
                    entities=entities,
                    max_hops=3,
                    max_results=top_k * 3,
                    include_communities=True,
                )
            except Exception as e:
                logger.warning(f"图谱检索失败: {e}")

        vb_results = vector_results.get("results", [])
        fused_results = self._fuse_results(
            vb_results, graph_results, top_k, fusion_strategy
        )

        return {
            "results": fused_results,
            "vector_results": vector_results,
            "graph_results": graph_results,
            "quality": {
                "action": vector_results.get("action", "accept"),
                "confidence": vector_results.get("confidence", 0.5),
            },
            "rewrite": rewrite_result,
            "fusion": {
                "strategy": fusion_strategy,
                "vector_count": len(vb_results),
                "graph_count": len(graph_results["entities"]) if graph_results else 0,
                "fused_count": len(fused_results),
            },
        }

    def _fuse_results(
        self,
        vector_results: List[Dict[str, Any]],
        graph_results: Optional[Dict[str, Any]],
        top_k: int,
        strategy: str
    ) -> List[Dict[str, Any]]:
        """多策略结果融合"""
        if strategy == "weighted_reciprocal":
            return self._weighted_reciprocal_fusion(vector_results, graph_results, top_k)
        elif strategy == "rrf":
            return self._rrf_fusion(vector_results, graph_results, top_k)
        return self._linear_fusion(vector_results, graph_results, top_k)

    def _weighted_reciprocal_fusion(
        self, vr: List[Dict[str, Any]], gr: Optional[Dict[str, Any]], top_k: int
    ) -> List[Dict[str, Any]]:
        """加权倒数排名融合"""
        k = 60

        combined = {}
        for rank, item in enumerate(vr, 1):
            key = item.get("content", "")[:100]
            vec_score = 1.0 / (k + rank)
            combined[key] = {
                "content": item.get("content", ""),
                "metadata": item.get("metadata", {}),
                "distance": item.get("distance"),
                "vec_rank": rank,
                "vec_score": vec_score,
                "graph_rank": None,
                "graph_score": 0.0,
                "graph_paths": [],
                "source": "vector",
            }

        if gr:
            entities = gr.get("entities", [])
            for rank, entity in enumerate(entities, 1):
                desc = entity.get("properties", {}).get("description", "") or entity["name"]
                key = desc[:100]
                graph_score = 1.0 / (k + rank)
                if key in combined:
                    combined[key]["graph_rank"] = rank
                    combined[key]["graph_score"] = graph_score
                    combined[key]["source"] = "both"
                else:
                    combined[key] = {
                        "content": f"[{entity['type']}] {entity['name']}: {desc}",
                        "metadata": {"type": "graph_entity", "entity_type": entity["type"]},
                        "distance": 1.0 - entity.get("score", 0.5),
                        "vec_rank": None,
                        "vec_score": 0.0,
                        "graph_rank": rank,
                        "graph_score": graph_score,
                        "graph_paths": [],
                        "source": "graph",
                    }

            for i, chain in enumerate(gr.get("reasoning_chains", [])):
                reasoning = chain.get("reasoning", "")
                if reasoning:
                    key = reasoning[:100]
                    if key not in combined:
                        combined[key] = {
                            "content": f"[推断链] {reasoning}",
                            "metadata": {"type": "reasoning_chain", "confidence": chain.get("confidence", 0.5)},
                            "distance": 1.0 - chain.get("confidence", 0.5),
                            "vec_rank": None,
                            "vec_score": 0.0,
                            "graph_rank": i + 1,
                            "graph_score": 1.0 / (k + i + 1),
                            "graph_paths": [],
                            "source": "reasoning",
                        }

        for item in combined.values():
            item["fused_score"] = (
                VECTOR_WEIGHT * item["vec_score"] +
                GRAPH_WEIGHT * item["graph_score"]
            )

        sorted_items = sorted(
            combined.values(),
            key=lambda x: x["fused_score"],
            reverse=True
        )

        return sorted_items[:top_k]

    def _rrf_fusion(
        self, vr: List[Dict[str, Any]], gr: Optional[Dict[str, Any]], top_k: int
    ) -> List[Dict[str, Any]]:
        """Reciprocal Rank Fusion"""
        return self._weighted_reciprocal_fusion(vr, gr, top_k)

    def _linear_fusion(
        self, vr: List[Dict[str, Any]], gr: Optional[Dict[str, Any]], top_k: int
    ) -> List[Dict[str, Any]]:
        """线性加权融合"""
        combined = {}

        for item in vr:
            key = item.get("content", "")[:100]
            similarity = 1.0 - item.get("distance", 0.5)
            combined[key] = {"content": item["content"], "metadata": item.get("metadata", {}),
                             "fused_score": similarity * VECTOR_WEIGHT, "source": "vector"}

        if gr:
            for entity in gr.get("entities", []):
                desc = entity.get("properties", {}).get("description", "") or entity["name"]
                key = desc[:100]
                gr_score = entity.get("score", 0.5) * GRAPH_WEIGHT
                if key in combined:
                    combined[key]["fused_score"] += gr_score
                    combined[key]["source"] = "both"
                else:
                    combined[key] = {"content": f"[{entity['type']}] {entity['name']}: {desc}",
                                     "metadata": {"type": "graph_entity"}, "fused_score": gr_score, "source": "graph"}

        sorted_items = sorted(combined.values(), key=lambda x: x["fused_score"], reverse=True)
        return sorted_items[:top_k]

    def format_context_from_fusion(self, search_result: Dict[str, Any]) -> str:
        """将融合检索结果格式化为LLM可直接使用的上下文字符串"""
        results = search_result.get("results", [])
        if not results:
            return ""

        parts = []
        for i, r in enumerate(results, 1):
            source_tag = ""
            if r.get("source") == "graph":
                source_tag = " [图谱]"
            elif r.get("source") == "reasoning":
                source_tag = " [推断]"
            elif r.get("source") == "both":
                source_tag = " [综合]"

            parts.append(f"[{i}{source_tag}] {r['content']}")

        quality = search_result.get("quality", {})
        if quality.get("action") == "refuse":
            parts.append("\n⚠️ 当前知识库信息不足以充分回答此问题")

        return "\n\n".join(parts)


_fusion_retriever: Optional[FusionRetriever] = None


def get_fusion_retriever() -> FusionRetriever:
    global _fusion_retriever
    if _fusion_retriever is None:
        _fusion_retriever = FusionRetriever()
    return _fusion_retriever