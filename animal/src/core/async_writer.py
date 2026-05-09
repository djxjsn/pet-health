"""
异步写入模块

提供异步向量数据库写入能力，避免阻塞主线程响应。
支持后台任务队列、写入失败重试和批量写入优化。
"""
import logging
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from queue import Queue, Empty
from enum import Enum

logger = logging.getLogger(__name__)


class WriteTaskType(str, Enum):
    """写入任务类型"""
    ADD_DOCUMENTS = "add_documents"
    UPDATE_DOCUMENTS = "update_documents"
    DELETE_DOCUMENTS = "delete_documents"


class WriteTask:
    """写入任务"""
    
    def __init__(
        self,
        task_type: WriteTaskType,
        kwargs: Dict[str, Any],
        max_retries: int = 3,
        on_success: Optional[Callable] = None,
        on_failure: Optional[Callable] = None
    ):
        self.task_type = task_type
        self.kwargs = kwargs
        self.max_retries = max_retries
        self.retries = 0
        self.on_success = on_success
        self.on_failure = on_failure
        self.created_at = time.time()
    
    def should_retry(self) -> bool:
        return self.retries < self.max_retries


class AsyncVectorWriter:
    """异步向量数据库写入器"""
    
    def __init__(self, max_queue_size: int = 1000, worker_count: int = 1):
        """初始化异步写入器
        
        Args:
            max_queue_size: 任务队列最大容量
            worker_count: 工作线程数量
        """
        self._queue: Queue = Queue(maxsize=max_queue_size)
        self._worker_count = worker_count
        self._workers: List[threading.Thread] = []
        self._running = False
        self._processed = 0
        self._failed = 0
        self._lock = threading.Lock()
    
    def start(self) -> None:
        """启动工作线程"""
        if self._running:
            return
        
        self._running = True
        for i in range(self._worker_count):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"async-vector-writer-{i}",
                daemon=True
            )
            worker.start()
            self._workers.append(worker)
        
        logger.info(f"异步写入器已启动，工作线程数: {self._worker_count}")
    
    def stop(self, timeout: float = 10.0) -> None:
        """停止工作线程"""
        self._running = False
        
        for _ in self._workers:
            self._queue.put(None)
        
        for worker in self._workers:
            worker.join(timeout=timeout)
        
        self._workers.clear()
        logger.info("异步写入器已停止")
    
    def add_documents_async(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        on_success: Optional[Callable] = None,
        on_failure: Optional[Callable] = None
    ) -> bool:
        """异步添加文档
        
        Args:
            documents: 文档列表
            metadatas: 元数据列表
            ids: 文档ID列表
            on_success: 成功回调
            on_failure: 失败回调
            
        Returns:
            是否成功加入队列
        """
        task = WriteTask(
            task_type=WriteTaskType.ADD_DOCUMENTS,
            kwargs={
                "documents": documents,
                "metadatas": metadatas,
                "ids": ids
            },
            on_success=on_success,
            on_failure=on_failure
        )
        return self._enqueue(task)
    
    def delete_documents_async(
        self,
        ids: List[str],
        on_success: Optional[Callable] = None,
        on_failure: Optional[Callable] = None
    ) -> bool:
        """异步删除文档"""
        task = WriteTask(
            task_type=WriteTaskType.DELETE_DOCUMENTS,
            kwargs={"ids": ids},
            on_success=on_success,
            on_failure=on_failure
        )
        return self._enqueue(task)
    
    def update_documents_async(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        on_success: Optional[Callable] = None,
        on_failure: Optional[Callable] = None
    ) -> bool:
        """异步更新文档"""
        task = WriteTask(
            task_type=WriteTaskType.UPDATE_DOCUMENTS,
            kwargs={
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas
            },
            on_success=on_success,
            on_failure=on_failure
        )
        return self._enqueue(task)
    
    @property
    def queue_size(self) -> int:
        """当前队列大小"""
        return self._queue.qsize()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """统计信息"""
        return {
            "queue_size": self.queue_size,
            "processed": self._processed,
            "failed": self._failed,
            "running": self._running,
            "worker_count": self._worker_count
        }
    
    def _enqueue(self, task: WriteTask) -> bool:
        """将任务加入队列"""
        try:
            self._queue.put_nowait(task)
            return True
        except Exception:
            logger.warning("异步写入队列已满，任务被丢弃")
            return False
    
    def _worker_loop(self) -> None:
        """工作线程主循环"""
        from src.core.vector_db import get_vector_db
        
        while self._running:
            try:
                task = self._queue.get(timeout=1.0)
                
                if task is None:
                    break
                
                self._execute_task(task, get_vector_db())
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"工作线程异常: {e}")
    
    def _execute_task(self, task: WriteTask, vector_db) -> None:
        """执行写入任务"""
        try:
            if task.task_type == WriteTaskType.ADD_DOCUMENTS:
                vector_db.add_documents(**task.kwargs)
            elif task.task_type == WriteTaskType.UPDATE_DOCUMENTS:
                vector_db.update_documents(**task.kwargs)
            elif task.task_type == WriteTaskType.DELETE_DOCUMENTS:
                vector_db.delete_documents(**task.kwargs)
            
            with self._lock:
                self._processed += 1
            
            if task.on_success:
                try:
                    task.on_success(task)
                except Exception as e:
                    logger.error(f"成功回调执行失败: {e}")
            
            logger.debug(f"异步写入成功: {task.task_type}")
            
        except Exception as e:
            task.retries += 1
            
            if task.should_retry():
                logger.warning(f"异步写入失败，重试 {task.retries}/{task.max_retries}: {e}")
                self._queue.put(task)
            else:
                with self._lock:
                    self._failed += 1
                
                logger.error(f"异步写入最终失败: {task.task_type}, 错误: {e}")
                
                if task.on_failure:
                    try:
                        task.on_failure(task, e)
                    except Exception:
                        pass


_async_writer: Optional[AsyncVectorWriter] = None


def get_async_writer() -> AsyncVectorWriter:
    """获取异步写入器实例（单例）"""
    global _async_writer
    if _async_writer is None:
        _async_writer = AsyncVectorWriter(max_queue_size=1000, worker_count=1)
        _async_writer.start()
    return _async_writer
