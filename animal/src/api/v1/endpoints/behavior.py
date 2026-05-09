"""
行为分析端点

提供行为分析、训练建议、历史查询等功能
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.models.pet import Pet
from src.schemas.behavior import (
    BehaviorAnalyzeRequest,
    BehaviorAnalyzeResponse,
    BehaviorAnalysisResponse,
    TrainingRecommendationRequest,
    TrainingRecommendationResponse,
)
from src.schemas.llm_output import BehaviorAnalysisResult, BehaviorCauseItem
from src.repositories.mongo_repositories import BehaviorAnalysisRepository
from src.db.crud.pet import get_pet_by_id

router = APIRouter()


@router.post("/analyze", response_model=BehaviorAnalyzeResponse, status_code=status.HTTP_200_OK)
async def behavior_analyze(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: BehaviorAnalyzeRequest,
) -> Any:
    """行为分析

    - 创建行为分析记录（MongoDB）
    - 执行AI行为分析（品种特性+年龄因素+知识库）
    - 写回分析结果和训练建议
    - 返回完整分析结果
    """
    # 验证宠物归属
    pet = get_pet_by_id(db, request.pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问该宠物信息")

    # 创建行为分析记录（MongoDB）
    analysis_data = {
        "user_id": current_user.user_id,
        "pet_id": request.pet_id,
        "behavior_description": request.behavior_description,
        "behavior_category": request.behavior_category,
    }
    analysis_id = BehaviorAnalysisRepository.create(analysis_data)

    # 执行行为分析
    try:
        from src.tools.behavior_tools import BehaviorAnalysisTool
        analysis_tool = BehaviorAnalysisTool(db=db)
        result = analysis_tool._run(
            pet_id=request.pet_id,
            behavior_description=request.behavior_description,
            behavior_category=request.behavior_category,
        )
    except Exception as e:
        BehaviorAnalysisRepository.update(analysis_id, {"status": "failed"})
        raise HTTPException(
            status_code=500,
            detail=f"行为分析失败: {str(e)}"
        )

    # 构建结构化的 analysis_result
    raw_causes = result.get("possible_causes", [])
    if isinstance(raw_causes, list) and len(raw_causes) > 0:
        possible_causes = []
        for cause in raw_causes:
            if isinstance(cause, dict):
                possible_causes.append(BehaviorCauseItem(
                    cause=cause.get("cause", cause.get("cause_text", "")),
                    probability=cause.get("probability", 0.5),
                    category=cause.get("category", cause.get("cause_category", "training")),
                ))
            elif isinstance(cause, str):
                possible_causes.append(BehaviorCauseItem(
                    cause=cause,
                    probability=0.5,
                    category="training",
                ))
    else:
        possible_causes = []

    analysis_result = BehaviorAnalysisResult(
        possible_causes=possible_causes,
        recommendations=result.get("recommendations", []),
    )

    # 写回AI分析结果
    BehaviorAnalysisRepository.update(
        analysis_id,
        {
            "behavior_category": result.get("behavior_category"),
            "analysis_result": analysis_result.model_dump(mode="json"),
            "breed_analysis": result.get("breed_analysis"),
            "severity_level": result.get("severity_level", 1),
            "status": "completed",
        }
    )

    return BehaviorAnalyzeResponse(
        analysis_id=analysis_id,
        pet_id=request.pet_id,
        behavior_category=result.get("behavior_category"),
        analysis_result=analysis_result,
        breed_analysis=result.get("breed_analysis"),
        recommendations=result.get("recommendations", []),
        severity_level=result.get("severity_level", 1),
    )


@router.get("/history", response_model=list[BehaviorAnalysisResponse])
async def list_behavior_history(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """获取用户行为分析历史"""
    analyses = BehaviorAnalysisRepository.list_by_user(
        user_id=current_user.user_id, skip=skip, limit=limit
    )
    return analyses


@router.get("/history/{pet_id}", response_model=list[BehaviorAnalysisResponse])
async def list_pet_behavior_history(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pet_id: str,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """获取特定宠物行为分析历史"""
    pet = get_pet_by_id(db, pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问该宠物信息")

    analyses = BehaviorAnalysisRepository.list_by_pet(pet_id, skip=skip, limit=limit)
    return analyses


@router.post("/training", response_model=TrainingRecommendationResponse, status_code=status.HTTP_200_OK)
async def get_training_recommendations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: TrainingRecommendationRequest,
) -> Any:
    """获取训练建议"""
    pet = get_pet_by_id(db, request.pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问该宠物信息")

    try:
        from src.tools.behavior_tools import TrainingRecommendationTool
        training_tool = TrainingRecommendationTool(db=db)
        result = training_tool._run(
            pet_id=request.pet_id,
            behavior_category=request.behavior_category,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取训练建议失败: {str(e)}")

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return TrainingRecommendationResponse(
        pet_id=request.pet_id,
        pet_name=result.get("pet_name"),
        behavior_category=result.get("behavior_category"),
        breed_specific_advice=result.get("breed_specific_advice", []),
        training_plan=result.get("training_plan", []),
        tips=result.get("tips", []),
    )
