import logging

from openai import AsyncOpenAI

from app.embeddings.base import EmbeddingProvider

logger = logging.getLogger("docuflow-openai-embed")


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI API-based embedding generator.
    Uses 'text-embedding-3-small' and requests exactly 384 dimensions
    via Matryoshka Representation Learning truncation.
    """

    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model_name = model_name
        self.client: AsyncOpenAI | None = None

    def _init_client(self) -> None:
        """
        Lazy-initializes the AsyncOpenAI client.
        """
        if self.client is None:
            logger.info(
                f"Initializing AsyncOpenAI client with model: {self.model_name}"
            )
            self.client = AsyncOpenAI(api_key=self.api_key)

    async def embed_query(self, text: str) -> list[float]:
        """
        Generates a 384-dimension vector for a single query text.
        """
        self._init_client()
        assert self.client is not None

        logger.info(f"Requesting OpenAI query vector from model {self.model_name}")
        response = await self.client.embeddings.create(
            input=[text],
            model=self.model_name,
            dimensions=384,  # Truncates to 384 dimensions using Matryoshka Learning
        )
        return response.data[0].embedding

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generates 384-dimension vectors for a list of document chunks.
        """
        self._init_client()
        assert self.client is not None

        logger.info(f"Requesting OpenAI vectors for {len(texts)} chunks")
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model_name,
            dimensions=384,  # Truncates to 384 dimensions using Matryoshka Learning
        )
        return [item.embedding for item in response.data]
