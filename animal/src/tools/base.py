from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from langchain.tools import BaseTool as LangChainBaseTool


class ToolInput(BaseModel):
    """工具输入基类"""
    pass


class BaseTool(LangChainBaseTool):
    """工具基类"""

    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    args_schema: type[BaseModel] = Field(..., description="参数模型")

    def _run(self, *args, **kwargs) -> Any:
        """执行工具"""
        pass
    
    def _arun(self, *args, **kwargs) -> Any:
        """异步执行工具(暂不实现)"""
        raise NotImplementedError("Async execution not implemented")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入参数"""
        try:
            self.args_schema(**input_data)
            return True
        except Exception:
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具的JSON Schema"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema.model_json_schema()
        }
