from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.search import SearchQueryRequest, SearchResponse, SearchResultItem
from app.services.orchestrator import AdaptiveRetrievalOrchestrator

router = APIRouter(prefix="/search", tags=["Search"])
orchestrator = AdaptiveRetrievalOrchestrator()


@router.post("/", response_model=SearchResponse)
async def perform_search(
    payload: SearchQueryRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Any:
    """
    Executes a semantic vector or keyword hybrid search across chunks.
    """
    # Query matching context chunks
    chunks = await orchestrator.retrieve(
        session,
        query=payload.query,
        document_id=payload.document_id,
        limit=payload.limit,
    )

    results = []
    for c in chunks:
        results.append(
            SearchResultItem(
                chunk_id=c["chunk_id"],
                document_id=c["document_id"],
                chunk_index=c["chunk_index"],
                content=c["content"],
                score=c["score"],
                retrieval_strategy=c["retrieval_strategy"],
            )
        )

    return SearchResponse(query=payload.query, results=results)
