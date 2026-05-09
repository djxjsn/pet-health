"""
商品搜索引擎

提供基于关键词、分类、价格的商品搜索功能。
"""
from typing import List, Dict, Any, Optional
import logging

from src.repositories.mongo_repositories import ProductRepository

logger = logging.getLogger(__name__)


class ProductSearcher:
    """商品搜索引擎"""
    
    def __init__(self):
        self.default_limit = 20
    
    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """执行商品搜索
        
        Args:
            query: 搜索关键词
            category: 商品分类
            price_min: 最低价格
            price_max: 最高价格
            limit: 返回数量
        
        Returns:
            搜索结果字典，包含products列表和统计信息
        """
        try:
            products = ProductRepository.search(
                query=query,
                category=category,
                price_min=price_min,
                price_max=price_max,
                limit=limit
            )
            
            total = ProductRepository.count(category=category)
            
            return {
                "products": products,
                "total": total,
                "returned": len(products),
                "query": {
                    "keyword": query,
                    "category": category,
                    "price_range": {"min": price_min, "max": price_max}
                }
            }
        except Exception as e:
            logger.error(f"商品搜索失败: {e}")
            return {"products": [], "total": 0, "error": str(e)}
    
    def search_by_category(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        """按分类搜索商品"""
        return ProductRepository.list_by_category(category=category, limit=limit)
    
    def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """获取商品详情"""
        return ProductRepository.get_by_id(product_id)
    
    def get_similar_products(self, product_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取相似商品（同分类、价格相近）"""
        product = ProductRepository.get_by_id(product_id)
        if not product:
            return []
        
        category = product.get("category")
        price = product.get("price", 0)
        
        # 价格范围：±30%
        price_min = price * 0.7 if price > 0 else None
        price_max = price * 1.3 if price > 0 else None
        
        similar_products = ProductRepository.search(
            category=category,
            price_min=price_min,
            price_max=price_max,
            limit=limit + 1  # +1 排除自身
        )
        
        # 排除当前商品
        return [p for p in similar_products if p.get("product_id") != product_id][:limit]


def get_product_searcher() -> ProductSearcher:
    """获取商品搜索引擎实例"""
    return ProductSearcher()
