import uuid
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from app.models.document import GraphEntity, GraphRelationship
from app.services.graph.graph_service import GraphService


@pytest.mark.asyncio
async def test_get_graph_empty(mock_db_session):
    """
    Tests get_graph returns empty nodes and edges when DB is empty.
    """
    mock_execute_res = MagicMock()
    mock_execute_res.scalars.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_execute_res

    service = GraphService()
    graph = await service.get_graph(mock_db_session)
    assert graph == {"nodes": [], "edges": []}


@pytest.mark.asyncio
async def test_get_graph_with_data(mock_db_session):
    """
    Tests get_graph formatting and retrieval.
    """
    doc_id = uuid.uuid4()
    mock_entity = GraphEntity(
        id=uuid.uuid4(),
        document_id=doc_id,
        name="Test Entity",
        type="SUPPLIER",
        properties={"description": "Test Supplier"},
    )
    mock_target = GraphEntity(
        id=uuid.uuid4(),
        document_id=doc_id,
        name="INV-99",
        type="INVOICE",
        properties={},
    )
    mock_relationship = GraphRelationship(
        id=uuid.uuid4(),
        document_id=doc_id,
        source_id=mock_entity.id,
        target_id=mock_target.id,
        type="ISSUED",
        properties={},
    )

    mock_execute_nodes = MagicMock()
    mock_execute_nodes.scalars.return_value.all.return_value = [
        mock_entity,
        mock_target,
    ]

    mock_execute_edges = MagicMock()
    mock_execute_edges.scalars.return_value.all.return_value = [mock_relationship]

    # Mock sequential executions
    mock_db_session.execute.side_effect = [mock_execute_nodes, mock_execute_edges]

    service = GraphService()
    graph = await service.get_graph(mock_db_session)

    assert len(graph["nodes"]) == 2
    assert graph["nodes"][0]["label"] == "Test Entity"
    assert graph["nodes"][0]["type"] == "SUPPLIER"
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["type"] == "ISSUED"


@pytest.mark.asyncio
async def test_api_get_graph(client: AsyncClient, mock_db_session):
    """
    Tests the GET /api/v1/graph REST API endpoint mapping.
    """
    mock_execute_res = MagicMock()
    mock_execute_res.scalars.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_execute_res

    response = await client.get("/api/v1/graph")
    assert response.status_code == 200
    assert response.json() == {"nodes": [], "edges": []}
