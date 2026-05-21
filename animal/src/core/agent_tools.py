"""
Agent工具管理器与预置工具集

提供统一的多工具协调与注册机制，包含：
1. ToolManager - 工具注册、发现、调用追踪
2. 预置工具 - 向量检索、图谱查询、症状分析、品种信息、营养建议
3. 工具组合 - 预定义的复合检索策略
"""
import logging
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


class ToolManager:
    """工具管理器 - 统一工具注册与协调"""

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._call_history: List[Dict[str, Any]] = []

    def register(
        self,
        name: str,
        func: Callable,
        description: str = "",
        category: str = "general",
        priority: int = 1
    ):
        """注册工具"""
        self._tools[name] = {
            "func": func,
            "description": description,
            "category": category,
            "priority": priority,
        }
        logger.debug(f"工具已注册: {name} [{category}]")

    def unregister(self, name: str):
        if name in self._tools:
            del self._tools[name]

    def call(self, name: str, *args, **kwargs) -> Any:
        """调用工具并记录"""
        if name not in self._tools:
            raise ValueError(f"工具未注册: {name}")

        result = self._tools[name]["func"](*args, **kwargs)
        self._call_history.append({
            "tool": name,
            "args": str(args)[:200],
            "kwargs": str(kwargs)[:200],
            "success": result is not None,
        })
        return result

    def get_tool_description(self, name: str) -> str:
        if name in self._tools:
            return self._tools[name]["description"]
        return ""

    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        tools = []
        for name, meta in self._tools.items():
            if category and meta["category"] != category:
                continue
            tools.append({
                "name": name,
                "description": meta["description"],
                "category": meta["category"],
                "priority": meta["priority"],
            })
        tools.sort(key=lambda x: x["priority"], reverse=True)
        return tools

    def get_call_stats(self) -> Dict[str, Any]:
        if not self._call_history:
            return {"total_calls": 0, "by_tool": {}}

        by_tool = {}
        for call in self._call_history:
            tool = call["tool"]
            by_tool[tool] = by_tool.get(tool, 0) + 1

        return {
            "total_calls": len(self._call_history),
            "by_tool": by_tool,
        }


_tool_manager: Optional[ToolManager] = None
_registered_agents: List["AgenticRAG"] = []


def get_tool_manager() -> ToolManager:
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager


def create_default_tools() -> Dict[str, Callable]:
    """创建并注册默认工具集"""
    tools = {}

    def knowledge_search(query: str) -> Dict[str, Any]:
        from src.core.knowledge_retriever import get_knowledge_retriever
        retriever = get_knowledge_retriever()
        if not retriever.is_available:
            return {"results": [], "error": "向量检索不可用"}
        results = retriever.search(query, top_k=5)
        return {"results": results, "count": len(results), "tool": "knowledge_search"}

    def knowledge_search_with_quality(query: str) -> Dict[str, Any]:
        from src.core.knowledge_retriever import get_knowledge_retriever
        retriever = get_knowledge_retriever()
        if not retriever.is_available:
            return {"results": [], "error": "向量检索不可用"}
        return retriever.search_with_quality(query, top_k=5)

    def graph_search(query: str) -> Dict[str, Any]:
        from src.core.graph_retriever import get_graph_retriever
        retriever = get_graph_retriever()
        if not retriever.graph_db.is_available:
            return {"results": [], "error": "图谱检索不可用"}
        return retriever.search(query, max_hops=3)

    def fusion_search(query: str) -> Dict[str, Any]:
        from src.core.fusion_retriever import get_fusion_retriever
        retriever = get_fusion_retriever()
        if not retriever.is_available:
            return {"results": [], "error": "融合检索不可用"}
        return retriever.search(query, top_k=5, enable_graph=True)

    def symptom_analysis(query: str) -> Dict[str, Any]:
        from src.core.knowledge_retriever import get_knowledge_retriever
        from src.core.graph_retriever import get_graph_retriever
        kr = get_knowledge_retriever()
        gr = get_graph_retriever()

        parts = []
        if kr.is_available:
            vector_results = kr.search(query=query, top_k=3, category="disease")
            parts.append({
                "source": "vector",
                "type": "disease_knowledge",
                "results": vector_results,
            })

        if gr.graph_db.is_available:
            graph_results = gr.search(query, max_hops=3, include_communities=True)
            parts.append({
                "source": "graph",
                "type": "related_entities",
                "entities": graph_results.get("entities", []),
                "reasoning_chains": graph_results.get("reasoning_chains", []),
            })

        return {"results": parts, "tool": "symptom_analysis"}

    def breed_info(query: str) -> Dict[str, Any]:
        from src.core.knowledge_retriever import get_knowledge_retriever
        retriever = get_knowledge_retriever()
        if not retriever.is_available:
            return {"results": [], "error": "检索不可用"}
        results = retriever.search(query=query, top_k=5)
        return {"results": results, "count": len(results), "tool": "breed_info"}

    def nutrition_advice(query: str) -> Dict[str, Any]:
        from src.core.knowledge_retriever import get_knowledge_retriever
        retriever = get_knowledge_retriever()
        if not retriever.is_available:
            return {"results": [], "error": "检索不可用"}
        results = retriever.search(query=query, top_k=3, category="nutrition")
        return {"results": results, "count": len(results), "tool": "nutrition_advice"}

    tools = {
        "knowledge_search": knowledge_search,
        "knowledge_search_quality": knowledge_search_with_quality,
        "graph_search": graph_search,
        "fusion_search": fusion_search,
        "symptom_analysis": symptom_analysis,
        "breed_info": breed_info,
        "nutrition_advice": nutrition_advice,
    }

    return tools


def setup_agent_tools(agent: "AgenticRAG") -> "AgenticRAG":
    """为Agent注册默认工具集"""
    tools = create_default_tools()
    for name, func in tools.items():
        agent.register_tool(name, func)
    _registered_agents.append(agent)
    logger.info(f"Agent工具初始化完成: {len(tools)}个工具")
    return agent