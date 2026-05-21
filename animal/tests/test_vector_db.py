"""
向量数据库测试（ChromaDB兼容）
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from src.core.vector_db_chroma import VectorDatabase


class TestVectorDatabase:
    """向量数据库测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_vector_db(self, monkeypatch):
        temp_dir = tempfile.mkdtemp()
        monkeypatch.setenv("CHROMA_PERSIST_DIR", temp_dir)
        monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test_collection")
        monkeypatch.setenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        VectorDatabase._instance = None
        
        yield
        
        VectorDatabase._instance = None
    
    def test_vector_db_singleton(self):
        mock_ef = Mock()
        with patch('src.core.vector_db_chroma._check_local_model_cache', return_value=True), \
             patch('src.core.vector_db_chroma.embedding_functions.SentenceTransformerEmbeddingFunction', return_value=mock_ef), \
             patch.object(VectorDatabase, '_get_or_create_collection', return_value=Mock()):
            db1 = VectorDatabase()
            db2 = VectorDatabase()
            assert db1 is db2
    
    def test_add_documents(self):
        mock_ef = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 3
        
        with patch('src.core.vector_db_chroma._check_local_model_cache', return_value=True), \
             patch('src.core.vector_db_chroma.embedding_functions.SentenceTransformerEmbeddingFunction', return_value=mock_ef), \
             patch.object(VectorDatabase, '_get_or_create_collection', return_value=mock_collection):
            db = VectorDatabase()
            
            documents = [
                "狗的常见疾病包括犬瘟热、细小病毒等",
                "猫的常见疾病包括猫瘟、猫鼻支等",
                "宠物需要定期接种疫苗"
            ]
            
            metadatas = [
                {"category": "dog", "type": "disease"},
                {"category": "cat", "type": "disease"},
                {"category": "general", "type": "vaccination"}
            ]
            
            db.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=["test_doc_1", "test_doc_2", "test_doc_3"]
            )
            
            mock_collection.add.assert_called_once()
            count = db.get_document_count()
            assert count >= 3
    
    def test_query_documents(self):
        mock_ef = Mock()
        mock_collection = Mock()
        mock_collection.add.return_value = None
        mock_collection.query.return_value = {
            'documents': [['狗的常见疾病包括犬瘟热']],
            'metadatas': [[{'category': 'dog'}]],
            'distances': [[0.1]]
        }
        
        with patch('src.core.vector_db_chroma._check_local_model_cache', return_value=True), \
             patch('src.core.vector_db_chroma.embedding_functions.SentenceTransformerEmbeddingFunction', return_value=mock_ef), \
             patch.object(VectorDatabase, '_get_or_create_collection', return_value=mock_collection):
            db = VectorDatabase()
            
            db.add_documents(
                documents=["狗的常见疾病包括犬瘟热"],
                metadatas=[{"category": "dog"}],
                ids=["test_query_doc"]
            )
            
            results = db.query(
                query_texts=["狗的疾病"],
                n_results=1
            )
            
            assert results is not None
            assert len(results['documents']) > 0
            assert len(results['documents'][0]) > 0
    
    def test_delete_documents(self):
        mock_ef = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 0
        mock_collection.delete.return_value = None
        
        with patch('src.core.vector_db_chroma._check_local_model_cache', return_value=True), \
             patch('src.core.vector_db_chroma.embedding_functions.SentenceTransformerEmbeddingFunction', return_value=mock_ef), \
             patch.object(VectorDatabase, '_get_or_create_collection', return_value=mock_collection):
            db = VectorDatabase()
            
            db.add_documents(
                documents=["测试删除文档"],
                ids=["test_delete_doc"]
            )
            
            db.delete_documents(ids=["test_delete_doc"])
            
            mock_collection.delete.assert_called_once_with(ids=["test_delete_doc"])
    
    def test_update_documents(self):
        mock_ef = Mock()
        mock_collection = Mock()
        mock_collection.update.return_value = None
        mock_collection.query.return_value = {
            'documents': [['更新后的文档']],
            'metadatas': [[{}]],
            'distances': [[0.05]]
        }
        
        with patch('src.core.vector_db_chroma._check_local_model_cache', return_value=True), \
             patch('src.core.vector_db_chroma.embedding_functions.SentenceTransformerEmbeddingFunction', return_value=mock_ef), \
             patch.object(VectorDatabase, '_get_or_create_collection', return_value=mock_collection):
            db = VectorDatabase()
            
            db.add_documents(
                documents=["原始文档"],
                ids=["test_update_doc"]
            )
            
            db.update_documents(
                ids=["test_update_doc"],
                documents=["更新后的文档"]
            )
            
            mock_collection.update.assert_called_once()
            
            results = db.query(
                query_texts=["更新后的文档"],
                n_results=1
            )
            
            assert results is not None

    def test_unavailable_embedding_raises_error(self, monkeypatch):
        with patch('src.core.vector_db_chroma._check_internet_connection', return_value=False), \
             patch('src.core.vector_db_chroma._check_local_model_cache', return_value=False):
            db = VectorDatabase()
            
            with pytest.raises(RuntimeError, match="嵌入模型不可用"):
                db.query(query_texts=["测试"], n_results=1)
            
            with pytest.raises(RuntimeError, match="嵌入模型不可用"):
                db.add_documents(documents=["测试"], ids=["test"])
