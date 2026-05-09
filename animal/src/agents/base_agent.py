"""
Agent 基类模块

定义 Agent 的核心抽象和状态管理
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from langchain_core.language_models import BaseLLM
from langchain_core.messages import BaseMessage
from sqlalchemy.orm import Session

from src.tools.base import BaseTool
from src.memory.conversation_memory import ConversationMemoryManager


class AgentStatus(str, Enum):
    """Agent 状态枚举"""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    INTEGRATING = "integrating"
    ERROR = "error"


@dataclass
class AgentState:
    """Agent 运行状态"""
    status: AgentStatus = AgentStatus.IDLE
    current_task: str = ""
    plan: List[Dict[str, Any]] = field(default_factory=list)
    results: List[Any] = field(default_factory=list)
    error: Optional[str] = None
    chat_history: List[BaseMessage] = field(default_factory=list)


class BaseAgent:
    """Agent 基类

    定义 Agent 的核心行为模式: plan -> execute -> integrate

    子类需要实现:
    - plan(): 根据用户输入规划任务
    - execute_action(): 执行单个任务动作
    - integrate_results(): 整合所有执行结果
    """

    def __init__(
        self,
        db: Session,
        llm: Optional[BaseLLM] = None,
        tools: Optional[List[BaseTool]] = None,
        memory_manager: Optional[ConversationMemoryManager] = None,
    ):
        self.db = db
        self.llm = llm
        self.tools = tools or []
        self.memory_manager = memory_manager
        self.state = AgentState()

    def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """执行 Agent 主循环

        Args:
            user_input: 用户输入
            context: 额外上下文信息

        Returns:
            Agent 的最终响应
        """
        context = context or {}
        self._run_context = context

        try:
            # 1. 规划阶段
            self.state.status = AgentStatus.PLANNING
            self.state.current_task = user_input
            self.state.plan = self.plan(user_input, context)

            if not self.state.plan:
                # 没有需要调用的工具，直接用 LLM 回复
                self.state.status = AgentStatus.INTEGRATING
                response = self._direct_response(user_input, context)
                return response

            # 2. 执行阶段
            self.state.status = AgentStatus.EXECUTING
            self.state.results = []
            for action in self.state.plan:
                result = self.execute_action(action)
                self.state.results.append(result)

            # 3. 整合阶段
            self.state.status = AgentStatus.INTEGRATING
            response = self.integrate_results(self.state.results)

            self.state.status = AgentStatus.IDLE
            return response

        except Exception as e:
            self.state.status = AgentStatus.ERROR
            self.state.error = str(e)
            return f"处理请求时出现错误: {str(e)}"

    def plan(self, user_input: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """规划任务 - 子类必须实现"""
        raise NotImplementedError

    def execute_action(self, action: Dict[str, Any]) -> Any:
        """执行单个动作 - 子类必须实现"""
        raise NotImplementedError

    def integrate_results(self, results: List[Any]) -> str:
        """整合结果 - 子类必须实现"""
        raise NotImplementedError

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """按名称获取已注册的工具"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def _direct_response(self, user_input: str, context: Dict[str, Any]) -> str:
        """当无需调用工具时，直接用 LLM 生成响应
        
        使用RAG提示词模板，结合检索到的上下文（如有）生成响应
        """
        if not self.llm:
            return "抱歉，我暂时无法处理您的请求。"

        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.output_parsers import StrOutputParser
        from src.core.rag_prompts import build_rag_prompt, build_direct_response_prompt

        relevant_context = context.get("relevant_context", [])
        pet_info = context.get("pet_info")
        
        if relevant_context:
            prompt_text = build_rag_prompt(
                query=user_input,
                retrieved_results=relevant_context,
                pet_info=pet_info
            )
        else:
            prompt_text = build_direct_response_prompt(query=user_input, pet_info=pet_info)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{user_input}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        try:
            response = chain.invoke({
                "system_message": prompt_text,
                "user_input": user_input,
                "chat_history": self.state.chat_history,
            })
            return response
        except Exception as e:
            return f"生成回复时出现错误: {str(e)}"
