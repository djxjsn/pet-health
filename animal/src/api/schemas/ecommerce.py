"""
电商模块 Pydantic Schema 定义

包含商家管理、购物车、订单、评价等请求/响应模型。
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ========== 商家管理 Schema ==========

class MerchantCreate(BaseModel):
    merchant_name: str = Field(..., max_length=100, description="商家名称")
    merchant_type: str = Field(default="general", description="商家类型: tcm/pet_food/pet_medicine/pet_toy/pet_house/general")
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
    tags: List[str] = Field(default_factory=list, description="标签列表")
    tcm_certification: Optional[Dict[str, Any]] = Field(None, description="中药资质认证信息")
    shipping_policy: Optional[Dict[str, Any]] = Field(None, description="配送策略")
    return_policy: Optional[Dict[str, Any]] = Field(None, description="退换货政策")


class MerchantUpdate(BaseModel):
    merchant_name: Optional[str] = Field(None, max_length=100)
    merchant_type: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    description: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    business_license: Optional[str] = None
    tags: Optional[List[str]] = None
    tcm_certification: Optional[Dict[str, Any]] = None
    shipping_policy: Optional[Dict[str, Any]] = None
    return_policy: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, description="状态: pending/active/suspended/rejected")


class MerchantResponse(BaseModel):
    merchant_id: str
    user_id: str
    merchant_name: str
    merchant_type: str
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    description: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    business_license: Optional[str] = None
    status: str
    rating: float = 0.0
    review_count: int = 0
    total_sales: int = 0
    product_count: int = 0
    tags: List[str] = Field(default_factory=list)
    is_verified: bool = False
    tcm_certification: Optional[Dict[str, Any]] = None
    shipping_policy: Optional[Dict[str, Any]] = None
    return_policy: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MerchantListResponse(BaseModel):
    merchants: List[MerchantResponse]
    total: int
    page: int
    page_size: int


# ========== 商品扩展 Schema ==========

class ProductCreateEx(BaseModel):
    name: str = Field(..., max_length=200, description="商品名称")
    category: str = Field(..., description="商品分类: food/toy/accessory/medicine/hygiene/clothing/nest")
    price: float = Field(..., ge=0, description="价格")
    original_price: Optional[float] = Field(None, ge=0, description="原价")
    brand: Optional[str] = Field(None, max_length=100, description="品牌名称")
    subcategory: Optional[str] = Field(None, description="子分类")
    image_url: Optional[str] = Field(None, description="商品图片URL")
    image_urls: List[str] = Field(default_factory=list, description="商品图片URL列表")
    description: Optional[str] = Field(None, description="商品描述")
    ingredients: Optional[List[Dict[str, Any]]] = Field(default=None, description="成分列表")
    nutrition_info: Optional[Dict[str, Any]] = Field(default=None, description="营养信息")
    suitable_for: Optional[List[str]] = Field(default=None, description="适用对象")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    stock: int = Field(default=0, ge=0, description="库存数量")
    merchant_id: Optional[str] = Field(None, description="所属商家ID")
    is_tcm_product: bool = Field(default=False, description="是否中药产品")
    tcm_properties: Optional[Dict[str, Any]] = Field(None, description="中药属性")
    specifications: Optional[List[Dict[str, Any]]] = Field(None, description="规格列表")


class ProductUpdateEx(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    brand: Optional[str] = None
    subcategory: Optional[str] = None
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    description: Optional[str] = None
    ingredients: Optional[List[Dict[str, Any]]] = None
    nutrition_info: Optional[Dict[str, Any]] = None
    suitable_for: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    stock: Optional[int] = None
    stock_status: Optional[str] = None
    is_tcm_product: Optional[bool] = None
    tcm_properties: Optional[Dict[str, Any]] = None
    specifications: Optional[List[Dict[str, Any]]] = None
    status: Optional[str] = Field(None, description="商品状态: on_sale/off_sale/draft")


class ProductResponseEx(BaseModel):
    _id: str
    product_id: str
    name: str
    brand: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    currency: str = "CNY"
    image_url: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    ingredients: Optional[List[Dict[str, Any]]] = None
    nutrition_info: Optional[Dict[str, Any]] = None
    suitable_for: Optional[List[str]] = None
    tags: List[str] = Field(default_factory=list)
    rating: float = 0.0
    review_count: int = 0
    sales_count: int = 0
    stock: int = 0
    stock_status: str = "in_stock"
    merchant_id: Optional[str] = None
    merchant_name: Optional[str] = None
    is_tcm_product: bool = False
    tcm_properties: Optional[Dict[str, Any]] = None
    specifications: Optional[List[Dict[str, Any]]] = None
    status: str = "on_sale"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ========== 购物车 Schema ==========

class CartAddRequest(BaseModel):
    product_id: str = Field(..., description="商品ID")
    quantity: int = Field(default=1, ge=1, le=99, description="数量")


class CartUpdateRequest(BaseModel):
    quantity: Optional[int] = Field(None, ge=1, le=99, description="数量")
    selected: Optional[bool] = Field(None, description="是否选中")


class CartItemResponse(BaseModel):
    cart_item_id: str
    user_id: str
    product_id: str
    product_name: str
    product_image_url: Optional[str] = None
    price: float
    quantity: int
    merchant_id: Optional[str] = None
    merchant_name: Optional[str] = None
    selected: bool = True
    stock: Optional[int] = None
    stock_status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_count: int
    selected_count: int
    total_amount: float
    selected_amount: float


class CartSelectRequest(BaseModel):
    selected: bool = Field(..., description="是否选中")
    item_ids: Optional[List[str]] = Field(None, description="指定项ID（不传则全选/全不选）")


# ========== 订单 Schema ==========

class OrderCreateRequest(BaseModel):
    shipping_name: str = Field(..., description="收货人姓名")
    shipping_phone: str = Field(..., description="收货人电话")
    shipping_address: str = Field(..., description="收货地址")
    shipping_province: Optional[str] = Field(None, description="省份")
    shipping_city: Optional[str] = Field(None, description="城市")
    shipping_district: Optional[str] = Field(None, description="区县")
    remark: Optional[str] = Field(None, max_length=200, description="订单备注")
    cart_item_ids: Optional[List[str]] = Field(None, description="指定购物车项ID（为空则使用所有选中项）")


class OrderItemResponse(BaseModel):
    order_item_id: str
    product_id: str
    product_name: str
    product_image_url: Optional[str] = None
    product_category: Optional[str] = None
    price: float
    quantity: int
    subtotal: float
    merchant_id: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    order_no: str
    items: List[OrderItemResponse]
    total_amount: float
    discount_amount: float = 0.0
    freight_amount: float = 0.0
    pay_amount: float
    status: str
    payment_method: Optional[str] = None
    payment_time: Optional[str] = None
    shipping_name: Optional[str] = None
    shipping_phone: Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_province: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_district: Optional[str] = None
    express_company: Optional[str] = None
    express_no: Optional[str] = None
    shipped_time: Optional[str] = None
    delivered_time: Optional[str] = None
    completed_time: Optional[str] = None
    cancelled_time: Optional[str] = None
    cancel_reason: Optional[str] = None
    remark: Optional[str] = None
    is_reviewed: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int


class OrderPayRequest(BaseModel):
    payment_method: str = Field(..., description="支付方式: wechat/alipay/balance")


class OrderCancelRequest(BaseModel):
    cancel_reason: Optional[str] = Field(None, max_length=200, description="取消原因")


class OrderShipRequest(BaseModel):
    express_company: str = Field(..., description="快递公司")
    express_no: str = Field(..., description="快递单号")


# ========== 评价 Schema ==========

class ReviewCreateRequest(BaseModel):
    order_id: str = Field(..., description="关联订单ID")
    order_item_id: str = Field(..., description="关联订单项ID")
    product_id: str = Field(..., description="商品ID")
    rating: int = Field(..., ge=1, le=5, description="评分 1-5星")
    content: Optional[str] = Field(None, max_length=1000, description="评价内容")
    image_urls: List[str] = Field(default_factory=list, description="评价图片URL列表")
    is_anonymous: bool = Field(default=False, description="是否匿名")
    tags: List[str] = Field(default_factory=list, description="评价标签")
    pet_info: Optional[Dict[str, Any]] = Field(None, description="宠物信息")


class ReviewReplyRequest(BaseModel):
    reply_content: str = Field(..., max_length=500, description="商家回复内容")


class ReviewResponse(BaseModel):
    review_id: str
    user_id: str
    user_nickname: Optional[str] = None
    user_avatar_url: Optional[str] = None
    order_id: str
    order_item_id: str
    product_id: str
    product_name: str
    merchant_id: Optional[str] = None
    rating: int
    content: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)
    reply_content: Optional[str] = None
    replied_at: Optional[str] = None
    is_anonymous: bool = False
    like_count: int = 0
    status: str = "published"
    tags: List[str] = Field(default_factory=list)
    pet_info: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    total: int
    page: int
    page_size: int
    rating_stats: Optional[Dict[str, Any]] = None


# ========== 热门搜索 Schema ==========

class HotSearchResponse(BaseModel):
    keywords: List[Dict[str, Any]]


# ========== 通用 Schema ==========

class PageRequest(BaseModel):
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class MessageResponse(BaseModel):
    message: str
    data: Optional[Any] = None
