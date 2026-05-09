from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from src.schemas.llm_output import BehaviorAnalysisResult


# ========== Behavior Analysis Schemas ==========

class BehaviorAnalysisCreate(BaseModel):
    pet_id: str = Field(..., description="宠物ID")
    behavior_description: str = Field(..., description="行为描述")
    behavior_category: Optional[str] = Field(
        None,
        description="行为类别: destructive/howling/aggression/food_refusal/excessive_licking/other"
    )


class BehaviorAnalysisResponse(BaseModel):
    analysis_id: str
    user_id: str
    pet_id: str
    behavior_description: Optional[str] = None
    behavior_category: Optional[str] = None
    possible_causes: Optional[List[Dict[str, Any]]] = None
    breed_analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    severity_level: int
    status: str
    conversation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ========== Behavior API Request/Response (OPT-B-03 Structured) ==========

class BehaviorAnalyzeRequest(BaseModel):
    """行为分析请求"""
    pet_id: str = Field(..., description="宠物ID")
    behavior_description: str = Field(..., description="行为描述，如'最近总拆家'")
    behavior_category: Optional[str] = Field(
        None,
        description="行为类别(可选): destructive/howling/aggression/food_refusal/excessive_licking/other"
    )


class BehaviorAnalyzeResponse(BaseModel):
    """行为分析响应 (OPT-B-03: 使用结构化输出)"""
    analysis_id: str
    pet_id: str
    behavior_category: Optional[str] = None
    analysis_result: BehaviorAnalysisResult = Field(
        ...,
        description="行为分析结果（结构化）"
    )
    breed_analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    severity_level: int
    disclaimer: str = Field(
        default="以上分析仅供参考，如有严重行为问题建议咨询专业宠物训练师。",
        description="免责声明"
    )


# ========== Training Recommendation Schemas ==========

class TrainingRecommendationRequest(BaseModel):
    """训练建议请求"""
    pet_id: str = Field(..., description="宠物ID")
    behavior_category: Optional[str] = Field(
        None,
        description="行为类别(可选)，不指定则基于宠物档案综合建议"
    )


class TrainingRecommendationResponse(BaseModel):
    """训练建议响应"""
    pet_id: str
    pet_name: Optional[str] = None
    behavior_category: Optional[str] = None
    breed_specific_advice: Optional[List[str]] = None
    training_plan: Optional[List[Dict[str, Any]]] = None
    tips: Optional[List[str]] = None
    disclaimer: str = Field(
        default="以上训练建议仅供参考，如行为问题严重建议咨询专业宠物训练师。",
        description="免责声明"
    )
