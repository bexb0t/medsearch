"""create spls table

Revision ID: d50797242e4e
Revises:
Create Date: 2024-01-13 15:11:59.226846

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d50797242e4e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "spls"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("set_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("published_date", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime,
            default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )
    op.create_unique_constraint("uq_spls_set_id", TABLE_NAME, ["set_id"])


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
