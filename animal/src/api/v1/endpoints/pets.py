from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.db.crud.pet import get_pet_by_id, get_pets_by_user, create_pet, update_pet, delete_pet
from src.models.user import User
from src.models.pet import Pet
from src.schemas.pet import PetCreate, PetUpdate, PetResponse, PetListResponse
from src.api.deps import get_current_user

router = APIRouter()


@router.post("", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet_profile(
    *,
    db: Session = Depends(get_db),
    pet_data: PetCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    pet = create_pet(db, user_id=current_user.user_id, pet_data=pet_data)
    return pet


@router.get("", response_model=PetListResponse)
def list_pets(
    *,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
) -> Any:
    pets, total = get_pets_by_user(db, user_id=current_user.user_id, page=page, page_size=page_size)
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
    pet = get_pet_by_id(db, pet_id=pet_id)
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="宠物不存在"
        )
    if pet.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该宠物信息"
        )
    return pet


@router.put("/{pet_id}", response_model=PetResponse)
def update_pet_profile(
    *,
    pet_id: str,
    db: Session = Depends(get_db),
    pet_data: PetUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    pet = get_pet_by_id(db, pet_id=pet_id)
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="宠物不存在"
        )
    if pet.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改该宠物信息"
        )
    pet = update_pet(db, pet=pet, pet_data=pet_data)
    return pet


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet_profile(
    *,
    pet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    pet = get_pet_by_id(db, pet_id=pet_id)
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="宠物不存在"
        )
    if pet.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除该宠物信息"
        )
    delete_pet(db, pet=pet)
