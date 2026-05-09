"""
知识检索器单元测试
"""
import pytest
from unittest.mock import Mock, patch

from src.core.knowledge_retriever import KnowledgeRetriever


class TestKnowledgeRetriever:
    """知识检索器测试"""
    
    @pytest.fixture
    def retriever(self):
        """创建检索器实例"""
        with patch('src.core.knowledge_retriever.get_vector_db'):
            retriever = KnowledgeRetriever(default_top_k=3)
            retriever.vector_db = Mock()
            return retriever
    
    def test_search_basic(self, retriever):
        """测试基本检索"""
        mock_results = {
            'documents': [['狗需要定期接种疫苗', '猫的饮食需要注意营养']],
            'metadatas': [[
                {'category': 'disease', 'doc_id': 'doc1'},
                {'category': 'nutrition', 'doc_id': 'doc2'}
            ]],
            'distances': [[0.1, 0.2]]
        }
        
        retriever.vector_db.query.return_value = mock_results
        
        results = retriever.search(query="宠物健康")
        
        assert len(results) == 2
        assert results[0]['content'] == '狗需要定期接种疫苗'
        assert results[0]['metadata']['category'] == 'disease'
        assert results[0]['distance'] == 0.1
    
    def test_search_with_category_filter(self, retriever):
        """测试按分类过滤"""
        retriever.search(query="宠物疫苗", category="disease")
        
        retriever.vector_db.query.assert_called_once()
        call_args = retriever.vector_db.query.call_args
        assert call_args[1]['where']['category'] == 'disease'
    
    def test_search_empty_results(self, retriever):
        """测试空结果"""
        retriever.vector_db.query.return_value = {'documents': [[]]}
        
        results = retriever.search(query="不相关内容")
        
        assert len(results) == 0
    
    def test_search_by_category(self, retriever):
        """测试按分类检索"""
        mock_results = {
            'documents': [['犬瘟热症状']],
            'metadatas': [[{'category': 'disease'}]],
            'distances': [[0.05]]
        }
        
        retriever.vector_db.query.return_value = mock_results
        
        results = retriever.search_by_category(
            query="犬瘟热",
            category="disease"
        )
        
        assert len(results) == 1
        assert results[0]['metadata']['category'] == 'disease'
