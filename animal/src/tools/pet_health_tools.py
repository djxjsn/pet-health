from typing import Dict, Any, Optional, List, Type
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.tools.base import BaseTool
from src.db.crud import get_pet_by_id, get_pets_by_user
from src.core.knowledge_retriever import get_knowledge_retriever


class PetInfoInput(BaseModel):
    """获取宠物信息工具输入"""
    pet_id: str = Field(..., description="宠物ID")


class PetInfoTool(BaseTool):
    """获取宠物信息工具"""
    
    name: str = "get_pet_info"
    description: str = "获取指定宠物的详细信息,包括名称、品种、年龄、健康状况等"
    args_schema: Type[BaseModel] = PetInfoInput
    
    db: Session = Field(..., description="数据库会话")
    
    def _run(self, pet_id: str) -> Dict[str, Any]:
        """执行获取宠物信息"""
        pet = get_pet_by_id(self.db, pet_id)
        if not pet:
            return {"error": f"未找到ID为{pet_id}的宠物"}
        
        return {
            "pet_id": pet.pet_id,
            "name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "gender": pet.gender,
            "birth_date": str(pet.birth_date) if pet.birth_date else None,
            "weight": float(pet.weight) if pet.weight else None,
            "is_vaccinated": pet.is_vaccinated,
            "is_neutered": pet.is_neutered,
            "photo_url": pet.photo_url
        }


class UserPetsInput(BaseModel):
    """获取用户宠物列表工具输入"""
    user_id: str = Field(..., description="用户ID")


class UserPetsTool(BaseTool):
    """获取用户宠物列表工具"""
    
    name: str = "get_user_pets"
    description: str = "获取用户所有的宠物列表"
    args_schema: Type[BaseModel] = UserPetsInput
    
    db: Session = Field(..., description="数据库会话")
    
    def _run(self, user_id: str) -> List[Dict[str, Any]]:
        """执行获取用户宠物列表"""
        pets, _ = get_pets_by_user(self.db, user_id, page=1, page_size=100)
        
        return [
            {
                "pet_id": pet.pet_id,
                "name": pet.name,
                "species": pet.species,
                "breed": pet.breed,
                "gender": pet.gender
            }
            for pet in pets
        ]


class HealthKnowledgeInput(BaseModel):
    """健康知识检索工具输入"""
    query: str = Field(..., description="查询内容")
    n_results: int = Field(3, description="返回结果数量")


class HealthKnowledgeTool(BaseTool):
    """健康知识检索工具"""
    
    name: str = "search_health_knowledge"
    description: str = "从知识库中检索宠物健康相关的知识和信息"
    args_schema: Type[BaseModel] = HealthKnowledgeInput
    
    def _run(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """执行健康知识检索（通过统一检索入口）"""
        retriever = get_knowledge_retriever()
        return retriever.search(query=query, top_k=n_results)


class SymptomAnalysisInput(BaseModel):
    """症状分析工具输入"""
    symptoms: List[str] = Field(..., description="症状列表")
    pet_species: str = Field(..., description="宠物物种")
    pet_age: Optional[int] = Field(None, description="宠物年龄(月)")


class SymptomAnalysisTool(BaseTool):
    """症状分析工具"""
    
    name: str = "analyze_symptoms"
    description: str = "分析宠物症状,提供可能的健康问题和建议"
    args_schema: Type[BaseModel] = SymptomAnalysisInput
    
    def _run(
        self,
        symptoms: List[str],
        pet_species: str,
        pet_age: Optional[int] = None
    ) -> Dict[str, Any]:
        """执行症状分析（通过统一检索入口）"""
        retriever = get_knowledge_retriever()
        search_results = retriever.search_for_symptom_analysis(
            symptoms=symptoms,
            pet_species=pet_species,
            pet_age=pet_age
        )
        
        possible_conditions = []
        for result in search_results:
            condition = {
                'description': result.get('content', ''),
                'relevance': 1 - result['distance'] if result.get('distance') is not None else 0.5
            }
            possible_conditions.append(condition)
        
        return {
            "symptoms": symptoms,
            "pet_species": pet_species,
            "pet_age": pet_age,
            "possible_conditions": possible_conditions,
            "recommendation": "建议咨询专业兽医进行详细检查"
        }


class NutritionAdviceInput(BaseModel):
    """营养建议工具输入"""
    pet_id: str = Field(..., description="宠物ID")
    health_condition: Optional[str] = Field(None, description="健康状况")


class NutritionAdviceTool(BaseTool):
    """营养建议工具"""
    
    name: str = "get_nutrition_advice"
    description: str = "根据宠物信息提供营养建议"
    args_schema: Type[BaseModel] = NutritionAdviceInput
    
    db: Session = Field(..., description="数据库会话")
    
    def _run(
        self,
        pet_id: str,
        health_condition: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行获取营养建议（通过统一检索入口）"""
        pet = get_pet_by_id(self.db, pet_id)
        if not pet:
            return {"error": f"未找到ID为{pet_id}的宠物"}
        
        age_months = None
        if pet.birth_date:
            from datetime import date
            age_days = (date.today() - pet.birth_date).days
            age_months = age_days // 30
        
        retriever = get_knowledge_retriever()
        search_results = retriever.search_for_nutrition_advice(
            species=pet.species,
            breed=pet.breed,
            age_months=age_months,
            health_condition=health_condition,
            weight=float(pet.weight) if pet.weight else None
        )
        
        recommendations = [result.get('content', '') for result in search_results]
        
        return {
            "pet_id": pet_id,
            "pet_name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "nutrition_recommendations": recommendations,
            "disclaimer": "以上建议仅供参考,具体饮食方案请咨询专业兽医"
        }
