from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.pet import Pet, PetAllergy, PetVaccination
from src.models.pet_owner import PetOwner
from src.models.user_profile import UserProfile
from src.schemas.pet import PetCreate, PetUpdate, AllergyCreate, AllergyUpdate, VaccinationCreate, VaccinationUpdate, PetOwnerCreate, PetOwnerUpdate


# ==================== Pet CRUD ====================

def get_pet_by_id(db: Session, pet_id: str, include_deleted: bool = False) -> Optional[Pet]:
    query = db.query(Pet).filter(Pet.pet_id == pet_id)
    if not include_deleted:
        query = query.filter(Pet.is_deleted == False)
    return query.first()


def get_pets_by_user(
    db: Session,
    user_id: str,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[Pet], int]:
    query = db.query(Pet).filter(Pet.user_id == user_id, Pet.is_deleted == False)
    total = query.count()
    pets = query.order_by(Pet.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return pets, total


def _sync_pet_count(db: Session, user_id: str) -> None:
    """同步 user_profiles.pet_count 冗余字段"""
    count = db.query(func.count(Pet.pet_id)).filter(
        Pet.user_id == user_id, Pet.is_deleted == False
    ).scalar()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        profile.pet_count = count


def create_pet(db: Session, user_id: str, pet_data: PetCreate) -> Pet:
    pet = Pet(
        user_id=user_id,
        name=pet_data.name,
        species=pet_data.species,
        breed=pet_data.breed,
        gender=pet_data.gender,
        birth_date=pet_data.birth_date,
        weight=pet_data.weight,
        photo_url=pet_data.photo_url,
        is_vaccinated=pet_data.is_vaccinated,
        is_neutered=pet_data.is_neutered,
        microchip_id=pet_data.microchip_id,
        blood_type=pet_data.blood_type,
        current_status=pet_data.current_status or "healthy",
        diet_type=pet_data.diet_type,
        spay_neuter_date=pet_data.spay_neuter_date,
        emergency_contact=pet_data.emergency_contact,
        source=pet_data.source,
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    _sync_pet_count(db, user_id)
    return pet


def update_pet(db: Session, pet: Pet, pet_data: PetUpdate) -> Pet:
    update_data = pet_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pet, field, value)
    db.commit()
    db.refresh(pet)
    return pet


def soft_delete_pet(db: Session, pet: Pet) -> None:
    """软删除宠物档案"""
    pet.is_deleted = True
    pet.deleted_at = datetime.utcnow()
    db.commit()
    _sync_pet_count(db, pet.user_id)


def delete_pet(db: Session, pet: Pet) -> None:
    """硬删除（仅内部使用，对外统一走软删除）"""
    user_id = pet.user_id
    db.delete(pet)
    db.commit()
    _sync_pet_count(db, user_id)


# ==================== Allergy CRUD ====================

def create_allergy(db: Session, pet_id: str, data: AllergyCreate) -> PetAllergy:
    allergy = PetAllergy(
        pet_id=pet_id,
        allergen_name=data.allergen_name,
        allergen_type=data.allergen_type,
        severity=data.severity,
        confirmed_by=data.confirmed_by,
        reaction_desc=data.reaction_desc,
        first_observed=data.first_observed,
        is_active=data.is_active if data.is_active is not None else True,
    )
    db.add(allergy)
    db.commit()
    db.refresh(allergy)
    return allergy


def get_allergies_by_pet(db: Session, pet_id: str, active_only: bool = True) -> List[PetAllergy]:
    query = db.query(PetAllergy).filter(PetAllergy.pet_id == pet_id)
    if active_only:
        query = query.filter(PetAllergy.is_active == True)
    return query.order_by(PetAllergy.severity.desc(), PetAllergy.created_at.desc()).all()


def get_allergy_by_id(db: Session, allergy_id: str) -> Optional[PetAllergy]:
    return db.query(PetAllergy).filter(PetAllergy.allergy_id == allergy_id).first()


def update_allergy(db: Session, allergy: PetAllergy, data: AllergyUpdate) -> PetAllergy:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(allergy, field, value)
    db.commit()
    db.refresh(allergy)
    return allergy


def delete_allergy(db: Session, allergy_id: str) -> bool:
    allergy = db.query(PetAllergy).filter(PetAllergy.allergy_id == allergy_id).first()
    if not allergy:
        return False
    db.delete(allergy)
    db.commit()
    return True


def check_allergy_conflict(db: Session, pet_id: str, ingredient_name: str) -> Optional[PetAllergy]:
    """检查某成分是否与宠物过敏源冲突（Agent 联动用）"""
    return db.query(PetAllergy).filter(
        PetAllergy.pet_id == pet_id,
        PetAllergy.is_active == True,
        PetAllergy.allergen_name.contains(ingredient_name),
    ).first()


# ==================== Vaccination CRUD ====================

def create_vaccination(db: Session, pet_id: str, data: VaccinationCreate) -> PetVaccination:
    vaccination = PetVaccination(
        pet_id=pet_id,
        vaccine_name=data.vaccine_name,
        vaccine_type=data.vaccine_type,
        dose_number=data.dose_number,
        administered_date=data.administered_date,
        next_due_date=data.next_due_date,
        vet_name=data.vet_name,
        hospital=data.hospital,
        batch_number=data.batch_number,
        manufacturer=data.manufacturer,
        notes=data.notes,
    )
    db.add(vaccination)
    db.commit()
    db.refresh(vaccination)

    # 自动更新宠物的 is_vaccinated 标记
    pet = db.query(Pet).filter(Pet.pet_id == pet_id).first()
    if pet and not pet.is_vaccinated:
        pet.is_vaccinated = True
        db.commit()

    return vaccination


def get_vaccinations_by_pet(db: Session, pet_id: str) -> List[PetVaccination]:
    return db.query(PetVaccination).filter(
        PetVaccination.pet_id == pet_id
    ).order_by(PetVaccination.administered_date.desc()).all()


def get_vaccination_by_id(db: Session, vaccination_id: str) -> Optional[PetVaccination]:
    return db.query(PetVaccination).filter(PetVaccination.vaccination_id == vaccination_id).first()


def update_vaccination(db: Session, vaccination: PetVaccination, data: VaccinationUpdate) -> PetVaccination:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vaccination, field, value)
    db.commit()
    db.refresh(vaccination)
    return vaccination


def delete_vaccination(db: Session, vaccination_id: str) -> bool:
    vaccination = db.query(PetVaccination).filter(PetVaccination.vaccination_id == vaccination_id).first()
    if not vaccination:
        return False
    db.delete(vaccination)
    db.commit()
    return True


def get_upcoming_vaccinations(db: Session, pet_id: str, days: int = 30) -> List[PetVaccination]:
    """获取即将到期的疫苗接种提醒"""
    from datetime import date as date_type
    today = date_type.today()
    future = today + __import__('datetime').timedelta(days=days)
    return db.query(PetVaccination).filter(
        PetVaccination.pet_id == pet_id,
        PetVaccination.next_due_date != None,
        PetVaccination.next_due_date >= today,
        PetVaccination.next_due_date <= future,
    ).order_by(PetVaccination.next_due_date.asc()).all()


# ==================== Pet Owner (共享权限) CRUD ====================

def grant_pet_access(db: Session, grantor_id: str, data: PetOwnerCreate) -> PetOwner:
    """授权用户访问宠物档案"""
    # 检查是否已存在
    existing = db.query(PetOwner).filter(
        PetOwner.pet_id == data.pet_id,
        PetOwner.user_id == data.user_id,
    ).first()
    if existing:
        # 更新已有记录
        existing.role = data.role
        existing.permission = data.permission
        existing.expires_at = data.expires_at
        existing.is_active = True
        existing.granted_by = grantor_id
        db.commit()
        db.refresh(existing)
        return existing

    owner = PetOwner(
        pet_id=data.pet_id,
        user_id=data.user_id,
        role=data.role,
        permission=data.permission,
        granted_by=grantor_id,
        expires_at=data.expires_at,
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner


def revoke_pet_access(db: Session, pet_id: str, user_id: str) -> bool:
    """撤销用户对宠物档案的访问权限"""
    owner = db.query(PetOwner).filter(
        PetOwner.pet_id == pet_id,
        PetOwner.user_id == user_id,
    ).first()
    if not owner:
        return False
    owner.is_active = False
    db.commit()
    return True


def get_pet_owners(db: Session, pet_id: str) -> List[PetOwner]:
    """获取宠物的所有授权用户"""
    return db.query(PetOwner).filter(
        PetOwner.pet_id == pet_id,
        PetOwner.is_active == True,
    ).all()


def get_user_shared_pets(db: Session, user_id: str) -> List[Pet]:
    """获取用户被授权访问的所有宠物"""
    owner_records = db.query(PetOwner).filter(
        PetOwner.user_id == user_id,
        PetOwner.is_active == True,
    ).all()
    pet_ids = [o.pet_id for o in owner_records]
    if not pet_ids:
        return []
    return db.query(Pet).filter(
        Pet.pet_id.in_(pet_ids),
        Pet.is_deleted == False,
    ).all()


def check_pet_permission(
    db: Session,
    pet_id: str,
    user_id: str,
    required_permission: str = "view",
) -> Optional[str]:
    """
    检查用户对宠物的访问权限

    Args:
        pet_id: 宠物ID
        user_id: 用户ID
        required_permission: 需要的最低权限 view/edit/full

    Returns:
        None if has permission, error message if not
    """
    # 1. 检查是否是宠物主人
    pet = db.query(Pet).filter(Pet.pet_id == pet_id, Pet.is_deleted == False).first()
    if pet and pet.user_id == user_id:
        return None  # 主人有完全权限

    # 2. 检查共享权限
    owner = db.query(PetOwner).filter(
        PetOwner.pet_id == pet_id,
        PetOwner.user_id == user_id,
        PetOwner.is_active == True,
    ).first()

    if not owner:
        return "无权访问该宠物信息"

    # 检查是否过期
    if owner.expires_at and owner.expires_at < datetime.utcnow():
        return "访问权限已过期"

    # 检查权限级别
    permission_levels = {"view": 1, "edit": 2, "full": 3}
    if permission_levels.get(owner.permission, 0) < permission_levels.get(required_permission, 1):
        return f"权限不足，需要 {required_permission} 权限"

    return None