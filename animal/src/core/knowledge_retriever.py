"""
知识检索器（统一检索入口）

提供基于向量语义的知识检索功能，支持分类过滤、标签过滤、
对话上下文检索、症状分析检索等多种检索场景。
所有RAG检索必须通过本模块进行，禁止直接调用VectorDatabase。
"""
from typing import List, Dict, Any, Optional
import logging

from src.core.vector_db import get_vector_db, VectorDatabase
from src.core.config import get_settings
from src.core.query_rewriter import get_query_rewriter
from src.core.search_cache import get_search_cache
from src.core.rag_monitor import get_rag_monitor

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """知识检索器 - 统一检索入口"""
    
    def __init__(self, default_top_k: Optional[int] = None, enable_query_rewrite: bool = True, enable_cache: bool = True):
        """初始化知识检索器
        
        Args:
            default_top_k: 默认返回结果数量，None则从配置读取
            enable_query_rewrite: 是否启用查询改写
            enable_cache: 是否启用检索缓存
        """
        settings = get_settings()
        self.vector_db: VectorDatabase = get_vector_db()
        self.default_top_k = default_top_k or settings.SEARCH_TOP_K
        self.default_similarity_threshold = settings.SIMILARITY_THRESHOLD
        self.overretrieval_factor = settings.SEARCH_OVERRETRIEVAL_FACTOR
        self.enable_query_rewrite = enable_query_rewrite
        self.enable_cache = enable_cache
        self._query_rewriter = get_query_rewriter() if enable_query_rewrite else None
        self._cache = get_search_cache() if enable_cache else None
        self._monitor = get_rag_monitor()
    
    @property
    def is_available(self) -> bool:
        """检查检索功能是否可用"""
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
        """检索相关知识（统一检索入口）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            category: 文档分类过滤
            tags: 标签过滤
            where: 自定义元数据过滤条件
            min_similarity: 最小相似度阈值（0-1，基于cosine距离换算）
        
        Returns:
            检索结果列表，每个结果包含content、metadata、distance
        """
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
        
        where_filter = {}
        if category:
            where_filter["category"] = category
        if where:
            where_filter.update(where)
        
        try:
            start_time = __import__('time').time()
            
            if self._query_rewriter:
                rewritten_query = self._query_rewriter.rewrite(query)
                multi_queries = self._query_rewriter.generate_multi_queries(query, num_variants=2)
            else:
                rewritten_query = query
                multi_queries = [query]
            
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
                formatted_results = all_results
            else:
                results = self.vector_db.query(
                    query_texts=[rewritten_query],
                    n_results=top_k * self.overretrieval_factor,
                    where=where_filter if where_filter else None
                )
                formatted_results = self._format_results(results)
            
            if min_similarity is not None:
                formatted_results = self._filter_by_similarity(formatted_results, min_similarity)
            
            if tags:
                formatted_results = self._filter_by_tags(formatted_results, tags)
            
            final_results = formatted_results[:top_k]
            
            if self._cache and final_results:
                self._cache.put(query, final_results, top_k, category, min_similarity)
            
            latency = __import__('time').time() - start_time
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
    
    def search_by_category(
        self,
        query: str,
        category: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """按分类检索知识
        
        Args:
            query: 查询文本
            category: 文档分类
            top_k: 返回结果数量
        
        Returns:
            检索结果列表
        """
        return self.search(query=query, top_k=top_k, category=category)
    
    def search_for_symptom_analysis(
        self,
        symptoms: List[str],
        pet_species: str,
        pet_age: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """症状分析专用检索
        
        Args:
            symptoms: 症状列表
            pet_species: 宠物物种
            pet_age: 宠物年龄（月）
        
        Returns:
            检索结果列表
        """
        symptom_text = ", ".join(symptoms)
        query_text = f"{pet_species} 症状: {symptom_text}"
        
        if pet_age:
            query_text += f" 年龄: {pet_age}个月"
        
        return self.search(query=query_text, top_k=5, category="disease")
    
    def search_for_nutrition_advice(
        self,
        species: str,
        breed: Optional[str] = None,
        age_months: Optional[int] = None,
        health_condition: Optional[str] = None,
        weight: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """营养建议专用检索
        
        Args:
            species: 宠物物种
            breed: 宠物品种
            age_months: 年龄（月）
            health_condition: 健康状况
            weight: 体重（kg）
        
        Returns:
            检索结果列表
        """
        query_parts = [f"{species} {breed or ''} 营养建议"]
        
        if age_months is not None:
            query_parts.append(f"年龄: {age_months}个月")
        if health_condition:
            query_parts.append(f"健康状况: {health_condition}")
        if weight:
            query_parts.append(f"体重: {weight}kg")
        
        query_text = " ".join(query_parts)
        return self.search(query=query_text, top_k=3, category="nutrition")
    
    def search_for_conversation_context(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """对话上下文检索
        
        Args:
            query: 查询文本
            conversation_id: 对话ID（可选，用于过滤）
            n_results: 返回结果数量
        
        Returns:
            相关上下文列表
        """
        where_filter = None
        if conversation_id:
            where_filter = {"conversation_id": conversation_id}
        
        return self.search(query=query, top_k=n_results, where=where_filter)
    
    def search_for_knowledge_enhancement(
        self,
        topic: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """知识增强检索
        
        Args:
            topic: 查询主题
            top_k: 返回结果数量
        
        Returns:
            检索结果列表
        """
        return self.search(query=topic, top_k=top_k)
    
    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化向量数据库检索结果
        
        Args:
            results: 向量数据库原始结果
        
        Returns:
            格式化后的结果列表
        """
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
    
    def _filter_by_similarity(
        self,
        results: List[Dict[str, Any]],
        min_similarity: float
    ) -> List[Dict[str, Any]]:
        """按相似度阈值过滤结果
        
        Args:
            results: 检索结果
            min_similarity: 最小相似度（0-1），cosine distance = 1 - similarity
        
        Returns:
            过滤后的结果
        """
        max_distance = 1.0 - min_similarity
        return [
            r for r in results
            if r.get("distance") is None or r["distance"] <= max_distance
        ]
    
    def _filter_by_tags(
        self,
        results: List[Dict[str, Any]],
        tags: List[str]
    ) -> List[Dict[str, Any]]:
        """按标签过滤结果
        
        Args:
            results: 检索结果
            tags: 要过滤的标签列表
        
        Returns:
            过滤后的结果
        """
        if not tags:
            return results
        
        filtered = []
        for result in results:
            result_tags = result.get("metadata", {}).get("tags", [])
            if isinstance(result_tags, list) and any(tag in result_tags for tag in tags):
                filtered.append(result)
        
        return filtered


_retriever_instance: Optional[KnowledgeRetriever] = None


def get_knowledge_retriever() -> KnowledgeRetriever:
    """获取知识检索器实例（单例）"""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeRetriever()
    return _retriever_instance
