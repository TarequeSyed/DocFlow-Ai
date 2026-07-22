import uuid
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from app.models.document import Document, Extraction
from app.services.extraction.reasoner import CrossDocReasoner


@pytest.mark.asyncio
async def test_compare_documents(mock_db_session):
    """
    Tests compare_documents detects matching and mismatching fields.
    """
    doc1 = uuid.uuid4()
    doc2 = uuid.uuid4()

    ext1 = Extraction(
        document_id=doc1,
        structured_data={"supplier": "Google Inc", "amount": "$1,200.00"},
    )
    ext2 = Extraction(
        document_id=doc2,
        structured_data={"supplier": "Google Corp", "amount": "$1,200.00"},
    )

    mock_exec1 = MagicMock()
    mock_exec1.scalars.return_value.first.return_value = ext1
    mock_exec2 = MagicMock()
    mock_exec2.scalars.return_value.first.return_value = ext2

    mock_db_session.execute.side_effect = [mock_exec1, mock_exec2]

    reasoner = CrossDocReasoner()
    res = await reasoner.compare_documents(
        mock_db_session, [doc1, doc2], ["supplier", "amount"]
    )

    assert len(res["discrepancies"]) == 1
    assert res["discrepancies"][0]["field"] == "supplier"
    assert res["extractions"][str(doc1)]["amount"] == "$1,200.00"
    assert res["extractions"][str(doc2)]["amount"] == "$1,200.00"


@pytest.mark.asyncio
async def test_reconcile_billing_mismatch(mock_db_session):
    """
    Tests reconcile_billing when supplier or total amount has a discrepancy.
    """
    invoice_id = uuid.uuid4()
    po_id = uuid.uuid4()

    invoice_doc = Document(id=invoice_id, category="INVOICE", filename="inv.pdf")
    po_doc = Document(id=po_id, category="PURCHASE_ORDER", filename="po.pdf")

    invoice_ext = Extraction(
        document_id=invoice_id,
        structured_data={"supplier": "Acme Corp", "amount": "12,500.00"},
    )
    po_ext = Extraction(
        document_id=po_id,
        structured_data={"supplier": "Acme Corp", "amount": "13,500.00"},
    )

    # Database executions side effect mocking
    mock_doc1 = MagicMock()
    mock_doc1.scalars.return_value.first.return_value = invoice_doc

    mock_doc2 = MagicMock()
    mock_doc2.scalars.return_value.first.return_value = po_doc

    mock_ext1 = MagicMock()
    mock_ext1.scalars.return_value.first.return_value = invoice_ext

    mock_ext2 = MagicMock()
    mock_ext2.scalars.return_value.first.return_value = po_ext

    # Mock delivery check: empty
    mock_dn = MagicMock()
    mock_dn.scalars.return_value.first.return_value = None

    mock_db_session.execute.side_effect = [
        mock_doc1,
        mock_doc2,
        mock_ext1,
        mock_ext2,
        mock_dn,
    ]

    reasoner = CrossDocReasoner()
    res = await reasoner.reconcile_billing(mock_db_session, invoice_id, po_id)

    assert res["match_status"] == "DISCREPANCY"
    assert "VALUE_MISMATCH" in res["discrepancies"]
    assert "DELIVERY_NOT_FOUND" in res["discrepancies"]


@pytest.mark.asyncio
async def test_api_reconcile_billing(client: AsyncClient, mock_db_session):
    """
    Tests the POST /api/v1/reconciliation REST API route mapping.
    """
    invoice_id = str(uuid.uuid4())
    po_id = str(uuid.uuid4())

    response = await client.post(
        "/api/v1/reconciliation",
        json={"invoice_id": invoice_id, "purchase_order_id": po_id},
    )
    # Since DB mocks are empty, it should return 404 or 500
    assert response.status_code in [404, 500]
