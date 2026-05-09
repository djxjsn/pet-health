"""
商品推荐引擎

提供基于规则、知识库和用户行为的个性化推荐功能。
"""
from typing import List, Dict, Any, Optional
import logging
import random

from src.repositories.mongo_repositories import (
    ProductRepository,
    ShoppingHistoryRepository
)
from src.core.knowledge_retriever import KnowledgeRetriever

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """商品推荐引擎"""
    
    def __init__(self):
        self.product_searcher = None
        self.knowledge_retriever = KnowledgeRetriever(default_top_k=5)
    
    def get_recommendations(
        self,
        user_id: str,
        pet_type: str = "dog",
        pet_age_group: str = "adult",
        health_conditions: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """获取个性化推荐
        
        Args:
            user_id: 用户ID
            pet_type: 宠物类型（dog/cat）
            pet_age_group: 年龄阶段（puppy/adult/senior）
            health_conditions: 健康问题列表
            limit: 推荐数量
        
        Returns:
            推荐结果字典，包含不同类型的推荐列表
        """
        recommendations = {
            "personalized": [],
            "knowledge_based": [],
            "popular": [],
            "health_focused": []
        }
        
        # 1. 基于用户历史的个性化推荐
        recommendations["personalized"] = self._get_personalized_recommendations(
            user_id=user_id,
            limit=limit // 2
        )
        
        # 2. 基于知识的推荐（使用RAG）
        if health_conditions:
            recommendations["health_focused"] = self._get_health_focused_recommendations(
                conditions=health_conditions,
                pet_type=pet_type,
                age_group=pet_age_group,
                limit=limit // 3
            )
        
        # 3. 热门/高评分商品
        recommendations["popular"] = self._get_popular_products(
            category=None,
            limit=limit // 4
        )
        
        # 4. 合并去重
        all_recommendations = self._merge_and_deduplicate(recommendations, limit)
        
        return {
            "recommendations": all_recommendations,
            "sources": {
                "personalized_count": len(recommendations["personalized"]),
                "knowledge_based_count": len(recommendations["knowledge_based"]),
                "popular_count": len(recommendations["popular"]),
                "health_focused_count": len(recommendations["health_focused"])
            }
        }
    
    def _get_personalized_recommendations(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """基于用户历史行为的个性化推荐"""
        try:
            history = ShoppingHistoryRepository.list_by_user(user_id, limit=50)
            
            if not history:
                return self._get_popular_products(limit=limit)
            
            # 提取用户浏览过的分类和标签
            viewed_categories = set()
            for item in history:
                product = ProductRepository.get_by_id(item.get("product_id", ""))
                if product:
                    if product.get("category"):
                        viewed_categories.add(product.get("category"))
            
            # 推荐同分类的其他商品
            recommended = []
            for category in list(viewed_categories)[:3]:  # 最多取3个分类
                products = ProductRepository.search(
                    category=category,
                    limit=2
                )
                recommended.extend(products)
            
            return recommended[:limit]
            
        except Exception as e:
            logger.error(f"获取个性化推荐失败: {e}")
            return self._get_popular_products(limit=limit)
    
    def _get_health_focused_recommendations(
        self,
        conditions: List[str],
        pet_type: str,
        age_group: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """基于健康问题的推荐"""
        try:
            # 使用RAG检索相关知识
            query = f"{pet_type} {age_group} {' '.join(conditions[:2])} 推荐"
            
            knowledge_results = self.knowledge_retriever.search(
                query=query,
                category="nutrition" if any(c in ["营养", "饮食", "肥胖"] for c in conditions) else "medication",
                top_k=3
            )
            
            # 根据知识结果推荐相关商品
            recommended = []
            
            # 如果有皮肤问题，推荐洗护用品
            if any(c in ["皮肤病", "过敏", "掉毛"] for c in conditions):
                hygiene_products = ProductRepository.search(
                    category="hygiene",
                    limit=2
                )
                recommended.extend(hygiene_products)
            
            # 如果有消化问题，推荐特殊食品
            if any(c in ["肠胃", "腹泻", "呕吐", "食欲不振"] for c in conditions):
                food_products = ProductRepository.search(
                    category="food",
                    limit=2
                )
                recommended.extend(food_products)
            
            return recommended[:limit]
            
        except Exception as e:
            logger.error(f"获取健康导向推荐失败: {e}")
            return []
    
    def _get_popular_products(
        self,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """获取热门/高评分商品"""
        try:
            return ProductRepository.search(
                category=category,
                sort_by="rating",
                sort_order=-1,
                limit=limit
            )
        except Exception as e:
            logger.error(f"获取热门商品失败: {e}")
            return []
    
    def _merge_and_deduplicate(
        self,
        recommendations: Dict[str, List],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """合并并去重推荐结果"""
        seen_ids = set()
        merged = []
        
        for source_list in [
            recommendations.get("personalized", []),
            recommendations.get("health_focused", []),
            recommendations.get("popular", []),
            recommendations.get("knowledge_based", [])
        ]:
            for item in source_list:
                product_id = item.get("product_id")
                if product_id and product_id not in seen_ids:
                    seen_ids.add(product_id)
                    merged.append(item)
                    
                    if len(merged) >= limit:
                        break
            
            if len(merged) >= limit:
                break
        
        return merged


def get_recommendation_engine() -> RecommendationEngine:
    """获取推荐引擎实例"""
    return RecommendationEngine()
