import uuid

from pydantic import BaseModel


class SearchQueryRequest(BaseModel):
    """
    Input schema for semantic search query requests.
    """

    query: str
    document_id: uuid.UUID | None = None
    limit: int = 5


class SearchResultItem(BaseModel):
    """
    Single search result match item containing details.
    """

    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    score: float
    retrieval_strategy: str


class SearchResponse(BaseModel):
    """
    Structured search results list.
    """

    query: str
    results: list[SearchResultItem]
