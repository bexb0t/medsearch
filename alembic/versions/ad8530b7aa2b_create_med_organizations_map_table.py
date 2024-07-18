"""create med_organizations_map table

Revision ID: ad8530b7aa2b
Revises: 9145fe789299
Create Date: 2024-01-13 20:37:51.207183

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ad8530b7aa2b"
down_revision: Union[str, None] = "9145fe789299"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "med_organization_map"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column("med_id", sa.Integer(), nullable=False),
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["med_id"], ["meds.id"]),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("med_id", "org_id"),
    )

    op.create_unique_constraint(
        "uq_med_organization_map_med_id_org_id",
        TABLE_NAME,
        ["med_id", "org_id"],
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
