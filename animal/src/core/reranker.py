"""
Re-ranking模块

对初检结果进行精排，提升检索结果的相关性排序质量。
支持基于Cross-Encoder的精排和基于规则的重排序。
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class RuleBasedReranker:
    """基于规则的重排序器"""
    
    def __init__(self):
        self.category_boost = {
            "disease": 1.2,
            "first_aid": 1.3,
            "medication": 1.1,
            "nutrition": 1.0,
            "behavior": 0.9
        }
        self.recency_weight = 0.1
        self.exact_match_bonus = 0.5
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """基于规则重排序
        
        Args:
            query: 原始查询
            results: 初检结果
            top_k: 返回结果数量
            
        Returns:
            重排序后的结果
        """
        if not results:
            return []
        
        scored_results = []
        query_terms = set(query.lower().split())
        
        for result in results:
            score = 1.0
            
            distance = result.get("distance")
            if distance is not None:
                similarity = 1 - distance
                score *= (0.5 + similarity * 0.5)
            
            metadata = result.get("metadata", {})
            category = metadata.get("category", "")
            if category in self.category_boost:
                score *= self.category_boost[category]
            
            content = result.get("content", "").lower()
            exact_matches = sum(1 for term in query_terms if term in content)
            if query_terms:
                match_ratio = exact_matches / len(query_terms)
                score += self.exact_match_bonus * match_ratio
            
            result_copy = dict(result)
            result_copy["rerank_score"] = score
            scored_results.append(result_copy)
        
        scored_results.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_results[:top_k]


class CrossEncoderReranker:
    """基于Cross-Encoder的重排序器
    
    使用sentence-transformers的Cross-Encoder模型进行精排。
    需要额外安装: pip install sentence-transformers
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        self.model_name = model_name
        self._model = None
        self._available = False
        self._init_model()
    
    def _init_model(self):
        """初始化Cross-Encoder模型"""
        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
            self._available = True
            logger.info(f"Cross-Encoder模型加载成功: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers未安装，Cross-Encoder重排序不可用")
        except Exception as e:
            logger.warning(f"Cross-Encoder模型加载失败: {e}")
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Cross-Encoder精排
        
        Args:
            query: 原始查询
            results: 初检结果
            top_k: 返回结果数量
            
        Returns:
            重排序后的结果
        """
        if not self._available or not results:
            return results[:top_k]
        
        try:
            pairs = [(query, r.get("content", "")) for r in results]
            scores = self._model.predict(pairs)
            
            scored_results = []
            for i, result in enumerate(results):
                result_copy = dict(result)
                result_copy["rerank_score"] = float(scores[i])
                scored_results.append(result_copy)
            
            scored_results.sort(key=lambda x: x["rerank_score"], reverse=True)
            return scored_results[:top_k]
            
        except Exception as e:
            logger.error(f"Cross-Encoder重排序失败: {e}")
            return results[:top_k]


class CompositeReranker:
    """组合重排序器
    
    先用规则重排序快速过滤，再用Cross-Encoder精排（如果可用）
    """
    
    def __init__(self, use_cross_encoder: bool = True):
        self.rule_reranker = RuleBasedReranker()
        self.cross_encoder = CrossEncoderReranker() if use_cross_encoder else None
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """组合重排序
        
        Args:
            query: 原始查询
            results: 初检结果
            top_k: 返回结果数量
            
        Returns:
            重排序后的结果
        """
        if not results:
            return []
        
        rule_results = self.rule_reranker.rerank(
            query=query,
            results=results,
            top_k=min(top_k * 3, len(results))
        )
        
        if self.cross_encoder and self.cross_encoder.is_available:
            return self.cross_encoder.rerank(
                query=query,
                results=rule_results,
                top_k=top_k
            )
        
        return rule_results[:top_k]


def get_reranker(use_cross_encoder: bool = True) -> CompositeReranker:
    """获取重排序器实例"""
    return CompositeReranker(use_cross_encoder=use_cross_encoder)
