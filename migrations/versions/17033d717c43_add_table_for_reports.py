"""add_table_for_reports

Revision ID: 17033d717c43
Revises: 7f62c15a3a9d
Create Date: 2025-04-16 03:56:12.935489

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "17033d717c43"
down_revision: Union[str, None] = "7f62c15a3a9d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "reports",
        sa.Column("report_id", sa.UUID(), nullable=False),
        sa.Column("report_created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("report_year_month", sa.String(length=7), nullable=False),
        sa.Column("month_income", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("month_expenses", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("balance", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("most_expensive_categories", sa.String(length=188), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("report_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("reports")
    # ### end Alembic commands ###
