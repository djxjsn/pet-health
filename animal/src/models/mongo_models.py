"""
MongoDB 文档模型定义

定义所有迁移到 MongoDB 的集合的文档结构。
基于方案 B：MySQL + MongoDB 混合架构实施。
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from pydantic import ConfigDict


# ========== 公共基础模型 ==========

class MongoBaseModel(BaseModel):
    """MongoDB 文档基础模型"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
    )
    
    id: Optional[str] = Field(default=None, alias="_id")


# ========== Conversations 集合 ==========

class ConversationDocument(MongoBaseModel):
    """对话文档模型"""
    conversation_id: str = Field(..., description="对话ID")
    user_id: str = Field(..., description="用户ID（关联MySQL users表）")
    pet_id: Optional[str] = Field(None, description="宠物ID（关联MySQL pets表）")
    title: Optional[str] = Field(None, max_length=100, description="对话标题")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0, description="消息数量")


# ========== Messages 集合 ==========

class MessageDocument(MongoBaseModel):
    """消息文档模型"""
    message_id: str = Field(..., description="消息ID")
    conversation_id: str = Field(..., description="对话ID（关联conversations集合）")
    role: str = Field(..., description="角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ========== Health Records 集合 ==========

class HealthRecordDocument(MongoBaseModel):
    """健康记录文档模型"""
    record_id: str = Field(..., description="记录ID")
    pet_id: str = Field(..., description="宠物ID（关联MySQL pets表）")
    record_type: str = Field(..., description="记录类型: checkup/vaccine/illness/allergy/surgery")
    symptoms: Optional[List[str]] = Field(None, description="症状列表")
    diagnosis: Optional[str] = Field(None, description="诊断结果")
    prescription: Optional[str] = Field(None, description="处方/用药")
    vet_name: Optional[str] = Field(None, description="兽医姓名")
    hospital: Optional[str] = Field(None, description="医院/诊所名称")
    record_date: Optional[date] = Field(None, description="就诊日期")
    next_checkup_date: Optional[date] = Field(None, description="下次检查日期")
    notes: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ========== Consultations 集合 ==========

class ConsultationDocument(MongoBaseModel):
    """AI健康咨询文档模型"""
    consultation_id: str = Field(..., description="咨询ID")
    user_id: str = Field(..., description="用户ID（关联MySQL users表）")
    pet_id: str = Field(..., description="宠物ID（关联MySQL pets表）")
    symptoms: Optional[List[str]] = Field(None, description="症状列表")
    description: Optional[str] = Field(None, description="用户描述")
    image_urls: Optional[List[str]] = Field(None, description="上传图片URL列表")
    diagnosis_result: Optional[Dict[str, Any]] = Field(None, description="AI诊断结果（OPT-H-03结构化）")
    recommendations: Optional[List[str]] = Field(None, description="AI建议列表")
    urgency_level: int = Field(default=1, description="紧急程度(1-5)")
    status: str = Field(default="pending", description="状态: pending/completed/cancelled")
    conversation_id: Optional[str] = Field(None, description="关联对话ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ========== Knowledge Documents 集合 ==========

class KnowledgeDocument(MongoBaseModel):
    """知识文档模型"""
    doc_id: str = Field(..., description="文档唯一标识")
    title: str = Field(..., max_length=200, description="文档标题")
    content: str = Field(..., description="文档内容")
    category: str = Field(..., description="文档分类: disease/medication/first_aid/nutrition/behavior")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    source: Optional[str] = Field(None, description="知识来源")
    status: str = Field(default="draft", description="状态: draft/published/archived")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    indexed: bool = Field(default=False, description="是否已向量化索引")
    indexed_at: Optional[datetime] = Field(None, description="向量化索引时间")


# ========== Shopping Products 集合 ==========

class Product(MongoBaseModel):
    """商品模型"""
    product_id: str = Field(..., description="商品唯一标识")
    name: str = Field(..., max_length=200, description="商品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌名称")
    category: str = Field(..., description="商品分类: food/toy/accessory/medicine/hygiene/clothing/nest")
    subcategory: Optional[str] = Field(None, description="子分类")
    price: float = Field(0.0, ge=0, description="价格")
    original_price: Optional[float] = Field(None, ge=0, description="原价（用于显示折扣）")
    currency: str = Field("CNY", description="货币单位")
    image_url: Optional[str] = Field(None, description="商品图片URL")
    image_urls: List[str] = Field(default_factory=list, description="商品图片URL列表（多图）")
    description: Optional[str] = Field(None, description="商品描述")
    ingredients: Optional[List[Dict[str, Any]]] = Field(default=None, description="成分列表")
    nutrition_info: Optional[Dict[str, Any]] = Field(default=None, description="营养信息")
    suitable_for: Optional[List[str]] = Field(None, description="适用对象（犬种、年龄段等）")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    rating: float = Field(0.0, ge=0, le=5, description="评分")
    review_count: int = Field(0, ge=0, description="评论数")
    sales_count: int = Field(0, ge=0, description="销量")
    stock: int = Field(0, ge=0, description="库存数量")
    stock_status: str = Field("in_stock", description="库存状态: in_stock/out_of_stock/limited")
    merchant_id: Optional[str] = Field(None, description="所属商家ID")
    merchant_name: Optional[str] = Field(None, description="商家名称（冗余存储）")
    is_tcm_product: bool = Field(default=False, description="是否中药产品")
    tcm_properties: Optional[Dict[str, Any]] = Field(None, description="中药属性（性味归经、功效等）")
    specifications: Optional[List[Dict[str, Any]]] = Field(None, description="规格列表")
    source_url: Optional[str] = Field(None, description="来源链接")
    status: str = Field(default="on_sale", description="商品状态: on_sale/off_sale/draft")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ShoppingHistory(MongoBaseModel):
    """购物历史记录模型"""
    history_id: str = Field(..., description="记录ID")
    user_id: str = Field(..., description="用户ID")
    pet_id: Optional[str] = Field(None, description="宠物ID")
    product_id: str = Field(..., description="商品ID")
    action_type: str = Field(..., description="操作类型: search/view/cart/purchase/wishlist")
    search_query: Optional[str] = Field(None, description="搜索关键词")
    price_at_time: Optional[float] = Field(None, description="当时价格")
    quantity: int = Field(1, ge=1, description="数量")
    recommendation_source: Optional[str] = Field(None, description="推荐来源: search/rule_based/knowledge_rag/personalized")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IngredientAnalysis(MongoBaseModel):
    """成分分析结果模型"""
    analysis_id: str = Field(..., description="分析ID")
    user_id: str = Field(..., description="用户ID")
    product_name: str = Field(..., description="商品名称")
    ingredients_text: str = Field(..., description="成分文本")
    pet_type: str = Field(..., description="宠物类型: dog/cat")
    breed: Optional[str] = Field(None, description="品种")
    age_group: Optional[str] = Field(None, description="年龄阶段: puppy/adult/senior")
    health_conditions: Optional[List[str]] = Field(None, description="健康问题列表")
    
    overall_safety: str = Field(..., description="整体安全性: safe/cautionary/unsafe")
    safety_score: float = Field(0.0, ge=0, le=100, description="安全分数")
    
    safe_ingredients: List[Dict[str, Any]] = Field(default=[], description="安全成分")
    caution_ingredients: List[Dict[str, Any]] = Field(default=[], description="需注意成分")
    unsafe_ingredients: List[Dict[str, Any]] = Field(default=[], description="不安全成分")
    allergen_warnings: List[Dict[str, Any]] = Field(default=[], description="过敏原警告")
    
    nutrition_assessment: Optional[Dict[str, Any]] = Field(None, description="营养评估")
    recommendations: List[str] = Field(default=[], description="建议列表")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ========== Behavior Analyses 集合 ==========

class BehaviorAnalysisDocument(MongoBaseModel):
    """行为分析文档模型"""
    analysis_id: str = Field(..., description="分析ID")
    user_id: str = Field(..., description="用户ID（关联MySQL users表）")
    pet_id: str = Field(..., description="宠物ID（关联MySQL pets表）")
    behavior_description: Optional[str] = Field(None, description="行为描述")
    behavior_category: Optional[str] = Field(None, description="行为类别")
    possible_causes: Optional[List[Dict[str, Any]]] = Field(None, description="可能原因列表（OPT-B-03结构化）")
    breed_analysis: Optional[Dict[str, Any]] = Field(None, description="品种特性分析结果")
    recommendations: Optional[List[str]] = Field(None, description="训练建议列表")
    severity_level: int = Field(default=1, description="严重程度(1-5)")
    status: str = Field(default="pending", description="状态: pending/completed")
    conversation_id: Optional[str] = Field(None, description="关联对话ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ========== E-Commerce: Merchant 集合 ==========

class Merchant(MongoBaseModel):
    """商家模型"""
    merchant_id: str = Field(..., description="商家唯一标识")
    user_id: str = Field(..., description="关联的用户ID")
    merchant_name: str = Field(..., max_length=100, description="商家名称")
    merchant_type: str = Field(
        default="tcm",
        description="商家类型: tcm(中药)/pet_food/pet_medicine/pet_toy/pet_house/general"
    )
    logo_url: Optional[str] = Field(None, description="商家Logo URL")
    cover_image_url: Optional[str] = Field(None, description="店铺封面图URL")
    description: Optional[str] = Field(None, max_length=2000, description="商家简介")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    address: Optional[str] = Field(None, description="详细地址")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    business_license: Optional[str] = Field(None, description="营业执照号")
    status: str = Field(default="pending", description="状态: pending/active/suspended/rejected")
    rating: float = Field(default=0.0, ge=0, le=5, description="商家评分")
    review_count: int = Field(default=0, ge=0, description="评价总数")
    total_sales: int = Field(default=0, ge=0, description="总销量")
    product_count: int = Field(default=0, ge=0, description="商品数量")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    is_verified: bool = Field(default=False, description="是否认证商家")
    tcm_certification: Optional[Dict[str, Any]] = Field(None, description="中药相关资质认证信息")
    shipping_policy: Optional[Dict[str, Any]] = Field(None, description="配送策略")
    return_policy: Optional[Dict[str, Any]] = Field(None, description="退换货政策")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ========== E-Commerce: Shopping Cart 集合 ==========

class CartItem(MongoBaseModel):
    """购物车项模型"""
    cart_item_id: str = Field(..., description="购物车项唯一标识")
    user_id: str = Field(..., description="用户ID")
    product_id: str = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称（冗余存储）")
    product_image_url: Optional[str] = Field(None, description="商品图片URL（冗余存储）")
    price: float = Field(..., ge=0, description="添加时单价（冗余存储）")
    quantity: int = Field(default=1, ge=1, le=99, description="数量")
    merchant_id: Optional[str] = Field(None, description="所属商家ID")
    merchant_name: Optional[str] = Field(None, description="商家名称（冗余存储）")
    selected: bool = Field(default=True, description="是否选中")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ========== E-Commerce: Order 集合 ==========

class OrderItem(MongoBaseModel):
    """订单项子模型"""
    order_item_id: str = Field(..., description="订单项唯一标识")
    product_id: str = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    product_image_url: Optional[str] = Field(None, description="商品图片URL")
    product_category: Optional[str] = Field(None, description="商品分类")
    price: float = Field(..., ge=0, description="下单时单价")
    quantity: int = Field(default=1, ge=1, description="购买数量")
    subtotal: float = Field(..., ge=0, description="小计金额")
    merchant_id: Optional[str] = Field(None, description="所属商家ID")


class Order(MongoBaseModel):
    """订单模型"""
    order_id: str = Field(..., description="订单唯一标识")
    user_id: str = Field(..., description="用户ID")
    order_no: str = Field(..., unique=True, description="订单编号（业务编号）")
    items: List[OrderItem] = Field(default_factory=list, description="订单商品列表")
    total_amount: float = Field(..., ge=0, description="订单总金额")
    discount_amount: float = Field(default=0.0, ge=0, description="优惠减免金额")
    freight_amount: float = Field(default=0.0, ge=0, description="运费金额")
    pay_amount: float = Field(..., ge=0, description="实际支付金额")
    status: str = Field(
        default="pending",
        description="订单状态: pending/paid/shipped/delivered/completed/cancelled/refunding/refunded"
    )
    payment_method: Optional[str] = Field(None, description="支付方式: wechat/alipay/balance")
    payment_time: Optional[datetime] = Field(None, description="支付时间")
    shipping_name: Optional[str] = Field(None, description="收货人姓名")
    shipping_phone: Optional[str] = Field(None, description="收货人电话")
    shipping_address: Optional[str] = Field(None, description="收货地址")
    shipping_province: Optional[str] = Field(None, description="收货省份")
    shipping_city: Optional[str] = Field(None, description="收货城市")
    shipping_district: Optional[str] = Field(None, description="收货区县")
    express_company: Optional[str] = Field(None, description="快递公司")
    express_no: Optional[str] = Field(None, description="快递单号")
    shipped_time: Optional[datetime] = Field(None, description="发货时间")
    delivered_time: Optional[datetime] = Field(None, description="签收时间")
    completed_time: Optional[datetime] = Field(None, description="完成时间")
    cancelled_time: Optional[datetime] = Field(None, description="取消时间")
    cancel_reason: Optional[str] = Field(None, description="取消原因")
    remark: Optional[str] = Field(None, description="订单备注")
    is_reviewed: bool = Field(default=False, description="是否已评价")
    auto_confirm_days: int = Field(default=15, description="自动确认收货天数")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ========== E-Commerce: Review 集合 ==========

class Review(MongoBaseModel):
    """产品评价/反馈模型"""
    review_id: str = Field(..., description="评价唯一标识")
    user_id: str = Field(..., description="用户ID")
    user_nickname: Optional[str] = Field(None, description="用户昵称（脱敏）")
    user_avatar_url: Optional[str] = Field(None, description="用户头像")
    order_id: str = Field(..., description="关联订单ID")
    order_item_id: str = Field(..., description="关联订单项ID")
    product_id: str = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称（冗余存储）")
    merchant_id: Optional[str] = Field(None, description="商家ID")
    rating: int = Field(..., ge=1, le=5, description="评分 1-5星")
    content: Optional[str] = Field(None, max_length=1000, description="评价内容")
    image_urls: List[str] = Field(default_factory=list, description="评价图片URL列表")
    reply_content: Optional[str] = Field(None, max_length=500, description="商家回复内容")
    replied_at: Optional[datetime] = Field(None, description="回复时间")
    is_anonymous: bool = Field(default=False, description="是否匿名评价")
    like_count: int = Field(default=0, ge=0, description="点赞数")
    status: str = Field(default="published", description="状态: published/hidden/deleted")
    tags: List[str] = Field(default_factory=list, description="评价标签：如 好评/物流快/包装好 等")
    pet_info: Optional[Dict[str, Any]] = Field(None, description="使用该商品的宠物信息")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
