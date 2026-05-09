"""
知识管理服务层

提供知识文档的业务逻辑处理，包括文档验证、状态管理等功能。
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.repositories.mongo_repositories import KnowledgeRepository


class KnowledgeService:
    """知识管理服务"""
    
    @staticmethod
    def create_document(
        title: str,
        content: str,
        category: str,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        status: str = "draft"
    ) -> str:
        """创建知识文档
        
        Args:
            title: 文档标题
            content: 文档内容
            category: 文档分类（disease/medication/first_aid/nutrition/behavior）
            tags: 标签列表
            source: 知识来源
            status: 文档状态（draft/published/archived）
        
        Returns:
            文档唯一标识（doc_id）
        
        Raises:
            ValueError: 当分类或状态无效时
        """
        valid_categories = ["disease", "medication", "first_aid", "nutrition", "behavior"]
        if category not in valid_categories:
            raise ValueError(f"无效的文档分类: {category}，必须是 {valid_categories} 之一")
        
        valid_statuses = ["draft", "published", "archived"]
        if status not in valid_statuses:
            raise ValueError(f"无效的文档状态: {status}，必须是 {valid_statuses} 之一")
        
        doc_id = f"knowledge_{category}_{uuid.uuid4().hex[:8]}"
        
        data = {
            "doc_id": doc_id,
            "title": title,
            "content": content,
            "category": category,
            "tags": tags or [],
            "source": source,
            "status": status,
            "indexed": False,
            "indexed_at": None
        }
        
        KnowledgeRepository.create(data)
        return doc_id
    
    @staticmethod
    def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
        """获取知识文档
        
        Args:
            doc_id: 文档唯一标识
        
        Returns:
            文档数据字典，不存在则返回None
        """
        return KnowledgeRepository.get_by_doc_id(doc_id)
    
    @staticmethod
    def list_documents(
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取知识文档列表
        
        Args:
            skip: 跳过数量
            limit: 返回数量
            category: 文档分类过滤
            status: 文档状态过滤
        
        Returns:
            文档列表
        """
        return KnowledgeRepository.list_all(skip=skip, limit=limit, category=category, status=status)
    
    @staticmethod
    def update_document(
        doc_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        status: Optional[str] = None
    ) -> bool:
        """更新知识文档
        
        Args:
            doc_id: 文档唯一标识
            title: 新标题
            content: 新内容
            category: 新分类
            tags: 新标签
            source: 新知识来源
            status: 新状态
        
        Returns:
            是否更新成功
        """
        existing = KnowledgeRepository.get_by_doc_id(doc_id)
        if not existing:
            return False
        
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if content is not None:
            update_data["content"] = content
        if category is not None:
            valid_categories = ["disease", "medication", "first_aid", "nutrition", "behavior"]
            if category not in valid_categories:
                raise ValueError(f"无效的文档分类: {category}")
            update_data["category"] = category
        if tags is not None:
            update_data["tags"] = tags
        if source is not None:
            update_data["source"] = source
        if status is not None:
            valid_statuses = ["draft", "published", "archived"]
            if status not in valid_statuses:
                raise ValueError(f"无效的文档状态: {status}")
            update_data["status"] = status
            update_data["indexed"] = False
            update_data["indexed_at"] = None
        
        if update_data:
            return KnowledgeRepository.update(doc_id, update_data)
        return False
    
    @staticmethod
    def publish_document(doc_id: str) -> bool:
        """发布知识文档
        
        Args:
            doc_id: 文档唯一标识
        
        Returns:
            是否发布成功
        """
        existing = KnowledgeRepository.get_by_doc_id(doc_id)
        if not existing:
            return False
        
        return KnowledgeRepository.update(doc_id, {
            "status": "published",
            "indexed": False,
            "indexed_at": None
        })
    
    @staticmethod
    def archive_document(doc_id: str) -> bool:
        """归档知识文档
        
        Args:
            doc_id: 文档唯一标识
        
        Returns:
            是否归档成功
        """
        return KnowledgeRepository.update(doc_id, {"status": "archived"})
    
    @staticmethod
    def delete_document(doc_id: str) -> bool:
        """删除知识文档
        
        Args:
            doc_id: 文档唯一标识
        
        Returns:
            是否删除成功
        """
        return KnowledgeRepository.delete(doc_id)
    
    @staticmethod
    def get_document_stats() -> Dict[str, Any]:
        """获取知识文档统计信息
        
        Returns:
            包含各类文档数量的字典
        """
        return {
            "total": KnowledgeRepository.count(),
            "by_status": {
                "draft": KnowledgeRepository.count(status="draft"),
                "published": KnowledgeRepository.count(status="published"),
                "archived": KnowledgeRepository.count(status="archived"),
            },
            "by_category": {
                "disease": KnowledgeRepository.count(category="disease"),
                "medication": KnowledgeRepository.count(category="medication"),
                "first_aid": KnowledgeRepository.count(category="first_aid"),
                "nutrition": KnowledgeRepository.count(category="nutrition"),
                "behavior": KnowledgeRepository.count(category="behavior"),
            }
        }
