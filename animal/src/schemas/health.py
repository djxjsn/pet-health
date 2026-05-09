from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from src.schemas.llm_output import SymptomAnalysisResult


# ========== Health Record Schemas ==========

class HealthRecordCreate(BaseModel):
    record_type: str = Field(..., description="记录类型: checkup/vaccine/illness/allergy/surgery")
    symptoms: Optional[List[str]] = Field(None, description="症状列表")
    diagnosis: Optional[str] = Field(None, description="诊断结果")
    prescription: Optional[str] = Field(None, description="处方/用药")
    vet_name: Optional[str] = Field(None, max_length=50, description="兽医姓名")
    hospital: Optional[str] = Field(None, max_length=100, description="医院/诊所名称")
    record_date: Optional[date] = Field(None, description="就诊日期")
    next_checkup_date: Optional[date] = Field(None, description="下次检查日期")
    notes: Optional[str] = Field(None, description="备注")


class HealthRecordResponse(BaseModel):
    record_id: str
    pet_id: str
    record_type: str
    symptoms: Optional[List[str]] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    vet_name: Optional[str] = None
    hospital: Optional[str] = None
    record_date: Optional[date] = None
    next_checkup_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ========== Consultation Schemas ==========

class ConsultationCreate(BaseModel):
    pet_id: str = Field(..., description="宠物ID")
    symptoms: Optional[List[str]] = Field(None, description="症状列表")
    description: Optional[str] = Field(None, description="用户描述")
    image_urls: Optional[List[str]] = Field(None, description="上传图片URL列表")


class ConsultationResponse(BaseModel):
    consultation_id: str
    user_id: str
    pet_id: str
    symptoms: Optional[List[str]] = None
    description: Optional[str] = None
    image_urls: Optional[List[str]] = None
    diagnosis_result: Optional[SymptomAnalysisResult] = None
    recommendations: Optional[List[str]] = None
    urgency_level: int
    status: str
    conversation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ========== Health API Request/Response (OPT-H-03 Structured) ==========

class HealthConsultRequest(BaseModel):
    """健康咨询请求"""
    pet_id: str = Field(..., description="宠物ID")
    symptoms: List[str] = Field(..., description="症状列表")
    description: Optional[str] = Field(None, description="详细描述")
    image_urls: Optional[List[str]] = Field(None, description="图片URL列表")


class HealthConsultResponse(BaseModel):
    """健康咨询响应 (OPT-H-03: 使用结构化诊断结果)"""
    consultation_id: str
    pet_id: str
    diagnosis_result: Optional[SymptomAnalysisResult] = None
    recommendations: Optional[List[str]] = None
    urgency_level: int
    urgency_reasoning: Optional[str] = None
    disclaimer: str = Field(
        default="以上建议仅供参考，不构成医疗诊断。如宠物情况紧急，请立即联系专业兽医。",
        description="免责声明"
    )


class SymptomAnalysisRequest(BaseModel):
    """症状分析请求（不创建咨询记录）"""
    pet_id: str = Field(..., description="宠物ID")
    symptoms: List[str] = Field(..., description="症状列表")
    description: Optional[str] = Field(None, description="补充描述")


class SymptomAnalysisResponse(BaseModel):
    """症状分析响应 (OPT-H-03: 使用结构化输出)"""
    diagnosis_result: SymptomAnalysisResult = Field(
        ...,
        description="诊断分析结果（结构化）"
    )
    urgency_level: int = Field(default=1, description="紧急程度(1-5)")
    urgency_reasoning: Optional[str] = Field(None, description="紧急度推理")
    recommendations: List[str] = Field(default_factory=list, description="建议列表")
    disclaimer: str = Field(
        default="以上分析仅供参考，不构成医疗诊断。如宠物情况紧急，请立即联系专业兽医。",
        description="免责声明"
    )
