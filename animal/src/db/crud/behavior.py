from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.behavior_analysis import BehaviorAnalysis
from src.schemas.behavior import BehaviorAnalysisCreate


def create_behavior_analysis(
    db: Session,
    user_id: str,
    analysis_data: BehaviorAnalysisCreate
) -> BehaviorAnalysis:
    """创建行为分析记录"""
    analysis = BehaviorAnalysis(
        user_id=user_id,
        pet_id=analysis_data.pet_id,
        behavior_description=analysis_data.behavior_description,
        behavior_category=analysis_data.behavior_category,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_behavior_analysis_by_id(db: Session, analysis_id: str) -> Optional[BehaviorAnalysis]:
    """根据ID获取行为分析记录"""
    return db.query(BehaviorAnalysis).filter(BehaviorAnalysis.analysis_id == analysis_id).first()


def get_user_behavior_analyses(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 20
) -> List[BehaviorAnalysis]:
    """获取用户的行为分析历史"""
    return db.query(BehaviorAnalysis).filter(
        BehaviorAnalysis.user_id == user_id
    ).order_by(desc(BehaviorAnalysis.created_at)).offset(skip).limit(limit).all()


def get_pet_behavior_analyses(
    db: Session,
    pet_id: str,
    skip: int = 0,
    limit: int = 20
) -> List[BehaviorAnalysis]:
    """获取特定宠物的行为分析历史"""
    return db.query(BehaviorAnalysis).filter(
        BehaviorAnalysis.pet_id == pet_id
    ).order_by(desc(BehaviorAnalysis.created_at)).offset(skip).limit(limit).all()


def update_behavior_analysis_result(
    db: Session,
    analysis_id: str,
    behavior_category: Optional[str] = None,
    possible_causes: Optional[list] = None,
    breed_analysis: Optional[dict] = None,
    recommendations: Optional[list] = None,
    severity_level: Optional[int] = None,
    status: Optional[str] = None
) -> Optional[BehaviorAnalysis]:
    """更新行为分析的AI结果"""
    analysis = get_behavior_analysis_by_id(db, analysis_id)
    if not analysis:
        return None

    if behavior_category is not None:
        analysis.behavior_category = behavior_category
    if possible_causes is not None:
        analysis.possible_causes = possible_causes
    if breed_analysis is not None:
        analysis.breed_analysis = breed_analysis
    if recommendations is not None:
        analysis.recommendations = recommendations
    if severity_level is not None:
        analysis.severity_level = severity_level
    if status is not None:
        analysis.status = status

    db.commit()
    db.refresh(analysis)
    return analysis
