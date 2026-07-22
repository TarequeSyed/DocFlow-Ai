import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SchemaCreateRequest(BaseModel):
    """
    Payload to register a new extraction schema template.
    """

    name: str
    description: str | None = None
    # Dict mapping field names to type/description constraints
    schema_definition: dict[str, Any]


class SchemaResponse(BaseModel):
    """
    Metadata representation of a registered extraction schema.
    """

    id: uuid.UUID
    name: str
    description: str | None = None
    schema_definition: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SchemaListResponse(BaseModel):
    """
    Paginated lists of extraction schema templates.
    """

    items: list[SchemaResponse]
    total: int


class ExtractionRequest(BaseModel):
    """
    Trigger payload to start structured extraction.
    """

    document_id: uuid.UUID
    schema_id: uuid.UUID


class CitationItem(BaseModel):
    """
    Citations pointing back to document snippets.
    """

    document_id: str
    chunk_id: str
    snippet: str
    page_number: int | None = None
    confidence_score: float
    retrieval_strategy: str


class ProvenanceDTO(BaseModel):
    """
    Standard aggregated provenance metrics.
    """

    citations: list[CitationItem]
    overall_confidence: float


class ExtractionResponse(BaseModel):
    """
    Retrieval response representing structured LLM output and audit trails.
    """

    id: uuid.UUID
    document_id: uuid.UUID
    schema_id: uuid.UUID | None
    structured_data: dict[str, Any] | None = None
    status: str
    error_message: str | None = None
    provenance: ProvenanceDTO | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
