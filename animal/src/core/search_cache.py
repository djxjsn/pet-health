"""
检索结果缓存模块

提供基于TTL的内存缓存，降低重复查询的响应时间。
支持缓存命中率统计、自动过期清理和缓存预热。
"""
import time
import hashlib
import json
import logging
import threading
from typing import List, Dict, Any, Optional, Tuple
from collections import OrderedDict

logger = logging.getLogger(__name__)


class SearchCache:
    """检索结果缓存（LRU + TTL）"""
    
    def __init__(self, max_size: int = 200, ttl_seconds: int = 3600):
        """初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 缓存过期时间（秒）
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Tuple[float, List[Dict[str, Any]]]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
    
    def get(
        self,
        query: str,
        top_k: Optional[int] = None,
        category: Optional[str] = None,
        min_similarity: Optional[float] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """获取缓存结果
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            category: 分类过滤
            min_similarity: 最小相似度
            
        Returns:
            缓存的检索结果，未命中返回None
        """
        cache_key = self._make_key(query, top_k, category, min_similarity)
        
        with self._lock:
            if cache_key in self._cache:
                timestamp, results = self._cache[cache_key]
                
                if time.time() - timestamp > self.ttl_seconds:
                    del self._cache[cache_key]
                    self._misses += 1
                    return None
                
                self._cache.move_to_end(cache_key)
                self._hits += 1
                logger.debug(f"缓存命中: {query[:30]}...")
                return results
            
            self._misses += 1
            return None
    
    def put(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: Optional[int] = None,
        category: Optional[str] = None,
        min_similarity: Optional[float] = None
    ) -> None:
        """存储检索结果到缓存
        
        Args:
            query: 查询文本
            results: 检索结果
            top_k: 返回结果数量
            category: 分类过滤
            min_similarity: 最小相似度
        """
        cache_key = self._make_key(query, top_k, category, min_similarity)
        
        with self._lock:
            if cache_key in self._cache:
                self._cache.move_to_end(cache_key)
            
            self._cache[cache_key] = (time.time(), results)
            
            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)
    
    def invalidate(self, query: str) -> int:
        """使指定查询的缓存失效
        
        Args:
            query: 查询文本
            
        Returns:
            清除的缓存条目数
        """
        removed = 0
        with self._lock:
            keys_to_remove = [k for k in self._cache if query in k]
            for k in keys_to_remove:
                del self._cache[k]
                removed += 1
        return removed
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def cleanup_expired(self) -> int:
        """清理过期缓存
        
        Returns:
            清理的条目数
        """
        removed = 0
        now = time.time()
        with self._lock:
            keys_to_remove = [
                k for k, (ts, _) in self._cache.items()
                if now - ts > self.ttl_seconds
            ]
            for k in keys_to_remove:
                del self._cache[k]
                removed += 1
        
        if removed > 0:
            logger.info(f"清理过期缓存: {removed}条")
        return removed
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total
    
    @property
    def size(self) -> int:
        """当前缓存大小"""
        return len(self._cache)
    
    @property
    def stats(self) -> Dict[str, Any]:
        """缓存统计信息"""
        return {
            "size": self.size,
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self.hit_rate:.2%}",
            "ttl_seconds": self.ttl_seconds
        }
    
    def _make_key(
        self,
        query: str,
        top_k: Optional[int],
        category: Optional[str],
        min_similarity: Optional[float]
    ) -> str:
        """生成缓存键"""
        key_parts = {
            "query": query.strip().lower(),
            "top_k": top_k,
            "category": category,
            "min_similarity": min_similarity
        }
        key_str = json.dumps(key_parts, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(key_str.encode()).hexdigest()


_search_cache: Optional[SearchCache] = None


def get_search_cache() -> SearchCache:
    """获取检索缓存实例（单例）"""
    global _search_cache
    if _search_cache is None:
        from src.core.config import get_settings
        settings = get_settings()
        _search_cache = SearchCache(
            max_size=200,
            ttl_seconds=3600
        )
    return _search_cache
