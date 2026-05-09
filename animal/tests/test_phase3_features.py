"""
Phase 3 功能测试

验证P2性能优化的正确性：
1. 检索结果缓存机制
2. 异步写入模块
3. chunk_id数据一致性
4. 系统监控告警体系
"""
import pytest
import time
from unittest.mock import Mock, MagicMock, patch


class TestSearchCache:
    """检索结果缓存测试"""

    def test_cache_put_and_get(self):
        """验证缓存读写"""
        from src.core.search_cache import SearchCache
        cache = SearchCache(max_size=10, ttl_seconds=60)
        
        results = [{"content": "测试结果", "distance": 0.1}]
        cache.put("测试查询", results, top_k=5)
        
        cached = cache.get("测试查询", top_k=5)
        assert cached is not None
        assert len(cached) == 1
        assert cached[0]["content"] == "测试结果"

    def test_cache_miss(self):
        """验证缓存未命中"""
        from src.core.search_cache import SearchCache
        cache = SearchCache()
        
        result = cache.get("不存在的查询", top_k=5)
        assert result is None

    def test_cache_ttl_expiry(self):
        """验证缓存TTL过期"""
        from src.core.search_cache import SearchCache
        cache = SearchCache(max_size=10, ttl_seconds=0)
        
        cache.put("测试查询", [{"content": "结果"}], top_k=5)
        time.sleep(0.1)
        
        cached = cache.get("测试查询", top_k=5)
        assert cached is None

    def test_cache_lru_eviction(self):
        """验证LRU淘汰策略"""
        from src.core.search_cache import SearchCache
        cache = SearchCache(max_size=3, ttl_seconds=60)
        
        for i in range(5):
            cache.put(f"查询{i}", [{"content": f"结果{i}"}], top_k=5)
        
        assert cache.size <= 3

    def test_cache_hit_rate(self):
        """验证命中率统计"""
        from src.core.search_cache import SearchCache
        cache = SearchCache()
        
        cache.put("查询1", [{"content": "结果"}], top_k=5)
        cache.get("查询1", top_k=5)
        cache.get("未命中查询", top_k=5)
        
        assert cache.hit_rate > 0

    def test_cache_invalidate(self):
        """验证缓存失效"""
        from src.core.search_cache import SearchCache
        cache = SearchCache()
        
        cache.put("狗发烧", [{"content": "结果"}], top_k=5)
        removed = cache.invalidate("狗发烧")
        assert removed >= 1
        
        cached = cache.get("狗发烧", top_k=5)
        assert cached is None

    def test_cache_stats(self):
        """验证缓存统计"""
        from src.core.search_cache import SearchCache
        cache = SearchCache(max_size=100, ttl_seconds=3600)
        
        stats = cache.stats
        assert "size" in stats
        assert "hit_rate" in stats
        assert "max_size" in stats

    def test_different_params_different_keys(self):
        """验证不同参数生成不同缓存键"""
        from src.core.search_cache import SearchCache
        cache = SearchCache()
        
        cache.put("查询", [{"content": "结果1"}], top_k=3)
        cache.put("查询", [{"content": "结果2"}], top_k=5)
        
        r1 = cache.get("查询", top_k=3)
        r2 = cache.get("查询", top_k=5)
        assert r1[0]["content"] == "结果1"
        assert r2[0]["content"] == "结果2"


class TestAsyncWriter:
    """异步写入模块测试"""

    def test_enqueue_task(self):
        """验证任务入队"""
        from src.core.async_writer import AsyncVectorWriter, WriteTaskType
        writer = AsyncVectorWriter(max_queue_size=100, worker_count=0)
        
        result = writer.add_documents_async(
            documents=["测试文档"],
            ids=["test_1"]
        )
        assert result is True
        assert writer.queue_size == 1

    def test_queue_full(self):
        """验证队列满时拒绝任务"""
        from src.core.async_writer import AsyncVectorWriter
        writer = AsyncVectorWriter(max_queue_size=2, worker_count=0)
        
        writer.add_documents_async(documents=["doc1"], ids=["1"])
        writer.add_documents_async(documents=["doc2"], ids=["2"])
        result = writer.add_documents_async(documents=["doc3"], ids=["3"])
        assert result is False

    def test_worker_processes_task(self):
        """验证工作线程处理任务"""
        from src.core.async_writer import AsyncVectorWriter
        
        with patch('src.core.async_writer.get_vector_db') as mock_vdb:
            mock_vdb_instance = Mock()
            mock_vdb_instance.add_documents.return_value = None
            mock_vdb.return_value = mock_vdb_instance
            
            writer = AsyncVectorWriter(max_queue_size=100, worker_count=1)
            writer.start()
            
            try:
                writer.add_documents_async(documents=["测试文档"], ids=["test_1"])
                time.sleep(1.0)
                
                assert writer.stats["processed"] >= 1
            finally:
                writer.stop(timeout=5.0)

    def test_stats(self):
        """验证统计信息"""
        from src.core.async_writer import AsyncVectorWriter
        writer = AsyncVectorWriter()
        
        stats = writer.stats
        assert "queue_size" in stats
        assert "processed" in stats
        assert "failed" in stats


class TestChunkIdConsistency:
    """chunk_id数据一致性测试"""

    def test_chunk_id_uniqueness(self):
        """验证不同内容生成不同chunk_id"""
        from src.core.text_chunker import TextChunker
        chunker = TextChunker()
        
        id1 = chunker._generate_chunk_id("doc1", 0, "这是第一段内容")
        id2 = chunker._generate_chunk_id("doc1", 1, "这是第二段内容")
        
        assert id1 != id2

    def test_chunk_id_deterministic(self):
        """验证相同输入生成相同chunk_id"""
        from src.core.text_chunker import TextChunker
        chunker = TextChunker()
        
        id1 = chunker._generate_chunk_id("doc1", 0, "相同内容")
        id2 = chunker._generate_chunk_id("doc1", 0, "相同内容")
        
        assert id1 == id2

    def test_chunk_id_format(self):
        """验证chunk_id格式"""
        from src.core.text_chunker import TextChunker
        chunker = TextChunker()
        
        chunk_id = chunker._generate_chunk_id("doc1", 0, "测试内容")
        assert chunk_id.startswith("chunk_")
        assert len(chunk_id) == len("chunk_") + 16

    def test_chunk_id_no_collision(self):
        """验证大量chunk_id不碰撞"""
        from src.core.text_chunker import TextChunker
        chunker = TextChunker()
        
        ids = set()
        for i in range(100):
            chunk_id = chunker._generate_chunk_id("doc1", i, f"内容{i}")
            ids.add(chunk_id)
        
        assert len(ids) == 100


class TestRAGMonitor:
    """系统监控告警测试"""

    def test_record_search(self):
        """验证检索记录"""
        from src.core.rag_monitor import RAGMonitor
        monitor = RAGMonitor()
        
        monitor.record_search(latency=0.5, result_count=3, success=True)
        monitor.record_search(latency=1.0, result_count=0, success=False)
        
        stats = monitor.get_stats()
        assert stats["search_total"]["value"] == 2
        assert stats["search_success"]["value"] == 1
        assert stats["search_failure"]["value"] == 1

    def test_record_cache_access(self):
        """验证缓存访问记录"""
        from src.core.rag_monitor import RAGMonitor
        monitor = RAGMonitor()
        
        monitor.record_cache_access(hit=True)
        monitor.record_cache_access(hit=True)
        monitor.record_cache_access(hit=False)
        
        stats = monitor.get_stats()
        assert stats["cache_hits"]["value"] == 2
        assert stats["cache_misses"]["value"] == 1

    def test_latency_histogram(self):
        """验证延迟直方图"""
        from src.core.rag_monitor import RAGMonitor
        monitor = RAGMonitor()
        
        monitor.record_search(latency=0.1, result_count=1, success=True)
        monitor.record_search(latency=0.5, result_count=2, success=True)
        monitor.record_search(latency=2.0, result_count=3, success=True)
        
        stats = monitor.get_stats()
        latency_stats = stats["search_latency_seconds"]
        assert latency_stats["count"] == 3
        assert latency_stats["min"] == 0.1
        assert latency_stats["max"] == 2.0

    def test_health_check(self):
        """验证健康检查"""
        from src.core.rag_monitor import RAGMonitor
        monitor = RAGMonitor()
        
        health = monitor.check_health()
        assert "status" in health
        assert "metrics" in health

    def test_alert_callback(self):
        """验证告警回调"""
        from src.core.rag_monitor import RAGMonitor
        monitor = RAGMonitor()
        
        alerts = []
        monitor.add_alert_callback(lambda t, m: alerts.append((t, m)))
        
        monitor.record_search(latency=10.0, result_count=1, success=True)
        
        assert len(alerts) >= 1
        assert alerts[0][0] == "HIGH_SEARCH_LATENCY"

    def test_update_gauge(self):
        """验证仪表盘更新"""
        from src.core.rag_monitor import RAGMonitor
        monitor = RAGMonitor()
        
        monitor.update_gauge("vector_db_doc_count", 42)
        monitor.update_gauge("embedding_available", 1.0)
        
        stats = monitor.get_stats()
        assert stats["vector_db_doc_count"]["value"] == 42
        assert stats["embedding_available"]["value"] == 1.0
