"""
DEV-008 工具执行器单元测试

测试工具调用执行器，包括单次调用、并行调用、链式调用、缓存、重试等功能
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.tools.tool_executor import (
    ToolExecutor,
    ToolCallResult,
    ToolCallStatus,
    ToolCallConfig,
    get_tool_executor,
)


class TestToolExecutorBasic:
    """工具执行器基本功能测试"""

    @pytest.fixture
    def executor(self):
        return ToolExecutor()

    def test_executor_initialization(self, executor):
        """测试执行器初始化"""
        assert executor is not None
        assert executor._registry is not None

    def test_list_available_tools(self, executor):
        """测试列出可用工具"""
        tools = executor.list_available_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "get_pet_info" in tools
        assert "get_weather" in tools

    def test_call_nonexistent_tool(self, executor):
        """测试调用不存在的工具"""
        result = executor.call_tool("nonexistent_tool")
        
        assert result.status == ToolCallStatus.FAILED
        assert "不存在" in result.error


class TestToolExecutorCaching:
    """工具执行器缓存测试"""

    def test_cache_enabled(self):
        """测试缓存启用"""
        config = ToolCallConfig(enable_cache=True)
        executor = ToolExecutor(config)
        
        with patch.object(executor._registry, 'get_tool') as mock_get:
            mock_tool = MagicMock()
            mock_tool._run.return_value = {"result": "test"}
            mock_get.return_value = mock_tool
            
            result1 = executor.call_tool("get_weather", city="北京")
            result2 = executor.call_tool("get_weather", city="北京")
            
            assert result2.cached == True
            mock_tool._run.assert_called_once()

    def test_cache_disabled(self):
        """测试缓存禁用"""
        config = ToolCallConfig(enable_cache=False)
        executor = ToolExecutor(config)
        
        with patch.object(executor._registry, 'get_tool') as mock_get:
            mock_tool = MagicMock()
            mock_tool._run.return_value = {"result": "test"}
            mock_get.return_value = mock_tool
            
            executor.call_tool("get_weather", city="北京")
            executor.call_tool("get_weather", city="北京")
            
            assert mock_tool._run.call_count == 2

    def test_different_params_no_cache(self):
        """测试不同参数不命中缓存"""
        config = ToolCallConfig(enable_cache=True)
        executor = ToolExecutor(config)
        
        with patch.object(executor._registry, 'get_tool') as mock_get:
            mock_tool = MagicMock()
            mock_tool._run.return_value = {"result": "test"}
            mock_get.return_value = mock_tool
            
            executor.call_tool("get_weather", city="北京")
            executor.call_tool("get_weather", city="上海")
            
            assert mock_tool._run.call_count == 2

    def test_clear_cache(self):
        """测试清除缓存"""
        config = ToolCallConfig(enable_cache=True)
        executor = ToolExecutor(config)
        
        with patch.object(executor._registry, 'get_tool') as mock_get:
            mock_tool = MagicMock()
            mock_tool._run.return_value = {"result": "test"}
            mock_get.return_value = mock_tool
            
            executor.call_tool("get_weather", city="北京")
            executor.clear_cache()
            executor.call_tool("get_weather", city="北京")
            
            assert mock_tool._run.call_count == 2


class TestToolExecutorRetry:
    """工具执行器重试机制测试"""

    def test_retry_on_failure(self):
        """测试失败重试"""
        config = ToolCallConfig(
            max_retries=2,
            retry_delay_ms=10
        )
        executor = ToolExecutor(config)
        
        with patch.object(executor._registry, 'get_tool') as mock_get:
            mock_tool = MagicMock()
            call_count = [0]
            
            def failing_run(**kwargs):
                call_count[0] += 1
                if call_count[0] < 3:
                    raise Exception("临时错误")
                return {"success": True}
            
            mock_tool._run.side_effect = failing_run
            mock_get.return_value = mock_tool
            
            result = executor.call_tool("get_weather", city="北京")
            
            assert result.status == ToolCallStatus.SUCCESS
            assert call_count[0] == 3

    def test_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        config = ToolCallConfig(max_retries=1, retry_delay_ms=10)
        executor = ToolExecutor(config)
        
        with patch.object(executor._registry, 'get_tool') as mock_get:
            mock_tool = MagicMock()
            mock_tool._run.side_effect = Exception("持续失败")
            mock_get.return_value = mock_tool
            
            result = executor.call_tool("get_weather", city="北京")
            
            assert result.status == ToolCallStatus.FAILED
            assert "持续失败" in result.error


class TestToolExecutorParallel:
    """工具执行器并行调用测试"""

    def test_parallel_call_success(self):
        """测试并行调用成功"""
        executor = ToolExecutor()
        
        tool_calls = [
            {"tool_name": "get_weather", "city": "北京"},
            {"tool_name": "get_weather", "city": "上海"},
            {"tool_name": "web_search", "query": "宠物健康"}
        ]
        
        results = executor.call_tools_parallel(tool_calls)
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, ToolCallResult)

    def test_parallel_call_mixed_results(self):
        """测试并行调用混合结果（部分成功部分失败）"""
        executor = ToolExecutor()
        
        tool_calls = [
            {"tool_name": "get_weather", "city": "北京"},
            {"tool_name": "nonexistent_tool"},
            {"tool_name": "web_search", "query": "test"}
        ]
        
        results = executor.call_tools_parallel(tool_calls)
        
        assert len(results) == 3
        success_count = sum(1 for r in results if r.status in [ToolCallStatus.SUCCESS, ToolCallStatus.CACHED])
        fail_count = sum(1 for r in results if r.status == ToolCallStatus.FAILED)
        
        assert fail_count >= 1  # 至少有一个失败


class TestToolExecutorChain:
    """工具执行器链式调用测试"""

    def test_basic_chain_execution(self):
        """测试基本链式执行"""
        executor = ToolExecutor(ToolCallConfig(enable_cache=False))
        
        chain = [
            {
                "tool_name": "get_weather",
                "city": "北京",
                "days": 3
            },
            {
                "tool_name": "web_search",
                "query": "宠物外出注意事项"
            }
        ]
        
        result = executor.call_tool_chain(chain)
        
        assert result["success"] == True
        assert len(result["steps"]) == 2
        assert result["completed_steps"] == 2

    def test_chain_with_context_passing(self):
        """测试带上下文传递的链式执行"""
        executor = ToolExecutor(ToolCallConfig(enable_cache=False))
        
        chain = [
            {
                "tool_name": "get_weather",
                "city": "广州",
                "output_key": "weather_data"
            },
            {
                "tool_name": "enhance_knowledge",
                "topic": "$weather_data"
            }
        ]
        
        result = executor.call_tool_chain(chain)
        
        assert result is not None
        assert "final_context" in result

    def test_chain_stops_on_required_failure(self):
        """测试必需步骤失败时停止"""
        executor = ToolExecutor()
        
        chain = [
            {"tool_name": "nonexistent_tool", "required": True},
            {"tool_name": "get_weather", "city": "北京"}
        ]
        
        result = executor.call_tool_chain(chain)
        
        assert result["success"] == False
        assert result["completed_steps"] == 1

    def test_chain_continues_on_optional_failure(self):
        """测试可选步骤失败时继续"""
        executor = ToolExecutor(ToolCallConfig(enable_cache=False))
        
        chain = [
            {"tool_name": "nonexistent_tool", "required": False},
            {"tool_name": "get_weather", "city": "深圳"}
        ]
        
        result = executor.call_tool_chain(chain)
        
        assert result["completed_steps"] == 2


class TestToolExecutorStats:
    """工具执行器统计功能测试"""

    def test_stats_recording(self):
        """测试统计记录"""
        executor = ToolExecutor(ToolCallConfig(enable_cache=False))
        
        executor.call_tool("get_weather", city="北京")
        executor.call_tool("get_weather", city="上海")
        executor.call_tool("web_search", query="test")
        
        stats = executor.get_stats()
        
        assert "get_weather" in stats
        assert stats["get_weather"]["total_calls"] == 2
        assert "web_search" in stats

    def test_stats_success_fail_counts(self):
        """测试成功/失败计数"""
        executor = ToolExecutor()
        
        executor.call_tool("get_weather", city="北京")  # 成功
        executor.call_tool("nonexistent_tool")  # 失败
        
        stats = executor.get_stats()
        
        weather_stats = stats.get("get_weather", {})
        assert weather_stats.get("success_count", 0) > 0


class TestToolExecutorHistory:
    """工具执行器历史记录测试"""

    def test_call_history_recorded(self):
        """测试调用历史记录"""
        executor = ToolExecutor(ToolCallConfig(enable_cache=False))
        
        executor.call_tool("get_weather", city="北京")
        executor.call_tool("web_search", query="test")
        
        history = executor.get_call_history(limit=10)
        
        assert len(history) == 2
        assert history[-1].tool_name == "web_search"

    def test_history_limit(self):
        """测试历史记录限制"""
        executor = ToolExecutor(ToolCallConfig(enable_cache=False))
        
        for i in range(10):
            executor.call_tool("get_weather", city=f"城市{i}")
        
        history = executor.get_call_history(limit=5)
        
        assert len(history) <= 5


class TestToolCallResult:
    """工具调用结果类测试"""

    def test_result_creation(self):
        """测试结果创建"""
        result = ToolCallResult(
            tool_name="test_tool",
            status=ToolCallStatus.SUCCESS,
            result={"data": "value"}
        )
        
        assert result.tool_name == "test_tool"
        assert result.status == ToolCallStatus.SUCCESS
        assert result.result == {"data": "value"}

    def test_result_timestamp(self):
        """测试时间戳自动生成"""
        before = time.time()
        result = ToolCallResult(
            tool_name="test",
            status=ToolCallStatus.PENDING
        )
        after = time.time()
        
        assert before <= result.timestamp <= after


class TestGetToolExecutor:
    """工厂函数测试"""

    def test_default_executor(self):
        """测试默认执行器创建"""
        executor = get_tool_executor()
        
        assert isinstance(executor, ToolExecutor)

    def test_custom_config_executor(self):
        """测试自定义配置执行器"""
        config = ToolCallConfig(timeout_seconds=60, max_retries=3)
        executor = get_tool_executor(config)
        
        assert executor.config.timeout_seconds == 60
        assert executor.config.max_retries == 3
