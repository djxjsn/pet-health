"""
知识管理API路由

提供知识文档的CRUD操作和知识检索接口。
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
import logging

from src.api.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    KnowledgeDocumentListResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
    KnowledgeIndexStats,
    KnowledgeIndexRebuildResponse
)
from src.services.knowledge_service import KnowledgeService
from src.core.knowledge_indexer import KnowledgeIndexer
from src.core.knowledge_retriever import KnowledgeRetriever
from src.services.knowledge_update_service import KnowledgeUpdateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["知识管理"])


@router.post("/search", response_model=KnowledgeSearchResponse, summary="知识检索")
async def search_knowledge(request: KnowledgeSearchRequest):
    """
    基于语义检索相关知识
    
    - **query**: 查询文本
    - **top_k**: 返回结果数量（1-20）
    - **category**: 按文档分类过滤（disease/medication/first_aid/nutrition/behavior）
    - **tags**: 按标签过滤
    """
    try:
        retriever = KnowledgeRetriever(default_top_k=request.top_k)
        
        results = retriever.search(
            query=request.query,
            top_k=request.top_k,
            category=request.category,
            tags=request.tags
        )
        
        formatted_results = [
            KnowledgeSearchResult(
                content=result.get("content", ""),
                metadata=result.get("metadata", {}),
                distance=result.get("distance")
            )
            for result in results
        ]
        
        return KnowledgeSearchResponse(
            query=request.query,
            total=len(formatted_results),
            results=formatted_results
        )
    except Exception as e:
        logger.error(f"知识检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"知识检索失败: {str(e)}")


@router.get("/documents", response_model=KnowledgeDocumentListResponse, summary="获取知识文档列表")
async def list_documents(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    category: Optional[str] = Query(None, description="文档分类过滤"),
    status: Optional[str] = Query(None, description="文档状态过滤")
):
    """获取知识文档列表，支持分类和状态过滤"""
    try:
        documents = KnowledgeService.list_documents(
            skip=skip,
            limit=limit,
            category=category,
            status=status
        )
        
        total = KnowledgeService.get_document_stats()["total"]
        
        return KnowledgeDocumentListResponse(
            total=total,
            skip=skip,
            limit=limit,
            documents=documents
        )
    except Exception as e:
        logger.error(f"获取知识文档列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")


@router.post("/documents", response_model=KnowledgeDocumentResponse, summary="创建知识文档")
async def create_document(document: KnowledgeDocumentCreate):
    """创建新的知识文档"""
    try:
        doc_id = KnowledgeService.create_document(
            title=document.title,
            content=document.content,
            category=document.category,
            tags=document.tags,
            source=document.source,
            status=document.status
        )
        
        doc = KnowledgeService.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=500, detail="文档创建失败")
        
        return KnowledgeDocumentResponse(**doc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建知识文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建文档失败: {str(e)}")


@router.get("/documents/{doc_id}", response_model=KnowledgeDocumentResponse, summary="获取知识文档")
async def get_document(doc_id: str):
    """获取单个知识文档详情"""
    try:
        doc = KnowledgeService.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        return KnowledgeDocumentResponse(**doc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文档失败: {str(e)}")


@router.put("/documents/{doc_id}", response_model=KnowledgeDocumentResponse, summary="更新知识文档")
async def update_document(doc_id: str, document: KnowledgeDocumentUpdate):
    """更新知识文档"""
    try:
        existing = KnowledgeService.get_document(doc_id)
        if not existing:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        success = KnowledgeService.update_document(
            doc_id=doc_id,
            title=document.title,
            content=document.content,
            category=document.category,
            tags=document.tags,
            source=document.source,
            status=document.status
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="文档更新失败")
        
        updated_doc = KnowledgeService.get_document(doc_id)
        return KnowledgeDocumentResponse(**updated_doc)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新知识文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新文档失败: {str(e)}")


@router.delete("/documents/{doc_id}", summary="删除知识文档")
async def delete_document(doc_id: str):
    """删除知识文档"""
    try:
        existing = KnowledgeService.get_document(doc_id)
        if not existing:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        indexer = KnowledgeIndexer()
        indexer.remove_document_index(doc_id)
        
        success = KnowledgeService.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=500, detail="文档删除失败")
        
        return {"message": "文档删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")


@router.post("/documents/{doc_id}/publish", response_model=KnowledgeDocumentResponse, summary="发布知识文档")
async def publish_document(doc_id: str):
    """发布知识文档（发布后等待索引）"""
    try:
        existing = KnowledgeService.get_document(doc_id)
        if not existing:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        success = KnowledgeService.publish_document(doc_id)
        if not success:
            raise HTTPException(status_code=500, detail="文档发布失败")
        
        updated_doc = KnowledgeService.get_document(doc_id)
        return KnowledgeDocumentResponse(**updated_doc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发布知识文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"发布文档失败: {str(e)}")


@router.post("/index/rebuild", response_model=KnowledgeIndexRebuildResponse, summary="重建知识索引")
async def rebuild_index():
    """重建整个知识索引（清空后重新索引所有已发布文档）"""
    try:
        indexer = KnowledgeIndexer()
        result = indexer.rebuild_index()
        
        return KnowledgeIndexRebuildResponse(
            total=result.get("total", 0),
            success=result.get("success", 0),
            failed=result.get("failed", 0),
            message=result.get("message")
        )
    except Exception as e:
        logger.error(f"重建索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"重建索引失败: {str(e)}")


@router.post("/index/update", summary="增量更新知识索引")
async def update_index():
    """索引所有未索引的已发布文档"""
    try:
        indexer = KnowledgeIndexer()
        result = indexer.index_all_documents()
        
        return {
            "total": result.get("total", 0),
            "success": result.get("success", 0),
            "failed": result.get("failed", 0),
            "completed_at": result.get("completed_at")
        }
    except Exception as e:
        logger.error(f"更新索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新索引失败: {str(e)}")


@router.get("/index/stats", response_model=KnowledgeIndexStats, summary="获取索引统计")
async def get_index_stats():
    """获取知识索引统计信息"""
    try:
        indexer = KnowledgeIndexer()
        stats = indexer.get_index_stats()
        
        return KnowledgeIndexStats(**stats)
    except Exception as e:
        logger.error(f"获取索引统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.post("/update/incremental", summary="增量更新")
async def incremental_update():
    """增量更新所有已发布但未索引的文档"""
    try:
        update_service = KnowledgeUpdateService()
        result = update_service.incremental_update()
        
        return result
    except Exception as e:
        logger.error(f"增量更新失败: {e}")
        raise HTTPException(status_code=500, detail=f"增量更新失败: {str(e)}")


@router.post("/update/check-changes", summary="检查文档变更")
async def check_and_update_changes():
    """检查已索引文档的变更并自动更新"""
    try:
        update_service = KnowledgeUpdateService()
        result = update_service.check_and_update_changed_docs()
        
        return result
    except Exception as e:
        logger.error(f"检查文档变更失败: {e}")
        raise HTTPException(status_code=500, detail=f"检查文档变更失败: {str(e)}")


@router.post("/update/batch-publish", summary="批量发布并索引")
async def batch_publish_and_index(doc_ids: List[str]):
    """批量发布文档并自动索引
    
    - **doc_ids**: 要发布的文档唯一标识列表
    """
    try:
        update_service = KnowledgeUpdateService()
        result = update_service.batch_publish_and_index(doc_ids)
        
        return result
    except Exception as e:
        logger.error(f"批量发布失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量发布失败: {str(e)}")


@router.get("/update/history", summary="获取更新历史")
async def get_update_history():
    """获取知识库更新统计信息"""
    try:
        update_service = KnowledgeUpdateService()
        result = update_service.get_update_history()
        
        return result
    except Exception as e:
        logger.error(f"获取更新历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取更新历史失败: {str(e)}")
