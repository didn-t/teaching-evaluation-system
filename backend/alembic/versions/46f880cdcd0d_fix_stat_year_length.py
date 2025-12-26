"""fix stat_year length

Revision ID: 46f880cdcd0d
Revises: bf1726f3c06d
Create Date: 2025-12-27 01:11:08.950564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46f880cdcd0d'
down_revision: Union[str, Sequence[str], None] = 'bf1726f3c06d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 修改 teacher_evaluation_stat 表的 stat_year 字段长度
    op.alter_column('teacher_evaluation_stat', 'stat_year',
                    type_=sa.String(length=12),  # 扩展到12个字符，支持如"2024-2025"格式
                    existing_type=sa.String(length=4))
    
    # 修改 college_evaluation_stat 表的 stat_year 字段长度
    op.alter_column('college_evaluation_stat', 'stat_year',
                    type_=sa.String(length=12),  # 扩展到12个字符，支持如"2024-2025"格式
                    existing_type=sa.String(length=4))
    
    # 修改 timetable 表的 academic_year 字段长度
    op.alter_column('timetable', 'academic_year',
                    type_=sa.String(length=12),  # 扩展到12个字符，支持如"2024-2025"格式
                    existing_type=sa.String(length=9))


def downgrade() -> None:
    """Downgrade schema."""
    # 降级操作：恢复原始长度
    op.alter_column('teacher_evaluation_stat', 'stat_year',
                    type_=sa.String(length=4),
                    existing_type=sa.String(length=12))
    
    op.alter_column('college_evaluation_stat', 'stat_year',
                    type_=sa.String(length=4),
                    existing_type=sa.String(length=12))
    
    op.alter_column('timetable', 'academic_year',
                    type_=sa.String(length=9),
                    existing_type=sa.String(length=12))