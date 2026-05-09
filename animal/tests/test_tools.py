"""
工具系统测试
"""
import pytest
from sqlalchemy.orm import Session
from src.tools.tool_registry import get_tool_registry, ToolRegistry
from src.tools.pet_health_tools import PetInfoTool, HealthKnowledgeTool
from src.db.crud import create_user, create_pet
from src.schemas.user import UserCreate
from src.schemas.pet import PetCreate


class TestToolRegistry:
    """工具注册管理器测试类"""
    
    def test_tool_registry_singleton(self):
        """测试单例模式"""
        registry1 = get_tool_registry()
        registry2 = get_tool_registry()
        assert registry1 is registry2
    
    def test_list_tools(self):
        """测试列出工具"""
        registry = get_tool_registry()
        tools = registry.list_tools()
        
        assert "get_pet_info" in tools
        assert "get_user_pets" in tools
        assert "search_health_knowledge" in tools
        assert "analyze_symptoms" in tools
        assert "get_nutrition_advice" in tools
    
    def test_get_tool(self, db_session: Session):
        """测试获取工具"""
        registry = get_tool_registry()
        tool = registry.get_tool("get_pet_info", db=db_session)
        
        assert tool is not None
        assert tool.name == "get_pet_info"
    
    def test_get_tools_schema(self):
        """测试获取工具Schema"""
        registry = get_tool_registry()
        schemas = registry.get_tools_schema()
        
        assert len(schemas) > 0
        assert all("name" in schema for schema in schemas)
        assert all("description" in schema for schema in schemas)
        assert all("parameters" in schema for schema in schemas)


class TestPetHealthTools:
    """宠物健康工具测试类"""
    
    @pytest.fixture
    def test_user(self, db_session: Session):
        """创建测试用户"""
        user_data = UserCreate(
            phone="13800000001",
            email="test@example.com",
            password="test1234"
        )
        user = create_user(db_session, user_data)
        return user
    
    @pytest.fixture
    def test_pet(self, db_session: Session, test_user):
        """创建测试宠物"""
        pet_data = PetCreate(
            name="旺财",
            species="dog",
            breed="金毛",
            gender="male"
        )
        pet = create_pet(db_session, test_user.user_id, pet_data)
        return pet
    
    def test_pet_info_tool(self, db_session: Session, test_pet):
        """测试宠物信息工具"""
        tool = PetInfoTool(db=db_session)
        
        result = tool._run(pet_id=test_pet.pet_id)
        
        assert result is not None
        assert result["pet_id"] == test_pet.pet_id
        assert result["name"] == "旺财"
        assert result["species"] == "dog"
    
    def test_pet_info_tool_not_found(self, db_session: Session):
        """测试宠物信息工具(宠物不存在)"""
        tool = PetInfoTool(db=db_session)
        
        result = tool._run(pet_id="non-existent-id")
        
        assert "error" in result
    
    def test_health_knowledge_tool(self):
        """测试健康知识检索工具"""
        tool = HealthKnowledgeTool()
        
        result = tool._run(query="狗的疾病", n_results=3)
        
        assert result is not None
        assert isinstance(result, list)
