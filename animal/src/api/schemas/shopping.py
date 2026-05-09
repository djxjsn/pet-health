"""
购物助手相关的Pydantic Schema定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """创建商品请求"""
    name: str = Field(..., max_length=200, description="商品名称")
    category: str = Field(..., description="商品分类: food/toy/accessory/medicine/hygiene/clothing")
    price: float = Field(..., ge=0, description="价格")
    brand: Optional[str] = Field(None, max_length=100, description="品牌名称")
    subcategory: Optional[str] = Field(None, description="子分类")
    image_url: Optional[str] = Field(None, description="商品图片URL")
    description: Optional[str] = Field(None, description="商品描述")
    ingredients: Optional[List[Dict[str, Any]]] = Field(default=None, description="成分列表")
    nutrition_info: Optional[Dict[str, Any]] = Field(default=None, description="营养信息")
    suitable_for: Optional[List[str]] = Field(default=None, description="适用对象")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")


class ProductResponse(BaseModel):
    """商品响应"""
    _id: str
    product_id: str
    name: str
    brand: Optional[str]
    category: str
    subcategory: Optional[str]
    price: float
    currency: str
    image_url: Optional[str]
    description: Optional[str]
    ingredients: Optional[List[Dict[str, Any]]]
    nutrition_info: Optional[Dict[str, Any]]
    suitable_for: Optional[List[str]]
    tags: Optional[List[str]]
    rating: float
    review_count: int
    stock_status: str
    created_at: str
    updated_at: str


class ProductSearchRequest(BaseModel):
    """商品搜索请求"""
    query: Optional[str] = Field(None, max_length=200, description="搜索关键词")
    category: Optional[str] = Field(None, description="商品分类过滤")
    price_min: Optional[float] = Field(None, ge=0, description="最低价格")
    price_max: Optional[float] = Field(None, ge=0, description="最高价格")
    limit: int = Field(default=20, ge=1, le=50, description="返回数量")


class ProductSearchResponse(BaseModel):
    """商品搜索响应"""
    products: List[ProductResponse]
    total: int
    returned: int
    query: Dict[str, Any]


class IngredientAnalysisRequest(BaseModel):
    """成分分析请求"""
    ingredients_text: str = Field(..., min_length=1, description="成分文本")
    pet_type: str = Field(..., description="宠物类型: dog/cat")
    breed: Optional[str] = Field(None, description="品种")
    age_group: Optional[str] = Field(None, description="年龄阶段: puppy/adult/senior")
    health_conditions: Optional[List[str]] = Field(default=None, description="健康问题列表")


class IngredientInfo(BaseModel):
    """成分信息"""
    name: str
    reason: Optional[str] = None
    benefit: Optional[str] = None
    severity: Optional[str] = None


class AllergenWarning(BaseModel):
    """过敏原警告"""
    category: str
    allergen: str
    found_in: str
    risk_level: str


class IngredientAnalysisResponse(BaseModel):
    """成分分析响应"""
    analysis_id: Optional[str] = None
    overall_safety: str
    safety_score: float
    safe_ingredients: List[IngredientInfo]
    caution_ingredients: List[IngredientInfo]
    unsafe_ingredients: List[IngredientInfo]
    allergen_warnings: List[AllergenWarning]
    recommendations: List[str]
    total_analyzed: int
    parsed_ingredients: Optional[List[str]] = None


class RecommendationRequest(BaseModel):
    """推荐请求"""
    user_id: str = Field(..., description="用户ID")
    pet_type: str = Field(default="dog", description="宠物类型: dog/cat")
    pet_age_group: str = Field(default="adult", description="年龄阶段: puppy/adult/senior")
    health_conditions: Optional[List[str]] = Field(default=None, description="健康问题列表")
    limit: int = Field(default=10, ge=1, le=20, description="推荐数量")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    recommendations: List[ProductResponse]
    sources: Dict[str, int]


class ShoppingActionRequest(BaseModel):
    """记录购物行为请求"""
    product_id: str = Field(..., description="商品ID")
    action_type: str = Field(..., description="操作类型: search/view/cart/purchase/wishlist")
    pet_id: Optional[str] = Field(None, description="宠物ID")
    search_query: Optional[str] = Field(None, description="搜索关键词")


class ProductCompareRequest(BaseModel):
    """商品对比请求"""
    product_ids: List[str] = Field(..., min_length=2, max_length=5, description="要对比的商品ID列表（2-5个）")
