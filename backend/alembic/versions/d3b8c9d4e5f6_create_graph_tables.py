"""create_graph_tables

Revision ID: d3b8c9d4e5f6
Revises: 3a7f8e8f7c9b
Create Date: 2026-07-21 23:55:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d3b8c9d4e5f6"
down_revision: str | Sequence[str] | None = "3a7f8e8f7c9b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "graph_entities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column(
            "properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_graph_entities_document_id"),
        "graph_entities",
        ["document_id"],
        unique=False,
    )

    op.create_table(
        "graph_relationships",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("target_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column(
            "properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_id"], ["graph_entities.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["target_id"], ["graph_entities.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_graph_relationships_document_id"),
        "graph_relationships",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_graph_relationships_source_id"),
        "graph_relationships",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_graph_relationships_target_id"),
        "graph_relationships",
        ["target_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_graph_relationships_target_id"), table_name="graph_relationships"
    )
    op.drop_index(
        op.f("ix_graph_relationships_source_id"), table_name="graph_relationships"
    )
    op.drop_index(
        op.f("ix_graph_relationships_document_id"), table_name="graph_relationships"
    )
    op.drop_table("graph_relationships")
    op.drop_index(op.f("ix_graph_entities_document_id"), table_name="graph_entities")
    op.drop_table("graph_entities")
