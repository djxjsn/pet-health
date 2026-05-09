"""
RAG系统监控模块

提供关键指标采集、性能统计和告警能力。
覆盖检索延迟、检索结果质量、缓存效率、向量库状态等核心指标。
"""
import time
import logging
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """指标类型"""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"


@dataclass
class MetricEntry:
    """指标条目"""
    name: str
    metric_type: MetricType
    value: float = 0.0
    count: int = 0
    min_value: float = float('inf')
    max_value: float = float('-inf')
    sum_value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    last_updated: float = 0.0


class RAGMonitor:
    """RAG系统监控器"""
    
    ALERT_THRESHOLDS = {
        "search_latency_p95": 5.0,
        "search_error_rate": 0.1,
        "cache_hit_rate_low": 0.3,
        "vector_db_doc_count_zero": True,
        "embedding_unavailable": True,
    }
    
    def __init__(self):
        self._metrics: Dict[str, MetricEntry] = {}
        self._lock = threading.Lock()
        self._alert_callbacks: List = []
        self._init_default_metrics()
    
    def _init_default_metrics(self):
        """初始化默认指标"""
        self._register_metric("search_total", MetricType.COUNTER, "检索总次数")
        self._register_metric("search_success", MetricType.COUNTER, "检索成功次数")
        self._register_metric("search_failure", MetricType.COUNTER, "检索失败次数")
        self._register_metric("search_latency_seconds", MetricType.HISTOGRAM, "检索延迟(秒)")
        self._register_metric("search_results_count", MetricType.HISTOGRAM, "检索结果数量")
        self._register_metric("cache_hits", MetricType.COUNTER, "缓存命中次数")
        self._register_metric("cache_misses", MetricType.COUNTER, "缓存未命中次数")
        self._register_metric("vector_db_doc_count", MetricType.GAUGE, "向量库文档数量")
        self._register_metric("embedding_available", MetricType.GAUGE, "嵌入模型可用性")
        self._register_metric("async_writer_queue_size", MetricType.GAUGE, "异步写入队列大小")
        self._register_metric("query_rewrite_total", MetricType.COUNTER, "查询改写总次数")
    
    def _register_metric(self, name: str, metric_type: MetricType, description: str = ""):
        """注册指标"""
        self._metrics[name] = MetricEntry(
            name=name,
            metric_type=metric_type
        )
    
    def record_search(self, latency: float, result_count: int, success: bool = True):
        """记录检索操作"""
        with self._lock:
            self._increment("search_total")
            if success:
                self._increment("search_success")
            else:
                self._increment("search_failure")
            self._observe("search_latency_seconds", latency)
            self._observe("search_results_count", result_count)
        
        if latency > self.ALERT_THRESHOLDS["search_latency_p95"]:
            self._fire_alert("HIGH_SEARCH_LATENCY", f"检索延迟过高: {latency:.2f}s")
    
    def record_cache_access(self, hit: bool):
        """记录缓存访问"""
        with self._lock:
            if hit:
                self._increment("cache_hits")
            else:
                self._increment("cache_misses")
    
    def update_gauge(self, name: str, value: float):
        """更新仪表盘指标"""
        with self._lock:
            if name in self._metrics:
                self._metrics[name].value = value
                self._metrics[name].last_updated = time.time()
    
    def record_query_rewrite(self):
        """记录查询改写"""
        with self._lock:
            self._increment("query_rewrite_total")
    
    def add_alert_callback(self, callback):
        """添加告警回调"""
        self._alert_callbacks.append(callback)
    
    def check_health(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            "status": "healthy",
            "issues": [],
            "metrics": {}
        }
        
        with self._lock:
            search_total = self._metrics["search_total"].value
            search_failure = self._metrics["search_failure"].value
            
            if search_total > 0:
                error_rate = search_failure / search_total
                if error_rate > self.ALERT_THRESHOLDS["search_error_rate"]:
                    health["status"] = "degraded"
                    health["issues"].append(f"检索错误率过高: {error_rate:.2%}")
            
            cache_hits = self._metrics["cache_hits"].value
            cache_misses = self._metrics["cache_misses"].value
            cache_total = cache_hits + cache_misses
            if cache_total > 10:
                hit_rate = cache_hits / cache_total
                if hit_rate < self.ALERT_THRESHOLDS["cache_hit_rate_low"]:
                    health["issues"].append(f"缓存命中率过低: {hit_rate:.2%}")
            
            for name, entry in self._metrics.items():
                health["metrics"][name] = {
                    "value": entry.value,
                    "count": entry.count,
                    "type": entry.metric_type.value
                }
        
        return health
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计摘要"""
        with self._lock:
            stats = {}
            for name, entry in self._metrics.items():
                if entry.metric_type == MetricType.COUNTER:
                    stats[name] = {"value": entry.value}
                elif entry.metric_type == MetricType.HISTOGRAM:
                    if entry.count > 0:
                        stats[name] = {
                            "count": entry.count,
                            "avg": entry.sum_value / entry.count,
                            "min": entry.min_value,
                            "max": entry.max_value,
                            "sum": entry.sum_value
                        }
                    else:
                        stats[name] = {"count": 0}
                elif entry.metric_type == MetricType.GAUGE:
                    stats[name] = {"value": entry.value}
            return stats
    
    def _increment(self, name: str, value: float = 1.0):
        """递增计数器"""
        if name in self._metrics:
            self._metrics[name].value += value
            self._metrics[name].count += 1
            self._metrics[name].last_updated = time.time()
    
    def _observe(self, name: str, value: float):
        """记录观测值"""
        if name in self._metrics:
            entry = self._metrics[name]
            entry.count += 1
            entry.sum_value += value
            entry.min_value = min(entry.min_value, value)
            entry.max_value = max(entry.max_value, value)
            entry.last_updated = time.time()
    
    def _fire_alert(self, alert_type: str, message: str):
        """触发告警"""
        logger.warning(f"[RAG告警] {alert_type}: {message}")
        for callback in self._alert_callbacks:
            try:
                callback(alert_type, message)
            except Exception as e:
                logger.error(f"告警回调执行失败: {e}")


_rag_monitor: Optional[RAGMonitor] = None


def get_rag_monitor() -> RAGMonitor:
    """获取RAG监控器实例（单例）"""
    global _rag_monitor
    if _rag_monitor is None:
        _rag_monitor = RAGMonitor()
    return _rag_monitor
