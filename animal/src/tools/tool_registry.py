from typing import Dict, List, Type, Optional, Any
from sqlalchemy.orm import Session

from src.tools.base import BaseTool
from src.tools.pet_health_tools import (
    PetInfoTool,
    UserPetsTool,
    HealthKnowledgeTool,
    SymptomAnalysisTool,
    NutritionAdviceTool,
)
from src.tools.health_tools import (
    HealthConsultTool,
    UrgencyAssessmentTool,
    HealthRecordTool,
)
from src.tools.behavior_tools import (
    BehaviorAnalysisTool,
    TrainingRecommendationTool,
)
from src.tools.external_tools import (
    WeatherTool,
    MapServiceTool,
    WebSearchTool,
    ImageRecognitionTool,
    KnowledgeEnhanceTool,
)


class ToolRegistry:
    """工具注册管理器"""
    
    _instance: Optional['ToolRegistry'] = None
    _tools: Dict[str, Type[BaseTool]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._register_default_tools()
        return cls._instance
    
    def _register_default_tools(self):
        """注册默认工具"""
        self.register_tool("get_pet_info", PetInfoTool)
        self.register_tool("get_user_pets", UserPetsTool)
        self.register_tool("search_health_knowledge", HealthKnowledgeTool)
        self.register_tool("analyze_symptoms", SymptomAnalysisTool)
        self.register_tool("get_nutrition_advice", NutritionAdviceTool)
        self.register_tool("health_consult", HealthConsultTool)
        self.register_tool("assess_urgency", UrgencyAssessmentTool)
        self.register_tool("get_health_records", HealthRecordTool)
        self.register_tool("analyze_behavior", BehaviorAnalysisTool)
        self.register_tool("get_training_recommendations", TrainingRecommendationTool)
        
        # 外部 API 集成工具
        self.register_tool("get_weather", WeatherTool)
        self.register_tool("search_nearby", MapServiceTool)
        self.register_tool("web_search", WebSearchTool)
        self.register_tool("recognize_image", ImageRecognitionTool)
        self.register_tool("enhance_knowledge", KnowledgeEnhanceTool)
    
    def register_tool(self, name: str, tool_class: Type[BaseTool]):
        """注册工具
        
        Args:
            name: 工具名称
            tool_class: 工具类
        """
        self._tools[name] = tool_class
    
    def unregister_tool(self, name: str):
        """注销工具
        
        Args:
            name: 工具名称
        """
        if name in self._tools:
            del self._tools[name]
    
    def get_tool(self, name: str, db: Optional[Session] = None, **kwargs) -> Optional[BaseTool]:
        """获取工具实例
        
        Args:
            name: 工具名称
            db: 数据库会话
            **kwargs: 其他参数
            
        Returns:
            工具实例
        """
        tool_class = self._tools.get(name)
        if not tool_class:
            return None
        
        if 'db' in tool_class.model_fields and db:
            kwargs['db'] = db
        
        return tool_class(**kwargs)
    
    def list_tools(self) -> List[str]:
        """列出所有注册的工具名称"""
        return list(self._tools.keys())
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        schemas = []
        for name, tool_class in self._tools.items():
            try:
                if 'db' in tool_class.model_fields:
                    schemas.append({
                        "name": name,
                        "description": tool_class.model_fields.get('description', tool_class.__doc__ or ''),
                        "parameters": tool_class.model_fields.get('args_schema', BaseModel).model_json_schema() if hasattr(tool_class, 'args_schema') else {},
                        "requires_db": True,
                    })
                else:
                    tool_instance = tool_class()
                    schemas.append(tool_instance.get_schema())
            except Exception:
                schemas.append({
                    "name": name,
                    "description": tool_class.__doc__ or '',
                    "parameters": {},
                })
        return schemas
    
    def get_tool_description(self, name: str) -> Optional[str]:
        """获取工具描述
        
        Args:
            name: 工具名称
            
        Returns:
            工具描述
        """
        tool_class = self._tools.get(name)
        if not tool_class:
            return None
        
        tool_instance = tool_class()
        return tool_instance.description


def get_tool_registry() -> ToolRegistry:
    """获取工具注册管理器实例(单例)"""
    return ToolRegistry()
