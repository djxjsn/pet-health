"""
知识管理相关的Pydantic Schema定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    """创建知识文档请求"""
    title: str = Field(..., max_length=200, description="文档标题")
    content: str = Field(..., description="文档内容")
    category: str = Field(..., description="文档分类: disease/medication/first_aid/nutrition/behavior")
    tags: Optional[List[str]] = Field(default=[], description="标签列表")
    source: Optional[str] = Field(None, description="知识来源")
    status: str = Field(default="draft", description="状态: draft/published/archived")


class KnowledgeDocumentUpdate(BaseModel):
    """更新知识文档请求"""
    title: Optional[str] = Field(None, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    category: Optional[str] = Field(None, description="文档分类: disease/medication/first_aid/nutrition/behavior")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    source: Optional[str] = Field(None, description="知识来源")
    status: Optional[str] = Field(None, description="状态: draft/published/archived")


class KnowledgeDocumentResponse(BaseModel):
    """知识文档响应"""
    model_config = {"populate_by_name": True}
    
    id: str = Field(..., alias="_id", description="MongoDB ID")
    doc_id: str = Field(..., description="文档唯一标识")
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    category: str = Field(..., description="文档分类")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    source: Optional[str] = Field(None, description="知识来源")
    status: str = Field(..., description="状态")
    indexed: bool = Field(..., description="是否已向量化索引")
    indexed_at: Optional[str] = Field(None, description="向量化索引时间")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class KnowledgeDocumentListResponse(BaseModel):
    """知识文档列表响应"""
    total: int = Field(..., description="总数")
    skip: int = Field(..., description="跳过数")
    limit: int = Field(..., description="限制数")
    documents: List[KnowledgeDocumentResponse] = Field(..., description="文档列表")


class KnowledgeSearchRequest(BaseModel):
    """知识检索请求"""
    query: str = Field(..., min_length=1, max_length=500, description="查询文本")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")
    category: Optional[str] = Field(None, description="文档分类过滤")
    tags: Optional[List[str]] = Field(None, description="标签过滤")


class KnowledgeSearchResult(BaseModel):
    """知识检索结果"""
    content: str = Field(..., description="知识内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    distance: Optional[float] = Field(None, description="距离分数（越小越相关）")


class KnowledgeSearchResponse(BaseModel):
    """知识检索响应"""
    query: str = Field(..., description="查询文本")
    total: int = Field(..., description="结果数量")
    results: List[KnowledgeSearchResult] = Field(..., description="检索结果列表")


class KnowledgeIndexStats(BaseModel):
    """知识索引统计响应"""
    vector_db_document_count: int = Field(..., description="向量数据库文档数")
    knowledge_documents: Dict[str, Any] = Field(..., description="知识文档统计")


class KnowledgeIndexRebuildResponse(BaseModel):
    """知识索引重建响应"""
    total: int = Field(..., description="总文档数")
    success: int = Field(..., description="成功数")
    failed: int = Field(..., description="失败数")
    message: Optional[str] = Field(None, description="消息")
