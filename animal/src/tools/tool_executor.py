"""
工具调用执行器

提供统一的工具调用框架，包括：
- 工具调用链编排
- 结果缓存和去重
- 错误重试机制
- 调用日志记录
- 并发调用支持
"""
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache

from src.tools.base import BaseTool
from src.tools.tool_registry import ToolRegistry, get_tool_registry

logger = logging.getLogger(__name__)


class ToolCallStatus(Enum):
    """工具调用状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CACHED = "cached"


@dataclass
class ToolCallResult:
    """工具调用结果"""
    tool_name: str
    status: ToolCallStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    cached: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class ToolCallConfig:
    """工具调用配置"""
    timeout_seconds: int = 30
    max_retries: int = 2
    retry_delay_ms: int = 500
    enable_cache: bool = True
    cache_ttl_seconds: int = 300


class ToolExecutor:
    """
    工具调用执行器
    
    提供统一的工具调用接口，支持：
    - 单个工具调用
    - 多工具并行调用
    - 工具链顺序调用
    - 结果缓存
    - 错误重试
    - 调用统计
    """

    def __init__(self, config: Optional[ToolCallConfig] = None):
        self.config = config or ToolCallConfig()
        self._registry: ToolRegistry = get_tool_registry()
        self._cache: Dict[str, ToolCallResult] = {}
        self._call_history: List[ToolCallResult] = []
        self._stats: Dict[str, Dict[str, Any]] = {}

    def call_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> ToolCallResult:
        """
        调用单个工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            ToolCallResult 调用结果
        """
        start_time = time.time()
        
        cache_key = self._generate_cache_key(tool_name, kwargs)
        
        if self.config.enable_cache and cache_key in self._cache:
            cached_result = self._cache[cache_key]
            if self._is_cache_valid(cached_result):
                logger.debug(f"工具 {tool_name} 命中缓存")
                return ToolCallResult(
                    tool_name=tool_name,
                    status=ToolCallStatus.CACHED,
                    result=cached_result.result,
                    execution_time_ms=0,
                    cached=True
                )
        
        tool_instance = self._get_tool_instance(tool_name)
        if not tool_instance:
            return ToolCallResult(
                tool_name=tool_name,
                status=ToolCallStatus.FAILED,
                error=f"工具不存在: {tool_name}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
        
        result = self._execute_with_retry(tool_instance, tool_name, **kwargs)
        
        if result.status == ToolCallStatus.SUCCESS and self.config.enable_cache:
            self._cache[cache_key] = result
        
        self._record_stats(tool_name, result)
        self._call_history.append(result)
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result

    def call_tools_parallel(
        self,
        tool_calls: List[Dict[str, Any]]
    ) -> List[ToolCallResult]:
        """
        并行调用多个工具
        
        Args:
            tool_calls: 工具调用列表，每个元素包含 tool_name 和参数
            
        Returns:
            List[ToolCallResult] 所有调用的结果列表
        """
        import concurrent.futures
        
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(tool_calls), 5)) as executor:
            future_to_call = {}
            
            for call in tool_calls:
                tool_name = call.get("tool_name")
                params = {k: v for k, v in call.items() if k != "tool_name"}
                
                future = executor.submit(self.call_tool, tool_name, **params)
                future_to_call[future] = tool_name
            
            for future in concurrent.futures.as_completed(future_to_call):
                tool_name = future_to_call[future]
                try:
                    result = future.result(timeout=self.config.timeout_seconds + 10)
                    results.append(result)
                except Exception as e:
                    results.append(ToolCallResult(
                        tool_name=tool_name,
                        status=ToolCallStatus.FAILED,
                        error=f"并行调用异常: {str(e)}"
                    ))
        
        return results

    def call_tool_chain(
        self,
        chain: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        按顺序执行工具链，前一个工具的输出可作为后续工具的输入
        
        Args:
            chain: 工具链定义，每个元素包含 tool_name 和可选的 input_mapping
            context: 初始上下文数据
            
        Returns:
            Dict 包含所有步骤的结果和最终输出
        """
        context = context or {}
        results = []
        current_context = context.copy()
        
        for step in chain:
            tool_name = step.get("tool_name")
            input_mapping = step.get("input_mapping", {})
            
            resolved_params = {}
            for param_name, source in input_mapping.items():
                if isinstance(source, str) and source.startswith("$"):
                    var_name = source[1:]
                    resolved_params[param_name] = current_context.get(var_name)
                else:
                    resolved_params[param_name] = source
            
            static_params = {
                k: v for k, v in step.items()
                if k not in ["tool_name", "input_mapping"]
            }
            resolved_params.update(static_params)
            
            result = self.call_tool(tool_name, **{k: v for k, v in resolved_params.items() if v is not None})
            
            step_result = {
                "step": len(results) + 1,
                "tool_name": tool_name,
                "status": result.status.value,
                "result": result.result
            }
            results.append(step_result)
            
            if result.status == ToolCallStatus.SUCCESS and result.result:
                current_context[f"step_{len(results)}_output"] = result.result
                
                if "output_key" in step:
                    current_context[step["output_key"]] = result.result
            
            if result.status == ToolCallStatus.FAILED and step.get("required", True):
                break
        
        return {
            "steps": results,
            "final_context": current_context,
            "completed_steps": len(results),
            "success": all(r["status"] == "success" for r in results)
        }

    def _get_tool_instance(self, tool_name: str, **kwargs) -> Optional[BaseTool]:
        """获取工具实例"""
        try:
            return self._registry.get_tool(tool_name, **kwargs)
        except Exception as e:
            logger.error(f"获取工具实例失败: {e}")
            return None

    def _execute_with_retry(
        self,
        tool: BaseTool,
        tool_name: str,
        **kwargs
    ) -> ToolCallResult:
        """带重试的工具执行"""
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                logger.info(f"调用工具 {tool_name} (尝试 {attempt + 1}/{self.config.max_retries + 1})")
                
                result_data = tool._run(**kwargs)
                
                return ToolCallResult(
                    tool_name=tool_name,
                    status=ToolCallStatus.SUCCESS,
                    result=result_data
                )
                
            except TimeoutError:
                last_error = "执行超时"
                logger.warning(f"工具 {tool_name} 执行超时 (尝试 {attempt + 1})")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"工具 {tool_name} 执行失败 (尝试 {attempt + 1}): {e}")
            
            if attempt < self.config.max_retries:
                time.sleep(self.config.retry_delay_ms / 1000)
        
        return ToolCallResult(
            tool_name=tool_name,
            status=ToolCallStatus.FAILED,
            error=last_error or "未知错误"
        )

    def _generate_cache_key(self, tool_name: str, params: Dict) -> str:
        """生成缓存键"""
        param_str = str(sorted(params.items()))
        raw_key = f"{tool_name}:{param_str}"
        return hashlib.md5(raw_key.encode()).hexdigest()

    def _is_cache_valid(self, cached_result: ToolCallResult) -> bool:
        """检查缓存是否有效"""
        age = time.time() - cached_result.timestamp
        return age < self.config.cache_ttl_seconds

    def _record_stats(self, tool_name: str, result: ToolCallResult):
        """记录调用统计"""
        if tool_name not in self._stats:
            self._stats[tool_name] = {
                "total_calls": 0,
                "success_count": 0,
                "fail_count": 0,
                "cache_hits": 0,
                "total_time_ms": 0
            }
        
        stats = self._stats[tool_name]
        stats["total_calls"] += 1
        stats["total_time_ms"] += result.execution_time_ms
        
        if result.status == ToolCallStatus.CACHED:
            stats["cache_hits"] += 1
        elif result.status == ToolCallStatus.SUCCESS:
            stats["success_count"] += 1
        else:
            stats["fail_count"] += 1

    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取调用统计信息"""
        return self._stats.copy()

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        logger.info("工具调用缓存已清除")

    def get_call_history(self, limit: int = 50) -> List[ToolCallResult]:
        """获取最近的调用历史"""
        return self._call_history[-limit:]

    def list_available_tools(self) -> List[str]:
        """列出所有可用工具"""
        return self._registry.list_tools()


def get_tool_executor(config: Optional[ToolCallConfig] = None) -> ToolExecutor:
    """获取工具执行器实例"""
    return ToolExecutor(config)
