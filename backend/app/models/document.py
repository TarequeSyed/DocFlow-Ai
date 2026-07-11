import uuid
from datetime import UTC, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQL Model for storing uploaded documents and their extracted raw text.
    """

    __tablename__ = "documents"

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="UNKNOWN", nullable=False)
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    extractions: Mapped[list["Extraction"]] = relationship(
        "Extraction", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base, UUIDPrimaryKeyMixin):
    """
    SQL Model for storing text chunks and pgvector embeddings.
    """

    __tablename__ = "document_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # 384-dimension vector field (matches FastEmbed BGE-small and Matryoshka OpenAI)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")


class ExtractionSchema(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQL Model representing target metadata parameters and JSON Schemas for extraction.
    """

    __tablename__ = "extraction_schemas"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    schema_definition: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Relationships
    extractions: Mapped[list["Extraction"]] = relationship(
        "Extraction", back_populates="schema"
    )


class Extraction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQL Model storing structured JSON extraction runs.
    """

    __tablename__ = "extractions"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schema_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("extraction_schemas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    structured_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship(
        "Document", back_populates="extractions"
    )
    schema: Mapped["ExtractionSchema"] = relationship(
        "ExtractionSchema", back_populates="extractions"
    )
