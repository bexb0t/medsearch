"""create meds table

Revision ID: d599bab7caf2
Revises: ff15ee5210b4
Create Date: 2024-01-13 20:36:19.076049

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d599bab7caf2"
down_revision: Union[str, None] = "ff15ee5210b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "meds"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("spl_id", sa.Integer(), nullable=False),
        sa.Column("med_form_id", sa.Integer()),
        sa.Column("code", sa.String(length=255), nullable=False),
        sa.Column("code_system", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("generic_name", sa.String(length=255), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["med_form_id"], ["med_forms.id"]
        ),  # Foreign key to med_forms table
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint("uq_meds_spl_id", TABLE_NAME, ["spl_id"])


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
