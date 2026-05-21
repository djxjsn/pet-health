"""
混合检索模块

结合向量语义检索和关键词检索（BM25），通过倒数排名融合（RRF）
实现更全面的检索覆盖，弥补单一检索策略的不足。

当后端为Qdrant时，优先使用Qdrant原生混合检索（稠密+稀疏向量），
性能更优且无需手动维护BM25索引。
当后端为ChromaDB时，回退到自实现BM25+RRF融合。
"""
import math
import re
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict

from src.core.vector_db import get_vector_db
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class BM25KeywordSearch:
    """BM25关键词检索（ChromaDB后端兼容用）"""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._documents: List[Dict[str, Any]] = []
        self._doc_freqs: Dict[str, int] = defaultdict(int)
        self._doc_lengths: List[int] = []
        self._avg_dl: float = 0.0
        self._tokenized_docs: List[List[str]] = []

    def index_documents(self, documents: List[Dict[str, Any]]):
        self._documents = documents
        self._doc_freqs = defaultdict(int)
        self._doc_lengths = []
        self._tokenized_docs = []

        for doc in documents:
            content = doc.get("content", "")
            tokens = self._tokenize(content)
            self._tokenized_docs.append(tokens)
            self._doc_lengths.append(len(tokens))

            seen_terms = set(tokens)
            for term in seen_terms:
                self._doc_freqs[term] += 1

        total_length = sum(self._doc_lengths)
        self._avg_dl = total_length / len(documents) if documents else 0

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if not self._documents:
            return []

        query_tokens = self._tokenize(query)
        scores = []
        N = len(self._documents)

        for i, doc_tokens in enumerate(self._tokenized_docs):
            score = 0.0
            dl = self._doc_lengths[i]

            tf_map = defaultdict(int)
            for token in doc_tokens:
                tf_map[token] += 1

            for qt in query_tokens:
                if qt not in tf_map:
                    continue
                tf = tf_map[qt]
                df = self._doc_freqs.get(qt, 0)
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
                tf_norm = (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * dl / max(self._avg_dl, 1))
                )
                score += idf * tf_norm

            scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in scores[:top_k]:
            if score > 0:
                result = dict(self._documents[idx])
                result["bm25_score"] = score
                results.append(result)

        return results

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r'[\u4e00-\u9fff]|[a-zA-Z0-9]+', text)
        return tokens


def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]],
    keyword_results: List[Dict[str, Any]],
    k: int = 60,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    rrf_scores: Dict[str, float] = defaultdict(float)
    content_map: Dict[str, Dict[str, Any]] = {}

    for rank, result in enumerate(vector_results):
        content_key = result.get("content", "")[:200]
        rrf_scores[content_key] += 1.0 / (k + rank + 1)
        if content_key not in content_map:
            content_map[content_key] = result

    for rank, result in enumerate(keyword_results):
        content_key = result.get("content", "")[:200]
        rrf_scores[content_key] += 1.0 / (k + rank + 1)
        if content_key not in content_map:
            content_map[content_key] = result

    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for content_key, rrf_score in sorted_results[:top_k]:
        result = dict(content_map[content_key])
        result["rrf_score"] = rrf_score
        results.append(result)

    return results


class HybridRetriever:
    """混合检索器（向量 + BM25）

    当后端为Qdrant时，使用Qdrant原生混合检索（稠密+稀疏向量RRF融合）。
    当后端为ChromaDB时，回退到自实现BM25+RRF融合。
    """

    def __init__(self):
        self.vector_db = get_vector_db()
        self._use_qdrant_hybrid = hasattr(self.vector_db, 'hybrid_search')
        self.bm25 = BM25KeywordSearch() if not self._use_qdrant_hybrid else None
        self._indexed = False

        if self._use_qdrant_hybrid:
            logger.info("HybridRetriever: 使用Qdrant原生混合检索模式")
        else:
            logger.info("HybridRetriever: 使用BM25+RRF兼容模式")

    def build_bm25_index(self, documents: Optional[List[Dict[str, Any]]] = None):
        if self._use_qdrant_hybrid:
            logger.info("Qdrant模式无需手动构建BM25索引，稀疏向量已内嵌")
            self._indexed = True
            return

        if documents is None:
            documents = self._load_documents_from_vector_db()

        if documents:
            self.bm25.index_documents(documents)
            self._indexed = True
            logger.info(f"BM25索引构建完成，文档数: {len(documents)}")

    def search(
        self,
        query: str,
        top_k: int = 5,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if self._use_qdrant_hybrid:
            return self._qdrant_hybrid_search(query, top_k, vector_weight, keyword_weight, category)

        return self._bm25_hybrid_search(query, top_k, vector_weight, keyword_weight, category)

    def _qdrant_hybrid_search(
        self,
        query: str,
        top_k: int,
        dense_weight: float,
        sparse_weight: float,
        category: Optional[str]
    ) -> List[Dict[str, Any]]:
        try:
            where_filter = {"category": category} if category else None
            results = self.vector_db.hybrid_search(
                query_text=query,
                n_results=top_k,
                where=where_filter,
                dense_weight=dense_weight,
                sparse_weight=sparse_weight,
            )
            return results
        except Exception as e:
            logger.error(f"Qdrant混合检索失败: {e}")
            return []

    def _bm25_hybrid_search(
        self,
        query: str,
        top_k: int,
        vector_weight: float,
        keyword_weight: float,
        category: Optional[str]
    ) -> List[Dict[str, Any]]:
        if not self.vector_db.is_available:
            logger.warning("向量数据库不可用，仅使用BM25检索")
            if self._indexed:
                return self.bm25.search(query, top_k=top_k)
            return []

        where_filter = {"category": category} if category else None

        try:
            vector_results_raw = self.vector_db.query(
                query_texts=[query],
                n_results=top_k * 2,
                where=where_filter
            )
            vector_results = self._format_vector_results(vector_results_raw)
        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            vector_results = []

        keyword_results = []
        if self._indexed:
            keyword_results = self.bm25.search(query, top_k=top_k * 2)

        if not vector_results and not keyword_results:
            return []

        if not vector_results:
            return keyword_results[:top_k]

        if not keyword_results:
            return vector_results[:top_k]

        fused = reciprocal_rank_fusion(
            vector_results=vector_results,
            keyword_results=keyword_results,
            top_k=top_k
        )

        return fused

    def _load_documents_from_vector_db(self) -> List[Dict[str, Any]]:
        try:
            if hasattr(self.vector_db, 'get_all_documents'):
                return self.vector_db.get_all_documents()

            all_data = self.vector_db.collection.get(include=["documents", "metadatas"])
            documents = []
            if all_data and all_data.get("documents"):
                for i, doc in enumerate(all_data["documents"]):
                    documents.append({
                        "content": doc,
                        "metadata": all_data["metadatas"][i] if all_data.get("metadatas") else {}
                    })
            return documents
        except Exception as e:
            logger.error(f"从向量库加载文档失败: {e}")
            return []

    def _format_vector_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        formatted = []
        if not results or 'documents' not in results or not results['documents']:
            return formatted

        for i in range(len(results['documents'][0])):
            doc = {
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i] if results.get('metadatas') else {},
                "distance": results['distances'][0][i] if results.get('distances') else None
            }
            formatted.append(doc)

        return formatted
