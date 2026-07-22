import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.services.graph.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["Graph"])
graph_service = GraphService()


@router.get("")
async def get_knowledge_graph(
    document_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> Any:
    """
    Retrieves the extracted knowledge graph nodes and edges.
    Supports filtering by document_id.
    """
    return await graph_service.get_graph(session, document_id)
