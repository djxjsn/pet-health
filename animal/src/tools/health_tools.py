"""
健康咨询工具集

提供健康咨询、紧急度评估、健康记录查询等工具
"""
import json
import logging
from typing import Dict, Any, List, Optional, Type

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate

from src.tools.base import BaseTool
from src.db.crud import get_pet_by_id, get_health_records_by_pet
from src.core.vector_db import get_vector_db

logger = logging.getLogger(__name__)


# ========== HealthConsultTool ==========

class HealthConsultInput(BaseModel):
    """健康咨询工具输入"""
    pet_id: str = Field(..., description="宠物ID")
    symptoms: List[str] = Field(..., description="症状列表")
    description: Optional[str] = Field(None, description="用户补充描述")


class HealthConsultTool(BaseTool):
    """健康咨询工具 - 编排完整咨询流程"""

    name: str = "health_consult"
    description: str = "对宠物进行健康咨询分析，结合宠物档案、症状描述和医学知识库生成诊断建议和紧急度评估"
    args_schema: Type[BaseModel] = HealthConsultInput

    db: Session = Field(..., description="数据库会话")

    def _run(
        self,
        pet_id: str,
        symptoms: List[str],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行健康咨询"""
        # 1. 加载宠物档案
        pet = get_pet_by_id(self.db, pet_id)
        if not pet:
            return {"error": f"未找到ID为{pet_id}的宠物"}

        # 2. 查询知识库
        symptom_text = ", ".join(symptoms)
        query_text = f"{pet.species} {pet.breed or ''} 症状: {symptom_text}"
        if description:
            query_text += f" 描述: {description}"

        vector_db = get_vector_db()
        kb_results = vector_db.query(query_texts=[query_text], n_results=5)

        knowledge_items = []
        if kb_results and kb_results.get('documents'):
            for i, doc in enumerate(kb_results['documents'][0]):
                knowledge_items.append({
                    'content': doc,
                    'relevance': 1 - kb_results['distances'][0][i] if kb_results.get('distances') else 0.5
                })

        # 3. 加载历史健康记录
        health_records = get_health_records_by_pet(self.db, pet_id, limit=5)
        history_text = ""
        for record in health_records:
            history_text += f"- {record.record_type}: {record.diagnosis or '无诊断'} ({record.record_date})\n"

        # 4. 使用LLM生成结构化诊断
        pet_info = {
            "name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "gender": pet.gender,
            "weight": float(pet.weight) if pet.weight else None,
            "is_vaccinated": pet.is_vaccinated,
            "is_neutered": pet.is_neutered,
        }

        # 尝试获取LLM进行结构化分析
        diagnosis_result = self._analyze_with_llm(
            pet_info=pet_info,
            symptoms=symptoms,
            description=description,
            knowledge=knowledge_items,
            history=history_text
        )

        # 5. 评估紧急度
        urgency = self._assess_urgency(symptoms, pet.species, diagnosis_result)

        return {
            "pet_id": pet_id,
            "pet_name": pet.name,
            "symptoms": symptoms,
            "diagnosis_result": diagnosis_result,
            "urgency_level": urgency["level"],
            "urgency_reasoning": urgency["reasoning"],
            "recommendations": diagnosis_result.get("recommendations", []),
            "disclaimer": "以上建议仅供参考，不构成医疗诊断。如宠物情况紧急，请立即联系专业兽医。"
        }

    def _analyze_with_llm(
        self,
        pet_info: Dict,
        symptoms: List[str],
        description: Optional[str],
        knowledge: List[Dict],
        history: str
    ) -> Dict[str, Any]:
        """使用LLM进行结构化症状分析 (OPT-H-03: 结构化输出)"""
        try:
            from src.core.llm import get_llm
            llm = get_llm()
        except Exception:
            return self._fallback_analysis(symptoms, knowledge)

        knowledge_text = "\n".join(
            f"- {item['content']} (相关度: {item['relevance']:.2f})"
            for item in knowledge[:3]
        )

        # OPT-H-03: 使用Pydantic schema强制LLM返回结构化JSON
        from src.schemas.llm_output import SymptomAnalysisResult
        from langchain_core.output_parsers import JsonOutputParser

        parser = JsonOutputParser(pydantic_object=SymptomAnalysisResult)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的宠物健康顾问。请根据以下信息进行症状分析。

宠物信息:
{pet_info}

症状: {symptoms}
用户描述: {description}

相关知识:
{knowledge}

历史健康记录:
{history}

{format_instructions}"""),
            ("human", "")
        ])

        chain = prompt | llm | parser

        try:
            result = chain.invoke({
                "pet_info": json.dumps(pet_info, ensure_ascii=False),
                "symptoms": ", ".join(symptoms),
                "description": description or "无",
                "knowledge": knowledge_text or "无相关知识点",
                "history": history or "无历史记录",
                "format_instructions": parser.get_format_instructions(),
            })
            return result
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM分析失败，使用降级方案: {e}")
            return self._fallback_analysis(symptoms, knowledge)

    def _fallback_analysis(self, symptoms: List[str], knowledge: List[Dict]) -> Dict[str, Any]:
        """降级方案: 无LLM时基于知识库的基本分析"""
        conditions = []
        for item in knowledge[:3]:
            conditions.append({
                "name": "需进一步确认",
                "description": item['content'],
                "confidence": item.get('relevance', 0.5)
            })

        return {
            "possible_conditions": conditions,
            "recommendations": ["建议咨询专业兽医进行详细检查"],
            "severity": "中等",
            "vet_recommended": True
        }

    def _assess_urgency(self, symptoms: List[str], species: str, diagnosis: Dict) -> Dict:
        """评估紧急程度"""
        # 紧急症状关键词
        emergency_keywords = ["抽搐", "呼吸困难", "昏迷", "大量出血", "呕吐不止", "无法排尿"]
        urgent_keywords = ["拒食", "精神萎靡", "持续呕吐", "腹泻带血", "高烧"]

        symptom_text = " ".join(symptoms)

        for kw in emergency_keywords:
            if kw in symptom_text:
                return {"level": 5, "reasoning": f"检测到紧急症状: {kw}"}

        for kw in urgent_keywords:
            if kw in symptom_text:
                return {"level": 4, "reasoning": f"检测到较急症状: {kw}"}

        severity = diagnosis.get("severity", "轻微")
        vet_recommended = diagnosis.get("vet_recommended", False)

        if severity == "严重" or vet_recommended:
            return {"level": 3, "reasoning": "AI分析建议就医"}
        elif severity == "中等":
            return {"level": 2, "reasoning": "症状中等，建议观察"}
        else:
            return {"level": 1, "reasoning": "症状轻微，可自行观察"}


# ========== UrgencyAssessmentTool ==========

class UrgencyAssessmentInput(BaseModel):
    """紧急度评估输入"""
    symptoms: List[str] = Field(..., description="症状列表")
    pet_species: str = Field(..., description="宠物物种")
    pet_breed: Optional[str] = Field(None, description="宠物品种")
    pet_age_months: Optional[int] = Field(None, description="宠物年龄(月)")


class UrgencyAssessmentTool(BaseTool):
    """紧急度评估工具"""

    name: str = "assess_urgency"
    description: str = "评估宠物症状的紧急程度(1-5)，考虑症状严重度、物种和年龄风险因素"
    args_schema: Type[BaseModel] = UrgencyAssessmentInput

    def _run(
        self,
        symptoms: List[str],
        pet_species: str,
        pet_breed: Optional[str] = None,
        pet_age_months: Optional[int] = None
    ) -> Dict[str, Any]:
        """执行紧急度评估"""
        emergency_keywords = ["抽搐", "呼吸困难", "昏迷", "大量出血", "呕吐不止", "无法排尿"]
        urgent_keywords = ["拒食", "精神萎靡", "持续呕吐", "腹泻带血", "高烧"]
        moderate_keywords = ["呕吐", "腹泻", "咳嗽", "打喷嚏", "掉毛"]

        symptom_text = " ".join(symptoms)

        # 基于关键词的紧急度
        urgency = 1
        reasoning = "症状轻微"

        for kw in emergency_keywords:
            if kw in symptom_text:
                urgency = 5
                reasoning = f"检测到紧急症状: {kw}"
                break

        if urgency < 5:
            for kw in urgent_keywords:
                if kw in symptom_text:
                    urgency = 4
                    reasoning = f"检测到较急症状: {kw}"
                    break

        if urgency < 4:
            for kw in moderate_keywords:
                if kw in symptom_text:
                    urgency = 2
                    reasoning = f"检测到中等症状: {kw}"
                    break

        # 年龄风险因子
        if pet_age_months is not None:
            if pet_age_months < 6:  # 幼宠
                urgency = min(5, urgency + 1)
                reasoning += "；幼宠风险更高"
            elif pet_age_months > 96:  # 老年宠(8岁+)
                urgency = min(5, urgency + 1)
                reasoning += "；老年宠物风险更高"

        # 品种特有风险（简化版）
        high_risk_breeds = {
            "dog": ["法斗", "巴哥", "斗牛", "柯基"],
            "cat": ["波斯猫", "折耳猫", "加菲猫"]
        }
        if pet_breed:
            risk_list = high_risk_breeds.get(pet_species, [])
            for breed_name in risk_list:
                if breed_name in (pet_breed or ""):
                    urgency = min(5, urgency + 1)
                    reasoning += f"；{pet_breed}品种有较高健康风险"
                    break

        return {
            "urgency_level": urgency,
            "reasoning": reasoning,
            "recommendation": self._get_urgency_recommendation(urgency)
        }

    def _get_urgency_recommendation(self, level: int) -> str:
        """根据紧急度返回建议"""
        recommendations = {
            1: "症状轻微，可自行观察。如有加重请及时咨询。",
            2: "建议观察1-2天，如症状持续或加重请咨询兽医。",
            3: "建议尽快咨询兽医，进行专业检查。",
            4: "建议尽快就医，不要拖延。",
            5: "请立即送往宠物医院急诊！",
        }
        return recommendations.get(level, "建议咨询兽医。")


# ========== HealthRecordTool ==========

class HealthRecordInput(BaseModel):
    """健康记录查询输入"""
    pet_id: str = Field(..., description="宠物ID")


class HealthRecordTool(BaseTool):
    """健康记录查询工具"""

    name: str = "get_health_records"
    description: str = "获取宠物的健康档案记录，用于了解宠物的病史和健康历史"
    args_schema: Type[BaseModel] = HealthRecordInput

    db: Session = Field(..., description="数据库会话")

    def _run(self, pet_id: str) -> List[Dict[str, Any]]:
        """获取宠物健康记录"""
        records = get_health_records_by_pet(self.db, pet_id, limit=10)

        return [
            {
                "record_id": r.record_id,
                "record_type": r.record_type,
                "symptoms": r.symptoms,
                "diagnosis": r.diagnosis,
                "prescription": r.prescription,
                "vet_name": r.vet_name,
                "hospital": r.hospital,
                "record_date": str(r.record_date) if r.record_date else None,
                "next_checkup_date": str(r.next_checkup_date) if r.next_checkup_date else None,
                "notes": r.notes,
            }
            for r in records
        ]
