"""
购物助手API路由

提供商品搜索、成分分析、个性化推荐等接口。
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
import logging

from src.api.schemas.shopping import (
    ProductCreate,
    ProductResponse,
    ProductSearchRequest,
    ProductSearchResponse,
    IngredientAnalysisRequest,
    IngredientAnalysisResponse,
    IngredientInfo,
    AllergenWarning,
    RecommendationRequest,
    RecommendationResponse,
    ShoppingActionRequest
)
from src.services.shopping_service import ShoppingService
from src.core.product_searcher import ProductSearcher
from src.core.recommendation_engine import RecommendationEngine
from src.core.ingredient_analyzer import IngredientAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/shopping", tags=["购物助手"])


@router.post("/search", response_model=ProductSearchResponse, summary="搜索商品")
async def search_products(request: ProductSearchRequest):
    """
    搜索宠物用品商品
    
    - **query**: 搜索关键词（模糊匹配名称、品牌、描述）
    - **category**: 商品分类（food/toy/accessory/medicine/hygiene/clothing）
    - **price_min/price_max**: 价格范围
    - **limit**: 返回数量（1-50）
    """
    try:
        searcher = ProductSearcher()
        result = searcher.search(
            query=request.query,
            category=request.category,
            price_min=request.price_min,
            price_max=request.price_max,
            limit=request.limit
        )
        
        products = [
            ProductResponse(**p) if p else None 
            for p in result.get("products", [])
        ]
        products = [p for p in products if p is not None]
        
        return ProductSearchResponse(
            products=products,
            total=result.get("total", 0),
            returned=len(products),
            query=result.get("query", {})
        )
    except Exception as e:
        logger.error(f"商品搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"商品搜索失败: {str(e)}")


@router.get("/products/{product_id}", response_model=ProductResponse, summary="获取商品详情")
async def get_product(product_id: str):
    """获取单个商品详细信息"""
    try:
        service = ShoppingService()
        product = service.get_product(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")
        
        return ProductResponse(**product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取商品失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取商品失败: {str(e)}")


@router.post("/products", response_model=ProductResponse, summary="创建商品")
async def create_product(product: ProductCreate):
    """创建新的商品（管理员功能）"""
    try:
        service = ShoppingService()
        product_id = service.create_product(
            name=product.name,
            category=product.category,
            price=product.price,
            brand=product.brand,
            subcategory=product.subcategory,
            image_url=product.image_url,
            description=product.description,
            ingredients=product.ingredients,
            nutrition_info=product.nutrition_info,
            suitable_for=product.suitable_for,
            tags=product.tags
        )
        
        created_product = service.get_product(product_id)
        return ProductResponse(**created_product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建商品失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建商品失败: {str(e)}")


@router.post("/analyze", response_model=IngredientAnalysisResponse, summary="分析成分安全性")
async def analyze_ingredients(request: IngredientAnalysisRequest):
    """
    分析宠物食品/用品成分的安全性
    
    - **ingredients_text**: 成分文本（从包装上复制）
    - **pet_type**: 宠物类型（dog/cat）
    - **breed**: 品种（可选）
    - **age_group**: 年龄阶段（puppy/adult/senior，可选）
    - **health_conditions**: 健康问题列表（可选）
    
    返回：
    - 安全性评分和等级
    - 安全成分列表
    - 需注意成分列表
    - 不安全成分列表
    - 过敏原警告
    - 个性化建议
    """
    try:
        analyzer = IngredientAnalyzer()
        result = analyzer.analyze(
            ingredients_text=request.ingredients_text,
            pet_type=request.pet_type,
            breed=request.breed,
            age_group=request.age_group,
            health_conditions=request.health_conditions or []
        )
        
        safe_ingredients = [IngredientInfo(**ing) for ing in result.get("safe_ingredients", [])]
        caution_ingredients = [IngredientInfo(**ing) for ing in result.get("caution_ingredients", [])]
        unsafe_ingredients = [IngredientInfo(**ing) for ing in result.get("unsafe_ingredients", [])]
        allergen_warnings = [AllergenWarning(**w) for w in result.get("allergen_warnings", [])]
        
        return IngredientAnalysisResponse(
            overall_safety=result["overall_safety"],
            safety_score=result["safety_score"],
            safe_ingredients=safe_ingredients,
            caution_ingredients=caution_ingredients,
            unsafe_ingredients=unsafe_ingredients,
            allergen_warnings=allergen_warnings,
            recommendations=result.get("recommendations", []),
            total_analyzed=result.get("total_analyzed", 0),
            parsed_ingredients=result.get("parsed_ingredients")
        )
    except Exception as e:
        logger.error(f"成分分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"成分分析失败: {str(e)}")


@router.post("/recommendations", response_model=RecommendationResponse, summary="获取个性化推荐")
async def get_recommendations(request: RecommendationRequest):
    """
    获取个性化商品推荐
    
    - **user_id**: 用户ID
    - **pet_type**: 宠物类型（dog/cat）
    - **pet_age_group**: 年龄阶段（puppy/adult/senior）
    - **health_conditions**: 健康问题列表（用于健康导向推荐）
    - **limit**: 推荐数量（1-20）
    
    推荐来源：
    - personalized: 基于用户历史行为
    - knowledge_based: 基于RAG知识检索
    - popular: 热门/高评分商品
    - health_focused: 基于健康问题的推荐
    """
    try:
        engine = RecommendationEngine()
        result = engine.get_recommendations(
            user_id=request.user_id,
            pet_type=request.pet_type,
            pet_age_group=request.pet_age_group,
            health_conditions=request.health_conditions,
            limit=request.limit
        )
        
        products = [
            ProductResponse(**p) if p else None 
            for p in result.get("recommendations", [])
        ]
        products = [p for p in products if p is not None]
        
        return RecommendationResponse(
            recommendations=products[:request.limit],
            sources=result.get("sources", {})
        )
    except Exception as e:
        logger.error(f"获取推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取推荐失败: {str(e)}")


@router.post("/action", summary="记录购物行为")
async def record_action(user_id: str, action: ShoppingActionRequest):
    """记录用户购物行为（浏览、加购、购买、收藏）"""
    try:
        service = ShoppingService()
        history_id = service.record_shopping_action(
            user_id=user_id,
            product_id=action.product_id,
            action_type=action.action_type,
            pet_id=action.pet_id,
            search_query=action.search_query
        )
        
        return {
            "message": "行为记录成功",
            "history_id": history_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"记录行为失败: {e}")
        raise HTTPException(status_code=500, detail=f"记录行为失败: {str(e)}")


@router.get("/compare", summary="对比多个商品")
async def compare_products(product_ids: str = Query(..., description="逗号分隔的商品ID列表（2-5个）")):
    """对比多个商品的详细信息"""
    try:
        id_list = [pid.strip() for pid in product_ids.split(",")]
        
        if len(id_list) < 2 or len(id_list) > 5:
            raise HTTPException(status_code=400, detail="请提供2-5个商品ID进行对比")
        
        service = ShoppingService()
        products = []
        
        for pid in id_list:
            product = service.get_product(pid)
            if product:
                products.append(ProductResponse(**product))
        
        if not products:
            raise HTTPException(status_code=404, detail="未找到任何有效商品")
        
        return {
            "total": len(products),
            "products": products
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"商品对比失败: {e}")
        raise HTTPException(status_code=500, detail=f"商品对比失败: {str(e)}")


@router.get("/categories", summary="获取商品分类统计")
async def get_categories():
    """获取各分类的商品数量统计"""
    try:
        service = ShoppingService()
        stats = service.get_product_stats()
        return stats
    except Exception as e:
        logger.error(f"获取分类统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分类统计失败: {str(e)}")


@router.get("/similar/{product_id}", summary="获取相似商品")
async def get_similar_products(product_id: str, limit: int = Query(5, ge=1, le=10)):
    """获取与指定商品相似的其他商品"""
    try:
        searcher = ProductSearcher()
        similar = searcher.get_similar_products(product_id, limit=limit)
        
        products = [ProductResponse(**p) for p in similar]
        
        return {
            "reference_product_id": product_id,
            "similar_count": len(products),
            "products": products
        }
    except Exception as e:
        logger.error(f"获取相似商品失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取相似商品失败: {str(e)}")
