import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger("docuflow-provenance")


class Citation(BaseModel):
    """
    Standard schema for a single source citation trace.
    Supports future bounding box coordinates from vision parsers.
    """

    document_id: str
    chunk_id: str
    snippet: str
    page_number: int | None = None
    confidence_score: float
    retrieval_strategy: str  # e.g., 'SEMANTIC', 'METADATA', 'HYBRID'
    bounding_boxes: list[dict[str, Any]] | None = (
        None  # Future Florence-2/LayoutLM boxes
    )


class ProvenanceReport(BaseModel):
    """
    Aggregation of citations and confidence metrics for an extraction target.
    """

    citations: list[Citation]
    overall_confidence: float


class ProvenanceService:
    """
    Assembles, compiles, and logs traceability chains (source citations)
    independently of raw document chunking or text extraction.
    """

    def compile_provenance(
        self,
        retrieved_chunks: list[dict[str, Any]],
        confidence_threshold: float = 0.5,
    ) -> ProvenanceReport:
        """
        Processes retrieved chunks and generates a structured, auditable citation trail.
        """
        logger.info(f"Compiling provenance from {len(retrieved_chunks)} chunks...")
        citations = []
        scores = []

        for chunk in retrieved_chunks:
            # Map chunk properties to Citation schema
            score = chunk.get("score", 1.0)
            scores.append(score)

            citations.append(
                Citation(
                    document_id=chunk.get("document_id", "UNKNOWN_DOC"),
                    chunk_id=chunk.get("chunk_id", "UNKNOWN_CHUNK"),
                    snippet=chunk.get("content", "")[:200],  # Keep trace snippet
                    page_number=chunk.get("metadata", {}).get("page_number"),
                    confidence_score=score,
                    retrieval_strategy=chunk.get("retrieval_strategy", "SEMANTIC"),
                    bounding_boxes=chunk.get("metadata", {}).get("bounding_boxes"),
                )
            )

        overall_confidence = sum(scores) / len(scores) if scores else 0.0

        logger.info(
            f"Provenance compiled. Overall confidence: {overall_confidence:.2f}"
        )
        return ProvenanceReport(
            citations=citations, overall_confidence=overall_confidence
        )
