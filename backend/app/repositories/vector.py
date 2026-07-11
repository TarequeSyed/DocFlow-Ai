import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentChunk


class VectorRepository:
    """
    Data Access Object managing PostgreSQL + pgvector embedding queries.
    """

    async def bulk_insert_chunks(
        self, session: AsyncSession, chunks: list[DocumentChunk]
    ) -> None:
        """
        Saves a list of document chunks in a batch transaction.
        """
        session.add_all(chunks)
        await session.commit()

    async def search_similarity(
        self,
        session: AsyncSession,
        document_id: uuid.UUID | None,
        query_vector: list[float],
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        """
        Computes cosine similarity ranking and returns matching chunks.
        Similarity score is derived as (1.0 - cosine_distance).
        """
        # pgvector cosine distance operator is mapping to <=>
        distance = DocumentChunk.embedding.cosine_distance(query_vector).label(
            "distance"
        )

        stmt = select(DocumentChunk, distance)
        if document_id is not None:
            stmt = stmt.where(DocumentChunk.document_id == document_id)

        stmt = stmt.order_by(distance).limit(limit)
        result = await session.execute(stmt)

        matches = []
        for row in result.all():
            chunk_obj = row[0]
            dist_val = row[1]
            # Convert distance value into confidence score
            score = 1.0 - float(dist_val) if dist_val is not None else 0.0
            matches.append((chunk_obj, score))

        return matches
