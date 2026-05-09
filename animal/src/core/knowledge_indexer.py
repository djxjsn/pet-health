"""
知识索引构建器

负责将知识文档分块并向量化存储到ChromaDB中。
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from src.core.vector_db import get_vector_db
from src.core.document_loader import DocumentLoader, Document
from src.core.text_chunker import TextChunker
from src.repositories.mongo_repositories import KnowledgeRepository
from src.services.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)


class KnowledgeIndexer:
    """知识索引构建器"""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        chunk_strategy: str = "semantic"
    ):
        """初始化索引构建器
        
        Args:
            chunk_size: 分块大小
            chunk_overlap: 分块重叠大小
            chunk_strategy: 分块策略（fixed/semantic/overlap）
        """
        self.vector_db = get_vector_db()
        self.document_loader = DocumentLoader()
        self.chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=chunk_strategy
        )
    
    def index_document(self, doc_id: str) -> bool:
        """索引单个知识文档
        
        Args:
            doc_id: 知识文档的唯一标识
        
        Returns:
            是否索引成功
        """
        doc = KnowledgeRepository.get_by_doc_id(doc_id)
        if not doc:
            logger.error(f"文档不存在: {doc_id}")
            return False
        
        if doc.get("status") != "published":
            logger.warning(f"文档未发布，跳过索引: {doc_id}")
            return False
        
        content = doc.get("content", "")
        if not content:
            logger.warning(f"文档内容为空: {doc_id}")
            return False
        
        metadata = {
            "doc_id": doc_id,
            "title": doc.get("title", ""),
            "category": doc.get("category", ""),
            "tags": doc.get("tags", []),
            "source": doc.get("source", "")
        }
        
        try:
            chunks = self.chunker.chunk_text(
                text=content,
                metadata=metadata,
                doc_id=doc_id
            )
            
            if not chunks:
                logger.warning(f"文档分块结果为空: {doc_id}")
                return False
            
            documents = []
            chunk_ids = []
            metadatas = []
            
            for chunk in chunks:
                chunk_metadata = chunk.metadata.copy()
                chunk_metadata["chunk_index"] = chunk.index
                chunk_metadata["total_chunks"] = chunk.total_chunks
                
                documents.append(chunk.content)
                chunk_ids.append(chunk.chunk_id)
                metadatas.append(chunk_metadata)
            
            self.vector_db.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            KnowledgeRepository.mark_indexed(doc_id)
            
            logger.info(f"成功索引文档: {doc_id}, 分块数: {len(chunks)}")
            return True
            
        except Exception as e:
            logger.error(f"索引文档失败: {doc_id}, 错误: {e}")
            return False
    
    def index_all_documents(self) -> Dict[str, Any]:
        """索引所有未索引的已发布文档
        
        Returns:
            包含索引统计信息的字典
        """
        unindexed_docs = KnowledgeRepository.list_unindexed()
        
        if not unindexed_docs:
            logger.info("没有待索引的文档")
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "message": "没有待索引的文档"
            }
        
        total = len(unindexed_docs)
        success = 0
        failed = 0
        failed_docs = []
        
        logger.info(f"开始索引 {total} 个文档...")
        
        for doc in unindexed_docs:
            doc_id = doc.get("doc_id")
            if self.index_document(doc_id):
                success += 1
            else:
                failed += 1
                failed_docs.append(doc_id)
        
        result = {
            "total": total,
            "success": success,
            "failed": failed,
            "failed_docs": failed_docs,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"索引完成: {result}")
        return result
    
    def rebuild_index(self) -> Dict[str, Any]:
        """重建整个知识索引（清空后重新索引）
        
        Returns:
            包含重建统计信息的字典
        """
        logger.info("开始重建知识索引...")
        
        try:
            self.vector_db.reset_collection()
            logger.info("已清空向量数据库集合")
            
            KnowledgeRepository.update_all_indexed(False)
            
            return self.index_all_documents()
            
        except Exception as e:
            logger.error(f"重建索引失败: {e}")
            return {
                "total": 0,
                "success": 0,
                "failed": 1,
                "error": str(e)
            }
    
    def remove_document_index(self, doc_id: str) -> bool:
        """移除单个文档的向量索引
        
        Args:
            doc_id: 知识文档的唯一标识
        
        Returns:
            是否移除成功
        """
        doc = KnowledgeRepository.get_by_doc_id(doc_id)
        if not doc:
            logger.error(f"文档不存在: {doc_id}")
            return False
        
        content = doc.get("content", "")
        metadata = {"doc_id": doc_id}
        
        try:
            chunks = self.chunker.chunk_text(
                text=content,
                metadata=metadata,
                doc_id=doc_id
            )
            
            chunk_ids = [chunk.chunk_id for chunk in chunks]
            
            if chunk_ids:
                self.vector_db.delete_documents(ids=chunk_ids)
                logger.info(f"已移除文档索引: {doc_id}, 分块数: {len(chunk_ids)}")
            
            KnowledgeRepository.update(doc_id, {
                "indexed": False,
                "indexed_at": None
            })
            
            return True
            
        except Exception as e:
            logger.error(f"移除文档索引失败: {doc_id}, 错误: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息
        
        Returns:
            包含索引统计的字典
        """
        vector_count = self.vector_db.get_document_count()
        
        doc_stats = KnowledgeService.get_document_stats()
        
        return {
            "vector_db_document_count": vector_count,
            "knowledge_documents": doc_stats
        }


def get_knowledge_indexer() -> KnowledgeIndexer:
    """获取知识索引构建器实例"""
    return KnowledgeIndexer()
