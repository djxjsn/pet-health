"""create conversations and messages tables

Revision ID: 003
Revises: 002
Create Date: 2026-04-10 15:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'conversations',
        sa.Column('conversation_id', sa.String(36), primary_key=True, comment='对话ID，UUID主键'),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, comment='用户ID，外键'),
        sa.Column('pet_id', sa.String(36), sa.ForeignKey('pets.pet_id', ondelete='SET NULL'), nullable=True, comment='宠物ID，外键(可选)'),
        sa.Column('title', sa.String(255), nullable=True, comment='对话标题'),
        sa.Column('context', sa.JSON(), nullable=True, comment='对话上下文信息'),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0', comment='消息数量'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )

    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_pet_id', 'conversations', ['pet_id'])
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'])

    op.create_table(
        'messages',
        sa.Column('message_id', sa.String(36), primary_key=True, comment='消息ID，UUID主键'),
        sa.Column('conversation_id', sa.String(36), sa.ForeignKey('conversations.conversation_id', ondelete='CASCADE'), nullable=False, comment='对话ID，外键'),
        sa.Column('role', sa.String(20), nullable=False, comment='消息角色: user/assistant/system'),
        sa.Column('content', sa.Text(), nullable=False, comment='消息内容'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='消息元数据'),
        sa.Column('vector_id', sa.String(255), nullable=True, comment='向量数据库中的文档ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )

    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')
