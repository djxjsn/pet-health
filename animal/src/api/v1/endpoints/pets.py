"""
宠物档案管理 API 端点

包含：宠物CRUD + 过敏源管理 + 疫苗管理 + 体重追踪 + 共享权限
"""
from typing import Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.influxdb import get_influxdb, InfluxDBManager
from src.db.crud import pet as pet_crud
from src.models.user import User
from src.models.pet import Pet
from src.schemas.pet import (
    PetCreate, PetUpdate, PetResponse, PetListResponse,
    AllergyCreate, AllergyUpdate, AllergyResponse,
    VaccinationCreate, VaccinationUpdate, VaccinationResponse,
    WeightRecordCreate, WeightRecordResponse,
    PetOwnerCreate, PetOwnerUpdate, PetOwnerResponse,
)
from src.api.deps import get_current_user

router = APIRouter()


def _check_access(db: Session, pet_id: str, user_id: str, permission: str = "view") -> Pet:
    """统一权限检查：主人完全放行，共享用户按权限级别判断"""
    pet = pet_crud.get_pet_by_id(db, pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    error = pet_crud.check_pet_permission(db, pet_id, user_id, permission)
    if error:
        raise HTTPException(status_code=403, detail=error)
    return pet


# ==================== 宠物 CRUD ====================

@router.post("", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet_profile(
    *,
    db: Session = Depends(get_db),
    pet_data: PetCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    pet = pet_crud.create_pet(db, user_id=current_user.user_id, pet_data=pet_data)
    return pet


@router.get("", response_model=PetListResponse)
def list_pets(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
) -> Any:
    pets, total = pet_crud.get_pets_by_user(db, user_id=current_user.user_id, page=page, page_size=page_size)
    return {
        "items": pets,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet_detail(
    *,
    pet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    return _check_access(db, pet_id, current_user.user_id, "view")


@router.put("/{pet_id}", response_model=PetResponse)
def update_pet_profile(
    *,
    pet_id: str,
    db: Session = Depends(get_db),
    pet_data: PetUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    pet = _check_access(db, pet_id, current_user.user_id, "edit")
    pet = pet_crud.update_pet(db, pet=pet, pet_data=pet_data)
    return pet


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet_profile(
    *,
    pet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """软删除宠物档案"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权删除该宠物信息")
    pet_crud.soft_delete_pet(db, pet=pet)


# ==================== 过敏源管理 ====================

@router.post("/{pet_id}/allergies", response_model=AllergyResponse, status_code=status.HTTP_201_CREATED)
def add_allergy(
    *,
    pet_id: str,
    allergy_data: AllergyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """为宠物添加过敏源记录"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作")
    return pet_crud.create_allergy(db, pet_id=pet_id, data=allergy_data)


@router.get("/{pet_id}/allergies", response_model=list[AllergyResponse])
def list_allergies(
    *,
    pet_id: str,
    active_only: bool = Query(True, description="仅显示活跃过敏源"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取宠物的过敏源列表"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问")
    return pet_crud.get_allergies_by_pet(db, pet_id=pet_id, active_only=active_only)


@router.put("/{pet_id}/allergies/{allergy_id}", response_model=AllergyResponse)
def update_allergy(
    *,
    pet_id: str,
    allergy_id: str,
    allergy_data: AllergyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """更新过敏源记录"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet or pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作")
    allergy = pet_crud.get_allergy_by_id(db, allergy_id)
    if not allergy or allergy.pet_id != pet_id:
        raise HTTPException(status_code=404, detail="过敏源记录不存在")
    return pet_crud.update_allergy(db, allergy=allergy, data=allergy_data)


@router.delete("/{pet_id}/allergies/{allergy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_allergy(
    *,
    pet_id: str,
    allergy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除过敏源记录"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet or pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作")
    success = pet_crud.delete_allergy(db, allergy_id)
    if not success:
        raise HTTPException(status_code=404, detail="过敏源记录不存在")


# ==================== 疫苗管理 ====================

@router.post("/{pet_id}/vaccinations", response_model=VaccinationResponse, status_code=status.HTTP_201_CREATED)
def add_vaccination(
    *,
    pet_id: str,
    vaccination_data: VaccinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """添加疫苗接种记录"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作")
    return pet_crud.create_vaccination(db, pet_id=pet_id, data=vaccination_data)


@router.get("/{pet_id}/vaccinations", response_model=list[VaccinationResponse])
def list_vaccinations(
    *,
    pet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取宠物的疫苗接种记录"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问")
    return pet_crud.get_vaccinations_by_pet(db, pet_id=pet_id)


@router.get("/{pet_id}/vaccinations/upcoming", response_model=list[VaccinationResponse])
def get_upcoming_vaccinations(
    *,
    pet_id: str,
    days: int = Query(30, ge=1, le=365, description="未来几天内到期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取即将到期的疫苗接种提醒"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权访问")
    return pet_crud.get_upcoming_vaccinations(db, pet_id=pet_id, days=days)


@router.put("/{pet_id}/vaccinations/{vaccination_id}", response_model=VaccinationResponse)
def update_vaccination(
    *,
    pet_id: str,
    vaccination_id: str,
    vaccination_data: VaccinationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """更新疫苗接种记录"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet or pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作")
    vaccination = pet_crud.get_vaccination_by_id(db, vaccination_id)
    if not vaccination or vaccination.pet_id != pet_id:
        raise HTTPException(status_code=404, detail="接种记录不存在")
    return pet_crud.update_vaccination(db, vaccination=vaccination, data=vaccination_data)


@router.delete("/{pet_id}/vaccinations/{vaccination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vaccination(
    *,
    pet_id: str,
    vaccination_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除疫苗接种记录"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet or pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作")
    success = pet_crud.delete_vaccination(db, vaccination_id)
    if not success:
        raise HTTPException(status_code=404, detail="接种记录不存在")


# ==================== 体重追踪（InfluxDB） ====================

@router.post("/{pet_id}/weight", status_code=status.HTTP_201_CREATED)
def record_weight(
    *,
    pet_id: str,
    weight_data: WeightRecordCreate,
    db: Session = Depends(get_db),
    influxdb: InfluxDBManager = Depends(get_influxdb),
    current_user: User = Depends(get_current_user),
) -> Any:
    """记录宠物体重（写入 InfluxDB 时序数据库）"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权操作")

    # 获取设备ID（如果有绑定设备则用设备ID，否则用 pet_id 作为标识）
    device_id = pet_id  # 降级：无设备时用 pet_id
    if pet.devices:
        device_id = pet.devices[0].device_id

    ts = weight_data.recorded_at or datetime.utcnow()
    influxdb.write_health_data(
        device_id=device_id,
        pet_id=pet_id,
        metric_name="weight",
        value=float(weight_data.weight),
        timestamp=ts,
    )

    # 同步更新 Pet 表的当前体重
    pet.weight = weight_data.weight
    db.commit()

    return {"status": "ok", "pet_id": pet_id, "weight": float(weight_data.weight), "timestamp": ts.isoformat()}


@router.get("/{pet_id}/weight/history", response_model=list[WeightRecordResponse])
def get_weight_history(
    *,
    pet_id: str,
    days: int = Query(90, ge=1, le=365, description="查询最近多少天"),
    interval: str = Query("1d", description="聚合间隔: 1d/1w/1M"),
    db: Session = Depends(get_db),
    influxdb: InfluxDBManager = Depends(get_influxdb),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取宠物体重变化历史"""
    _check_access(db, pet_id, current_user.user_id, "view")

    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    device_id = pet_id
    if pet and pet.devices:
        device_id = pet.devices[0].device_id

    from datetime import timedelta
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    records = influxdb.query_metrics(
        device_id=device_id,
        metric_name="weight",
        start_time=start_time,
        end_time=end_time,
        interval=interval,
    )

    return [
        WeightRecordResponse(
            pet_id=pet_id,
            weight=r["value"],
            unit="kg",
            timestamp=r["timestamp"],
        )
        for r in records
    ]


# ==================== 共享权限管理 ====================

@router.post("/{pet_id}/share", response_model=PetOwnerResponse, status_code=status.HTTP_201_CREATED)
def grant_access(
    *,
    pet_id: str,
    share_data: PetOwnerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """授权其他用户访问宠物档案（仅主人可操作）"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="仅宠物主人可以授权共享")

    share_data.pet_id = pet_id
    return pet_crud.grant_pet_access(db, grantor_id=current_user.user_id, data=share_data)


@router.get("/{pet_id}/share", response_model=list[PetOwnerResponse])
def list_shared_users(
    *,
    pet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取宠物的共享用户列表"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="仅宠物主人可查看共享列表")
    return pet_crud.get_pet_owners(db, pet_id=pet_id)


@router.delete("/{pet_id}/share/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_access(
    *,
    pet_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """撤销用户对宠物档案的访问权限"""
    pet = pet_crud.get_pet_by_id(db, pet_id=pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    if pet.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="仅宠物主人可以撤销共享")
    success = pet_crud.revoke_pet_access(db, pet_id=pet_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="共享记录不存在")


@router.get("/shared-with-me", response_model=list[PetResponse])
def list_shared_with_me(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """获取别人共享给我的宠物列表"""
    return pet_crud.get_user_shared_pets(db, user_id=current_user.user_id)