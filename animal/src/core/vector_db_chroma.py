"""
ChromaDB向量数据库管理类（旧版兼容）

当VECTOR_DB_BACKEND=chroma时使用此实现。
生产环境推荐使用Qdrant（vector_db.py中的QdrantVectorDatabase）。
"""
import os
import logging
import socket
from typing import List, Optional, Dict, Any

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

from chromadb import PersistentClient
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from .config import get_settings

logger = logging.getLogger(__name__)


def _check_internet_connection(host="huggingface.co", port=443, timeout=3) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.timeout, socket.error, OSError):
        return False


def _check_local_model_cache(model_name: str) -> bool:
    try:
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
        model_short_name = model_name.split("/")[-1]
        for root, dirs, files in os.walk(cache_dir):
            if model_short_name in root or model_short_name in dirs:
                config_file = os.path.join(root, "config.json")
                if os.path.exists(config_file):
                    return True
        return False
    except Exception:
        return False


def _load_embedding_with_timeout(model_name: str, timeout_seconds: int = 30):
    import threading
    result = [None]
    error = [None]

    def _load():
        try:
            result[0] = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model_name
            )
        except Exception as e:
            error[0] = e

    thread = threading.Thread(target=_load)
    thread.start()
    thread.join(timeout=timeout_seconds)

    if thread.is_alive():
        logger.error(f"嵌入模型加载超时 ({timeout_seconds}s)")
        return None

    if error[0]:
        raise error[0]
    return result[0]


class VectorDatabase:
    _instance: Optional['VectorDatabase'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        settings = get_settings()
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        self.embedding_model_name = settings.EMBEDDING_MODEL
        self._embedding_available = True

        os.makedirs(self.persist_dir, exist_ok=True)

        self.client = PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        self.embedding_function = self._initialize_embedding_function()
        self.collection = self._get_or_create_collection()
        self._initialized = True

    def _initialize_embedding_function(self):
        if _check_local_model_cache(self.embedding_model_name):
            try:
                ef = _load_embedding_with_timeout(self.embedding_model_name, timeout_seconds=120)
                if ef:
                    logger.info(f"成功从本地缓存加载嵌入模型: {self.embedding_model_name}")
                    return ef
            except Exception as e:
                logger.warning(f"本地缓存加载嵌入模型失败: {e}")

        if _check_internet_connection():
            try:
                ef = _load_embedding_with_timeout(self.embedding_model_name, timeout_seconds=120)
                if ef:
                    logger.info(f"成功下载并加载嵌入模型: {self.embedding_model_name}")
                    return ef
            except Exception as e:
                logger.error(f"下载嵌入模型失败: {e}")

        logger.warning("嵌入模型不可用（离线模式）。RAG检索功能将不可用。")
        self._embedding_available = False
        return None

    @property
    def is_available(self) -> bool:
        return self._embedding_available and self.embedding_function is not None

    def _get_or_create_collection(self):
        try:
            if not self._embedding_available or self.embedding_function is None:
                return self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            return self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            error_msg = str(e)
            if "embedding function" in error_msg.lower() and "already exists" in error_msg.lower():
                self.client.delete_collection(self.collection_name)
                return self.client.get_or_create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"}
                )
            raise

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None) -> None:
        if not self.is_available:
            raise RuntimeError("嵌入模型不可用")
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query_texts: List[str], n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.is_available:
            raise RuntimeError("嵌入模型不可用")
        return self.collection.query(query_texts=query_texts, n_results=n_results, where=where)

    def delete_documents(self, ids: List[str]) -> None:
        self.collection.delete(ids=ids)

    def update_documents(self, ids: List[str], documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        if not self.is_available:
            raise RuntimeError("嵌入模型不可用")
        self.collection.update(ids=ids, documents=documents, metadatas=metadatas)

    def get_document_count(self) -> int:
        return self.collection.count()

    def reset_collection(self) -> None:
        self.client.delete_collection(self.collection_name)
        self.collection = self._get_or_create_collection()
