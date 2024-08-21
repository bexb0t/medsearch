"""create spl_parsing_issues table

Revision ID: f5ce30c9347f
Revises: e54e8f781005
Create Date: 2024-07-30 23:22:30.290522

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import LONGTEXT

# revision identifiers, used by Alembic.
revision: str = "f5ce30c9347f"
down_revision: Union[str, None] = "e54e8f781005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "spl_parsing_issues"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("spl_id", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text, nullable=False),
        sa.Column("xml_content", LONGTEXT, nullable=False),
        sa.Column("xml_structure", LONGTEXT, nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime,
            default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.ForeignKeyConstraint(["spl_id"], ["spls.id"]),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
