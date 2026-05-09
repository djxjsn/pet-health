import os
import logging
import socket
from typing import List, Optional, Dict, Any

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

from chromadb import Client, PersistentClient
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from .config import get_settings

logger = logging.getLogger(__name__)


def _check_internet_connection(host="huggingface.co", port=443, timeout=3) -> bool:
    """检查是否可以访问 HuggingFace"""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.timeout, socket.error, OSError):
        return False


def _check_local_model_cache(model_name: str) -> bool:
    """检查嵌入模型是否已在本地缓存（仅检查文件系统，不触发下载）"""
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
    """带超时的嵌入模型加载"""
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
        logger.error(f"嵌入模型加载超时 ({timeout_seconds}s)，请检查网络或手动下载模型")
        return None

    if error[0]:
        raise error[0]
    return result[0]


class VectorDatabase:
    """向量数据库管理类"""
    
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
        """初始化嵌入函数，确保向量空间不阻塞其他功能

        降级策略：
        1. 仅检查本地文件系统缓存（不触发网络请求）
        2. 有本地缓存时加载模型（30秒超时）
        3. 均失败时标记嵌入不可用，RAG检索功能不可用但不影响登录/聊天
        """
        if _check_local_model_cache(self.embedding_model_name):
            try:
                ef = _load_embedding_with_timeout(self.embedding_model_name, timeout_seconds=120)
                if ef:
                    logger.info(f"成功从本地缓存加载嵌入模型: {self.embedding_model_name}")
                    return ef
                logger.warning("本地嵌入模型加载超时")
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

        logger.warning(
            "嵌入模型不可用（离线模式）。"
            "RAG检索功能将不可用，登录/认证等基础功能正常。"
        )
        self._embedding_available = False
        return None
    
    @property
    def is_available(self) -> bool:
        """检查向量数据库是否可用（嵌入模型已加载）"""
        return self._embedding_available and self.embedding_function is not None
    
    def _get_or_create_collection(self):
        """获取或创建集合
        
        处理嵌入函数冲突：
        如果集合已存在但嵌入函数不匹配，先删除再重建
        """
        try:
            if not self._embedding_available or self.embedding_function is None:
                logger.warning("嵌入模型不可用，创建无嵌入函数的集合（仅支持已有数据查询）")
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
                logger.warning(
                    f"集合嵌入函数冲突: {error_msg}。"
                    f"正在删除旧集合并使用新嵌入函数重建..."
                )
                self.client.delete_collection(self.collection_name)
                return self.client.get_or_create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"}
                )
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """添加文档到向量数据库
        
        Args:
            documents: 文档列表
            metadatas: 元数据列表
            ids: 文档ID列表
            
        Raises:
            RuntimeError: 嵌入模型不可用时抛出异常
        """
        if not self.is_available:
            raise RuntimeError(
                "嵌入模型不可用，无法添加文档到向量数据库。"
                "请检查网络连接或手动下载嵌入模型。"
            )
        
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(
        self,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """查询相似文档
        
        Args:
            query_texts: 查询文本列表
            n_results: 返回结果数量
            where: 过滤条件
            
        Returns:
            查询结果
            
        Raises:
            RuntimeError: 嵌入模型不可用时抛出异常
        """
        if not self.is_available:
            raise RuntimeError(
                "嵌入模型不可用，无法执行语义检索。"
                "请检查网络连接或手动下载嵌入模型。"
            )
        
        return self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where
        )
    
    def delete_documents(self, ids: List[str]) -> None:
        """删除文档
        
        Args:
            ids: 要删除的文档ID列表
        """
        self.collection.delete(ids=ids)
    
    def update_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """更新文档
        
        Args:
            ids: 文档ID列表
            documents: 新文档内容列表
            metadatas: 新元数据列表
            
        Raises:
            RuntimeError: 嵌入模型不可用时抛出异常
        """
        if not self.is_available:
            raise RuntimeError(
                "嵌入模型不可用，无法更新文档向量。"
                "请检查网络连接或手动下载嵌入模型。"
            )
        
        self.collection.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        return self.collection.count()
    
    def reset_collection(self) -> None:
        """重置集合"""
        self.client.delete_collection(self.collection_name)
        self.collection = self._get_or_create_collection()


def get_vector_db() -> VectorDatabase:
    """获取向量数据库实例（单例）"""
    return VectorDatabase()
