from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """
    Abstract interface for document text chunk and search query embeddings.
    Allows backend services to generate vector spaces without knowing the provider.
    """

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """
        Generates a numeric vector representation for a search query.
        """
        pass

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generates numeric vector representations for a list of document text chunks.
        """
        pass
