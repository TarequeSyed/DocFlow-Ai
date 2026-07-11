import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from app.embeddings.base import EmbeddingProvider

logger = logging.getLogger("docuflow-fastembed")


class FastEmbedProvider(EmbeddingProvider):
    """
    Local CPU-based text embedding generator using the fastembed library.
    Bypasses PyTorch, utilizing ONNX Runtime under the hood.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self.model = None
        self._executor = ThreadPoolExecutor(max_workers=1)

    def _init_model(self) -> None:
        """
        Lazy-initializes the FastEmbed model.
        """
        if self.model is None:
            # Lazy import to avoid loading heavy ONNX runtime unless selected
            from fastembed import TextEmbedding

            logger.info(f"Initializing FastEmbed model: {self.model_name}")
            self.model = TextEmbedding(model_name=self.model_name)

    async def embed_query(self, text: str) -> list[float]:
        """
        Generates a 384-dimension vector for a query text.
        """
        results = await self.embed_documents([text])
        return results[0]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generates 384-dimension vectors for a list of document chunks.
        Runs CPU work in a separate thread.
        """
        self._init_model()
        assert self.model is not None

        loop = asyncio.get_running_loop()
        logger.info(f"Generating FastEmbed vectors for {len(texts)} chunks...")

        # Offload the synchronous model.embed generator resolution to the thread pool
        generator = await loop.run_in_executor(
            self._executor, lambda: list(self.model.embed(texts))
        )

        # Convert numpy floats/arrays to standard list[float]
        return [list(map(float, vector)) for vector in generator]
