import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.services.extraction.reasoner import CrossDocReasoner

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])
reasoner = CrossDocReasoner()


class ReconcileRequest(BaseModel):
    invoice_id: uuid.UUID
    purchase_order_id: uuid.UUID


@router.post("")
async def run_billing_reconciliation(
    req: ReconcileRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Any:
    """
    Executes a 3-way billing reconciliation audit matching invoice, PO,
    and associated delivery note metadata references.
    """
    try:
        return await reasoner.reconcile_billing(
            session, req.invoice_id, req.purchase_order_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reconciliation audit execution failed: {e}",
        ) from e
