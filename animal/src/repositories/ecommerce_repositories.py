"""
电商模块 MongoDB Repository 层

提供购物车、订单、评价、商家的 CRUD 操作接口。
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId

from src.core.mongodb import get_mongo_collection


# ========== Merchant Repository ==========

class MerchantRepository:
    """商家集合操作"""

    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        collection = get_mongo_collection("merchants")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(merchant_id: str) -> Optional[Dict[str, Any]]:
        collection = get_mongo_collection("merchants")
        doc = collection.find_one({"merchant_id": merchant_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def get_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
        collection = get_mongo_collection("merchants")
        doc = collection.find_one({"user_id": user_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def list_merchants(
        status: Optional[str] = None,
        merchant_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        collection = get_mongo_collection("merchants")
        query = {}
        if status:
            query["status"] = status
        if merchant_type:
            query["merchant_type"] = merchant_type
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    @staticmethod
    def update(merchant_id: str, update_data: Dict[str, Any]) -> bool:
        collection = get_mongo_collection("merchants")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"merchant_id": merchant_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(merchant_id: str) -> bool:
        collection = get_mongo_collection("merchants")
        result = collection.delete_one({"merchant_id": merchant_id})
        return result.deleted_count > 0

    @staticmethod
    def count(status: Optional[str] = None, merchant_type: Optional[str] = None) -> int:
        collection = get_mongo_collection("merchants")
        query = {}
        if status:
            query["status"] = status
        if merchant_type:
            query["merchant_type"] = merchant_type
        return collection.count_documents(query)

    @staticmethod
    def increment_product_count(merchant_id: str, delta: int = 1) -> bool:
        collection = get_mongo_collection("merchants")
        result = collection.update_one(
            {"merchant_id": merchant_id},
            {"$inc": {"product_count": delta}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    @staticmethod
    def increment_sales(merchant_id: str, amount: int = 1) -> bool:
        collection = get_mongo_collection("merchants")
        result = collection.update_one(
            {"merchant_id": merchant_id},
            {"$inc": {"total_sales": amount}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0


# ========== Cart Repository ==========

class CartRepository:
    """购物车集合操作"""

    @staticmethod
    def add_item(data: Dict[str, Any]) -> str:
        collection = get_mongo_collection("cart_items")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_item(cart_item_id: str) -> Optional[Dict[str, Any]]:
        collection = get_mongo_collection("cart_items")
        doc = collection.find_one({"cart_item_id": cart_item_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def get_user_cart(user_id: str) -> List[Dict[str, Any]]:
        collection = get_mongo_collection("cart_items")
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    @staticmethod
    def find_item(user_id: str, product_id: str) -> Optional[Dict[str, Any]]:
        collection = get_mongo_collection("cart_items")
        doc = collection.find_one({"user_id": user_id, "product_id": product_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def update_item(cart_item_id: str, update_data: Dict[str, Any]) -> bool:
        collection = get_mongo_collection("cart_items")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"cart_item_id": cart_item_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete_item(cart_item_id: str) -> bool:
        collection = get_mongo_collection("cart_items")
        result = collection.delete_one({"cart_item_id": cart_item_id})
        return result.deleted_count > 0

    @staticmethod
    def delete_user_cart(user_id: str) -> int:
        collection = get_mongo_collection("cart_items")
        result = collection.delete_many({"user_id": user_id})
        return result.deleted_count

    @staticmethod
    def delete_selected_items(user_id: str) -> int:
        collection = get_mongo_collection("cart_items")
        result = collection.delete_many({"user_id": user_id, "selected": True})
        return result.deleted_count

    @staticmethod
    def count_user_items(user_id: str) -> int:
        collection = get_mongo_collection("cart_items")
        return collection.count_documents({"user_id": user_id})

    @staticmethod
    def update_selection(user_id: str, selected: bool, item_ids: Optional[List[str]] = None) -> int:
        collection = get_mongo_collection("cart_items")
        query = {"user_id": user_id}
        if item_ids:
            query["cart_item_id"] = {"$in": item_ids}
        result = collection.update_many(
            query,
            {"$set": {"selected": selected, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count


# ========== Order Repository ==========

class OrderRepository:
    """订单集合操作"""

    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        collection = get_mongo_collection("orders")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(order_id: str) -> Optional[Dict[str, Any]]:
        collection = get_mongo_collection("orders")
        doc = collection.find_one({"order_id": order_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def get_by_order_no(order_no: str) -> Optional[Dict[str, Any]]:
        collection = get_mongo_collection("orders")
        doc = collection.find_one({"order_no": order_no})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def list_by_user(
        user_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        collection = get_mongo_collection("orders")
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    @staticmethod
    def list_by_merchant(
        merchant_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        collection = get_mongo_collection("orders")
        query = {"items.merchant_id": merchant_id}
        if status:
            query["status"] = status
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    @staticmethod
    def update(order_id: str, update_data: Dict[str, Any]) -> bool:
        collection = get_mongo_collection("orders")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"order_id": order_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    @staticmethod
    def count_by_user(user_id: str, status: Optional[str] = None) -> int:
        collection = get_mongo_collection("orders")
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        return collection.count_documents(query)

    @staticmethod
    def count_by_merchant(merchant_id: str, status: Optional[str] = None) -> int:
        collection = get_mongo_collection("orders")
        query = {"items.merchant_id": merchant_id}
        if status:
            query["status"] = status
        return collection.count_documents(query)


# ========== Review Repository ==========

class ReviewRepository:
    """评价集合操作"""

    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        collection = get_mongo_collection("reviews")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = collection.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(review_id: str) -> Optional[Dict[str, Any]]:
        collection = get_mongo_collection("reviews")
        doc = collection.find_one({"review_id": review_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def list_by_product(
        product_id: str,
        status: str = "published",
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: int = -1,
    ) -> List[Dict[str, Any]]:
        collection = get_mongo_collection("reviews")
        query = {"product_id": product_id}
        if status:
            query["status"] = status
        cursor = collection.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    @staticmethod
    def list_by_user(
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        collection = get_mongo_collection("reviews")
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    @staticmethod
    def list_by_merchant(
        merchant_id: str,
        status: str = "published",
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        collection = get_mongo_collection("reviews")
        query = {"merchant_id": merchant_id}
        if status:
            query["status"] = status
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    @staticmethod
    def update(review_id: str, update_data: Dict[str, Any]) -> bool:
        collection = get_mongo_collection("reviews")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"review_id": review_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(review_id: str) -> bool:
        collection = get_mongo_collection("reviews")
        result = collection.delete_one({"review_id": review_id})
        return result.deleted_count > 0

    @staticmethod
    def count_by_product(product_id: str, status: str = "published") -> int:
        collection = get_mongo_collection("reviews")
        query = {"product_id": product_id}
        if status:
            query["status"] = status
        return collection.count_documents(query)

    @staticmethod
    def get_product_rating_stats(product_id: str) -> Dict[str, Any]:
        collection = get_mongo_collection("reviews")
        pipeline = [
            {"$match": {"product_id": product_id, "status": "published"}},
            {"$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"},
                "total_count": {"$sum": 1},
                "rating_5": {"$sum": {"$cond": [{"$eq": ["$rating", 5]}, 1, 0]}},
                "rating_4": {"$sum": {"$cond": [{"$eq": ["$rating", 4]}, 1, 0]}},
                "rating_3": {"$sum": {"$cond": [{"$eq": ["$rating", 3]}, 1, 0]}},
                "rating_2": {"$sum": {"$cond": [{"$eq": ["$rating", 2]}, 1, 0]}},
                "rating_1": {"$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}},
            }}
        ]
        results = list(collection.aggregate(pipeline))
        if results:
            r = results[0]
            return {
                "avg_rating": round(r["avg_rating"], 1) if r["avg_rating"] else 0.0,
                "total_count": r["total_count"],
                "distribution": {
                    "5": r["rating_5"],
                    "4": r["rating_4"],
                    "3": r["rating_3"],
                    "2": r["rating_2"],
                    "1": r["rating_1"],
                }
            }
        return {"avg_rating": 0.0, "total_count": 0, "distribution": {}}

    @staticmethod
    def increment_like(review_id: str) -> bool:
        collection = get_mongo_collection("reviews")
        result = collection.update_one(
            {"review_id": review_id},
            {"$inc": {"like_count": 1}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    @staticmethod
    def find_user_product_review(user_id: str, product_id: str) -> Optional[Dict[str, Any]]:
        collection = get_mongo_collection("reviews")
        doc = collection.find_one({"user_id": user_id, "product_id": product_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
