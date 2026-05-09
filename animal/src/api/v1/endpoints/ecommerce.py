"""
电商模块 API 路由

提供商家管理、商品管理（扩展）、购物车、订单、评价等接口。
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
import logging

from src.api.schemas.ecommerce import (
    MerchantCreate, MerchantUpdate, MerchantResponse, MerchantListResponse,
    ProductCreateEx, ProductUpdateEx, ProductResponseEx,
    CartAddRequest, CartUpdateRequest, CartItemResponse, CartResponse, CartSelectRequest,
    OrderCreateRequest, OrderResponse, OrderListResponse, OrderPayRequest, OrderCancelRequest, OrderShipRequest,
    ReviewCreateRequest, ReviewResponse, ReviewListResponse, ReviewReplyRequest,
    HotSearchResponse, MessageResponse,
)
from src.services.ecommerce_service import (
    MerchantService, ProductService, CartService, OrderService, ReviewService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ecommerce", tags=["电商模块"])


# ========== 商家管理 ==========

@router.post("/merchants", response_model=MerchantResponse, summary="创建商家")
async def create_merchant(user_id: str, data: MerchantCreate):
    try:
        merchant_id = await MerchantService.create_merchant(user_id, data.model_dump())
        merchant = await MerchantService.get_merchant(merchant_id)
        return MerchantResponse(**merchant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建商家失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建商家失败: {str(e)}")


@router.get("/merchants/{merchant_id}", response_model=MerchantResponse, summary="获取商家详情")
async def get_merchant(merchant_id: str):
    merchant = await MerchantService.get_merchant(merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")
    return MerchantResponse(**merchant)


@router.get("/merchants", response_model=MerchantListResponse, summary="获取商家列表")
async def list_merchants(
    status: Optional[str] = None,
    merchant_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        result = await MerchantService.list_merchants(
            status=status, merchant_type=merchant_type, page=page, page_size=page_size
        )
        return MerchantListResponse(**result)
    except Exception as e:
        logger.error(f"获取商家列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取商家列表失败: {str(e)}")


@router.put("/merchants/{merchant_id}", response_model=MerchantResponse, summary="更新商家信息")
async def update_merchant(merchant_id: str, data: MerchantUpdate):
    try:
        result = await MerchantService.update_merchant(merchant_id, data.model_dump(exclude_none=True))
        if not result:
            raise HTTPException(status_code=400, detail="更新失败")
        merchant = await MerchantService.get_merchant(merchant_id)
        return MerchantResponse(**merchant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新商家失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新商家失败: {str(e)}")


@router.get("/merchants/me/{user_id}", response_model=MerchantResponse, summary="获取当前用户的商家信息")
async def get_my_merchant(user_id: str):
    merchant = await MerchantService.get_merchant_by_user(user_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="尚未注册商家")
    return MerchantResponse(**merchant)


# ========== 商品管理（扩展） ==========

@router.post("/products", response_model=ProductResponseEx, summary="商家上架商品")
async def create_product(merchant_id: str, data: ProductCreateEx):
    try:
        product_id = await ProductService.create_product(merchant_id, data.model_dump())
        product = await ProductService.get_product(product_id)
        return ProductResponseEx(**product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建商品失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建商品失败: {str(e)}")


@router.put("/products/{product_id}", response_model=ProductResponseEx, summary="更新商品信息")
async def update_product(product_id: str, data: ProductUpdateEx):
    try:
        result = await ProductService.update_product(product_id, data.model_dump(exclude_none=True))
        if not result:
            raise HTTPException(status_code=400, detail="更新失败")
        product = await ProductService.get_product(product_id)
        return ProductResponseEx(**product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新商品失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新商品失败: {str(e)}")


@router.delete("/products/{product_id}", summary="删除商品")
async def delete_product(product_id: str):
    try:
        result = await ProductService.delete_product(product_id)
        if not result:
            raise HTTPException(status_code=400, detail="删除失败")
        return MessageResponse(message="商品已删除")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"删除商品失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除商品失败: {str(e)}")


@router.get("/products", summary="商品列表（扩展版）")
async def list_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    merchant_id: Optional[str] = None,
    is_tcm: Optional[bool] = None,
    sort_by: str = Query("created_at"),
    sort_order: int = Query(-1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        if query:
            await ProductService.record_hot_search(query)
        result = await ProductService.search_products(
            query=query, category=category, price_min=price_min, price_max=price_max,
            merchant_id=merchant_id, is_tcm=is_tcm, sort_by=sort_by,
            sort_order=sort_order, page=page, page_size=page_size,
        )
        return result
    except Exception as e:
        logger.error(f"获取商品列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取商品列表失败: {str(e)}")


@router.get("/products/{product_id}", response_model=ProductResponseEx, summary="获取商品详情")
async def get_product(product_id: str):
    product = await ProductService.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ProductResponseEx(**product)


@router.get("/hot-search", response_model=HotSearchResponse, summary="热门搜索")
async def get_hot_search(limit: int = Query(10, ge=1, le=50)):
    keywords = await ProductService.get_hot_search(limit)
    return HotSearchResponse(keywords=keywords)


@router.get("/categories", summary="获取分类统计")
async def get_category_stats():
    return await ProductService.get_category_stats()


# ========== 购物车 ==========

@router.post("/cart/add", response_model=CartItemResponse, summary="添加到购物车")
async def add_to_cart(user_id: str, data: CartAddRequest):
    try:
        cart_item_id = await CartService.add_to_cart(user_id, data.product_id, data.quantity)
        cart = await CartService.get_cart(user_id)
        for item in cart["items"]:
            if item["cart_item_id"] == cart_item_id:
                return CartItemResponse(**item)
        raise HTTPException(status_code=500, detail="添加购物车失败")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"添加购物车失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加购物车失败: {str(e)}")


@router.get("/cart", response_model=CartResponse, summary="获取购物车")
async def get_cart(user_id: str):
    return await CartService.get_cart(user_id)


@router.put("/cart/{cart_item_id}", response_model=CartItemResponse, summary="更新购物车项")
async def update_cart_item(user_id: str, cart_item_id: str, data: CartUpdateRequest):
    try:
        result = await CartService.update_cart_item(user_id, cart_item_id, data.model_dump(exclude_none=True))
        if not result:
            raise HTTPException(status_code=400, detail="更新失败")
        cart = await CartService.get_cart(user_id)
        for item in cart["items"]:
            if item["cart_item_id"] == cart_item_id:
                return CartItemResponse(**item)
        raise HTTPException(status_code=404, detail="购物车项不存在")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新购物车失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新购物车失败: {str(e)}")


@router.delete("/cart/{cart_item_id}", summary="删除购物车项")
async def remove_cart_item(user_id: str, cart_item_id: str):
    try:
        result = await CartService.remove_cart_item(user_id, cart_item_id)
        if not result:
            raise HTTPException(status_code=400, detail="删除失败")
        return MessageResponse(message="已从购物车移除")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"删除购物车项失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除购物车项失败: {str(e)}")


@router.put("/cart/select", summary="选中/取消选中购物车项")
async def update_cart_selection(user_id: str, data: CartSelectRequest):
    try:
        count = await CartService.update_selection(user_id, data.selected, data.item_ids)
        return MessageResponse(message=f"已更新{count}项选中状态")
    except Exception as e:
        logger.error(f"更新购物车选中状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新选中状态失败: {str(e)}")


@router.delete("/cart/clear", summary="清空购物车")
async def clear_cart(user_id: str):
    try:
        count = await CartService.clear_cart(user_id)
        return MessageResponse(message=f"已清空购物车，共{count}项")
    except Exception as e:
        logger.error(f"清空购物车失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空购物车失败: {str(e)}")


# ========== 订单 ==========

@router.post("/orders", response_model=OrderResponse, summary="创建订单")
async def create_order(user_id: str, data: OrderCreateRequest):
    try:
        order_id = await OrderService.create_order(user_id, data.model_dump())
        order = await OrderService.get_order(order_id)
        return OrderResponse(**order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建订单失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")


@router.get("/orders", response_model=OrderListResponse, summary="获取订单列表")
async def list_orders(
    user_id: str,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        result = await OrderService.list_orders(user_id, status=status, page=page, page_size=page_size)
        return OrderListResponse(**result)
    except Exception as e:
        logger.error(f"获取订单列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取订单列表失败: {str(e)}")


@router.get("/orders/{order_id}", response_model=OrderResponse, summary="获取订单详情")
async def get_order(order_id: str):
    order = await OrderService.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return OrderResponse(**order)


@router.post("/orders/{order_id}/pay", summary="支付订单")
async def pay_order(order_id: str, data: OrderPayRequest):
    try:
        result = await OrderService.pay_order(order_id, data.payment_method)
        if not result:
            raise HTTPException(status_code=400, detail="支付失败")
        return MessageResponse(message="支付成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"支付订单失败: {e}")
        raise HTTPException(status_code=500, detail=f"支付订单失败: {str(e)}")


@router.post("/orders/{order_id}/cancel", summary="取消订单")
async def cancel_order(order_id: str, data: Optional[OrderCancelRequest] = None):
    try:
        reason = data.cancel_reason if data else None
        result = await OrderService.cancel_order(order_id, reason)
        if not result:
            raise HTTPException(status_code=400, detail="取消失败")
        return MessageResponse(message="订单已取消")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"取消订单失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消订单失败: {str(e)}")


@router.post("/orders/{order_id}/confirm", summary="确认收货")
async def confirm_order(order_id: str):
    try:
        result = await OrderService.confirm_order(order_id)
        if not result:
            raise HTTPException(status_code=400, detail="确认收货失败")
        return MessageResponse(message="已确认收货")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"确认收货失败: {e}")
        raise HTTPException(status_code=500, detail=f"确认收货失败: {str(e)}")


@router.post("/orders/{order_id}/ship", summary="商家发货")
async def ship_order(order_id: str, data: OrderShipRequest):
    try:
        result = await OrderService.ship_order(order_id, data.express_company, data.express_no)
        if not result:
            raise HTTPException(status_code=400, detail="发货失败")
        return MessageResponse(message="已发货")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"发货失败: {e}")
        raise HTTPException(status_code=500, detail=f"发货失败: {str(e)}")


# ========== 评价 ==========

@router.post("/reviews", response_model=ReviewResponse, summary="创建评价")
async def create_review(user_id: str, data: ReviewCreateRequest):
    try:
        review_id = await ReviewService.create_review(user_id, data.model_dump())
        from src.repositories.ecommerce_repositories import ReviewRepository
        review = ReviewRepository.get_by_id(review_id)
        return ReviewResponse(**review)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建评价失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建评价失败: {str(e)}")


@router.get("/reviews/product/{product_id}", response_model=ReviewListResponse, summary="获取商品评价列表")
async def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
):
    try:
        result = await ReviewService.get_product_reviews(product_id, page=page, page_size=page_size, sort_by=sort_by)
        return ReviewListResponse(**result)
    except Exception as e:
        logger.error(f"获取评价列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取评价列表失败: {str(e)}")


@router.get("/reviews/user/{user_id}", response_model=ReviewListResponse, summary="获取用户评价列表")
async def get_user_reviews(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        result = await ReviewService.get_user_reviews(user_id, page=page, page_size=page_size)
        return ReviewListResponse(**result)
    except Exception as e:
        logger.error(f"获取用户评价失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户评价失败: {str(e)}")


@router.post("/reviews/{review_id}/reply", summary="商家回复评价")
async def reply_review(review_id: str, merchant_id: str, data: ReviewReplyRequest):
    try:
        result = await ReviewService.reply_review(review_id, merchant_id, data.reply_content)
        if not result:
            raise HTTPException(status_code=400, detail="回复失败")
        return MessageResponse(message="回复成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"回复评价失败: {e}")
        raise HTTPException(status_code=500, detail=f"回复评价失败: {str(e)}")


@router.post("/reviews/{review_id}/like", summary="点赞评价")
async def like_review(review_id: str):
    try:
        result = await ReviewService.like_review(review_id)
        if not result:
            raise HTTPException(status_code=400, detail="点赞失败")
        return MessageResponse(message="点赞成功")
    except Exception as e:
        logger.error(f"点赞评价失败: {e}")
        raise HTTPException(status_code=500, detail=f"点赞评价失败: {str(e)}")
