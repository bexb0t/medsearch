"""create med_forms table

Revision ID: ff15ee5210b4
Revises: d50797242e4e
Create Date: 2024-07-07 18:59:54.931061

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ff15ee5210b4"
down_revision: Union[str, None] = "d50797242e4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "med_forms"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=255)),
        sa.Column("code_system", sa.String(length=255)),
        sa.Column("name", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
