"""
Redis 缓存架构

提供热点数据缓存能力，支持商品信息、购物车、热门搜索等场景。
采用连接池管理、序列化/反序列化、TTL策略、缓存穿透保护等机制。
"""
import json
import hashlib
import logging
from typing import Any, Optional, List, Dict, Callable
from datetime import timedelta
from functools import wraps

import redis
from redis.connection import ConnectionPool

from src.config.third_party_config import get_third_party_config

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis 缓存管理器"""

    _instance: Optional['RedisCache'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        config = get_third_party_config()
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._url = config.redis_url
        self._initialized = True
        self._connected = False

    def connect(self) -> redis.Redis:
        if self._client is not None and self._connected:
            return self._client

        try:
            self._pool = ConnectionPool.from_url(
                self._url,
                max_connections=50,
                socket_timeout=5,
                socket_connect_timeout=3,
                retry_on_timeout=True,
                decode_responses=True,
            )
            self._client = redis.Redis(connection_pool=self._pool)
            self._client.ping()
            self._connected = True
            logger.info(f"Redis 缓存连接成功: {self._url}")
            return self._client
        except redis.ConnectionError as e:
            logger.warning(f"Redis 连接失败: {e}，缓存功能将降级")
            self._connected = False
            return None
        except Exception as e:
            logger.warning(f"Redis 初始化异常: {e}，缓存功能将降级")
            self._connected = False
            return None

    @property
    def client(self) -> Optional[redis.Redis]:
        if self._client is None or not self._connected:
            return self.connect()
        return self._client

    def close(self):
        if self._pool:
            self._pool.disconnect()
            self._pool = None
            self._client = None
            self._connected = False
            logger.info("Redis 缓存连接已关闭")

    def is_available(self) -> bool:
        if not self._connected or self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            self._connected = False
            return False

    def _serialize(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, default=str)

    def _deserialize(self, value: Optional[str]) -> Any:
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def get(self, key: str) -> Any:
        if not self.is_available():
            return None
        try:
            value = self.client.get(key)
            return self._deserialize(value)
        except Exception as e:
            logger.warning(f"Redis GET 失败 key={key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        ttl_timedelta: Optional[timedelta] = None,
    ) -> bool:
        if not self.is_available():
            return False
        try:
            serialized = self._serialize(value)
            ex = ttl or (int(ttl_timedelta.total_seconds()) if ttl_timedelta else None)
            self.client.set(key, serialized, ex=ex)
            return True
        except Exception as e:
            logger.warning(f"Redis SET 失败 key={key}: {e}")
            return False

    def delete(self, *keys: str) -> int:
        if not self.is_available() or not keys:
            return 0
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.warning(f"Redis DELETE 失败 keys={keys}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        if not self.is_available():
            return False
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.warning(f"Redis EXISTS 失败 key={key}: {e}")
            return False

    def mget(self, *keys: str) -> List[Any]:
        if not self.is_available() or not keys:
            return []
        try:
            values = self.client.mget(keys)
            return [self._deserialize(v) for v in values]
        except Exception as e:
            logger.warning(f"Redis MGET 失败 keys={keys}: {e}")
            return []

    def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        if not self.is_available() or not mapping:
            return False
        try:
            serialized = {k: self._serialize(v) for k, v in mapping.items()}
            pipe = self.client.pipeline()
            pipe.mset(serialized)
            if ttl:
                for key in mapping.keys():
                    pipe.expire(key, ttl)
            pipe.execute()
            return True
        except Exception as e:
            logger.warning(f"Redis MSET 失败: {e}")
            return False

    def hget(self, name: str, key: str) -> Any:
        if not self.is_available():
            return None
        try:
            value = self.client.hget(name, key)
            return self._deserialize(value)
        except Exception as e:
            logger.warning(f"Redis HGET 失败 name={name} key={key}: {e}")
            return None

    def hset(self, name: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self.is_available():
            return False
        try:
            serialized = self._serialize(value)
            self.client.hset(name, key, serialized)
            if ttl:
                self.client.expire(name, ttl)
            return True
        except Exception as e:
            logger.warning(f"Redis HSET 失败 name={name} key={key}: {e}")
            return False

    def hgetall(self, name: str) -> Dict[str, Any]:
        if not self.is_available():
            return {}
        try:
            data = self.client.hgetall(name)
            return {k: self._deserialize(v) for k, v in data.items()}
        except Exception as e:
            logger.warning(f"Redis HGETALL 失败 name={name}: {e}")
            return {}

    def hdel(self, name: str, *keys: str) -> int:
        if not self.is_available():
            return 0
        try:
            return self.client.hdel(name, *keys)
        except Exception as e:
            logger.warning(f"Redis HDEL 失败 name={name}: {e}")
            return 0

    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        if not self.is_available():
            return None
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            logger.warning(f"Redis INCR 失败 key={key}: {e}")
            return None

    def decr(self, key: str, amount: int = 1) -> Optional[int]:
        if not self.is_available():
            return None
        try:
            return self.client.decr(key, amount)
        except Exception as e:
            logger.warning(f"Redis DECR 失败 key={key}: {e}")
            return None

    def zadd(self, name: str, mapping: Dict[str, float]) -> int:
        if not self.is_available():
            return 0
        try:
            return self.client.zadd(name, mapping)
        except Exception as e:
            logger.warning(f"Redis ZADD 失败 name={name}: {e}")
            return 0

    def zrevrange(self, name: str, start: int, end: int, withscores: bool = False) -> List:
        if not self.is_available():
            return []
        try:
            return self.client.zrevrange(name, start, end, withscores=withscores)
        except Exception as e:
            logger.warning(f"Redis ZREVRANGE 失败 name={name}: {e}")
            return []

    def zincrby(self, name: str, amount: float, value: str) -> Optional[float]:
        if not self.is_available():
            return None
        try:
            return self.client.zincrby(name, amount, value)
        except Exception as e:
            logger.warning(f"Redis ZINCRBY 失败 name={name}: {e}")
            return None

    def sadd(self, name: str, *values: str) -> int:
        if not self.is_available():
            return 0
        try:
            return self.client.sadd(name, *values)
        except Exception as e:
            logger.warning(f"Redis SADD 失败 name={name}: {e}")
            return 0

    def smembers(self, name: str) -> set:
        if not self.is_available():
            return set()
        try:
            return self.client.smembers(name)
        except Exception as e:
            logger.warning(f"Redis SMEMBERS 失败 name={name}: {e}")
            return set()

    def keys(self, pattern: str) -> List[str]:
        if not self.is_available():
            return []
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.warning(f"Redis KEYS 失败 pattern={pattern}: {e}")
            return []

    def set_nx(self, key: str, value: Any, ttl: int = 30) -> bool:
        if not self.is_available():
            return False
        try:
            serialized = self._serialize(value)
            return self.client.set(key, serialized, nx=True, ex=ttl)
        except Exception as e:
            logger.warning(f"Redis SET NX 失败 key={key}: {e}")
            return False


def get_redis_cache() -> RedisCache:
    return RedisCache()


class CacheKeyBuilder:
    """缓存 Key 构建器"""

    PREFIX_PRODUCT = "ecom:product"
    PREFIX_CART = "ecom:cart"
    PREFIX_HOT_SEARCH = "ecom:hot_search"
    PREFIX_CATEGORY = "ecom:category"
    PREFIX_MERCHANT = "ecom:merchant"
    PREFIX_REVIEW = "ecom:review"
    PREFIX_ORDER = "ecom:order"

    @staticmethod
    def product(product_id: str) -> str:
        return f"{CacheKeyBuilder.PREFIX_PRODUCT}:{product_id}"

    @staticmethod
    def product_list(category: Optional[str] = None, page: int = 1, size: int = 20) -> str:
        return f"{CacheKeyBuilder.PREFIX_PRODUCT}:list:{category or 'all'}:{page}:{size}"

    @staticmethod
    def cart(user_id: str) -> str:
        return f"{CacheKeyBuilder.PREFIX_CART}:{user_id}"

    @staticmethod
    def hot_search() -> str:
        return f"{CacheKeyBuilder.PREFIX_HOT_SEARCH}:ranking"

    @staticmethod
    def category_stats() -> str:
        return f"{CacheKeyBuilder.PREFIX_CATEGORY}:stats"

    @staticmethod
    def merchant(merchant_id: str) -> str:
        return f"{CacheKeyBuilder.PREFIX_MERCHANT}:{merchant_id}"

    @staticmethod
    def review(product_id: str, page: int = 1) -> str:
        return f"{CacheKeyBuilder.PREFIX_REVIEW}:{product_id}:{page}"

    @staticmethod
    def order(order_id: str) -> str:
        return f"{CacheKeyBuilder.PREFIX_ORDER}:{order_id}"

    @staticmethod
    def user_orders(user_id: str, page: int = 1) -> str:
        return f"{CacheKeyBuilder.PREFIX_ORDER}:user:{user_id}:{page}"


class CacheTTL:
    """缓存 TTL 配置"""

    PRODUCT_DETAIL = 1800
    PRODUCT_LIST = 600
    CART = 86400
    HOT_SEARCH = 300
    CATEGORY_STATS = 3600
    MERCHANT_INFO = 1800
    REVIEW_LIST = 600
    ORDER_DETAIL = 1800
    USER_ORDERS = 300
    NULL_CACHE = 60


def cache_result(
    key_builder: Callable[..., str],
    ttl: int = CacheTTL.PRODUCT_DETAIL,
    null_cache_ttl: int = CacheTTL.NULL_CACHE,
):
    """
    缓存装饰器

    自动缓存函数返回值，支持空值缓存防穿透。
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_redis_cache()
            if not cache.is_available():
                return await func(*args, **kwargs)

            cache_key = key_builder(*args, **kwargs)
            cached = cache.get(cache_key)
            if cached is not None:
                if cached == "__NULL__":
                    return None
                return cached

            result = await func(*args, **kwargs)

            if result is None:
                cache.set(cache_key, "__NULL__", ttl=null_cache_ttl)
            else:
                cache.set(cache_key, result, ttl=ttl)

            return result
        return wrapper
    return decorator


def invalidate_cache(*key_patterns: str):
    """
    缓存失效装饰器

    在函数执行后，删除匹配的缓存键。
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            cache = get_redis_cache()
            if cache.is_available():
                for pattern in key_patterns:
                    keys = cache.keys(pattern)
                    if keys:
                        cache.delete(*keys)

            return result
        return wrapper
    return decorator
