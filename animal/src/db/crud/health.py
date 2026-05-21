from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.health_record import HealthRecord, Consultation
from src.schemas.health import HealthRecordCreate, ConsultationCreate


# ========== Health Record CRUD ==========

def create_health_record(
    db: Session,
    pet_id: str,
    record_data: HealthRecordCreate
) -> HealthRecord:
    """创建健康记录"""
    record = HealthRecord(
        pet_id=pet_id,
        record_type=record_data.record_type,
        symptoms=record_data.symptoms,
        structured_symptoms=[s.model_dump() for s in record_data.structured_symptoms] if record_data.structured_symptoms else None,
        diagnosis=record_data.diagnosis,
        structured_diagnosis=record_data.structured_diagnosis.model_dump() if record_data.structured_diagnosis else None,
        prescription=record_data.prescription,
        vet_name=record_data.vet_name,
        hospital=record_data.hospital,
        record_date=record_data.record_date,
        next_checkup_date=record_data.next_checkup_date,
        notes=record_data.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_health_record_by_id(db: Session, record_id: str, include_deleted: bool = False) -> Optional[HealthRecord]:
    """根据ID获取健康记录"""
    query = db.query(HealthRecord).filter(HealthRecord.record_id == record_id)
    if not include_deleted:
        query = query.filter(HealthRecord.is_deleted == 0)
    return query.first()


def get_health_records_by_pet(
    db: Session,
    pet_id: str,
    record_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[HealthRecord]:
    """获取宠物的健康记录列表（排除已软删除）"""
    query = db.query(HealthRecord).filter(HealthRecord.pet_id == pet_id, HealthRecord.is_deleted == 0)
    if record_type:
        query = query.filter(HealthRecord.record_type == record_type)
    return query.order_by(desc(HealthRecord.record_date)).offset(skip).limit(limit).all()


def soft_delete_health_record(db: Session, record_id: str) -> bool:
    """软删除健康记录"""
    record = get_health_record_by_id(db, record_id)
    if not record:
        return False
    record.is_deleted = 1
    record.deleted_at = datetime.utcnow()
    db.commit()
    return True


def delete_health_record(db: Session, record_id: str) -> bool:
    """硬删除健康记录（仅内部使用）"""
    record = db.query(HealthRecord).filter(HealthRecord.record_id == record_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


# ========== Consultation CRUD ==========

def create_consultation(
    db: Session,
    user_id: str,
    consultation_data: ConsultationCreate
) -> Consultation:
    """创建健康咨询记录"""
    consultation = Consultation(
        user_id=user_id,
        pet_id=consultation_data.pet_id,
        symptoms=consultation_data.symptoms,
        description=consultation_data.description,
        image_urls=consultation_data.image_urls,
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


def get_consultation_by_id(db: Session, consultation_id: str, include_deleted: bool = False) -> Optional[Consultation]:
    """根据ID获取咨询记录"""
    query = db.query(Consultation).filter(Consultation.consultation_id == consultation_id)
    if not include_deleted:
        query = query.filter(Consultation.is_deleted == 0)
    return query.first()


def get_user_consultations(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 20
) -> List[Consultation]:
    """获取用户的咨询历史（排除已软删除）"""
    return db.query(Consultation).filter(
        Consultation.user_id == user_id,
        Consultation.is_deleted == 0,
    ).order_by(desc(Consultation.created_at)).offset(skip).limit(limit).all()


def get_pet_consultations(
    db: Session,
    pet_id: str,
    skip: int = 0,
    limit: int = 20
) -> List[Consultation]:
    """获取宠物的咨询历史（排除已软删除）"""
    return db.query(Consultation).filter(
        Consultation.pet_id == pet_id,
        Consultation.is_deleted == 0,
    ).order_by(desc(Consultation.created_at)).offset(skip).limit(limit).all()


def update_consultation_result(
    db: Session,
    consultation_id: str,
    diagnosis_result: Optional[dict] = None,
    recommendations: Optional[list] = None,
    urgency_level: Optional[int] = None,
    status: Optional[str] = None
) -> Optional[Consultation]:
    """更新咨询的AI分析结果"""
    consultation = get_consultation_by_id(db, consultation_id)
    if not consultation:
        return None

    if diagnosis_result is not None:
        consultation.diagnosis_result = diagnosis_result
    if recommendations is not None:
        consultation.recommendations = recommendations
    if urgency_level is not None:
        consultation.urgency_level = urgency_level
    if status is not None:
        consultation.status = status

    db.commit()
    db.refresh(consultation)
    return consultation