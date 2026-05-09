"""create health_records and consultations tables

Revision ID: 004
Revises: 003
Create Date: 2026-04-11 15:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'health_records',
        sa.Column('record_id', sa.String(36), primary_key=True, comment='记录ID，UUID主键'),
        sa.Column('pet_id', sa.String(36), sa.ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False, comment='宠物ID，外键'),
        sa.Column('record_type', sa.Enum('checkup', 'vaccine', 'illness', 'allergy', 'surgery', name='record_type_enum'), nullable=False, comment='记录类型'),
        sa.Column('symptoms', sa.JSON(), nullable=True, comment='症状列表'),
        sa.Column('diagnosis', sa.Text(), nullable=True, comment='诊断结果'),
        sa.Column('prescription', sa.Text(), nullable=True, comment='处方/用药'),
        sa.Column('vet_name', sa.String(50), nullable=True, comment='兽医姓名'),
        sa.Column('hospital', sa.String(100), nullable=True, comment='医院/诊所名称'),
        sa.Column('record_date', sa.Date(), nullable=True, comment='就诊日期'),
        sa.Column('next_checkup_date', sa.Date(), nullable=True, comment='下次检查日期'),
        sa.Column('notes', sa.Text(), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )

    op.create_index('ix_health_records_pet_id', 'health_records', ['pet_id'])
    op.create_index('ix_health_records_record_type', 'health_records', ['record_type'])
    op.create_index('ix_health_records_record_date', 'health_records', ['record_date'])

    op.create_table(
        'consultations',
        sa.Column('consultation_id', sa.String(36), primary_key=True, comment='咨询ID，UUID主键'),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, comment='用户ID，外键'),
        sa.Column('pet_id', sa.String(36), sa.ForeignKey('pets.pet_id', ondelete='CASCADE'), nullable=False, comment='宠物ID，外键'),
        sa.Column('symptoms', sa.JSON(), nullable=True, comment='症状列表'),
        sa.Column('description', sa.Text(), nullable=True, comment='用户描述'),
        sa.Column('image_urls', sa.JSON(), nullable=True, comment='上传图片URL列表'),
        sa.Column('diagnosis_result', sa.JSON(), nullable=True, comment='AI诊断结果'),
        sa.Column('recommendations', sa.JSON(), nullable=True, comment='AI建议列表'),
        sa.Column('urgency_level', sa.Integer(), nullable=False, server_default='1', comment='紧急程度(1-5)'),
        sa.Column('status', sa.Enum('pending', 'completed', 'cancelled', name='consultation_status_enum'), nullable=False, server_default='pending', comment='状态'),
        sa.Column('conversation_id', sa.String(36), sa.ForeignKey('conversations.conversation_id', ondelete='SET NULL'), nullable=True, comment='关联对话ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )

    op.create_index('ix_consultations_user_id', 'consultations', ['user_id'])
    op.create_index('ix_consultations_pet_id', 'consultations', ['pet_id'])
    op.create_index('ix_consultations_urgency_level', 'consultations', ['urgency_level'])
    op.create_index('ix_consultations_status', 'consultations', ['status'])


def downgrade() -> None:
    op.drop_table('consultations')
    op.drop_table('health_records')
