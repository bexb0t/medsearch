"""create ingredients table

Revision ID: dbffea26af42
Revises: ad8530b7aa2b
Create Date: 2024-01-13 20:38:39.472490

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dbffea26af42"
down_revision: Union[str, None] = "ad8530b7aa2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "ingredients"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255)),
        sa.Column("code", sa.String(length=255)),
        sa.Column("code_system", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint(
        "uq_ingredients_code_code_system", TABLE_NAME, ["code", "code_system"]
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
