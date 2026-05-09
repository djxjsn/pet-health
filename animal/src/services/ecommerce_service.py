"""
电商模块服务层

整合 Redis 缓存和分布式锁，提供商家管理、购物车、订单、评价等核心业务逻辑。
"""
import uuid
import time
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.repositories.ecommerce_repositories import (
    MerchantRepository,
    CartRepository,
    OrderRepository,
    ReviewRepository,
)
from src.repositories.mongo_repositories import ProductRepository
from src.core.redis_cache import (
    get_redis_cache,
    CacheKeyBuilder,
    CacheTTL,
)
from src.core.distributed_lock import distributed_lock, LockKeyBuilder

logger = logging.getLogger(__name__)


class MerchantService:
    """商家管理服务"""

    @staticmethod
    async def create_merchant(user_id: str, data: Dict[str, Any]) -> str:
        merchant_id = f"merchant_{uuid.uuid4().hex[:8]}"
        data["merchant_id"] = merchant_id
        data["user_id"] = user_id
        data["status"] = "pending"
        data["rating"] = 0.0
        data["review_count"] = 0
        data["total_sales"] = 0
        data["product_count"] = 0
        data["is_verified"] = False

        MerchantRepository.create(data)
        return merchant_id

    @staticmethod
    async def get_merchant(merchant_id: str) -> Optional[Dict[str, Any]]:
        cache = get_redis_cache()
        cache_key = CacheKeyBuilder.merchant(merchant_id)
        cached = cache.get(cache_key)
        if cached and cached != "__NULL__":
            return cached

        merchant = MerchantRepository.get_by_id(merchant_id)
        if merchant:
            cache.set(cache_key, merchant, ttl=CacheTTL.MERCHANT_INFO)
        else:
            cache.set(cache_key, "__NULL__", ttl=CacheTTL.NULL_CACHE)
        return merchant

    @staticmethod
    async def get_merchant_by_user(user_id: str) -> Optional[Dict[str, Any]]:
        return MerchantRepository.get_by_user_id(user_id)

    @staticmethod
    async def update_merchant(merchant_id: str, update_data: Dict[str, Any]) -> bool:
        result = MerchantRepository.update(merchant_id, update_data)
        if result:
            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.merchant(merchant_id))
        return result

    @staticmethod
    async def list_merchants(
        status: Optional[str] = None,
        merchant_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        skip = (page - 1) * page_size
        merchants = MerchantRepository.list_merchants(
            status=status, merchant_type=merchant_type, skip=skip, limit=page_size
        )
        total = MerchantRepository.count(status=status, merchant_type=merchant_type)
        return {
            "merchants": merchants,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_merchant_products(
        merchant_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        skip = (page - 1) * page_size
        products = ProductRepository.search(
            query=None, category=None, skip=skip, limit=page_size
        )
        merchant_products = [p for p in products if p.get("merchant_id") == merchant_id]
        return {
            "products": merchant_products,
            "total": len(merchant_products),
            "page": page,
            "page_size": page_size,
        }


class ProductService:
    """商品服务（含缓存）"""

    @staticmethod
    async def get_product(product_id: str) -> Optional[Dict[str, Any]]:
        cache = get_redis_cache()
        cache_key = CacheKeyBuilder.product(product_id)
        cached = cache.get(cache_key)
        if cached and cached != "__NULL__":
            return cached

        product = ProductRepository.get_by_id(product_id)
        if product:
            cache.set(cache_key, product, ttl=CacheTTL.PRODUCT_DETAIL)
        else:
            cache.set(cache_key, "__NULL__", ttl=CacheTTL.NULL_CACHE)
        return product

    @staticmethod
    async def create_product(merchant_id: str, data: Dict[str, Any]) -> str:
        async with distributed_lock(LockKeyBuilder.merchant_product(merchant_id)):
            merchant = MerchantRepository.get_by_id(merchant_id)
            if not merchant:
                raise ValueError(f"商家不存在: {merchant_id}")
            if merchant.get("status") != "active":
                raise ValueError("商家未激活，无法上架商品")

            category = data.get("category", "")
            valid_categories = ["food", "toy", "accessory", "medicine", "hygiene", "clothing", "nest"]
            if category not in valid_categories:
                raise ValueError(f"无效的商品分类: {category}")

            product_id = f"product_{category}_{uuid.uuid4().hex[:8]}"
            data["product_id"] = product_id
            data["merchant_id"] = merchant_id
            data["merchant_name"] = merchant.get("merchant_name")
            data["rating"] = 0.0
            data["review_count"] = 0
            data["sales_count"] = 0
            data["stock_status"] = "in_stock" if data.get("stock", 0) > 0 else "out_of_stock"
            data["status"] = "on_sale"

            ProductRepository.create(data)
            MerchantRepository.increment_product_count(merchant_id, 1)

            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.category_stats())

            return product_id

    @staticmethod
    async def update_product(product_id: str, update_data: Dict[str, Any]) -> bool:
        async with distributed_lock(LockKeyBuilder.product_update(product_id)):
            if "stock" in update_data:
                stock = update_data["stock"]
                update_data["stock_status"] = "in_stock" if stock > 0 else "out_of_stock"
                if 0 < stock <= 10:
                    update_data["stock_status"] = "limited"

            result = ProductRepository.update(product_id, update_data)
            if result:
                cache = get_redis_cache()
                cache.delete(CacheKeyBuilder.product(product_id))
                cache.delete(CacheKeyBuilder.category_stats())
            return result

    @staticmethod
    async def delete_product(product_id: str) -> bool:
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError(f"商品不存在: {product_id}")

        result = ProductRepository.delete(product_id)
        if result:
            merchant_id = product.get("merchant_id")
            if merchant_id:
                MerchantRepository.increment_product_count(merchant_id, -1)

            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.product(product_id))
            cache.delete(CacheKeyBuilder.category_stats())
        return result

    @staticmethod
    async def search_products(
        query: Optional[str] = None,
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        merchant_id: Optional[str] = None,
        is_tcm: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: int = -1,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        cache = get_redis_cache()
        cache_key = CacheKeyBuilder.product_list(category, page, page_size)
        cached = cache.get(cache_key)
        if cached and cached != "__NULL__":
            return cached

        skip = (page - 1) * page_size
        products = ProductRepository.search(
            query=query,
            category=category,
            price_min=price_min,
            price_max=price_max,
            skip=skip,
            limit=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        if merchant_id:
            products = [p for p in products if p.get("merchant_id") == merchant_id]
        if is_tcm is not None:
            products = [p for p in products if p.get("is_tcm_product") == is_tcm]

        total = ProductRepository.count(category=category)

        result = {
            "products": products,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

        cache.set(cache_key, result, ttl=CacheTTL.PRODUCT_LIST)
        return result

    @staticmethod
    async def record_hot_search(keyword: str):
        cache = get_redis_cache()
        if cache.is_available():
            cache.zincrby(CacheKeyBuilder.hot_search(), 1, keyword)

    @staticmethod
    async def get_hot_search(limit: int = 10) -> List[Dict[str, Any]]:
        cache = get_redis_cache()
        if not cache.is_available():
            return []

        results = cache.zrevrange(CacheKeyBuilder.hot_search(), 0, limit - 1, withscores=True)
        return [{"keyword": kw, "score": int(score)} for kw, score in results]

    @staticmethod
    async def get_category_stats() -> Dict[str, Any]:
        cache = get_redis_cache()
        cache_key = CacheKeyBuilder.category_stats()
        cached = cache.get(cache_key)
        if cached and cached != "__NULL__":
            return cached

        stats = {
            "total_products": ProductRepository.count(),
            "by_category": {
                "food": ProductRepository.count(category="food"),
                "toy": ProductRepository.count(category="toy"),
                "accessory": ProductRepository.count(category="accessory"),
                "medicine": ProductRepository.count(category="medicine"),
                "hygiene": ProductRepository.count(category="hygiene"),
                "clothing": ProductRepository.count(category="clothing"),
                "nest": ProductRepository.count(category="nest"),
            }
        }
        cache.set(cache_key, stats, ttl=CacheTTL.CATEGORY_STATS)
        return stats


class CartService:
    """购物车服务（含Redis缓存）"""

    @staticmethod
    async def add_to_cart(user_id: str, product_id: str, quantity: int = 1) -> str:
        async with distributed_lock(LockKeyBuilder.cart_operation(user_id)):
            product = ProductRepository.get_by_id(product_id)
            if not product:
                raise ValueError(f"商品不存在: {product_id}")
            if product.get("stock", 0) < quantity:
                raise ValueError("库存不足")
            if product.get("status") != "on_sale":
                raise ValueError("商品已下架")

            existing = CartRepository.find_item(user_id, product_id)
            if existing:
                new_quantity = existing.get("quantity", 0) + quantity
                if new_quantity > 99:
                    raise ValueError("单商品最多添加99件")
                CartRepository.update_item(
                    existing["cart_item_id"],
                    {"quantity": new_quantity}
                )
                cart_item_id = existing["cart_item_id"]
            else:
                cart_item_id = f"cart_{uuid.uuid4().hex[:8]}"
                CartRepository.add_item({
                    "cart_item_id": cart_item_id,
                    "user_id": user_id,
                    "product_id": product_id,
                    "product_name": product.get("name"),
                    "product_image_url": product.get("image_url"),
                    "price": product.get("price", 0),
                    "quantity": quantity,
                    "merchant_id": product.get("merchant_id"),
                    "merchant_name": product.get("merchant_name"),
                    "selected": True,
                })

            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.cart(user_id))

            return cart_item_id

    @staticmethod
    async def get_cart(user_id: str) -> Dict[str, Any]:
        cache = get_redis_cache()
        cache_key = CacheKeyBuilder.cart(user_id)
        cached = cache.get(cache_key)
        if cached and cached != "__NULL__":
            return cached

        items = CartRepository.get_user_cart(user_id)
        product_ids = [item["product_id"] for item in items]
        stock_map = {}
        for pid in product_ids:
            product = ProductRepository.get_by_id(pid)
            if product:
                stock_map[pid] = {
                    "stock": product.get("stock", 0),
                    "stock_status": product.get("stock_status", "out_of_stock"),
                    "price": product.get("price", 0),
                }

        for item in items:
            pid = item["product_id"]
            if pid in stock_map:
                item["stock"] = stock_map[pid]["stock"]
                item["stock_status"] = stock_map[pid]["stock_status"]

        total_count = len(items)
        selected_count = sum(1 for item in items if item.get("selected", True))
        total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        selected_amount = sum(
            item.get("price", 0) * item.get("quantity", 1)
            for item in items if item.get("selected", True)
        )

        result = {
            "items": items,
            "total_count": total_count,
            "selected_count": selected_count,
            "total_amount": round(total_amount, 2),
            "selected_amount": round(selected_amount, 2),
        }

        cache.set(cache_key, result, ttl=CacheTTL.CART)
        return result

    @staticmethod
    async def update_cart_item(user_id: str, cart_item_id: str, update_data: Dict[str, Any]) -> bool:
        item = CartRepository.get_item(cart_item_id)
        if not item or item.get("user_id") != user_id:
            raise ValueError("购物车项不存在或无权操作")

        if "quantity" in update_data:
            product = ProductRepository.get_by_id(item["product_id"])
            if product and product.get("stock", 0) < update_data["quantity"]:
                raise ValueError("库存不足")

        result = CartRepository.update_item(cart_item_id, update_data)
        if result:
            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.cart(user_id))
        return result

    @staticmethod
    async def remove_cart_item(user_id: str, cart_item_id: str) -> bool:
        item = CartRepository.get_item(cart_item_id)
        if not item or item.get("user_id") != user_id:
            raise ValueError("购物车项不存在或无权操作")

        result = CartRepository.delete_item(cart_item_id)
        if result:
            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.cart(user_id))
        return result

    @staticmethod
    async def update_selection(user_id: str, selected: bool, item_ids: Optional[List[str]] = None) -> int:
        count = CartRepository.update_selection(user_id, selected, item_ids)
        if count:
            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.cart(user_id))
        return count

    @staticmethod
    async def clear_cart(user_id: str) -> int:
        count = CartRepository.delete_user_cart(user_id)
        if count:
            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.cart(user_id))
        return count


class OrderService:
    """订单服务（含分布式锁）"""

    @staticmethod
    async def create_order(user_id: str, data: Dict[str, Any]) -> str:
        async with distributed_lock(LockKeyBuilder.order_create(user_id), timeout=15):
            cart = await CartService.get_cart(user_id)
            items = cart.get("items", [])

            if data.get("cart_item_ids"):
                item_ids = set(data["cart_item_ids"])
                items = [i for i in items if i["cart_item_id"] in item_ids]
            else:
                items = [i for i in items if i.get("selected", True)]

            if not items:
                raise ValueError("购物车为空或没有选中的商品")

            order_items = []
            total_amount = 0.0
            for item in items:
                product = ProductRepository.get_by_id(item["product_id"])
                if not product:
                    raise ValueError(f"商品不存在: {item['product_name']}")
                if product.get("stock", 0) < item["quantity"]:
                    raise ValueError(f"库存不足: {item['product_name']}")
                if product.get("status") != "on_sale":
                    raise ValueError(f"商品已下架: {item['product_name']}")

                subtotal = item["price"] * item["quantity"]
                order_item_id = f"oi_{uuid.uuid4().hex[:8]}"
                order_items.append({
                    "order_item_id": order_item_id,
                    "product_id": item["product_id"],
                    "product_name": item["product_name"],
                    "product_image_url": item.get("product_image_url"),
                    "product_category": product.get("category"),
                    "price": item["price"],
                    "quantity": item["quantity"],
                    "subtotal": round(subtotal, 2),
                    "merchant_id": item.get("merchant_id"),
                })
                total_amount += subtotal

            freight_amount = 0.0 if total_amount >= 99 else 10.0
            pay_amount = round(total_amount + freight_amount, 2)

            timestamp = int(time.time())
            order_no = f"ORD{timestamp}{uuid.uuid4().hex[:6].upper()}"
            order_id = f"order_{uuid.uuid4().hex[:8]}"

            order_data = {
                "order_id": order_id,
                "user_id": user_id,
                "order_no": order_no,
                "items": order_items,
                "total_amount": round(total_amount, 2),
                "discount_amount": 0.0,
                "freight_amount": freight_amount,
                "pay_amount": pay_amount,
                "status": "pending",
                "shipping_name": data.get("shipping_name"),
                "shipping_phone": data.get("shipping_phone"),
                "shipping_address": data.get("shipping_address"),
                "shipping_province": data.get("shipping_province"),
                "shipping_city": data.get("shipping_city"),
                "shipping_district": data.get("shipping_district"),
                "remark": data.get("remark"),
                "is_reviewed": False,
            }

            OrderRepository.create(order_data)

            for item in items:
                product = ProductRepository.get_by_id(item["product_id"])
                if product:
                    new_stock = product.get("stock", 0) - item["quantity"]
                    ProductRepository.update(item["product_id"], {
                        "stock": new_stock,
                        "stock_status": "in_stock" if new_stock > 10 else ("limited" if new_stock > 0 else "out_of_stock"),
                        "sales_count": product.get("sales_count", 0) + item["quantity"],
                    })
                    cache = get_redis_cache()
                    cache.delete(CacheKeyBuilder.product(item["product_id"]))

                merchant_id = item.get("merchant_id")
                if merchant_id:
                    MerchantRepository.increment_sales(merchant_id, item["quantity"])

            if data.get("cart_item_ids"):
                for cid in data["cart_item_ids"]:
                    CartRepository.delete_item(cid)
            else:
                CartRepository.delete_selected_items(user_id)

            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.cart(user_id))

            return order_id

    @staticmethod
    async def get_order(order_id: str) -> Optional[Dict[str, Any]]:
        cache = get_redis_cache()
        cache_key = CacheKeyBuilder.order(order_id)
        cached = cache.get(cache_key)
        if cached and cached != "__NULL__":
            return cached

        order = OrderRepository.get_by_id(order_id)
        if order:
            cache.set(cache_key, order, ttl=CacheTTL.ORDER_DETAIL)
        else:
            cache.set(cache_key, "__NULL__", ttl=CacheTTL.NULL_CACHE)
        return order

    @staticmethod
    async def list_orders(
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        cache = get_redis_cache()
        cache_key = CacheKeyBuilder.user_orders(user_id, page)
        cached = cache.get(cache_key)
        if cached and cached != "__NULL__":
            return cached

        skip = (page - 1) * page_size
        orders = OrderRepository.list_by_user(user_id, status=status, skip=skip, limit=page_size)
        total = OrderRepository.count_by_user(user_id, status=status)

        result = {
            "orders": orders,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
        cache.set(cache_key, result, ttl=CacheTTL.USER_ORDERS)
        return result

    @staticmethod
    async def pay_order(order_id: str, payment_method: str) -> bool:
        async with distributed_lock(LockKeyBuilder.order_pay(order_id)):
            order = OrderRepository.get_by_id(order_id)
            if not order:
                raise ValueError("订单不存在")
            if order.get("status") != "pending":
                raise ValueError(f"订单状态不允许支付: {order.get('status')}")

            result = OrderRepository.update(order_id, {
                "status": "paid",
                "payment_method": payment_method,
                "payment_time": datetime.utcnow().isoformat(),
            })

            if result:
                cache = get_redis_cache()
                cache.delete(CacheKeyBuilder.order(order_id))
            return result

    @staticmethod
    async def cancel_order(order_id: str, cancel_reason: Optional[str] = None) -> bool:
        async with distributed_lock(LockKeyBuilder.order_cancel(order_id)):
            order = OrderRepository.get_by_id(order_id)
            if not order:
                raise ValueError("订单不存在")
            if order.get("status") not in ("pending", "paid"):
                raise ValueError(f"订单状态不允许取消: {order.get('status')}")

            result = OrderRepository.update(order_id, {
                "status": "cancelled",
                "cancelled_time": datetime.utcnow().isoformat(),
                "cancel_reason": cancel_reason,
            })

            if result:
                for item in order.get("items", []):
                    product = ProductRepository.get_by_id(item["product_id"])
                    if product:
                        new_stock = product.get("stock", 0) + item["quantity"]
                        ProductRepository.update(item["product_id"], {
                            "stock": new_stock,
                            "stock_status": "in_stock" if new_stock > 10 else ("limited" if new_stock > 0 else "out_of_stock"),
                            "sales_count": max(0, product.get("sales_count", 0) - item["quantity"]),
                        })
                        cache = get_redis_cache()
                        cache.delete(CacheKeyBuilder.product(item["product_id"]))

                cache = get_redis_cache()
                cache.delete(CacheKeyBuilder.order(order_id))

            return result

    @staticmethod
    async def confirm_order(order_id: str) -> bool:
        order = OrderRepository.get_by_id(order_id)
        if not order:
            raise ValueError("订单不存在")
        if order.get("status") != "shipped":
            raise ValueError(f"订单状态不允许确认收货: {order.get('status')}")

        result = OrderRepository.update(order_id, {
            "status": "completed",
            "completed_time": datetime.utcnow().isoformat(),
        })
        if result:
            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.order(order_id))
        return result

    @staticmethod
    async def ship_order(order_id: str, express_company: str, express_no: str) -> bool:
        order = OrderRepository.get_by_id(order_id)
        if not order:
            raise ValueError("订单不存在")
        if order.get("status") != "paid":
            raise ValueError(f"订单状态不允许发货: {order.get('status')}")

        result = OrderRepository.update(order_id, {
            "status": "shipped",
            "express_company": express_company,
            "express_no": express_no,
            "shipped_time": datetime.utcnow().isoformat(),
        })
        if result:
            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.order(order_id))
        return result


class ReviewService:
    """评价服务"""

    @staticmethod
    async def create_review(user_id: str, data: Dict[str, Any]) -> str:
        order = OrderRepository.get_by_id(data["order_id"])
        if not order:
            raise ValueError("订单不存在")
        if order.get("user_id") != user_id:
            raise ValueError("无权评价此订单")
        if order.get("status") != "completed":
            raise ValueError("订单未完成，无法评价")

        order_item = None
        for item in order.get("items", []):
            if item.get("order_item_id") == data["order_item_id"]:
                order_item = item
                break
        if not order_item:
            raise ValueError("订单项不存在")

        existing = ReviewRepository.find_user_product_review(user_id, data["product_id"])
        if existing:
            raise ValueError("已评价过此商品")

        review_id = f"review_{uuid.uuid4().hex[:8]}"
        review_data = {
            "review_id": review_id,
            "user_id": user_id,
            "order_id": data["order_id"],
            "order_item_id": data["order_item_id"],
            "product_id": data["product_id"],
            "product_name": order_item.get("product_name", ""),
            "merchant_id": order_item.get("merchant_id"),
            "rating": data["rating"],
            "content": data.get("content"),
            "image_urls": data.get("image_urls", []),
            "is_anonymous": data.get("is_anonymous", False),
            "tags": data.get("tags", []),
            "pet_info": data.get("pet_info"),
            "like_count": 0,
            "status": "published",
        }

        ReviewRepository.create(review_data)

        rating_stats = ReviewRepository.get_product_rating_stats(data["product_id"])
        ProductRepository.update(data["product_id"], {
            "rating": rating_stats.get("avg_rating", 0.0),
            "review_count": rating_stats.get("total_count", 0),
        })

        OrderRepository.update(data["order_id"], {"is_reviewed": True})

        cache = get_redis_cache()
        cache.delete(CacheKeyBuilder.product(data["product_id"]))
        cache.delete(CacheKeyBuilder.review(data["product_id"]))

        return review_id

    @staticmethod
    async def get_product_reviews(
        product_id: str,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
    ) -> Dict[str, Any]:
        cache = get_redis_cache()
        cache_key = CacheKeyBuilder.review(product_id, page)
        cached = cache.get(cache_key)
        if cached and cached != "__NULL__":
            return cached

        skip = (page - 1) * page_size
        reviews = ReviewRepository.list_by_product(
            product_id, skip=skip, limit=page_size, sort_by=sort_by
        )
        total = ReviewRepository.count_by_product(product_id)
        rating_stats = ReviewRepository.get_product_rating_stats(product_id)

        result = {
            "reviews": reviews,
            "total": total,
            "page": page,
            "page_size": page_size,
            "rating_stats": rating_stats,
        }

        cache.set(cache_key, result, ttl=CacheTTL.REVIEW_LIST)
        return result

    @staticmethod
    async def reply_review(review_id: str, merchant_id: str, reply_content: str) -> bool:
        review = ReviewRepository.get_by_id(review_id)
        if not review:
            raise ValueError("评价不存在")
        if review.get("merchant_id") != merchant_id:
            raise ValueError("无权回复此评价")

        result = ReviewRepository.update(review_id, {
            "reply_content": reply_content,
            "replied_at": datetime.utcnow().isoformat(),
        })
        if result:
            cache = get_redis_cache()
            cache.delete(CacheKeyBuilder.review(review["product_id"]))
        return result

    @staticmethod
    async def like_review(review_id: str) -> bool:
        return ReviewRepository.increment_like(review_id)

    @staticmethod
    async def get_user_reviews(
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        skip = (page - 1) * page_size
        reviews = ReviewRepository.list_by_user(user_id, skip=skip, limit=page_size)
        return {
            "reviews": reviews,
            "total": len(reviews),
            "page": page,
            "page_size": page_size,
        }
