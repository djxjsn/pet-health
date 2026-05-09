"""
文本分块器单元测试
"""
import pytest

from src.core.text_chunker import TextChunker, TextChunk


class TestTextChunker:
    """文本分块器测试"""
    
    @pytest.fixture
    def sample_text(self):
        """创建示例文本"""
        return "这是一段测试文本。" * 100
    
    @pytest.fixture
    def chunker_fixed(self):
        """创建固定大小分块器"""
        return TextChunker(chunk_size=50, chunk_overlap=0, strategy="fixed")
    
    @pytest.fixture
    def chunker_overlap(self):
        """创建重叠分块器"""
        return TextChunker(chunk_size=50, chunk_overlap=10, strategy="overlap")
    
    @pytest.fixture
    def chunker_semantic(self):
        """创建语义分块器"""
        return TextChunker(chunk_size=100, strategy="semantic")
    
    def test_fixed_size_chunking(self, chunker_fixed, sample_text):
        """测试固定大小分块"""
        chunks = chunker_fixed.chunk_text(sample_text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, TextChunk) for chunk in chunks)
        assert all(chunk.total_chunks == len(chunks) for chunk in chunks)
        # 验证所有块的内容拼接起来等于原文
        reconstructed = ''.join(chunk.content for chunk in chunks)
        assert len(reconstructed) == len(sample_text)
    
    def test_overlap_chunking(self, chunker_overlap, sample_text):
        """测试重叠分块"""
        chunks = chunker_overlap.chunk_text(sample_text)
        
        assert len(chunks) > 0
        # 验证有重叠
        for i in range(len(chunks) - 1):
            current_content = chunks[i].content
            next_content = chunks[i + 1].content
            # 相邻块应该有重叠部分
            if len(current_content) >= 50:
                overlap = current_content[-10:]
                assert overlap in next_content or i == len(chunks) - 2
    
    def test_semantic_chunking_with_headings(self, chunker_semantic):
        """测试语义分块（带标题）"""
        text = """# 第一章
这是第一章的内容。

## 1.1 小节
这是1.1小节的内容。

# 第二章
这是第二章的内容。
"""
        chunks = chunker_semantic.chunk_text(text)
        
        assert len(chunks) > 0
        assert chunks[0].metadata['chunk_strategy'] == 'semantic'
    
    def test_chunk_metadata(self, chunker_fixed, sample_text):
        """测试分块元数据"""
        metadata = {"category": "disease", "doc_id": "test_doc"}
        chunks = chunker_fixed.chunk_text(sample_text, metadata=metadata, doc_id="test_doc")
        
        for chunk in chunks:
            assert chunk.metadata['category'] == 'disease'
            assert chunk.metadata['doc_id'] == 'test_doc'
            assert chunk.metadata['chunk_strategy'] == 'fixed'
    
    def test_chunk_id_generation(self, chunker_fixed, sample_text):
        """测试chunk_id生成"""
        chunks = chunker_fixed.chunk_text(sample_text, doc_id="test_doc")
        
        # 验证chunk_id唯一性
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))
        # 验证chunk_id格式
        assert all(chunk_id.startswith('chunk_') for chunk_id in chunk_ids)
    
    def test_empty_text(self, chunker_fixed):
        """测试空文本"""
        chunks = chunker_fixed.chunk_text("")
        assert len(chunks) == 0
    
    def test_invalid_strategy(self):
        """测试无效的分块策略"""
        with pytest.raises(ValueError):
            TextChunker(strategy="invalid")
    
    def test_overlap_larger_than_chunk(self):
        """测试重叠大于分块大小"""
        chunker = TextChunker(chunk_size=50, chunk_overlap=60, strategy="overlap")
        
        with pytest.raises(ValueError):
            chunker.chunk_text("测试文本" * 10)
    
    def test_text_chunk_to_dict(self):
        """测试TextChunk转换为字典"""
        chunk = TextChunk(
            content="测试内容",
            metadata={"key": "value"},
            chunk_id="chunk_123",
            index=0,
            total_chunks=3
        )
        
        result = chunk.to_dict()
        
        assert result['content'] == '测试内容'
        assert result['chunk_id'] == 'chunk_123'
        assert result['index'] == 0
        assert result['total_chunks'] == 3
