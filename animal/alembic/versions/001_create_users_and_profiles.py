"""create users and user_profiles tables

Revision ID: 001
Revises: None
Create Date: 2026-04-08 22:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(36), primary_key=True, comment='用户ID，UUID主键'),
        sa.Column('phone', sa.String(20), nullable=False, unique=True, comment='手机号码，唯一约束'),
        sa.Column('email', sa.String(255), nullable=True, unique=True, comment='电子邮箱，唯一约束'),
        sa.Column('password_hash', sa.String(255), nullable=False, comment='加密后的密码'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1'), comment='账户是否激活'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('0'), comment='是否为超级管理员'),
        sa.Column('last_login_at', sa.DateTime(), nullable=True, comment='最后登录时间'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )

    op.create_index('ix_users_phone', 'users', ['phone'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    op.create_table(
        'user_profiles',
        sa.Column('profile_id', sa.String(36), primary_key=True, comment='档案ID，UUID主键'),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, unique=True, comment='关联用户ID'),
        sa.Column('full_name', sa.String(100), nullable=True, comment='用户真实姓名'),
        sa.Column('gender', sa.Enum('male', 'female', 'other', 'unspecified', name='gender_enum'), nullable=False, server_default='unspecified', comment='性别'),
        sa.Column('date_of_birth', sa.Date(), nullable=True, comment='出生日期'),
        sa.Column('avatar_url', sa.String(500), nullable=True, comment='头像URL地址'),
        sa.Column('address', sa.String(500), nullable=True, comment='联系地址'),
        sa.Column('bio', sa.Text(), nullable=True, comment='个人简介'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )

    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'], unique=True)
    op.create_index('ix_user_profiles_full_name', 'user_profiles', ['full_name'])


def downgrade() -> None:
    op.drop_table('user_profiles')
    op.drop_table('users')

    op.execute("DROP TYPE IF EXISTS gender_enum")
