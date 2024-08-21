"""create med_ingredients_map table

Revision ID: e54e8f781005
Revises: dbffea26af42
Create Date: 2024-01-13 20:39:56.860145

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e54e8f781005"
down_revision: Union[str, None] = "dbffea26af42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "med_ingredient_map"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("med_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime,
            default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.ForeignKeyConstraint(["med_id"], ["meds.id"]),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"]),
        sa.PrimaryKeyConstraint("med_id", "ingredient_id"),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
