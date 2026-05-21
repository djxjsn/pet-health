from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from src.schemas.llm_output import SymptomAnalysisResult


# ========== 结构化症状模型 ==========

class StructuredSymptom(BaseModel):
    """结构化症状描述"""
    name: str = Field(..., description="症状名称: 呕吐/腹泻/咳嗽/跛行等")
    duration: Optional[str] = Field(None, description="持续时间: 2天/1周等")
    severity: Optional[int] = Field(None, ge=1, le=5, description="严重程度 1-5")
    onset: Optional[str] = Field(None, description="起病方式: sudden(急性)/gradual(渐进)")
    frequency: Optional[str] = Field(None, description="频率: 4次/天/间歇性等")
    character: Optional[str] = Field(None, description="特征: 水样便/干咳/湿咳等")
    body_location: Optional[str] = Field(None, description="部位: 左前肢/腹部/耳部等")
    notes: Optional[str] = Field(None, description="补充说明")


class StructuredDiagnosis(BaseModel):
    """结构化诊断结果"""
    primary: str = Field(..., description="主要诊断: 急性肠胃炎")
    icd_code: Optional[str] = Field(None, description="国际疾病编码: A09")
    differential: Optional[List[str]] = Field(None, description="鉴别诊断列表")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="诊断置信度 0-1")
    severity: Optional[str] = Field(None, description="严重程度: mild/moderate/severe/critical")
    is_chronic: Optional[bool] = Field(None, description="是否慢性病")


# ========== Health Record Schemas ==========

class HealthRecordCreate(BaseModel):
    record_type: str = Field(..., description="记录类型: checkup/vaccine/illness/allergy/surgery")
    # 兼容旧版：纯文本症状列表
    symptoms: Optional[List[str]] = Field(None, description="症状列表(简版)")
    # 结构化症状（新版）
    structured_symptoms: Optional[List[StructuredSymptom]] = Field(None, description="结构化症状列表")
    # 兼容旧版：纯文本诊断
    diagnosis: Optional[str] = Field(None, description="诊断结果(简版)")
    # 结构化诊断（新版）
    structured_diagnosis: Optional[StructuredDiagnosis] = Field(None, description="结构化诊断结果")
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
    structured_symptoms: Optional[List[StructuredSymptom]] = None
    diagnosis: Optional[str] = None
    structured_diagnosis: Optional[StructuredDiagnosis] = None
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


# ========== Health API Request/Response ==========

class HealthConsultRequest(BaseModel):
    """健康咨询请求"""
    pet_id: str = Field(..., description="宠物ID")
    symptoms: List[str] = Field(..., description="症状列表")
    description: Optional[str] = Field(None, description="详细描述")
    image_urls: Optional[List[str]] = Field(None, description="图片URL列表")


class HealthConsultResponse(BaseModel):
    """健康咨询响应"""
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
    """症状分析响应"""
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