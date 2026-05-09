"""
宠物知识科普API路由

提供宠物品种百科和健康知识的公开检索接口。
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from src.api.schemas.encyclopedia import (
    BreedListResponse, BreedDetailResponse,
    HealthListResponse, HealthDetailResponse,
    SearchKnowledgeResponse,
)
from src.services.encyclopedia_service import EncyclopediaService

router = APIRouter(prefix="/encyclopedia", tags=["宠物知识科普"])


@router.get("/breeds/{species}", response_model=BreedListResponse, summary="获取品种列表")
async def get_breeds(species: str):
    """获取指定物种的品种列表

    - **species**: 物种 cat/dog
    """
    if species not in ("cat", "dog"):
        raise HTTPException(status_code=400, detail="物种类型不合法，仅支持 cat/dog")
    breeds = EncyclopediaService.get_breeds(species)
    return BreedListResponse(species=species, breeds=breeds)


@router.get("/breed/{breed_id}", response_model=BreedDetailResponse, summary="获取品种详情")
async def get_breed_detail(breed_id: str):
    """获取单个品种的详细信息"""
    breed = EncyclopediaService.get_breed_detail(breed_id)
    if not breed:
        raise HTTPException(status_code=404, detail="品种不存在")
    return BreedDetailResponse(breed=breed)


@router.get("/health/{species}", response_model=HealthListResponse, summary="获取健康知识列表")
async def get_health_conditions(species: str):
    """获取按类别分组的健康病症列表

    - **species**: 物种 cat/dog/both
    """
    if species not in ("cat", "dog", "both"):
        raise HTTPException(status_code=400, detail="物种类型不合法，仅支持 cat/dog/both")
    categories = EncyclopediaService.get_health_conditions(species)
    return HealthListResponse(species=species, categories=categories)


@router.get("/health/detail/{condition_id}", response_model=HealthDetailResponse, summary="获取病症详情")
async def get_health_detail(condition_id: str):
    """获取单个病症的详细信息"""
    condition = EncyclopediaService.get_health_detail(condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="病症不存在")
    return HealthDetailResponse(condition=condition)


@router.get("/search", response_model=SearchKnowledgeResponse, summary="搜索知识")
async def search_knowledge(
    query: str = Query(..., min_length=1, max_length=100, description="搜索关键词")
):
    """搜索品种和健康知识

    - **query**: 搜索关键词
    """
    result = EncyclopediaService.search_knowledge(query)
    return SearchKnowledgeResponse(**result)
