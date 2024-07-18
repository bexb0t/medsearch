"""create organizations table

Revision ID: 9145fe789299
Revises: d599bab7caf2
Create Date: 2024-01-13 20:37:18.205789

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9145fe789299"
down_revision: Union[str, None] = "d599bab7caf2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "organizations"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text()),
        sa.Column("nih_id_extension", sa.String(length=255)),
        sa.Column("nih_id_root", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column(
            "updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint(
        "uq_organizations_id_extension_id_root",
        TABLE_NAME,
        ["nih_id_extension", "nih_id_root"],
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
