"""
知识更新服务

提供知识库的增量更新、版本管理和定时更新任务功能。
"""
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from src.core.knowledge_indexer import KnowledgeIndexer
from src.repositories.mongo_repositories import KnowledgeRepository
from src.services.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


class KnowledgeUpdateService:
    """知识更新服务"""
    
    @staticmethod
    def calculate_content_hash(content: str) -> str:
        """计算内容哈希值，用于检测内容变更"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def incremental_update() -> Dict[str, Any]:
        """增量更新知识索引
        
        只更新已发布但未索引的文档
        
        Returns:
            更新结果统计
        """
        logger.info("开始增量更新知识索引...")
        
        unindexed_docs = KnowledgeRepository.list_unindexed()
        
        if not unindexed_docs:
            logger.info("没有待更新的文档")
            return {
                "updated": 0,
                "failed": 0,
                "message": "没有待更新的文档"
            }
        
        indexer = KnowledgeIndexer()
        updated = 0
        failed = 0
        failed_docs = []
        
        for doc in unindexed_docs:
            doc_id = doc.get("doc_id")
            try:
                success = indexer.index_document(doc_id)
                if success:
                    updated += 1
                else:
                    failed += 1
                    failed_docs.append(doc_id)
            except Exception as e:
                logger.error(f"更新文档索引失败: {doc_id}, 错误: {e}")
                failed += 1
                failed_docs.append(doc_id)
        
        result = {
            "updated": updated,
            "failed": failed,
            "failed_docs": failed_docs,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"增量更新完成: {result}")
        return result
    
    @staticmethod
    def check_and_update_changed_docs() -> Dict[str, Any]:
        """检查已索引文档的变更并更新
        
        对比已发布文档的内容哈希，更新发生变化的文档
        
        Returns:
            更新结果统计
        """
        logger.info("开始检查文档变更...")
        
        published_docs = KnowledgeRepository.list_published(limit=1000)
        
        indexer = KnowledgeIndexer()
        updated = 0
        unchanged = 0
        failed = 0
        
        for doc in published_docs:
            if not doc.get("indexed"):
                continue
            
            doc_id = doc.get("doc_id")
            content = doc.get("content", "")
            current_hash = KnowledgeUpdateService.calculate_content_hash(content)
            
            stored_hash = doc.get("content_hash")
            
            if stored_hash and stored_hash != current_hash:
                logger.info(f"检测到文档变更: {doc_id}")
                try:
                    indexer.remove_document_index(doc_id)
                    success = indexer.index_document(doc_id)
                    
                    if success:
                        KnowledgeRepository.update(doc_id, {
                            "content_hash": current_hash
                        })
                        updated += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"更新文档失败: {doc_id}, 错误: {e}")
                    failed += 1
            else:
                unchanged += 1
        
        result = {
            "total_checked": len(published_docs),
            "updated": updated,
            "unchanged": unchanged,
            "failed": failed,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"文档变更检查完成: {result}")
        return result
    
    @staticmethod
    def batch_publish_and_index(doc_ids: List[str]) -> Dict[str, Any]:
        """批量发布文档并索引
        
        Args:
            doc_ids: 要发布的文档ID列表
        
        Returns:
            批量操作结果
        """
        logger.info(f"开始批量发布并索引 {len(doc_ids)} 个文档...")
        
        indexer = KnowledgeIndexer()
        published = 0
        indexed = 0
        failed = 0
        failed_docs = []
        
        for doc_id in doc_ids:
            try:
                publish_success = KnowledgeService.publish_document(doc_id)
                if publish_success:
                    published += 1
                    
                    index_success = indexer.index_document(doc_id)
                    if index_success:
                        indexed += 1
                    else:
                        failed += 1
                        failed_docs.append(doc_id)
                else:
                    failed += 1
                    failed_docs.append(doc_id)
            except Exception as e:
                logger.error(f"批量发布失败: {doc_id}, 错误: {e}")
                failed += 1
                failed_docs.append(doc_id)
        
        result = {
            "total": len(doc_ids),
            "published": published,
            "indexed": indexed,
            "failed": failed,
            "failed_docs": failed_docs,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"批量发布完成: {result}")
        return result
    
    @staticmethod
    def get_update_history() -> Dict[str, Any]:
        """获取更新统计信息
        
        Returns:
            更新统计信息
        """
        total_docs = KnowledgeRepository.count()
        published_docs = KnowledgeRepository.count(status="published")
        indexed_docs = KnowledgeRepository.count(status="published")
        
        indexer = KnowledgeIndexer()
        stats = indexer.get_index_stats()
        
        return {
            "total_documents": total_docs,
            "published_documents": published_docs,
            "indexed_documents": indexed_docs,
            "vector_db_count": stats.get("vector_db_document_count", 0),
            "last_checked": datetime.utcnow().isoformat()
        }


def get_knowledge_update_service() -> KnowledgeUpdateService:
    """获取知识更新服务实例"""
    return KnowledgeUpdateService()
