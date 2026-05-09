from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.pet import Pet
from src.models.user_profile import UserProfile
from src.schemas.pet import PetCreate, PetUpdate


def get_pet_by_id(db: Session, pet_id: str) -> Optional[Pet]:
    return db.query(Pet).filter(Pet.pet_id == pet_id).first()


def get_pets_by_user(
    db: Session,
    user_id: str,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[List[Pet], int]:
    query = db.query(Pet).filter(Pet.user_id == user_id)
    total = query.count()
    pets = query.order_by(Pet.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return pets, total


def _sync_pet_count(db: Session, user_id: str) -> None:
    """同步 user_profiles.pet_count 冗余字段"""
    count = db.query(func.count(Pet.pet_id)).filter(Pet.user_id == user_id).scalar()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        profile.pet_count = count
        db.commit()


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


def delete_pet(db: Session, pet: Pet) -> None:
    user_id = pet.user_id
    db.delete(pet)
    db.commit()
    _sync_pet_count(db, user_id)
