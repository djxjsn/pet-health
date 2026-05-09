"""
购物助手服务层

提供商品管理、购物历史、成分分析的业务逻辑处理。
"""
import uuid
from typing import List, Optional, Dict, Any

from src.repositories.mongo_repositories import (
    ProductRepository,
    ShoppingHistoryRepository,
    IngredientAnalysisRepository
)


class ShoppingService:
    """购物助手服务"""
    
    @staticmethod
    def create_product(
        name: str,
        category: str,
        price: float,
        brand: Optional[str] = None,
        subcategory: Optional[str] = None,
        image_url: Optional[str] = None,
        description: Optional[str] = None,
        ingredients: Optional[List[Dict[str, Any]]] = None,
        nutrition_info: Optional[Dict[str, Any]] = None,
        suitable_for: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """创建商品
        
        Args:
            name: 商品名称
            category: 商品分类（food/toy/accessory/medicine/hygiene/clothing）
            price: 价格
        
        Returns:
            商品唯一标识
        """
        valid_categories = ["food", "toy", "accessory", "medicine", "hygiene", "clothing"]
        if category not in valid_categories:
            raise ValueError(f"无效的商品分类: {category}，必须是 {valid_categories} 之一")
        
        product_id = f"product_{category}_{uuid.uuid4().hex[:8]}"
        
        data = {
            "product_id": product_id,
            "name": name,
            "brand": brand,
            "category": category,
            "subcategory": subcategory,
            "price": price,
            "image_url": image_url,
            "description": description,
            "ingredients": ingredients or [],
            "nutrition_info": nutrition_info or {},
            "suitable_for": suitable_for or [],
            "tags": tags or [],
            "rating": 0.0,
            "review_count": 0,
            "stock_status": "in_stock"
        }
        
        ProductRepository.create(data)
        return product_id
    
    @staticmethod
    def search_products(
        query: Optional[str] = None,
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """搜索商品"""
        return ProductRepository.search(
            query=query,
            category=category,
            price_min=price_min,
            price_max=price_max,
            skip=skip,
            limit=limit
        )
    
    @staticmethod
    def get_product(product_id: str) -> Optional[Dict[str, Any]]:
        """获取商品详情"""
        return ProductRepository.get_by_id(product_id)
    
    @staticmethod
    def record_shopping_action(
        user_id: str,
        product_id: str,
        action_type: str,
        pet_id: Optional[str] = None,
        search_query: Optional[str] = None,
        recommendation_source: Optional[str] = None
    ) -> str:
        """记录用户购物行为
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            action_type: 操作类型（search/view/cart/purchase/wishlist）
        
        Returns:
            历史记录ID
        """
        history_id = f"history_{uuid.uuid4().hex[:8]}"
        
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品不存在: {product_id}")
        
        data = {
            "history_id": history_id,
            "user_id": user_id,
            "pet_id": pet_id,
            "product_id": product_id,
            "action_type": action_type,
            "search_query": search_query,
            "price_at_time": product.get("price"),
            "quantity": 1,
            "recommendation_source": recommendation_source
        }
        
        ShoppingHistoryRepository.create(data)
        return history_id
    
    @staticmethod
    def get_user_preferences(user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        return ShoppingHistoryRepository.get_user_preferences(user_id)
    
    @staticmethod
    def save_ingredient_analysis(analysis_data: Dict[str, Any]) -> str:
        """保存成分分析结果"""
        analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
        analysis_data["analysis_id"] = analysis_id
        
        IngredientAnalysisRepository.create(analysis_data)
        return analysis_id
    
    @staticmethod
    def get_product_stats() -> Dict[str, Any]:
        """获取商品统计信息"""
        return {
            "total_products": ProductRepository.count(),
            "by_category": {
                "food": ProductRepository.count(category="food"),
                "toy": ProductRepository.count(category="toy"),
                "accessory": ProductRepository.count(category="accessory"),
                "medicine": ProductRepository.count(category="medicine"),
                "hygiene": ProductRepository.count(category="hygiene"),
                "clothing": ProductRepository.count(category="clothing")
            }
        }


def get_shopping_service() -> ShoppingService:
    """获取购物助手服务实例"""
    return ShoppingService()
