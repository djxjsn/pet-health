"""
Phase 1 回归测试

验证P0紧急修复的正确性：
1. 嵌入模型降级Bug修复 - 确保不使用DefaultEmbeddingFunction
2. 统一检索入口 - 确保所有检索通过KnowledgeRetriever
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
import tempfile
import os


class TestEmbeddingDegradationFix:
    """嵌入模型降级Bug修复测试"""

    @pytest.fixture(autouse=True)
    def reset_singleton(self, monkeypatch):
        """每个测试前重置VectorDatabase单例"""
        from src.core.vector_db import VectorDatabase
        VectorDatabase._instance = None
        yield
        VectorDatabase._instance = None

    def test_no_default_embedding_function_on_network_failure(self, monkeypatch):
        """验证网络不可用时不使用DefaultEmbeddingFunction"""
        from src.core.vector_db import VectorDatabase

        monkeypatch.setenv("CHROMA_PERSIST_DIR", tempfile.mkdtemp())
        monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_degradation")
        monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        with patch('src.core.vector_db._check_internet_connection', return_value=False), \
             patch('src.core.vector_db._check_local_model_cache', return_value=False):
            db = VectorDatabase()

            assert db.embedding_function is None
            assert db._embedding_available is False
            assert db.is_available is False

    def test_query_raises_error_when_unavailable(self, monkeypatch):
        """验证嵌入不可用时query操作抛出RuntimeError"""
        from src.core.vector_db import VectorDatabase

        monkeypatch.setenv("CHROMA_PERSIST_DIR", tempfile.mkdtemp())
        monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_query_error")
        monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        with patch('src.core.vector_db._check_internet_connection', return_value=False), \
             patch('src.core.vector_db._check_local_model_cache', return_value=False):
            db = VectorDatabase()

            with pytest.raises(RuntimeError, match="嵌入模型不可用"):
                db.query(query_texts=["测试查询"], n_results=3)

    def test_add_documents_raises_error_when_unavailable(self, monkeypatch):
        """验证嵌入不可用时add_documents操作抛出RuntimeError"""
        from src.core.vector_db import VectorDatabase

        monkeypatch.setenv("CHROMA_PERSIST_DIR", tempfile.mkdtemp())
        monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_add_error")
        monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        with patch('src.core.vector_db._check_internet_connection', return_value=False), \
             patch('src.core.vector_db._check_local_model_cache', return_value=False):
            db = VectorDatabase()

            with pytest.raises(RuntimeError, match="嵌入模型不可用"):
                db.add_documents(documents=["测试文档"], ids=["test_1"])

    def test_update_documents_raises_error_when_unavailable(self, monkeypatch):
        """验证嵌入不可用时update_documents操作抛出RuntimeError"""
        from src.core.vector_db import VectorDatabase

        monkeypatch.setenv("CHROMA_PERSIST_DIR", tempfile.mkdtemp())
        monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_update_error")
        monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        with patch('src.core.vector_db._check_internet_connection', return_value=False), \
             patch('src.core.vector_db._check_local_model_cache', return_value=False):
            db = VectorDatabase()

            with pytest.raises(RuntimeError, match="嵌入模型不可用"):
                db.update_documents(ids=["test_1"], documents=["更新文档"])

    def test_local_cache_used_when_available(self, monkeypatch):
        """验证本地缓存可用时优先使用本地模型"""
        from src.core.vector_db import VectorDatabase

        tmp_dir = tempfile.mkdtemp()
        monkeypatch.setenv("CHROMA_PERSIST_DIR", tmp_dir)
        monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_local_cache")
        monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        mock_ef = Mock()
        mock_ef.name.return_value = "mock_embedding"

        with patch('src.core.vector_db._check_local_model_cache', return_value=True), \
             patch('src.core.vector_db._check_internet_connection', return_value=False), \
             patch('src.core.vector_db.embedding_functions.SentenceTransformerEmbeddingFunction', return_value=mock_ef), \
             patch.object(VectorDatabase, '_get_or_create_collection', return_value=Mock()):
            db = VectorDatabase()

            assert db.embedding_function is mock_ef
            assert db._embedding_available is True
            assert db.is_available is True

    def test_delete_documents_works_when_unavailable(self, monkeypatch):
        """验证嵌入不可用时delete_documents仍可工作（不需要嵌入）"""
        from src.core.vector_db import VectorDatabase

        monkeypatch.setenv("CHROMA_PERSIST_DIR", tempfile.mkdtemp())
        monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_delete_ok")
        monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        with patch('src.core.vector_db._check_internet_connection', return_value=False), \
             patch('src.core.vector_db._check_local_model_cache', return_value=False):
            db = VectorDatabase()
            db.collection = Mock()

            db.delete_documents(ids=["test_1"])
            db.collection.delete.assert_called_once_with(ids=["test_1"])

    def test_get_document_count_works_when_unavailable(self, monkeypatch):
        """验证嵌入不可用时get_document_count仍可工作"""
        from src.core.vector_db import VectorDatabase

        monkeypatch.setenv("CHROMA_PERSIST_DIR", tempfile.mkdtemp())
        monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_count_ok")
        monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        with patch('src.core.vector_db._check_internet_connection', return_value=False), \
             patch('src.core.vector_db._check_local_model_cache', return_value=False):
            db = VectorDatabase()
            db.collection = Mock()
            db.collection.count.return_value = 42

            assert db.get_document_count() == 42


class TestUnifiedRetrievalEntry:
    """统一检索入口测试"""

    @pytest.fixture
    def mock_retriever(self):
        """创建mock检索器"""
        with patch('src.core.knowledge_retriever.get_vector_db') as mock_vdb:
            mock_vdb_instance = Mock()
            mock_vdb_instance.is_available = True
            mock_vdb.return_value = mock_vdb_instance

            from src.core.knowledge_retriever import KnowledgeRetriever
            retriever = KnowledgeRetriever(default_top_k=3)
            retriever.vector_db = mock_vdb_instance
            return retriever

    def test_search_returns_empty_when_unavailable(self):
        """验证嵌入不可用时检索返回空列表"""
        with patch('src.core.knowledge_retriever.get_vector_db') as mock_vdb:
            mock_vdb_instance = Mock()
            mock_vdb_instance.is_available = False
            mock_vdb.return_value = mock_vdb_instance

            from src.core.knowledge_retriever import KnowledgeRetriever
            retriever = KnowledgeRetriever()

            results = retriever.search(query="宠物健康")
            assert results == []

    def test_search_with_category_filter(self, mock_retriever):
        """验证分类过滤功能"""
        mock_results = {
            'documents': [['犬瘟热症状']],
            'metadatas': [[{'category': 'disease'}]],
            'distances': [[0.1]]
        }
        mock_retriever.vector_db.query.return_value = mock_results

        results = mock_retriever.search(query="犬瘟热", category="disease")

        call_args = mock_retriever.vector_db.query.call_args
        assert call_args[1]['where']['category'] == 'disease'

    def test_search_with_similarity_threshold(self, mock_retriever):
        """验证相似度阈值过滤"""
        mock_results = {
            'documents': [['高相关', '低相关', '中等相关', '极高相关']],
            'metadatas': [[{}, {}, {}, {}]],
            'distances': [[0.1, 0.8, 0.4, 0.05]]
        }
        mock_retriever.vector_db.query.return_value = mock_results

        results = mock_retriever.search(query="测试", min_similarity=0.5, top_k=5)

        assert len(results) == 3
        assert all(r['distance'] <= 0.5 for r in results)

    def test_search_for_symptom_analysis(self, mock_retriever):
        """验证症状分析专用检索"""
        mock_results = {
            'documents': [['犬瘟热症状描述']],
            'metadatas': [[{'category': 'disease'}]],
            'distances': [[0.15]]
        }
        mock_retriever.vector_db.query.return_value = mock_results

        results = mock_retriever.search_for_symptom_analysis(
            symptoms=["发烧", "咳嗽"],
            pet_species="狗",
            pet_age=12
        )

        call_args = mock_retriever.vector_db.query.call_args
        query_text = call_args[1]['query_texts'][0]
        assert "狗" in query_text
        assert "发烧" in query_text
        assert "12个月" in query_text

    def test_search_for_nutrition_advice(self, mock_retriever):
        """验证营养建议专用检索"""
        mock_results = {
            'documents': [['金毛营养建议']],
            'metadatas': [[{'category': 'nutrition'}]],
            'distances': [[0.2]]
        }
        mock_retriever.vector_db.query.return_value = mock_results

        results = mock_retriever.search_for_nutrition_advice(
            species="狗",
            breed="金毛",
            age_months=24,
            weight=25.0
        )

        call_args = mock_retriever.vector_db.query.call_args
        query_text = call_args[1]['query_texts'][0]
        assert "金毛" in query_text
        assert "营养建议" in query_text

    def test_search_for_conversation_context(self, mock_retriever):
        """验证对话上下文检索"""
        mock_results = {
            'documents': [['之前讨论的内容']],
            'metadatas': [[{'conversation_id': 'conv_123'}]],
            'distances': [[0.3]]
        }
        mock_retriever.vector_db.query.return_value = mock_results

        results = mock_retriever.search_for_conversation_context(
            query="金毛饮食",
            conversation_id="conv_123",
            n_results=3
        )

        call_args = mock_retriever.vector_db.query.call_args
        assert call_args[1]['where']['conversation_id'] == 'conv_123'

    def test_search_for_knowledge_enhancement(self, mock_retriever):
        """验证知识增强检索"""
        mock_results = {
            'documents': [['知识内容1', '知识内容2', '知识内容3', '知识内容4', '知识内容5']],
            'metadatas': [[{}, {}, {}, {}, {}]],
            'distances': [[0.1, 0.2, 0.3, 0.4, 0.5]]
        }
        mock_retriever.vector_db.query.return_value = mock_results

        results = mock_retriever.search_for_knowledge_enhancement(
            topic="犬瘟热预防",
            top_k=5
        )

        assert len(results) == 5
        call_args = mock_retriever.vector_db.query.call_args
        assert call_args[1]['n_results'] == 10


class TestToolsUseUnifiedRetriever:
    """验证工具层使用统一检索入口"""

    def test_health_knowledge_tool_uses_retriever(self):
        """验证HealthKnowledgeTool使用KnowledgeRetriever"""
        mock_retriever = Mock()
        mock_retriever.search.return_value = [
            {"content": "宠物健康知识", "metadata": {"category": "disease"}, "distance": 0.1}
        ]

        with patch('src.tools.pet_health_tools.get_knowledge_retriever', return_value=mock_retriever):
            from src.tools.pet_health_tools import HealthKnowledgeTool
            tool = HealthKnowledgeTool()
            result = tool._run(query="宠物疫苗", n_results=3)

            assert isinstance(result, list)
            mock_retriever.search.assert_called_once_with(query="宠物疫苗", top_k=3)

    def test_symptom_analysis_tool_uses_retriever(self):
        """验证SymptomAnalysisTool使用KnowledgeRetriever"""
        with patch('src.core.knowledge_retriever.get_vector_db') as mock_vdb:
            mock_vdb_instance = Mock()
            mock_vdb_instance.is_available = True
            mock_vdb.return_value = mock_vdb_instance

            mock_results = {
                'documents': [['犬瘟热症状']],
                'metadatas': [[{'category': 'disease'}]],
                'distances': [[0.15]]
            }
            mock_vdb_instance.query.return_value = mock_results

            from src.tools.pet_health_tools import SymptomAnalysisTool
            tool = SymptomAnalysisTool()
            result = tool._run(symptoms=["发烧", "咳嗽"], pet_species="狗")

            assert "possible_conditions" in result
            assert result["pet_species"] == "狗"

    def test_knowledge_enhance_tool_uses_retriever(self):
        """验证KnowledgeEnhanceTool使用KnowledgeRetriever"""
        with patch('src.core.knowledge_retriever.get_vector_db') as mock_vdb:
            mock_vdb_instance = Mock()
            mock_vdb_instance.is_available = True
            mock_vdb.return_value = mock_vdb_instance

            mock_results = {
                'documents': [['犬瘟热知识']],
                'metadatas': [[{'category': 'disease'}]],
                'distances': [[0.1]]
            }
            mock_vdb_instance.query.return_value = mock_results

            from src.tools.external_tools import KnowledgeEnhanceTool
            tool = KnowledgeEnhanceTool()
            result = tool._run(topic="犬瘟热", depth="standard")

            assert "internal_knowledge" in result


class TestConversationMemoryIntegration:
    """对话记忆与统一检索入口集成测试"""

    def test_retrieve_relevant_context_uses_retriever(self):
        """验证对话记忆检索使用KnowledgeRetriever"""
        with patch('src.core.knowledge_retriever.get_vector_db') as mock_vdb, \
             patch('src.memory.conversation_memory.get_vector_db') as mock_mem_vdb:
            mock_vdb_instance = Mock()
            mock_vdb_instance.is_available = True
            mock_vdb.return_value = mock_vdb_instance
            mock_mem_vdb.return_value = mock_vdb_instance

            mock_results = {
                'documents': [['之前讨论的宠物健康内容']],
                'metadatas': [[{'conversation_id': 'conv_123'}]],
                'distances': [[0.2]]
            }
            mock_vdb_instance.query.return_value = mock_results

            from src.memory.conversation_memory import ConversationMemoryManager
            mock_db = Mock()
            memory = ConversationMemoryManager(db=mock_db)

            results = memory.retrieve_relevant_context(
                query="宠物健康",
                n_results=3,
                conversation_id="conv_123"
            )

            assert isinstance(results, list)

    def test_add_message_handles_unavailable_embedding(self):
        """验证嵌入不可用时add_message不崩溃"""
        with patch('src.memory.conversation_memory.get_vector_db') as mock_vdb:
            mock_vdb_instance = Mock()
            mock_vdb_instance.is_available = False
            mock_vdb.return_value = mock_vdb_instance

            from src.memory.conversation_memory import ConversationMemoryManager
            mock_db = Mock()
            memory = ConversationMemoryManager(db=mock_db)

            with patch('src.memory.conversation_memory.create_message') as mock_create:
                mock_message = Mock()
                mock_create.return_value = mock_message

                result = memory.add_message(
                    conversation_id="conv_123",
                    role="user",
                    content="测试消息",
                    store_in_vector_db=True
                )

                mock_create.assert_called_once()
