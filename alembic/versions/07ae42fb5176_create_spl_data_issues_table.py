"""create spl_data_issues table

Revision ID: 07ae42fb5176
Revises: f5ce30c9347f
Create Date: 2024-07-30 23:33:38.415928

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "07ae42fb5176"
down_revision: Union[str, None] = "f5ce30c9347f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "spl_data_issues"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("spl_id", sa.Integer(), nullable=False),
        # this is an enum in code, but we'll make it  text here so we don't
        # have to do a migration just because we added a new operation ttype
        sa.Column("operation_type", sa.String(100), nullable=False),
        sa.Column("table_name", sa.String(128)),
        sa.Column("error_message", sa.Text, nullable=False),
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
