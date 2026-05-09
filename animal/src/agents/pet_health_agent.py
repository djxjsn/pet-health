import json
import logging
from typing import Dict, Any, List, Optional
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session

from src.agents.base_agent import BaseAgent
from src.tools.tool_registry import get_tool_registry
from src.memory.conversation_memory import ConversationMemoryManager
from src.core.rag_prompts import build_integrate_prompt, build_direct_response_prompt

logger = logging.getLogger(__name__)


class PetHealthAgent(BaseAgent):
    """宠物健康助手Agent"""

    def __init__(
        self,
        db: Session,
        llm: Optional[BaseLLM] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ):
        # 如果未提供 LLM，尝试自动初始化
        if llm is None:
            try:
                from src.core.llm import get_llm
                llm = get_llm()
            except Exception as e:
                logger.warning(f"LLM 自动初始化失败: {e}")

        tool_registry = get_tool_registry()
        tools = []

        for tool_name in tool_registry.list_tools():
            tool = tool_registry.get_tool(tool_name, db=db)
            if tool:
                tools.append(tool)

        memory_manager = ConversationMemoryManager(db)

        super().__init__(
            db=db,
            llm=llm,
            tools=tools,
            memory_manager=memory_manager
        )

        self.user_id = user_id
        self.conversation_id = conversation_id
    
    def plan(self, user_input: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """规划任务
        
        根据用户输入和上下文,决定需要调用哪些工具
        """
        tools_description = self._get_tools_description()
        
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{user_input}")
        ])

        system_message = f"""你是一个宠物健康助手的任务规划器。
你的职责是根据用户的问题,决定需要调用哪些工具来获取信息。

可用工具:
{tools_description}

请根据用户输入,返回一个JSON格式的行动计划列表。
每个行动包含:
- tool: 工具名称
- args: 工具参数
- reason: 调用原因

示例输出:
[
    {{"tool": "get_user_pets", "args": {{"user_id": "xxx"}}, "reason": "获取用户的宠物列表"}},
    {{"tool": "get_pet_info", "args": {{"pet_id": "xxx"}}, "reason": "获取特定宠物的详细信息"}}
]

只返回JSON数组,不要包含其他文字。"""

        chat_history = []
        if self.conversation_id:
            chat_history = self.memory_manager.get_conversation_history(
                self.conversation_id,
                limit=5
            )
        
        chain = planning_prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({
                "system_message": system_message,
                "user_input": user_input,
                "chat_history": chat_history
            })
            
            actions = json.loads(result)
            
            if self.user_id:
                for action in actions:
                    if action.get("tool") == "get_user_pets":
                        action["args"]["user_id"] = self.user_id
            
            return actions
        except Exception as e:
            return []
    
    def execute_action(self, action: Dict[str, Any]) -> Any:
        """执行单个行动"""
        tool_name = action.get("tool")
        tool_args = action.get("args", {})
        
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "error": f"工具 {tool_name} 不存在",
                "action": action
            }
        
        try:
            result = tool._run(**tool_args)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "action": action
            }
    
    def integrate_results(self, results: List[Any]) -> str:
        """整合结果

        将所有工具执行结果整合成一个连贯的响应。
        使用RAG提示词模板确保结构化输出。
        """
        results_text = json.dumps(results, ensure_ascii=False, indent=2)
        pet_info = getattr(self, "_run_context", {}).get("pet_info")

        integration_prompt_text = build_integrate_prompt(
            query=self.state.current_task,
            tool_results=results_text,
            pet_info=pet_info
        )
        
        integration_prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{user_input}")
        ])
        
        chat_history = []
        if self.conversation_id:
            chat_history = self.memory_manager.get_conversation_history(
                self.conversation_id,
                limit=5
            )
        
        chain = integration_prompt | self.llm | StrOutputParser()
        
        try:
            response = chain.invoke({
                "system_message": integration_prompt_text,
                "user_input": self.state.current_task,
                "chat_history": chat_history
            })
            return response
        except Exception as e:
            return f"抱歉,处理您的请求时出现了问题: {str(e)}"
    
    def chat(
        self,
        user_input: str,
        conversation_id: Optional[str] = None,
        pet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """与用户对话
        
        Args:
            user_input: 用户输入
            conversation_id: 对话ID
            pet_id: 宠物ID
            
        Returns:
            包含响应和相关信息的字典
        """
        if conversation_id:
            self.conversation_id = conversation_id
        elif not self.conversation_id:
            conversation = self.memory_manager.create_new_conversation(
                user_id=self.user_id,
                pet_id=pet_id,
                title=user_input[:50]
            )
            self.conversation_id = conversation.get("conversation_id")
        
        self.memory_manager.add_message(
            conversation_id=self.conversation_id,
            role="user",
            content=user_input
        )
        
        context = {}
        if pet_id:
            context["pet_id"] = pet_id
            try:
                from src.models.pet import Pet
                pet = db.query(Pet).filter(Pet.pet_id == pet_id).first()
                if pet:
                    context["pet_info"] = {
                        "name": pet.name,
                        "species": pet.species,
                        "breed": pet.breed,
                        "gender": pet.gender,
                    }
            except Exception as e:
                logger.debug(f"获取宠物信息失败: {e}")
        
        relevant_context = self.memory_manager.retrieve_relevant_context(
            query=user_input,
            n_results=3
        )
        context["relevant_context"] = relevant_context
        
        response = self.run(user_input, context)
        
        self.memory_manager.add_message(
            conversation_id=self.conversation_id,
            role="assistant",
            content=response
        )
        
        return {
            "conversation_id": self.conversation_id,
            "response": response,
            "relevant_context": relevant_context
        }
    
    def _get_tools_description(self) -> str:
        """获取工具描述"""
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
