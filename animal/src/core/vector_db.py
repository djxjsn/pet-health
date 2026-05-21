"""
Qdrant向量数据库管理类

基于Qdrant的高性能向量存储与检索，替代ChromaDB。
支持稠密+稀疏混合检索、HNSW索引优化、int8量化压缩。
保持与VectorDatabase相同的接口，实现无缝切换。
"""
import os
import uuid
import logging
from typing import List, Optional, Dict, Any

import uuid

_NAMESPACE_DNS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

def _str_to_uuid(s: str) -> str:
    return str(uuid.uuid5(_NAMESPACE_DNS, s))

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    SearchRequest,
    Filter,
    FieldCondition,
    MatchValue,
    HnswConfigDiff,
    OptimizersConfigDiff,
    ScalarQuantization,
    ScalarType,
    ScalarQuantizationConfig,
    SparseVectorParams,
    SparseVector,
    NamedSparseVector,
    OrderValue,
    PointIdsList,
)
from sentence_transformers import SentenceTransformer

from .config import get_settings

logger = logging.getLogger(__name__)


class QdrantVectorDatabase:
    """Qdrant向量数据库管理类"""

    _instance: Optional['QdrantVectorDatabase'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        settings = get_settings()
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.embedding_model_name = settings.EMBEDDING_MODEL
        self.embedding_dimension = settings.EMBEDDING_DIMENSION
        self.dense_weight = settings.HYBRID_SEARCH_DENSE_WEIGHT
        self.sparse_weight = settings.HYBRID_SEARCH_SPARSE_WEIGHT
        self._embedding_available = True
        self._local_mode = True
        self._sparse_supported = False

        self._init_client(settings)
        self._init_embedding_model(settings)
        self._init_collection(settings)

        self._initialized = True

    def _init_client(self, settings):
        if hasattr(settings, 'QDRANT_LOCAL_PATH') and settings.QDRANT_LOCAL_PATH:
            self._init_local_client(settings)
        else:
            self._init_remote_client(settings)

    def _init_local_client(self, settings):
        try:
            import os
            os.makedirs(settings.QDRANT_LOCAL_PATH, exist_ok=True)
            self.client = QdrantClient(path=settings.QDRANT_LOCAL_PATH)
            self._local_mode = True
            logger.info(f"Qdrant本地模式启动: {settings.QDRANT_LOCAL_PATH}")
        except Exception as e:
            logger.error(f"Qdrant本地模式启动失败: {e}")
            self._embedding_available = False
            self.client = None

    def _init_remote_client(self, settings):
        try:
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                grpc_port=settings.QDRANT_GRPC_PORT,
                prefer_grpc=settings.QDRANT_PREFER_GRPC,
                api_key=settings.QDRANT_API_KEY,
                timeout=30,
            )
            self._local_mode = False
            logger.info(
                f"Qdrant远程连接成功: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}"
            )
        except Exception as e:
            logger.error(f"Qdrant远程连接失败: {e}，尝试本地模式...")
            self._embedding_available = False
            self.client = None

    def _init_embedding_model(self, settings):
        try:
            self.embedding_model = SentenceTransformer(
                self.embedding_model_name,
                device=settings.EMBEDDING_DEVICE,
            )
            logger.info(f"嵌入模型加载成功: {self.embedding_model_name}")
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {e}")
            self.embedding_model = None
            self._embedding_available = False

    def _init_collection(self, settings):
        if self.client is None:
            return

        try:
            existing = self.client.collection_exists(self.collection_name)
            if existing:
                logger.info(f"Qdrant集合已存在: {self.collection_name}")
                return

            vectors_config = {
                "dense": VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(
                        m=settings.QDRANT_HNSW_M,
                        ef_construct=settings.QDRANT_HNSW_EF_CONSTRUCT,
                    ),
                )
            }

            sparse_vectors_config = {"sparse": SparseVectorParams()}

            quantization_config = None
            if settings.QDRANT_ENABLE_QUANTIZATION and not self._local_mode:
                quantization_config = ScalarQuantization(
                    scalar=ScalarQuantizationConfig(
                        type=ScalarType.INT8,
                        quantile=0.99,
                        always_ram=True,
                    )
                )

            kwargs = {
                "collection_name": self.collection_name,
                "vectors_config": vectors_config,
                "optimizers_config": OptimizersConfigDiff(
                    indexing_threshold=20000,
                ),
            }

            if quantization_config:
                kwargs["quantization_config"] = quantization_config

            try:
                kwargs["sparse_vectors_config"] = sparse_vectors_config
                self.client.create_collection(**kwargs)
                self._sparse_supported = True
            except Exception as e:
                logger.warning(f"稀疏向量不支持（可能为本地模式），使用稠密向量模式: {e}")
                self.client.create_collection(**kwargs)
                self._sparse_supported = False

            logger.info(f"Qdrant集合创建成功: {self.collection_name}")

        except Exception as e:
            logger.error(f"Qdrant集合初始化失败: {e}")

    @property
    def is_available(self) -> bool:
        return (
            self._embedding_available
            and self.embedding_model is not None
            and self.client is not None
        )

    def _encode(self, texts: List[str]) -> List[List[float]]:
        if not self.is_available:
            raise RuntimeError("嵌入模型不可用")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        if hasattr(embeddings, 'tolist'):
            return embeddings.tolist()
        return [list(e) if hasattr(e, '__iter__') else [e] for e in embeddings]

    def _encode_sparse(self, texts: List[str]) -> List[Dict[int, float]]:
        from collections import Counter
        import re

        results = []
        for text in texts:
            tokens = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z0-9]+', text.lower())
            token_counts = Counter(tokens)
            sparse_vec = {}
            for token, count in token_counts.items():
                token_id = hash(token) % 25000
                sparse_vec[token_id] = float(count)
            results.append(sparse_vec)
        return results

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        if not self.is_available:
            raise RuntimeError("嵌入模型不可用，无法添加文档")

        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        embeddings = self._encode(documents)

        if self._sparse_supported:
            sparse_embeddings = self._encode_sparse(documents)

        points = []
        for i, (raw_id, doc, embedding) in enumerate(
            zip(ids, documents, embeddings)
        ):
            point_id = _str_to_uuid(raw_id) if self._local_mode else raw_id

            payload = {"content": doc, "_raw_id": raw_id}
            if metadatas and i < len(metadatas):
                clean_meta = {}
                for k, v in metadatas[i].items():
                    if isinstance(v, (str, int, float, bool)):
                        clean_meta[k] = v
                    elif isinstance(v, list):
                        clean_meta[k] = [str(item) for item in v]
                    else:
                        clean_meta[k] = str(v)
                payload.update(clean_meta)

            if self._sparse_supported:
                sparse_emb = sparse_embeddings[i]
                sparse_vector = SparseVector(
                    indices=list(sparse_emb.keys()),
                    values=list(sparse_emb.values())
                )
                vector_data = {"dense": embedding, "sparse": sparse_vector}
            else:
                vector_data = {"dense": embedding}

            point = PointStruct(
                id=point_id,
                vector=vector_data,
                payload=payload,
            )
            points.append(point)

        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )

        logger.info(f"成功添加 {len(points)} 个文档到Qdrant")

    def query(
        self,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.is_available:
            raise RuntimeError("嵌入模型不可用，无法执行检索")

        query_embedding = self._encode(query_texts)[0]

        qdrant_filter = self._build_filter(where)

        try:
            kwargs = {
                "collection_name": self.collection_name,
                "query": query_embedding,
                "using": "dense",
                "limit": n_results,
                "query_filter": qdrant_filter,
                "with_payload": True,
            }

            results = self.client.query_points(**kwargs)
        except Exception as e:
            logger.error(f"Qdrant查询失败: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        return self._format_qdrant_results(results.points)

    def hybrid_search(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        dense_weight: Optional[float] = None,
        sparse_weight: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        if not self.is_available:
            raise RuntimeError("嵌入模型不可用，无法执行混合检索")

        if not self._sparse_supported:
            logger.debug("稀疏向量不可用，回退到稠密检索")
            result = self.query(query_texts=[query_text], n_results=n_results, where=where)
            return self._format_results_as_list(result)

        dw = dense_weight if dense_weight is not None else self.dense_weight
        sw = sparse_weight if sparse_weight is not None else self.sparse_weight

        query_embedding = self._encode([query_text])[0]
        query_sparse = self._encode_sparse([query_text])[0]
        qdrant_filter = self._build_filter(where)

        try:
            dense_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                using="dense",
                limit=n_results * 3,
                query_filter=qdrant_filter,
                with_payload=True,
                score_threshold=0.3,
            )

            sparse_results = self.client.query_points(
                collection_name=self.collection_name,
                query=SparseVector(indices=list(query_sparse.keys()), values=list(query_sparse.values())),
                using="sparse",
                limit=n_results * 3,
                query_filter=qdrant_filter,
                with_payload=True,
            )

            fused = self._reciprocal_rank_fusion(
                dense_results.points,
                sparse_results.points,
                dw,
                sw,
                n_results,
            )
            return fused

        except Exception as e:
            logger.error(f"Qdrant混合检索失败: {e}")
            return []

    def _reciprocal_rank_fusion(
        self,
        dense_points,
        sparse_points,
        dense_weight: float,
        sparse_weight: float,
        top_k: int,
        k: int = 60,
    ) -> List[Dict[str, Any]]:
        rrf_scores: Dict[str, float] = {}
        point_map: Dict[str, Any] = {}

        for rank, point in enumerate(dense_points):
            pid = str(point.id)
            rrf_scores[pid] = rrf_scores.get(pid, 0) + dense_weight / (k + rank + 1)
            if pid not in point_map:
                point_map[pid] = point

        for rank, point in enumerate(sparse_points):
            pid = str(point.id)
            rrf_scores[pid] = rrf_scores.get(pid, 0) + sparse_weight / (k + rank + 1)
            if pid not in point_map:
                point_map[pid] = point

        sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]

        results = []
        for pid in sorted_ids:
            point = point_map[pid]
            payload = point.payload or {}
            score = point.score if hasattr(point, "score") and point.score else 0.0
            distance = 1.0 - score

            results.append({
                "content": payload.get("content", ""),
                "metadata": {k: v for k, v in payload.items() if k != "content"},
                "distance": distance,
                "rrf_score": rrf_scores[pid],
            })

        return results

    def delete_documents(self, ids: List[str]) -> None:
        if self.client is None:
            return

        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=ids),
            )
            logger.info(f"成功删除 {len(ids)} 个文档")
        except Exception as e:
            logger.error(f"删除文档失败: {e}")

    def update_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.add_documents(documents=documents, metadatas=metadatas, ids=ids)

    def get_document_count(self) -> int:
        if self.client is None:
            return 0
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        except Exception:
            return 0

    def reset_collection(self) -> None:
        if self.client is None:
            return
        try:
            self.client.delete_collection(self.collection_name)
            settings = get_settings()
            self._init_collection(settings)
            logger.info(f"Qdrant集合已重置: {self.collection_name}")
        except Exception as e:
            logger.error(f"重置集合失败: {e}")

    def get_all_documents(self) -> List[Dict[str, Any]]:
        if self.client is None:
            return []
        try:
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000,
                with_payload=True,
                with_vectors=False,
            )
            results = []
            for point in points:
                payload = point.payload or {}
                results.append({
                    "content": payload.get("content", ""),
                    "metadata": {k: v for k, v in payload.items() if k != "content"},
                })
            return results
        except Exception as e:
            logger.error(f"获取所有文档失败: {e}")
            return []

    def _build_filter(self, where: Optional[Dict[str, Any]] = None) -> Optional[Filter]:
        if not where:
            return None

        conditions = []
        for key, value in where.items():
            if isinstance(value, str):
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))

        if not conditions:
            return None

        return Filter(must=conditions)

    def _format_qdrant_results(self, points) -> Dict[str, Any]:
        documents = []
        metadatas = []
        distances = []

        for point in points:
            payload = point.payload or {}
            content = payload.get("content", "")
            metadata = {k: v for k, v in payload.items() if k != "content"}
            score = point.score if hasattr(point, "score") and point.score else 0.0
            distance = 1.0 - score

            documents.append(content)
            metadatas.append(metadata)
            distances.append(distance)

        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances],
        }

    def _format_results_as_list(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        if not result or 'documents' not in result or not result['documents']:
            return results
        for i in range(len(result['documents'][0])):
            results.append({
                "content": result['documents'][0][i],
                "metadata": result['metadatas'][0][i] if result.get('metadatas') else {},
                "distance": result['distances'][0][i] if result.get('distances') else 1.0,
                "rrf_score": 0.0,
            })
        return results


def get_vector_db():
    settings = get_settings()
    backend = getattr(settings, "VECTOR_DB_BACKEND", "chroma")

    if backend == "qdrant":
        return QdrantVectorDatabase()
    else:
        from .vector_db_chroma import VectorDatabase
        return VectorDatabase()
