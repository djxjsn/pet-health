"""
LLM结构化输出Schema定义

定义所有Agent工具的结构化输出模型，用于强制LLM返回标准JSON格式。
基于OPT-H-03优化方案实施。
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ========== 症状分析结构化输出 ==========

class ConditionItem(BaseModel):
    """可能的疾病/情况"""
    name: str = Field(..., description="疾病或情况名称")
    description: str = Field(..., description="详细描述")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度(0-1)")


class SymptomAnalysisResult(BaseModel):
    """症状分析LLM结构化输出"""
    possible_conditions: List[ConditionItem] = Field(
        ..., description="可能的疾病/情况列表"
    )
    recommendations: List[str] = Field(
        ..., description="建议列表"
    )
    severity: Literal["轻微", "中等", "严重", "紧急"] = Field(
        ..., description="严重程度"
    )
    vet_recommended: bool = Field(
        ..., description="是否建议就医"
    )


# ========== 行为分析结构化输出 ==========

class BehaviorCauseItem(BaseModel):
    """可能的行为原因"""
    cause: str = Field(..., description="原因描述")
    probability: float = Field(..., ge=0.0, le=1.0, description="概率(0-1)")
    category: Literal["breed", "age", "environment", "health", "training"] = Field(
        ..., description="原因分类"
    )


class BehaviorAnalysisResult(BaseModel):
    """行为分析LLM结构化输出"""
    possible_causes: List[BehaviorCauseItem] = Field(
        ..., description="可能的原因列表"
    )
    recommendations: List[str] = Field(
        ..., description="训练建议列表"
    )


# ========== 健康咨询完整输出 ==========

class HealthConsultationOutput(BaseModel):
    """健康咨询完整输出(包含LLM分析结果)"""
    pet_id: str = Field(..., description="宠物ID")
    pet_name: str = Field(..., description="宠物名称")
    symptoms: List[str] = Field(..., description="症状列表")
    diagnosis_result: SymptomAnalysisResult = Field(
        ..., description="诊断分析结果"
    )
    urgency_level: int = Field(..., ge=1, le=5, description="紧急程度(1-5)")
    urgency_reasoning: str = Field(..., description="紧急度推理")
    recommendations: List[str] = Field(..., description="建议列表")
    disclaimer: str = Field(
        default="以上建议仅供参考，不构成医疗诊断。如宠物情况紧急，请立即联系专业兽医。",
        description="免责声明"
    )


# ========== 行为分析完整输出 ==========

class BehaviorAnalysisOutput(BaseModel):
    """行为分析完整输出(包含LLM分析结果)"""
    pet_id: str = Field(..., description="宠物ID")
    pet_name: str = Field(..., description="宠物名称")
    behavior_category: str = Field(..., description="行为类别")
    possible_causes: List[BehaviorCauseItem] = Field(
        ..., description="可能的原因列表"
    )
    breed_analysis: dict = Field(..., description="品种特性分析")
    recommendations: List[str] = Field(..., description="训练建议列表")
    severity_level: int = Field(..., ge=1, le=5, description="严重程度(1-5)")
    disclaimer: str = Field(
        default="以上分析仅供参考，如有严重行为问题建议咨询专业宠物训练师。",
        description="免责声明"
    )
