"""
宠物共享档案模型 - 多用户共享宠物访问权限

场景：
  - 家庭多人共同养一只宠物
  - 宠物医院查看主人授权的档案
  - 宠物寄养期间临时授权
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, CHAR, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from src.core.database import MySQLBase as Base


class PetOwner(Base):
    """宠物共享权限表（多对多）"""
    __tablename__ = "pet_owners"
    __table_args__ = (
        UniqueConstraint("pet_id", "user_id", name="uq_pet_user"),
    )

    id = Column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="主键ID"
    )
    pet_id = Column(
        CHAR(36),
        ForeignKey("pets.pet_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="宠物ID"
    )
    user_id = Column(
        CHAR(36),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="被授权用户ID"
    )
    role = Column(
        Enum("owner", "family", "vet", "sitter", name="pet_owner_role_enum"),
        default="family",
        nullable=False,
        comment="角色: owner(主人)/family(家人)/vet(兽医)/sitter(寄养人)"
    )
    permission = Column(
        Enum("view", "edit", "full", name="pet_owner_permission_enum"),
        default="view",
        nullable=False,
        comment="权限: view(只读)/edit(可编辑)/full(完全控制)"
    )
    granted_by = Column(
        CHAR(36),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="授权人用户ID"
    )
    granted_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="授权时间"
    )
    expires_at = Column(
        DateTime,
        nullable=True,
        comment="过期时间(用于临时授权，如寄养场景)"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否生效"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间"
    )

    pet = relationship("Pet", backref="pet_owners")
    user = relationship("User", foreign_keys=[user_id], backref="shared_pets")
    grantor = relationship("User", foreign_keys=[granted_by])

    def __repr__(self):
        return f"<PetOwner(pet_id={self.pet_id}, user_id={self.user_id}, role={self.role}, permission={self.permission})>"