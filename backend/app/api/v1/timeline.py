import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.services.timeline.timeline_service import TimelineService

router = APIRouter(prefix="/timeline", tags=["Timeline"])
timeline_service = TimelineService()


@router.get("")
async def get_timeline_reconstruction(
    document_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> Any:
    """
    Retrieves the chronological timeline event sequence.
    Supports filtering by document_id to show related flows.
    """
    return await timeline_service.reconstruct_timeline(session, document_id)
