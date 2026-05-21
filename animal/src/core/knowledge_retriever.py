"""
知识检索器（统一检索入口）

提供基于向量语义的知识检索功能，支持分类过滤、标签过滤、
对话上下文检索、症状分析检索等多种检索场景。
当后端为Qdrant时，自动启用稠密+稀疏混合检索。
所有RAG检索必须通过本模块进行，禁止直接调用VectorDatabase。

Phase 2更新:
- 集成LLMQueryRewriter（LLM驱动查询改写，规则引擎兜底）
- 检索结果返回查询元数据（intent/category/entities）
- 支持Self-RAG + CRAG质量评估流水线
"""
import time
import logging
from typing import List, Dict, Any, Optional

from src.core.vector_db import get_vector_db
from src.core.config import get_settings
from src.core.query_rewriter import get_query_rewriter
from src.core.search_cache import get_search_cache
from src.core.rag_monitor import get_rag_monitor

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """知识检索器 - 统一检索入口"""

    def __init__(self, default_top_k: Optional[int] = None, enable_query_rewrite: bool = True, enable_cache: bool = True):
        settings = get_settings()
        self.vector_db = get_vector_db()
        self.default_top_k = default_top_k or settings.SEARCH_TOP_K
        self.default_similarity_threshold = settings.SIMILARITY_THRESHOLD
        self.overretrieval_factor = settings.SEARCH_OVERRETRIEVAL_FACTOR
        self.enable_query_rewrite = enable_query_rewrite
        self.enable_cache = enable_cache
        self._query_rewriter = get_query_rewriter() if enable_query_rewrite else None
        self._llm_rewriter = self._init_llm_rewriter()
        self._cache = get_search_cache() if enable_cache else None
        self._monitor = get_rag_monitor()
        self._use_hybrid = hasattr(self.vector_db, 'hybrid_search')

    def _init_llm_rewriter(self):
        try:
            from src.core.llm_query_rewriter import get_llm_query_rewriter
            rw = get_llm_query_rewriter()
            logger.info("LLMQueryRewriter集成成功")
            return rw
        except Exception as e:
            logger.warning(f"LLMQueryRewriter不可用，使用规则改写器: {e}")
            return None

    @property
    def is_available(self) -> bool:
        return self.vector_db.is_available

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        min_similarity: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        if not self.is_available:
            logger.warning("嵌入模型不可用，知识检索功能暂不可用")
            return []

        if top_k is None:
            top_k = self.default_top_k

        if min_similarity is None:
            min_similarity = self.default_similarity_threshold

        if self._cache:
            cached = self._cache.get(query, top_k, category, min_similarity)
            if cached is not None:
                self._monitor.record_cache_access(hit=True)
                return cached[:top_k]
            else:
                self._monitor.record_cache_access(hit=False)

        try:
            start_time = time.time()

            if self._llm_rewriter:
                rewrite_result = self._llm_rewriter.rewrite(query)
                rewritten_query = rewrite_result["rewritten"]
                inferred_category = rewrite_result.get("category")
                if inferred_category and not category:
                    category = inferred_category
                multi_queries = self._llm_rewriter.generate_multi_queries(
                    query, rewritten_query, num_variants=2
                )
            elif self._query_rewriter:
                rewritten_query = self._query_rewriter.rewrite(query)
                multi_queries = self._query_rewriter.generate_multi_queries(query, num_variants=2)
            else:
                rewritten_query = query
                multi_queries = [query]

            where_filter = {}
            if category:
                where_filter["category"] = category
            if where:
                where_filter.update(where)

            if self._use_hybrid:
                formatted_results = self._hybrid_search(
                    rewritten_query, multi_queries, top_k, where_filter
                )
            else:
                formatted_results = self._vector_search(
                    rewritten_query, multi_queries, top_k, where_filter
                )

            if min_similarity is not None:
                formatted_results = self._filter_by_similarity(formatted_results, min_similarity)

            if tags:
                formatted_results = self._filter_by_tags(formatted_results, tags)

            final_results = formatted_results[:top_k]

            if self._cache and final_results:
                self._cache.put(query, final_results, top_k, category, min_similarity)

            latency = time.time() - start_time
            self._monitor.record_search(
                latency=latency,
                result_count=len(final_results),
                success=True
            )

            return final_results

        except RuntimeError as e:
            logger.error(f"知识检索失败（嵌入模型不可用）: {e}")
            self._monitor.record_search(latency=0, result_count=0, success=False)
            return []
        except Exception as e:
            logger.error(f"知识检索失败: {e}")
            self._monitor.record_search(latency=0, result_count=0, success=False)
            return []

    def _hybrid_search(
        self,
        rewritten_query: str,
        multi_queries: List[str],
        top_k: int,
        where_filter: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        all_results = []
        seen_contents = set()

        queries_to_search = list(set([rewritten_query] + multi_queries))

        for q in queries_to_search:
            try:
                partial = self.vector_db.hybrid_search(
                    query_text=q,
                    n_results=top_k * 2,
                    where=where_filter if where_filter else None,
                )
                for r in partial:
                    content_key = r.get("content", "")[:100]
                    if content_key not in seen_contents:
                        seen_contents.add(content_key)
                        all_results.append(r)
            except Exception as e:
                logger.warning(f"混合检索子查询失败: {e}")

        all_results.sort(key=lambda x: x.get("distance", 1.0))
        return all_results

    def _vector_search(
        self,
        rewritten_query: str,
        multi_queries: List[str],
        top_k: int,
        where_filter: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        if len(multi_queries) > 1:
            all_results = []
            seen_contents = set()

            for q in multi_queries:
                partial = self.vector_db.query(
                    query_texts=[q],
                    n_results=top_k,
                    where=where_filter if where_filter else None
                )
                formatted = self._format_results(partial)
                for r in formatted:
                    content_key = r.get("content", "")[:100]
                    if content_key not in seen_contents:
                        seen_contents.add(content_key)
                        all_results.append(r)

            all_results.sort(key=lambda x: x.get("distance", 1.0))
            return all_results
        else:
            results = self.vector_db.query(
                query_texts=[rewritten_query],
                n_results=top_k * self.overretrieval_factor,
                where=where_filter if where_filter else None
            )
            return self._format_results(results)

    def search_by_category(self, query: str, category: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.search(query=query, top_k=top_k, category=category)

    def search_for_symptom_analysis(self, symptoms: List[str], pet_species: str, pet_age: Optional[int] = None) -> List[Dict[str, Any]]:
        symptom_text = ", ".join(symptoms)
        query_text = f"{pet_species} 症状: {symptom_text}"
        if pet_age:
            query_text += f" 年龄: {pet_age}个月"
        return self.search(query=query_text, top_k=5, category="disease")

    def search_for_nutrition_advice(self, species: str, breed: Optional[str] = None, age_months: Optional[int] = None, health_condition: Optional[str] = None, weight: Optional[float] = None) -> List[Dict[str, Any]]:
        query_parts = [f"{species} {breed or ''} 营养建议"]
        if age_months is not None:
            query_parts.append(f"年龄: {age_months}个月")
        if health_condition:
            query_parts.append(f"健康状况: {health_condition}")
        if weight:
            query_parts.append(f"体重: {weight}kg")
        query_text = " ".join(query_parts)
        return self.search(query=query_text, top_k=3, category="nutrition")

    def search_for_conversation_context(self, query: str, conversation_id: Optional[str] = None, n_results: int = 3) -> List[Dict[str, Any]]:
        where_filter = None
        if conversation_id:
            where_filter = {"conversation_id": conversation_id}
        return self.search(query=query, top_k=n_results, where=where_filter)

    def search_for_knowledge_enhancement(self, topic: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.search(query=topic, top_k=top_k)

    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        formatted = []
        if not results or 'documents' not in results:
            return formatted
        if not results['documents'] or len(results['documents']) == 0:
            return formatted
        for i in range(len(results['documents'][0])):
            doc = {
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'] else {},
                "distance": results['distances'][0][i] if 'distances' in results and results['distances'] else None
            }
            formatted.append(doc)
        return formatted

    def _filter_by_similarity(self, results: List[Dict[str, Any]], min_similarity: float) -> List[Dict[str, Any]]:
        max_distance = 1.0 - min_similarity
        return [
            r for r in results
            if r.get("distance") is None or r["distance"] <= max_distance
        ]

    def _filter_by_tags(self, results: List[Dict[str, Any]], tags: List[str]) -> List[Dict[str, Any]]:
        if not tags:
            return results
        filtered = []
        for result in results:
            result_tags = result.get("metadata", {}).get("tags", [])
            if isinstance(result_tags, list) and any(tag in result_tags for tag in tags):
                filtered.append(result)
        return filtered

    def search_with_quality(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        enable_self_rag: bool = True,
        enable_crag: bool = True,
    ) -> Dict[str, Any]:
        """增强检索 + Self-RAG评估 + CRAG纠正流水线

        Returns:
            {
                "results": 最终检索结果列表,
                "raw_results": 原始检索结果,
                "retrieval_eval": Self-RAG检索评估,
                "crag_decision": CRAG纠正决策,
                "confidence": 综合置信度,
                "action": accept/supplement/web_search/refuse,
                "web_results": Web补充结果（如触发）,
            }
        """
        results = self.search(query=query, top_k=top_k * 2, category=category)

        retrieval_eval = None
        if enable_self_rag and results:
            try:
                from src.core.self_rag import get_self_rag
                self_rag = get_self_rag()
                if self_rag.is_available:
                    retrieval_eval = self_rag.evaluate_retrieval(query, results)
            except Exception as e:
                logger.warning(f"Self-RAG评估跳过: {e}")

        crag_decision = {"action": "accept", "confidence": 0.7}
        if enable_crag:
            try:
                from src.core.corrective_rag import get_corrective_rag
                crag = get_corrective_rag()
                crag_decision = crag.evaluate_and_correct(
                    query=query,
                    retrieval_results=results,
                    retrieval_eval=retrieval_eval,
                )
            except Exception as e:
                logger.warning(f"CRAG决策跳过: {e}")

        final_results = results[:top_k]

        if crag_decision.get("action") == "web_search":
            web_results = crag_decision.get("web_results", [])
            if web_results:
                final_results = self._merge_web_results(final_results, web_results)[:top_k]

        if crag_decision.get("action") == "refuse":
            final_results = []

        return {
            "results": final_results,
            "raw_results": results,
            "retrieval_eval": retrieval_eval,
            "crag_decision": crag_decision,
            "confidence": crag_decision.get("confidence", 0.5),
            "action": crag_decision.get("action", "accept"),
            "web_results": crag_decision.get("web_results", []),
        }

    def _merge_web_results(
        self, kb_results: List[Dict[str, Any]], web_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """合并知识库结果和Web搜索结果"""
        merged = list(kb_results)
        seen = set()
        for r in merged:
            content_key = r.get("content", "")[:100]
            seen.add(content_key)

        for wr in web_results:
            content_key = wr.get("content", "")[:100]
            if content_key not in seen:
                seen.add(content_key)
                merged.append(wr)
        return merged


_retriever_instance: Optional[KnowledgeRetriever] = None


def get_knowledge_retriever() -> KnowledgeRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeRetriever()
    return _retriever_instance
