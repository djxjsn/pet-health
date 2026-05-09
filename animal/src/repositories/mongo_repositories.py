"""
MongoDB Repository 层

提供 MongoDB 集合的 CRUD 操作接口，替代原有的 SQLAlchemy ORM。
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from bson import ObjectId

from src.core.mongodb import get_mongo_collection


# ========== Conversations Repository ==========

class ConversationRepository:
    """对话集合操作"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """创建对话"""
        collection = get_mongo_collection("conversations")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        data["message_count"] = 0
        result = collection.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_id(conversation_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取对话"""
        collection = get_mongo_collection("conversations")
        doc = collection.find_one({"conversation_id": conversation_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    @staticmethod
    def list_by_user(user_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户的对话列表"""
        collection = get_mongo_collection("conversations")
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def update(conversation_id: str, update_data: Dict[str, Any]) -> bool:
        """更新对话"""
        collection = get_mongo_collection("conversations")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"conversation_id": conversation_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(conversation_id: str) -> bool:
        """删除对话及其消息"""
        collection = get_mongo_collection("conversations")
        messages_collection = get_mongo_collection("messages")
        
        result = collection.delete_one({"conversation_id": conversation_id})
        messages_collection.delete_many({"conversation_id": conversation_id})
        return result.deleted_count > 0


# ========== Messages Repository ==========

class MessageRepository:
    """消息集合操作"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """创建消息"""
        collection = get_mongo_collection("messages")
        data["created_at"] = datetime.utcnow()
        result = collection.insert_one(data)
        
        # 更新对话的消息计数
        ConversationRepository.update(
            data["conversation_id"],
            {"$inc": {"message_count": 1}}
        )
        return str(result.inserted_id)
    
    @staticmethod
    def list_by_conversation(conversation_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """获取对话的消息列表"""
        collection = get_mongo_collection("messages")
        cursor = collection.find({"conversation_id": conversation_id}).sort("created_at", 1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def get_by_id(message_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取消息"""
        collection = get_mongo_collection("messages")
        doc = collection.find_one({"message_id": message_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc


# ========== Health Records Repository ==========

class HealthRecordRepository:
    """健康记录集合操作"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """创建健康记录"""
        collection = get_mongo_collection("health_records")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = collection.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_id(record_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取记录"""
        collection = get_mongo_collection("health_records")
        doc = collection.find_one({"record_id": record_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    @staticmethod
    def list_by_pet(pet_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """获取宠物的健康记录"""
        collection = get_mongo_collection("health_records")
        cursor = collection.find({"pet_id": pet_id}).sort("record_date", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def update(record_id: str, update_data: Dict[str, Any]) -> bool:
        """更新记录"""
        collection = get_mongo_collection("health_records")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"record_id": record_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(record_id: str) -> bool:
        """删除记录"""
        collection = get_mongo_collection("health_records")
        result = collection.delete_one({"record_id": record_id})
        return result.deleted_count > 0


# ========== Consultations Repository ==========

class ConsultationRepository:
    """AI咨询记录集合操作"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """创建咨询记录"""
        collection = get_mongo_collection("consultations")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        data["status"] = data.get("status", "pending")
        data["urgency_level"] = data.get("urgency_level", 1)
        result = collection.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_id(consultation_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取咨询"""
        collection = get_mongo_collection("consultations")
        doc = collection.find_one({"consultation_id": consultation_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    @staticmethod
    def list_by_user(user_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户的咨询记录"""
        collection = get_mongo_collection("consultations")
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def list_by_pet(pet_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """获取宠物的咨询记录"""
        collection = get_mongo_collection("consultations")
        cursor = collection.find({"pet_id": pet_id}).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def update(consultation_id: str, update_data: Dict[str, Any]) -> bool:
        """更新咨询"""
        collection = get_mongo_collection("consultations")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"consultation_id": consultation_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(consultation_id: str) -> bool:
        """删除咨询"""
        collection = get_mongo_collection("consultations")
        result = collection.delete_one({"consultation_id": consultation_id})
        return result.deleted_count > 0


# ========== Knowledge Documents Repository ==========

class KnowledgeRepository:
    """知识文档集合操作"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """创建知识文档"""
        collection = get_mongo_collection("knowledge_documents")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        data["status"] = data.get("status", "draft")
        data["indexed"] = data.get("indexed", False)
        result = collection.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取知识文档"""
        collection = get_mongo_collection("knowledge_documents")
        doc = collection.find_one({"doc_id": doc_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    @staticmethod
    def get_by_doc_id(doc_id: str) -> Optional[Dict[str, Any]]:
        """根据文档唯一标识获取知识文档"""
        collection = get_mongo_collection("knowledge_documents")
        doc = collection.find_one({"doc_id": doc_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    @staticmethod
    def list_all(
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取知识文档列表"""
        collection = get_mongo_collection("knowledge_documents")
        query = {}
        if category:
            query["category"] = category
        if status:
            query["status"] = status
        
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def list_by_category(category: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """按分类获取知识文档"""
        return KnowledgeRepository.list_all(skip=skip, limit=limit, category=category)
    
    @staticmethod
    def list_published(skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """获取已发布的知识文档"""
        return KnowledgeRepository.list_all(skip=skip, limit=limit, status="published")
    
    @staticmethod
    def list_unindexed() -> List[Dict[str, Any]]:
        """获取未向量化的已发布文档"""
        collection = get_mongo_collection("knowledge_documents")
        cursor = collection.find({"status": "published", "indexed": False})
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def update(doc_id: str, update_data: Dict[str, Any]) -> bool:
        """更新知识文档"""
        collection = get_mongo_collection("knowledge_documents")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"doc_id": doc_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def mark_indexed(doc_id: str) -> bool:
        """标记文档已向量化索引"""
        collection = get_mongo_collection("knowledge_documents")
        result = collection.update_one(
            {"doc_id": doc_id},
            {
                "$set": {
                    "indexed": True,
                    "indexed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(doc_id: str) -> bool:
        """删除知识文档"""
        collection = get_mongo_collection("knowledge_documents")
        result = collection.delete_one({"doc_id": doc_id})
        return result.deleted_count > 0
    
    @staticmethod
    def count(category: Optional[str] = None, status: Optional[str] = None) -> int:
        """统计知识文档数量"""
        collection = get_mongo_collection("knowledge_documents")
        query = {}
        if category:
            query["category"] = category
        if status:
            query["status"] = status
        return collection.count_documents(query)
    
    @staticmethod
    def update_all_indexed(indexed: bool = False) -> int:
        """批量更新所有文档的索引状态
        
        Args:
            indexed: 是否已索引
        
        Returns:
            更新的文档数量
        """
        collection = get_mongo_collection("knowledge_documents")
        result = collection.update_many(
            {},
            {
                "$set": {
                    "indexed": indexed,
                    "indexed_at": None if not indexed else datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count


# ========== Shopping Products Repository ==========

class ProductRepository:
    """商品集合操作"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """创建商品"""
        collection = get_mongo_collection("products")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = collection.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_id(product_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取商品"""
        collection = get_mongo_collection("products")
        doc = collection.find_one({"product_id": product_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    @staticmethod
    def search(
        query: Optional[str] = None,
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> List[Dict[str, Any]]:
        """搜索商品
        
        Args:
            query: 搜索关键词（模糊匹配名称、品牌、描述）
            category: 商品分类过滤
            price_min: 最低价格
            price_max: 最高价格
            skip: 跳过数量
            limit: 返回数量
            sort_by: 排序字段
            sort_order: 排序方向（1升序，-1降序）
        
        Returns:
            商品列表
        """
        collection = get_mongo_collection("products")
        filter_query = {}
        
        if category:
            filter_query["category"] = category
        
        if price_min is not None or price_max is not None:
            filter_query["price"] = {}
            if price_min is not None:
                filter_query["price"]["$gte"] = price_min
            if price_max is not None:
                filter_query["price"]["$lte"] = price_max
        
        if query:
            import re
            filter_query["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"brand": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query]}}
            ]
        
        cursor = collection.find(filter_query).sort(sort_by, sort_order).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def list_by_category(category: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """按分类获取商品"""
        return ProductRepository.search(category=category, skip=skip, limit=limit)
    
    @staticmethod
    def update(product_id: str, update_data: Dict[str, Any]) -> bool:
        """更新商品"""
        collection = get_mongo_collection("products")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"product_id": product_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(product_id: str) -> bool:
        """删除商品"""
        collection = get_mongo_collection("products")
        result = collection.delete_one({"product_id": product_id})
        return result.deleted_count > 0
    
    @staticmethod
    def count(category: Optional[str] = None) -> int:
        """统计商品数量"""
        collection = get_mongo_collection("products")
        query = {}
        if category:
            query["category"] = category
        return collection.count_documents(query)


# ========== Shopping History Repository ==========

class ShoppingHistoryRepository:
    """购物历史记录集合操作"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """创建购物历史记录"""
        collection = get_mongo_collection("shopping_history")
        data["created_at"] = datetime.utcnow()
        result = collection.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def list_by_user(
        user_id: str,
        action_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取用户的购物历史"""
        collection = get_mongo_collection("shopping_history")
        query = {"user_id": user_id}
        if action_type:
            query["action_type"] = action_type
        
        cursor = collection.find(query).sort("created_at", -1).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def get_user_preferences(user_id: str) -> Dict[str, Any]:
        """获取用户偏好统计"""
        collection = get_mongo_collection("shopping_history")
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$action_type",
                "count": {"$sum": 1},
                "categories": {"$addToSet": "$category"}
            }}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        preferences = {
            "total_actions": sum(r.get("count", 0) for r in results),
            "by_action_type": {r["_id"]: r["count"] for r in results}
        }
        
        return preferences


# ========== Ingredient Analysis Repository ==========

class IngredientAnalysisRepository:
    """成分分析结果集合操作"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """创建成分分析记录"""
        collection = get_mongo_collection("ingredient_analyses")
        data["created_at"] = datetime.utcnow()
        result = collection.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取分析结果"""
        collection = get_mongo_collection("ingredient_analyses")
        doc = collection.find_one({"analysis_id": analysis_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    @staticmethod
    def list_by_user(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的分析历史"""
        collection = get_mongo_collection("ingredient_analyses")
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs


# ========== Behavior Analyses Repository ==========

class BehaviorAnalysisRepository:
    """行为分析集合操作"""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """创建行为分析"""
        collection = get_mongo_collection("behavior_analyses")
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        data["status"] = data.get("status", "pending")
        data["severity_level"] = data.get("severity_level", 1)
        result = collection.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取分析"""
        collection = get_mongo_collection("behavior_analyses")
        doc = collection.find_one({"analysis_id": analysis_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    @staticmethod
    def list_by_user(user_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户的行为分析"""
        collection = get_mongo_collection("behavior_analyses")
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def list_by_pet(pet_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """获取宠物的行为分析"""
        collection = get_mongo_collection("behavior_analyses")
        cursor = collection.find({"pet_id": pet_id}).sort("created_at", -1).skip(skip).limit(limit)
        docs = list(cursor)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    
    @staticmethod
    def update(analysis_id: str, update_data: Dict[str, Any]) -> bool:
        """更新分析"""
        collection = get_mongo_collection("behavior_analyses")
        update_data["updated_at"] = datetime.utcnow()
        result = collection.update_one(
            {"analysis_id": analysis_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(analysis_id: str) -> bool:
        """删除分析"""
        collection = get_mongo_collection("behavior_analyses")
        result = collection.delete_one({"analysis_id": analysis_id})
        return result.deleted_count > 0
