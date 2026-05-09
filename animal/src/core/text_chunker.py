"""
文本分块器

提供多种文本分块策略，将长文档分割为适合向量化的短文本块。
"""
import re
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TextChunk:
    """文本块数据类"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    index: int
    total_chunks: int
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "chunk_id": self.chunk_id,
            "index": self.index,
            "total_chunks": self.total_chunks
        }


class TextChunker:
    """文本分块器"""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        strategy: str = "semantic"
    ):
        """初始化分块器
        
        Args:
            chunk_size: 每块的目标大小（token数或字符数）
            chunk_overlap: 块之间的重叠大小
            strategy: 分块策略（fixed/semantic/overlap）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        
        valid_strategies = ["fixed", "semantic", "overlap"]
        if strategy not in valid_strategies:
            raise ValueError(f"无效的分块策略: {strategy}，必须是 {valid_strategies} 之一")
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> List[TextChunk]:
        """对文本进行分块
        
        Args:
            text: 待分块的文本
            metadata: 元数据
            doc_id: 文档ID，用于生成chunk_id
        
        Returns:
            TextChunk列表
        """
        if self.strategy == "fixed":
            return self._fixed_size_chunk(text, metadata, doc_id)
        elif self.strategy == "semantic":
            return self._semantic_chunk(text, metadata, doc_id)
        elif self.strategy == "overlap":
            return self._overlap_chunk(text, metadata, doc_id)
        else:
            raise ValueError(f"不支持的分块策略: {self.strategy}")
    
    def _fixed_size_chunk(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> List[TextChunk]:
        """固定大小分块"""
        chunks = []
        text_length = len(text)
        
        for i in range(0, text_length, self.chunk_size):
            chunk_content = text[i:i + self.chunk_size]
            
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata["chunk_strategy"] = "fixed"
            
            chunk_id = self._generate_chunk_id(doc_id, i, chunk_content)
            
            chunks.append(TextChunk(
                content=chunk_content,
                metadata=chunk_metadata,
                chunk_id=chunk_id,
                index=len(chunks),
                total_chunks=0  # 后续更新
            ))
        
        total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total
        
        return chunks
    
    def _semantic_chunk(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> List[TextChunk]:
        """语义分块（按段落/标题分割）"""
        chunks = []
        
        # 按Markdown标题分割
        sections = re.split(r'(?=^#{1,6}\s+)', text, flags=re.MULTILINE)
        
        current_section = ""
        for section in sections:
            if len(current_section) + len(section) <= self.chunk_size:
                current_section += section
            else:
                if current_section.strip():
                    chunk_metadata = metadata.copy() if metadata else {}
                    chunk_metadata["chunk_strategy"] = "semantic"
                    
                    chunk_id = self._generate_chunk_id(doc_id, len(chunks), current_section)
                    
                    chunks.append(TextChunk(
                        content=current_section.strip(),
                        metadata=chunk_metadata,
                        chunk_id=chunk_id,
                        index=len(chunks),
                        total_chunks=0
                    ))
                current_section = section
        
        if current_section.strip():
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata["chunk_strategy"] = "semantic"
            
            chunk_id = self._generate_chunk_id(doc_id, len(chunks), current_section)
            
            chunks.append(TextChunk(
                content=current_section.strip(),
                metadata=chunk_metadata,
                chunk_id=chunk_id,
                index=len(chunks),
                total_chunks=0
            ))
        
        total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total
        
        return chunks
    
    def _overlap_chunk(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> List[TextChunk]:
        """重叠分块"""
        chunks = []
        text_length = len(text)
        step = self.chunk_size - self.chunk_overlap
        
        if step <= 0:
            raise ValueError(f"chunk_size ({self.chunk_size}) 必须大于 chunk_overlap ({self.chunk_overlap})")
        
        for i in range(0, text_length, step):
            chunk_content = text[i:i + self.chunk_size]
            
            if not chunk_content.strip():
                break
            
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata["chunk_strategy"] = "overlap"
            
            chunk_id = self._generate_chunk_id(doc_id, i, chunk_content)
            
            chunks.append(TextChunk(
                content=chunk_content,
                metadata=chunk_metadata,
                chunk_id=chunk_id,
                index=len(chunks),
                total_chunks=0
            ))
            
            if i + self.chunk_size >= text_length:
                break
        
        total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total
        
        return chunks
    
    def _generate_chunk_id(self, doc_id: Optional[str], position: int, content: str) -> str:
        """生成唯一的chunk_id
        
        使用SHA256 + 更多位数避免碰撞，包含内容摘要确保唯一性
        """
        if doc_id:
            hash_input = f"{doc_id}_{position}_{content[:200]}"
        else:
            hash_input = f"{position}_{content[:200]}"
        
        hash_value = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()[:16]
        return f"chunk_{hash_value}"
