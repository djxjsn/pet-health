"""create pets table

Revision ID: 002
Revises: 001
Create Date: 2026-04-10 10:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'pets',
        sa.Column('pet_id', sa.String(36), primary_key=True, comment='宠物ID，UUID主键'),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, comment='关联用户ID，外键'),
        sa.Column('name', sa.String(50), nullable=False, comment='宠物名称'),
        sa.Column('species', sa.String(20), nullable=False, comment='物种: dog, cat, bird, rabbit, hamster, fish, other'),
        sa.Column('breed', sa.String(50), nullable=True, comment='品种'),
        sa.Column('gender', sa.Enum('male', 'female', 'unknown', name='pet_gender_enum'), nullable=False, server_default='unknown', comment='性别'),
        sa.Column('birth_date', sa.Date(), nullable=True, comment='出生日期'),
        sa.Column('weight', sa.Numeric(5, 2), nullable=True, comment='体重(kg)'),
        sa.Column('photo_url', sa.String(500), nullable=True, comment='宠物照片URL'),
        sa.Column('is_vaccinated', sa.Boolean(), nullable=False, server_default=sa.text('0'), comment='是否已接种疫苗'),
        sa.Column('is_neutered', sa.Boolean(), nullable=False, server_default=sa.text('0'), comment='是否已绝育'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )

    op.create_index('ix_pets_user_id', 'pets', ['user_id'])
    op.create_index('ix_pets_species', 'pets', ['species'])
    op.create_index('ix_pets_created_at', 'pets', ['created_at'])


def downgrade() -> None:
    op.drop_table('pets')

    op.execute("DROP TYPE IF EXISTS pet_gender_enum")
