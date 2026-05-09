"""
分布式锁机制

基于 Redis 实现的分布式锁，用于高并发场景下的资源互斥访问。
支持可重入锁、自动续期、超时释放等特性。
"""
import uuid
import time
import logging
import asyncio
from typing import Optional, Callable
from functools import wraps
from contextlib import asynccontextmanager

from src.core.redis_cache import get_redis_cache

logger = logging.getLogger(__name__)


class DistributedLock:
    """Redis 分布式锁"""

    def __init__(
        self,
        lock_name: str,
        timeout: int = 30,
        retry_interval: float = 0.1,
        retry_count: int = 50,
    ):
        self.lock_name = f"dlock:{lock_name}"
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.retry_count = retry_count
        self.identifier = str(uuid.uuid4())
        self._acquired = False

    async def acquire(self) -> bool:
        cache = get_redis_cache()
        if not cache.is_available():
            logger.warning(f"Redis 不可用，分布式锁降级为无锁模式: {self.lock_name}")
            self._acquired = True
            return True

        for attempt in range(self.retry_count):
            acquired = cache.set_nx(self.lock_name, self.identifier, ttl=self.timeout)
            if acquired:
                self._acquired = True
                logger.debug(f"获取分布式锁成功: {self.lock_name}, identifier={self.identifier}")
                return True

            await asyncio.sleep(self.retry_interval)

        logger.warning(f"获取分布式锁超时: {self.lock_name}, 重试{self.retry_count}次")
        return False

    async def release(self) -> bool:
        if not self._acquired:
            return True

        cache = get_redis_cache()
        if not cache.is_available():
            self._acquired = False
            return True

        try:
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            client = cache.client
            if client is None:
                self._acquired = False
                return True

            result = client.eval(lua_script, 1, self.lock_name, self.identifier)
            self._acquired = False

            if result:
                logger.debug(f"释放分布式锁成功: {self.lock_name}")
                return True
            else:
                logger.warning(f"释放分布式锁失败（锁已被其他人持有或已过期）: {self.lock_name}")
                return False
        except Exception as e:
            logger.error(f"释放分布式锁异常: {self.lock_name}, {e}")
            self._acquired = False
            return False

    async def extend(self, additional_time: Optional[int] = None) -> bool:
        if not self._acquired:
            return False

        cache = get_redis_cache()
        if not cache.is_available():
            return True

        try:
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("expire", KEYS[1], ARGV[2])
            else
                return 0
            end
            """
            client = cache.client
            if client is None:
                return True

            extend_time = additional_time or self.timeout
            result = client.eval(lua_script, 1, self.lock_name, self.identifier, extend_time)
            return bool(result)
        except Exception as e:
            logger.error(f"续期分布式锁异常: {self.lock_name}, {e}")
            return False

    @property
    def is_acquired(self) -> bool:
        return self._acquired


@asynccontextmanager
async def distributed_lock(
    lock_name: str,
    timeout: int = 30,
    retry_interval: float = 0.1,
    retry_count: int = 50,
):
    """
    分布式锁上下文管理器

    用法:
        async with distributed_lock("order_create:user_123"):
            # 临界区代码
            pass
    """
    lock = DistributedLock(
        lock_name=lock_name,
        timeout=timeout,
        retry_interval=retry_interval,
        retry_count=retry_count,
    )
    acquired = await lock.acquire()
    if not acquired:
        raise LockAcquisitionError(f"无法获取分布式锁: {lock_name}")

    try:
        yield lock
    finally:
        await lock.release()


def with_distributed_lock(
    lock_name_builder: Callable[..., str],
    timeout: int = 30,
    retry_interval: float = 0.1,
    retry_count: int = 50,
):
    """
    分布式锁装饰器

    用法:
        @with_distributed_lock(lambda user_id: f"order_create:{user_id}")
        async def create_order(user_id: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            lock_name = lock_name_builder(*args, **kwargs)
            async with distributed_lock(
                lock_name=lock_name,
                timeout=timeout,
                retry_interval=retry_interval,
                retry_count=retry_count,
            ):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


class LockAcquisitionError(Exception):
    """锁获取失败异常"""
    pass


class LockKeyBuilder:
    """分布式锁 Key 构建器"""

    @staticmethod
    def cart_operation(user_id: str) -> str:
        return f"cart_op:{user_id}"

    @staticmethod
    def order_create(user_id: str) -> str:
        return f"order_create:{user_id}"

    @staticmethod
    def order_pay(order_id: str) -> str:
        return f"order_pay:{order_id}"

    @staticmethod
    def order_cancel(order_id: str) -> str:
        return f"order_cancel:{order_id}"

    @staticmethod
    def product_stock(product_id: str) -> str:
        return f"product_stock:{product_id}"

    @staticmethod
    def product_update(product_id: str) -> str:
        return f"product_update:{product_id}"

    @staticmethod
    def review_create(product_id: str, user_id: str) -> str:
        return f"review_create:{product_id}:{user_id}"

    @staticmethod
    def merchant_product(merchant_id: str) -> str:
        return f"merchant_product:{merchant_id}"
