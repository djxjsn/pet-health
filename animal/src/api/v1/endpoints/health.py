"""
健康咨询与症状分析端点

提供健康咨询、症状分析、咨询历史等功能

架构变更(v2.0): health_records/consultations 从 MySQL 迁移到 MongoDB
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.models.pet import Pet
from src.schemas.health import (
    HealthConsultRequest,
    HealthConsultResponse,
    SymptomAnalysisRequest,
    SymptomAnalysisResponse,
    ConsultationCreate,
    ConsultationResponse,
    HealthRecordCreate,
    HealthRecordResponse,
)
from src.schemas.llm_output import SymptomAnalysisResult, ConditionItem
from src.db.crud.pet import get_pet_by_id
from src.repositories.mongo_repositories import (
    HealthRecordRepository,
    ConsultationRepository,
)

router = APIRouter()


@router.post("/consult", response_model=HealthConsultResponse, status_code=status.HTTP_200_OK)
async def health_consult(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: HealthConsultRequest,
) -> Any:
    """健康咨询

    - 创建咨询记录
    - 执行AI症状分析
    - 写回诊断结果和紧急度评估
    - 返回完整咨询结果
    """
    # 验证宠物归属
    pet = get_pet_by_id(db, request.pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问该宠物信息")

    # 创建咨询记录 (MongoDB)
    import uuid
    consultation_id = str(uuid.uuid4())
    consultation_doc = {
        "consultation_id": consultation_id,
        "user_id": current_user.user_id,
        "pet_id": request.pet_id,
        "symptoms": request.symptoms,
        "description": request.description,
        "image_urls": request.image_urls,
        "status": "pending",
        "urgency_level": 1,
    }
    ConsultationRepository.create(consultation_doc)

    # 执行健康咨询分析
    try:
        from src.tools.health_tools import HealthConsultTool
        consult_tool = HealthConsultTool(db=db)
        result = consult_tool._run(
            pet_id=request.pet_id,
            symptoms=request.symptoms,
            description=request.description
        )
    except Exception as e:
        # 分析失败时仍保留咨询记录，标记为pending
        ConsultationRepository.update(consultation_id, {"status": "pending"})
        raise HTTPException(
            status_code=500,
            detail=f"健康分析失败: {str(e)}"
        )

    # 构建结构化的 diagnosis_result
    raw_diagnosis = result.get("diagnosis_result", {})
    diagnosis_result = SymptomAnalysisResult(
        possible_conditions=raw_diagnosis.get("possible_conditions", []),
        recommendations=result.get("recommendations", []),
        severity=raw_diagnosis.get("severity", "未知"),
        vet_recommended=raw_diagnosis.get("vet_recommended", False),
    )
    recommendations = result.get("recommendations", [])
    urgency_level = result.get("urgency_level", 1)
    urgency_reasoning = result.get("urgency_reasoning", "")

    ConsultationRepository.update(
        consultation_id,
        {
            "diagnosis_result": diagnosis_result.model_dump(mode="json"),
            "recommendations": recommendations,
            "urgency_level": urgency_level,
            "status": "completed",
        }
    )

    return HealthConsultResponse(
        consultation_id=consultation_id,
        pet_id=request.pet_id,
        diagnosis_result=diagnosis_result,
        recommendations=recommendations,
        urgency_level=urgency_level,
        urgency_reasoning=urgency_reasoning,
    )


@router.post("/analyze", response_model=SymptomAnalysisResponse, status_code=status.HTTP_200_OK)
async def symptom_analysis(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: SymptomAnalysisRequest,
) -> Any:
    """症状分析（不创建咨询记录）

    - 快速分析症状
    - 返回可能的情况和建议
    - 不记录到数据库
    """
    pet = get_pet_by_id(db, request.pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问该宠物信息")

    try:
        from src.tools.health_tools import HealthConsultTool, UrgencyAssessmentTool
        consult_tool = HealthConsultTool(db=db)
        result = consult_tool._run(
            pet_id=request.pet_id,
            symptoms=request.symptoms,
            description=request.description
        )

        urgency_tool = UrgencyAssessmentTool()
        urgency_result = urgency_tool._run(
            symptoms=request.symptoms,
            pet_species=pet.species,
            pet_breed=pet.breed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

    diagnosis = result.get("diagnosis_result", {})
    possible_conditions = diagnosis.get("possible_conditions", [])
    condition_items = []
    for cond in possible_conditions:
        if isinstance(cond, dict):
            condition_items.append(ConditionItem(
                name=cond.get("name", "未知"),
                description=cond.get("description", ""),
                confidence=cond.get("confidence", 0.5),
            ))
    diagnosis_result = SymptomAnalysisResult(
        possible_conditions=condition_items,
        recommendations=diagnosis.get("recommendations", result.get("recommendations", [])),
        severity=diagnosis.get("severity", "中等"),
        vet_recommended=diagnosis.get("vet_recommended", False),
    )
    return SymptomAnalysisResponse(
        diagnosis_result=diagnosis_result,
        urgency_level=urgency_result.get("urgency_level", 1),
        urgency_reasoning=urgency_result.get("reasoning"),
        recommendations=result.get("recommendations", []),
    )


@router.get("/consultations", response_model=list[ConsultationResponse])
async def list_consultations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """获取用户咨询历史"""
    consultations = ConsultationRepository.list_by_user(
        current_user.user_id, skip=skip, limit=limit
    )
    return [
        ConsultationResponse(
            consultation_id=c["consultation_id"],
            user_id=c["user_id"],
            pet_id=c["pet_id"],
            symptoms=c.get("symptoms"),
            description=c.get("description"),
            image_urls=c.get("image_urls"),
            diagnosis_result=c.get("diagnosis_result"),
            recommendations=c.get("recommendations"),
            urgency_level=c.get("urgency_level", 1),
            status=c.get("status", "pending"),
            conversation_id=c.get("conversation_id"),
            created_at=c["created_at"],
            updated_at=c["updated_at"],
        )
        for c in consultations
    ]


@router.get("/consultations/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation_detail(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    consultation_id: str,
) -> Any:
    """获取咨询详情"""
    consultation = ConsultationRepository.get_by_id(consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="咨询记录不存在")
    if consultation["user_id"] != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问此咨询记录")
    return ConsultationResponse(
        consultation_id=consultation["consultation_id"],
        user_id=consultation["user_id"],
        pet_id=consultation["pet_id"],
        symptoms=consultation.get("symptoms"),
        description=consultation.get("description"),
        image_urls=consultation.get("image_urls"),
        diagnosis_result=consultation.get("diagnosis_result"),
        recommendations=consultation.get("recommendations"),
        urgency_level=consultation.get("urgency_level", 1),
        status=consultation.get("status", "pending"),
        conversation_id=consultation.get("conversation_id"),
        created_at=consultation["created_at"],
        updated_at=consultation["updated_at"],
    )


@router.post("/records", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pet_id: str,
    record_data: HealthRecordCreate,
) -> Any:
    """手动添加健康记录"""
    pet = get_pet_by_id(db, pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作该宠物信息")

    import uuid
    record_id = str(uuid.uuid4())
    doc = {
        "record_id": record_id,
        "pet_id": pet_id,
        "record_type": record_data.record_type,
        "symptoms": record_data.symptoms,
        "diagnosis": record_data.diagnosis,
        "prescription": record_data.prescription,
        "vet_name": record_data.vet_name,
        "hospital": record_data.hospital,
        "record_date": record_data.record_date,
        "next_checkup_date": record_data.next_checkup_date,
        "notes": record_data.notes,
    }
    HealthRecordRepository.create(doc)

    return HealthRecordResponse(
        record_id=record_id,
        pet_id=pet_id,
        record_type=record_data.record_type,
        symptoms=record_data.symptoms,
        diagnosis=record_data.diagnosis,
        prescription=record_data.prescription,
        vet_name=record_data.vet_name,
        hospital=record_data.hospital,
        record_date=record_data.record_date,
        next_checkup_date=record_data.next_checkup_date,
        notes=record_data.notes,
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get("/records/{pet_id}", response_model=list[HealthRecordResponse])
async def list_health_records(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pet_id: str,
    record_type: str = None,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """获取宠物健康记录"""
    pet = get_pet_by_id(db, pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问该宠物信息")

    records = HealthRecordRepository.list_by_pet(pet_id, skip=skip, limit=limit)
    return [
        HealthRecordResponse(
            record_id=r["record_id"],
            pet_id=r["pet_id"],
            record_type=r["record_type"],
            symptoms=r.get("symptoms"),
            diagnosis=r.get("diagnosis"),
            prescription=r.get("prescription"),
            vet_name=r.get("vet_name"),
            hospital=r.get("hospital"),
            record_date=r.get("record_date"),
            next_checkup_date=r.get("next_checkup_date"),
            notes=r.get("notes"),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in records
    ]
