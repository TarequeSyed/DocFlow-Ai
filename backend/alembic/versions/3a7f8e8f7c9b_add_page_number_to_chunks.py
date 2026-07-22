"""add_page_number_to_chunks

Revision ID: 3a7f8e8f7c9b
Revises: 52a122e1a3bc
Create Date: 2026-07-21 23:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3a7f8e8f7c9b"
down_revision: str | Sequence[str] | None = "52a122e1a3bc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "document_chunks", sa.Column("page_number", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("document_chunks", "page_number")
