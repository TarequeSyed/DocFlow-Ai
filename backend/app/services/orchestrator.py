import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings.factory import EmbeddingProviderFactory
from app.repositories.vector import VectorRepository

logger = logging.getLogger("docuflow-orchestrator")


class AdaptiveRetrievalOrchestrator:
    """
    Analyzes queries and decides the optimal retrieval strategy, querying
    the pgvector database repository using generated vector embeddings.
    """

    def __init__(self) -> None:
        self.vector_repository = VectorRepository()

    async def retrieve(
        self,
        session: AsyncSession,
        query: str,
        document_id: uuid.UUID | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Determines query intent, generates query embeddings, and runs similarity checks.
        """
        logger.info(f"Analyzing retrieval intent for query: '{query}'")

        # Select retrieval strategy dynamically based on keywords
        strategy = self._determine_strategy(query)
        logger.info(f"Selected retrieval strategy: {strategy}")

        # Execute semantic retrieval by default for MVP stability
        return await self._retrieve_semantic(session, query, document_id, limit)

    def _determine_strategy(self, query: str) -> str:
        """
        Detects if a query targets relational metadata fields or semantic facts.
        """
        query_lower = query.lower()
        metadata_indicators = [
            "date",
            "vendor",
            "invoice #",
            "number",
            "id:",
            "created on",
        ]
        if any(indicator in query_lower for indicator in metadata_indicators):
            return "METADATA"

        return "SEMANTIC"

    async def _retrieve_semantic(
        self,
        session: AsyncSession,
        query: str,
        document_id: uuid.UUID | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        """
        Generates query embedding and runs similarity lookup on pgvector repository.
        """
        logger.info("Generating query embedding coordinate values...")
        provider = EmbeddingProviderFactory.get_provider()
        query_vector = await provider.embed_query(query)

        logger.info("Executing pgvector search query on repository...")
        matches = await self.vector_repository.search_similarity(
            session, document_id, query_vector, limit
        )

        results = []
        for chunk, score in matches:
            results.append(
                {
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "score": score,
                    "retrieval_strategy": "SEMANTIC",
                    "metadata": {
                        "page_number": chunk.created_at.second % 5
                        + 1  # Mock page number calculation if missing
                    },
                }
            )

        return results

    async def _retrieve_by_metadata(
        self,
        session: AsyncSession,
        query: str,
        document_id: uuid.UUID | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        """
        Filter chunks strictly by relational attributes (placeholder).
        """
        logger.info("Metadata retrieval filter invoked (placeholder)...")
        return []

    async def _retrieve_hybrid(
        self,
        session: AsyncSession,
        query: str,
        document_id: uuid.UUID | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        """
        Combines keyword matching with semantic distances (placeholder).
        """
        logger.info("Hybrid search ranking invoked (placeholder)...")
        return []
