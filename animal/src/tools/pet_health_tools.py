from typing import Dict, Any, Optional, List, Type
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.tools.base import BaseTool
from src.db.crud.pet import (
    get_pet_by_id, get_pets_by_user,
    get_allergies_by_pet, check_allergy_conflict,
    get_vaccinations_by_pet, get_upcoming_vaccinations,
)
from src.core.knowledge_retriever import get_knowledge_retriever


class PetInfoInput(BaseModel):
    """获取宠物信息工具输入"""
    pet_id: str = Field(..., description="宠物ID")


class PetInfoTool(BaseTool):
    """获取宠物信息工具（含过敏源和疫苗信息）"""
    
    name: str = "get_pet_info"
    description: str = "获取指定宠物的详细信息,包括名称、品种、年龄、健康状况、过敏源、疫苗接种记录等"
    args_schema: Type[BaseModel] = PetInfoInput
    
    db: Session = Field(..., description="数据库会话")
    
    def _run(self, pet_id: str) -> Dict[str, Any]:
        """执行获取宠物信息"""
        pet = get_pet_by_id(self.db, pet_id)
        if not pet:
            return {"error": f"未找到ID为{pet_id}的宠物"}
        
        # 获取过敏源
        allergies = get_allergies_by_pet(self.db, pet_id, active_only=True)
        allergy_list = [
            {
                "allergen": a.allergen_name,
                "type": a.allergen_type,
                "severity": a.severity,
                "reaction": a.reaction_desc,
            }
            for a in allergies
        ]
        
        # 获取疫苗记录摘要
        vaccinations = get_vaccinations_by_pet(self.db, pet_id)
        vaccine_summary = [
            {
                "name": v.vaccine_name,
                "date": str(v.administered_date),
                "next_due": str(v.next_due_date) if v.next_due_date else None,
            }
            for v in vaccinations[:5]  # 最近5条
        ]
        
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
            "current_status": pet.current_status,
            "blood_type": pet.blood_type,
            "diet_type": pet.diet_type,
            "allergies": allergy_list,
            "vaccinations": vaccine_summary,
            "photo_url": pet.photo_url,
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
                "gender": pet.gender,
                "current_status": pet.current_status,
            }
            for pet in pets
        ]


class AllergyCheckInput(BaseModel):
    """过敏源检查工具输入"""
    pet_id: str = Field(..., description="宠物ID")
    ingredient_name: str = Field(..., description="要检查的成分/物质名称")


class AllergyCheckTool(BaseTool):
    """过敏源冲突检查工具（Agent 联动核心）"""
    
    name: str = "check_allergy_conflict"
    description: str = "检查某个成分或物质是否与宠物的过敏源冲突。在推荐食品、药品、用品前必须调用此工具。"
    args_schema: Type[BaseModel] = AllergyCheckInput
    
    db: Session = Field(..., description="数据库会话")
    
    def _run(self, pet_id: str, ingredient_name: str) -> Dict[str, Any]:
        """检查成分是否与宠物过敏源冲突"""
        conflict = check_allergy_conflict(self.db, pet_id, ingredient_name)
        if conflict:
            return {
                "has_conflict": True,
                "warning": f"警告：该宠物对「{conflict.allergen_name}」过敏（严重程度：{conflict.severity}），反应：{conflict.reaction_desc or '未记录'}",
                "allergen": conflict.allergen_name,
                "severity": conflict.severity,
                "recommendation": "请避免推荐含有该成分的产品，建议寻找替代方案",
            }
        return {
            "has_conflict": False,
            "message": f"未发现宠物对「{ingredient_name}」的过敏记录",
        }


class VaccinationReminderInput(BaseModel):
    """疫苗提醒工具输入"""
    pet_id: str = Field(..., description="宠物ID")
    days: int = Field(30, description="查询未来多少天内到期的疫苗")


class VaccinationReminderTool(BaseTool):
    """疫苗接种提醒工具"""
    
    name: str = "get_vaccination_reminders"
    description: str = "获取宠物即将到期的疫苗接种提醒"
    args_schema: Type[BaseModel] = VaccinationReminderInput
    
    db: Session = Field(..., description="数据库会话")
    
    def _run(self, pet_id: str, days: int = 30) -> Dict[str, Any]:
        """获取即将到期的疫苗提醒"""
        upcoming = get_upcoming_vaccinations(self.db, pet_id, days=days)
        if not upcoming:
            return {
                "has_reminder": False,
                "message": f"未来 {days} 天内无到期疫苗",
            }
        
        reminders = [
            {
                "vaccine_name": v.vaccine_name,
                "next_due_date": str(v.next_due_date),
                "dose_number": v.dose_number,
                "hospital": v.hospital,
            }
            for v in upcoming
        ]
        
        return {
            "has_reminder": True,
            "count": len(reminders),
            "reminders": reminders,
            "message": f"有 {len(reminders)} 个疫苗即将到期，请及时接种",
        }


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
        """执行健康知识检索（默认启用质量门禁）"""
        retriever = get_knowledge_retriever()
        quality_result = retriever.search_with_quality(
            query=query,
            top_k=n_results,
            enable_self_rag=True,
            enable_crag=True,
        )

        results = quality_result.get("results", [])
        action = quality_result.get("action", "accept")
        confidence = quality_result.get("confidence", 0.0)

        if action == "refuse":
            return [{
                "content": "当前知识库证据不足，建议尽快咨询专业兽医进行面诊。",
                "metadata": {
                    "type": "quality_gate_refuse",
                    "action": action,
                    "confidence": confidence,
                },
                "distance": 1.0,
            }]

        for item in results:
            metadata = item.get("metadata", {}) if isinstance(item, dict) else {}
            if isinstance(metadata, dict):
                metadata["quality_action"] = action
                metadata["quality_confidence"] = confidence
                item["metadata"] = metadata
        return results


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
        """执行症状分析（P2: 接入质量门禁）"""
        retriever = get_knowledge_retriever()
        symptom_text = ", ".join(symptoms)
        query_text = f"{pet_species} 症状: {symptom_text}"
        if pet_age:
            query_text += f" 年龄: {pet_age}个月"

        quality_result = retriever.search_with_quality(
            query=query_text,
            top_k=5,
            category="disease",
            enable_self_rag=True,
            enable_crag=True,
        )
        search_results = quality_result.get("results", [])
        action = quality_result.get("action", "accept")
        confidence = quality_result.get("confidence", 0.0)

        possible_conditions = []
        for result in search_results:
            condition = {
                'description': result.get('content', ''),
                'relevance': 1 - result['distance'] if result.get('distance') is not None else 0.5
            }
            possible_conditions.append(condition)

        recommendation = "建议咨询专业兽医进行详细检查"
        if action == "refuse":
            recommendation = "当前证据不足，建议尽快前往宠物医院进行面诊检查"

        return {
            "symptoms": symptoms,
            "pet_species": pet_species,
            "pet_age": pet_age,
            "possible_conditions": possible_conditions,
            "recommendation": recommendation,
            "quality_action": action,
            "quality_confidence": confidence,
        }


class NutritionAdviceInput(BaseModel):
    """营养建议工具输入"""
    pet_id: str = Field(..., description="宠物ID")
    health_condition: Optional[str] = Field(None, description="健康状况")


class NutritionAdviceTool(BaseTool):
    """营养建议工具"""
    
    name: str = "get_nutrition_advice"
    description: str = "根据宠物信息提供营养建议（自动检查过敏源）"
    args_schema: Type[BaseModel] = NutritionAdviceInput
    
    db: Session = Field(..., description="数据库会话")
    
    def _run(
        self,
        pet_id: str,
        health_condition: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行获取营养建议（P2: 接入质量门禁）"""
        pet = get_pet_by_id(self.db, pet_id)
        if not pet:
            return {"error": f"未找到ID为{pet_id}的宠物"}
        
        age_months = None
        if pet.birth_date:
            from datetime import date
            age_days = (date.today() - pet.birth_date).days
            age_months = age_days // 30
        
        retriever = get_knowledge_retriever()
        query_parts = [f"{pet.species} {pet.breed or ''} 营养建议"]
        if age_months is not None:
            query_parts.append(f"年龄: {age_months}个月")
        if health_condition:
            query_parts.append(f"健康状况: {health_condition}")
        if pet.weight:
            query_parts.append(f"体重: {float(pet.weight)}kg")
        query_text = " ".join(query_parts)

        quality_result = retriever.search_with_quality(
            query=query_text,
            top_k=3,
            category="nutrition",
            enable_self_rag=True,
            enable_crag=True,
        )
        search_results = quality_result.get("results", [])
        action = quality_result.get("action", "accept")
        confidence = quality_result.get("confidence", 0.0)

        recommendations = [result.get('content', '') for result in search_results]
        if action == "refuse" and not recommendations:
            recommendations = ["当前知识库证据不足，建议由兽医根据体况提供个性化营养方案"]
        
        # 获取过敏源信息，附加到建议中
        allergies = get_allergies_by_pet(self.db, pet_id, active_only=True)
        allergy_warnings = []
        if allergies:
            allergy_names = [a.allergen_name for a in allergies]
            allergy_warnings.append(f"注意：该宠物有以下过敏源：{', '.join(allergy_names)}，请避免推荐含有这些成分的食品")
        
        return {
            "pet_id": pet_id,
            "pet_name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "nutrition_recommendations": recommendations,
            "allergy_warnings": allergy_warnings,
            "quality_action": action,
            "quality_confidence": confidence,
            "disclaimer": "以上建议仅供参考,具体饮食方案请咨询专业兽医"
        }