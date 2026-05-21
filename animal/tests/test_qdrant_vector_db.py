"""
Qdrant向量数据库测试

测试QdrantVectorDatabase的核心功能，包括：
- 单例模式
- 文档添加/查询/删除/更新
- 混合检索（稠密+稀疏）
- RRF融合
- 向后兼容（get_vector_db路由）
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from src.core.vector_db import QdrantVectorDatabase, get_vector_db


class TestQdrantVectorDatabase:
    """Qdrant向量数据库测试类"""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        QdrantVectorDatabase._instance = None
        yield
        QdrantVectorDatabase._instance = None

    @pytest.fixture
    def mock_qdrant_db(self):
        with patch('src.core.vector_db.QdrantClient') as mock_client_cls, \
             patch('src.core.vector_db.SentenceTransformer') as mock_st_cls:

            mock_client = MagicMock()
            mock_client.collection_exists.return_value = True
            mock_client_cls.return_value = mock_client

            mock_model = MagicMock()
            mock_model.encode.return_value = [[0.1] * 512, [0.2] * 512]
            mock_st_cls.return_value = mock_model

            with patch('src.core.vector_db.get_settings') as mock_settings:
                settings = MagicMock()
                settings.QDRANT_HOST = "localhost"
                settings.QDRANT_PORT = 6333
                settings.QDRANT_GRPC_PORT = 6334
                settings.QDRANT_PREFER_GRPC = False
                settings.QDRANT_API_KEY = None
                settings.QDRANT_COLLECTION_NAME = "test_collection"
                settings.EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
                settings.EMBEDDING_DIMENSION = 512
                settings.EMBEDDING_DEVICE = "cpu"
                settings.EMBEDDING_PRELOAD = True
                settings.QDRANT_HNSW_M = 16
                settings.QDRANT_HNSW_EF_CONSTRUCT = 128
                settings.QDRANT_ENABLE_QUANTIZATION = True
                settings.HYBRID_SEARCH_DENSE_WEIGHT = 0.7
                settings.HYBRID_SEARCH_SPARSE_WEIGHT = 0.3
                mock_settings.return_value = settings

                db = QdrantVectorDatabase()
                yield db, mock_client, mock_model

    def test_singleton_pattern(self, mock_qdrant_db):
        db1, _, _ = mock_qdrant_db
        db2 = QdrantVectorDatabase()
        assert db1 is db2

    def test_is_available(self, mock_qdrant_db):
        db, _, _ = mock_qdrant_db
        assert db.is_available is True

    def test_add_documents(self, mock_qdrant_db):
        db, mock_client, _ = mock_qdrant_db

        db.add_documents(
            documents=["狗的常见疾病包括犬瘟热", "猫的常见疾病包括猫瘟"],
            metadatas=[
                {"category": "dog", "type": "disease"},
                {"category": "cat", "type": "disease"}
            ],
            ids=["doc_1", "doc_2"]
        )

        mock_client.upsert.assert_called_once()
        call_args = mock_client.upsert.call_args
        assert call_args[1]["collection_name"] == "test_collection"
        points = call_args[1]["points"]
        assert len(points) == 2
        assert points[0].payload["content"] == "狗的常见疾病包括犬瘟热"
        assert points[0].payload["category"] == "dog"

    def test_query(self, mock_qdrant_db):
        db, mock_client, _ = mock_qdrant_db

        mock_point = MagicMock()
        mock_point.payload = {"content": "犬瘟热症状", "category": "disease"}
        mock_point.score = 0.85

        mock_result = MagicMock()
        mock_result.points = [mock_point]
        mock_client.query_points.return_value = mock_result

        results = db.query(query_texts=["狗发烧"], n_results=1)

        assert "documents" in results
        assert len(results["documents"][0]) == 1
        assert results["documents"][0][0] == "犬瘟热症状"

    def test_query_with_filter(self, mock_qdrant_db):
        db, mock_client, _ = mock_qdrant_db

        mock_point = MagicMock()
        mock_point.payload = {"content": "犬瘟热", "category": "disease"}
        mock_point.score = 0.9

        mock_result = MagicMock()
        mock_result.points = [mock_point]
        mock_client.query_points.return_value = mock_result

        results = db.query(
            query_texts=["狗疾病"],
            n_results=1,
            where={"category": "disease"}
        )

        assert results is not None
        call_args = mock_client.query_points.call_args
        assert call_args[1]["query_filter"] is not None

    def test_hybrid_search(self, mock_qdrant_db):
        db, mock_client, _ = mock_qdrant_db

        dense_point = MagicMock()
        dense_point.id = "doc_1"
        dense_point.payload = {"content": "犬瘟热症状", "category": "disease"}
        dense_point.score = 0.85

        sparse_point = MagicMock()
        sparse_point.id = "doc_2"
        sparse_point.payload = {"content": "细小病毒症状", "category": "disease"}
        sparse_point.score = 0.7

        dense_result = MagicMock()
        dense_result.points = [dense_point]
        sparse_result = MagicMock()
        sparse_result.points = [sparse_point]

        mock_client.query_points.side_effect = [dense_result, sparse_result]

        results = db.hybrid_search(
            query_text="狗发烧拉肚子",
            n_results=5
        )

        assert len(results) >= 1
        assert "content" in results[0]
        assert "distance" in results[0]
        assert "rrf_score" in results[0]

    def test_delete_documents(self, mock_qdrant_db):
        db, mock_client, _ = mock_qdrant_db

        db.delete_documents(ids=["doc_1", "doc_2"])

        mock_client.delete.assert_called_once()
        call_args = mock_client.delete.call_args
        assert call_args[1]["collection_name"] == "test_collection"

    def test_get_document_count(self, mock_qdrant_db):
        db, mock_client, _ = mock_qdrant_db

        mock_info = MagicMock()
        mock_info.points_count = 42
        mock_client.get_collection.return_value = mock_info

        count = db.get_document_count()
        assert count == 42

    def test_reset_collection(self, mock_qdrant_db):
        db, mock_client, _ = mock_qdrant_db

        db.reset_collection()

        mock_client.delete_collection.assert_called_once_with("test_collection")

    def test_get_all_documents(self, mock_qdrant_db):
        db, mock_client, _ = mock_qdrant_db

        mock_point = MagicMock()
        mock_point.payload = {"content": "测试文档", "category": "test"}
        mock_client.scroll.return_value = ([mock_point], None)

        docs = db.get_all_documents()
        assert len(docs) == 1
        assert docs[0]["content"] == "测试文档"

    def test_sparse_encoding(self, mock_qdrant_db):
        db, _, _ = mock_qdrant_db

        sparse_vecs = db._encode_sparse(["犬瘟热 症状"])
        assert len(sparse_vecs) == 1
        assert isinstance(sparse_vecs[0], dict)
        assert len(sparse_vecs[0]) > 0

    def test_build_filter(self, mock_qdrant_db):
        db, _, _ = mock_qdrant_db

        f = db._build_filter(None)
        assert f is None

        f = db._build_filter({"category": "disease"})
        assert f is not None
        assert len(f.must) == 1

        f = db._build_filter({"category": "disease", "type": "symptom"})
        assert f is not None
        assert len(f.must) == 2


class TestGetVectorDBRouting:
    """测试get_vector_db路由功能"""

    def test_qdrant_backend(self):
        with patch('src.core.vector_db.get_settings') as mock_settings:
            settings = MagicMock()
            settings.VECTOR_DB_BACKEND = "qdrant"
            mock_settings.return_value = settings

            with patch('src.core.vector_db.QdrantVectorDatabase') as mock_cls:
                mock_instance = MagicMock()
                mock_cls.return_value = mock_instance
                mock_cls._instance = None

                result = get_vector_db()
                assert result is mock_instance

    def test_chroma_backend(self):
        with patch('src.core.vector_db.get_settings') as mock_settings:
            settings = MagicMock()
            settings.VECTOR_DB_BACKEND = "chroma"
            mock_settings.return_value = settings

            with patch('src.core.vector_db_chroma.VectorDatabase') as mock_cls:
                mock_instance = MagicMock()
                mock_cls.return_value = mock_instance
                mock_cls._instance = None

                result = get_vector_db()
                assert result is mock_instance
