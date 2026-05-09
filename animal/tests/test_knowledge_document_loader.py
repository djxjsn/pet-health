"""
文档加载器单元测试
"""
import pytest
import tempfile
import os
from pathlib import Path

from src.core.document_loader import DocumentLoader, Document


class TestDocumentLoader:
    """文档加载器测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def loader(self, temp_dir):
        """创建加载器实例"""
        return DocumentLoader(base_dir=temp_dir)
    
    def test_load_text_file(self, loader, temp_dir):
        """测试加载TXT文件"""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文档")
        
        doc = loader.load_file(test_file, category="disease")
        
        assert isinstance(doc, Document)
        assert doc.content == "这是一个测试文档"
        assert doc.metadata['category'] == 'disease'
        assert doc.metadata['filename'] == 'test.txt'
    
    def test_load_markdown_file(self, loader, temp_dir):
        """测试加载Markdown文件"""
        test_file = os.path.join(temp_dir, "test.md")
        content = "# 标题\n\n这是一段Markdown内容"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        doc = loader.load_file(test_file, category="nutrition")
        
        assert doc.content == content
        assert doc.metadata['category'] == 'nutrition'
    
    def test_load_json_file(self, loader, temp_dir):
        """测试加载JSON文件"""
        import json
        test_file = os.path.join(temp_dir, "test.json")
        data = {"content": "JSON内容", "key": "value"}
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        doc = loader.load_file(test_file, category="behavior")
        
        assert doc.content == "JSON内容"
    
    def test_load_file_not_found(self, loader):
        """测试文件不存在"""
        with pytest.raises(FileNotFoundError):
            loader.load_file("nonexistent.txt", category="disease")
    
    def test_load_unsupported_format(self, loader, temp_dir):
        """测试不支持的文件格式"""
        test_file = os.path.join(temp_dir, "test.pdf")
        with open(test_file, 'w') as f:
            f.write("fake pdf")
        
        with pytest.raises(ValueError):
            loader.load_file(test_file, category="disease")
    
    def test_load_directory(self, loader, temp_dir):
        """测试加载目录"""
        # 创建测试文件
        for i in range(3):
            test_file = os.path.join(temp_dir, f"doc_{i}.txt")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"文档{i}")
        
        docs = loader.load_directory(directory=temp_dir, category="disease")
        
        assert len(docs) == 3
        assert all(doc.metadata['category'] == 'disease' for doc in docs)
    
    def test_document_to_dict(self):
        """测试Document转换为字典"""
        doc = Document(
            content="测试内容",
            metadata={"key": "value"},
            source="test_source"
        )
        
        result = doc.to_dict()
        
        assert result['content'] == '测试内容'
        assert result['metadata'] == {'key': 'value'}
        assert result['source'] == 'test_source'
