"""add supervisor_scope

Revision ID: 20260102_01
Revises: 780a0831f2f7
Create Date: 2026-01-02

"""

# 22300417陈俫坤开发：督导负责范围表迁移
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260102_01"
down_revision: Union[str, Sequence[str], None] = "780a0831f2f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "supervisor_scope",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="督导范围ID"),
        sa.Column(
            "supervisor_user_id",
            sa.BigInteger(),
            sa.ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
            comment="督导用户ID（user.id）",
        ),
        sa.Column("scope_type", sa.String(length=16), nullable=False, comment="范围类型 college/research_room"),
        sa.Column("scope_id", sa.BigInteger(), nullable=False, comment="范围对象ID"),
        sa.Column("create_time", sa.DateTime(), server_default=sa.text("now()"), nullable=True, comment="创建时间"),
        sa.Column("is_delete", sa.Boolean(), nullable=True, comment="逻辑删除"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("supervisor_user_id", "scope_type", "scope_id", name="uk_supervisor_scope"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        comment="督导负责范围配置",
    )

    op.create_index("idx_supervisor_scope_user_type", "supervisor_scope", ["supervisor_user_id", "scope_type"], unique=False)
    op.create_index(op.f("ix_supervisor_scope_is_delete"), "supervisor_scope", ["is_delete"], unique=False)
    op.create_index(op.f("ix_supervisor_scope_scope_type"), "supervisor_scope", ["scope_type"], unique=False)
    op.create_index(op.f("ix_supervisor_scope_scope_id"), "supervisor_scope", ["scope_id"], unique=False)
    op.create_index(op.f("ix_supervisor_scope_supervisor_user_id"), "supervisor_scope", ["supervisor_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_supervisor_scope_supervisor_user_id"), table_name="supervisor_scope")
    op.drop_index(op.f("ix_supervisor_scope_scope_id"), table_name="supervisor_scope")
    op.drop_index(op.f("ix_supervisor_scope_scope_type"), table_name="supervisor_scope")
    op.drop_index(op.f("ix_supervisor_scope_is_delete"), table_name="supervisor_scope")
    op.drop_index("idx_supervisor_scope_user_type", table_name="supervisor_scope")
    op.drop_table("supervisor_scope")
