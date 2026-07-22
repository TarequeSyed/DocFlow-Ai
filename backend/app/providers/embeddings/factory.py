import logging

from app.core.config import settings
from app.providers.embeddings.base import EmbeddingProvider
from app.providers.embeddings.fastembed_provider import FastEmbedProvider
from app.providers.embeddings.openai_provider import OpenAIEmbeddingProvider

logger = logging.getLogger("docuflow-embeddings-factory")


class EmbeddingProviderFactory:
    """
    Factory pattern for instantiation and lookup of EmbeddingProvider instances.
    Provides a singleton cache to avoid multiple loader threadpools.
    """

    _instance: EmbeddingProvider | None = None

    @classmethod
    def get_provider(cls) -> EmbeddingProvider:
        """
        Retrieves the singleton instances of the configured embedding provider.
        Selection logic resides entirely here, keeping business logic clean.
        """
        if cls._instance is not None:
            return cls._instance

        provider_type = settings.EMBEDDING_PROVIDER.strip().lower()
        logger.info(
            f"Resolving embedding provider for configuration: '{provider_type}'"
        )

        if provider_type == "fastembed":
            cls._instance = FastEmbedProvider(model_name=settings.FASTEMBED_MODEL)
        elif provider_type == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for 'openai' provider.")
            cls._instance = OpenAIEmbeddingProvider(
                api_key=settings.OPENAI_API_KEY,
                model_name=settings.OPENAI_EMBEDDING_MODEL,
            )
        else:
            raise ValueError(
                f"Unsupported embedding provider: {settings.EMBEDDING_PROVIDER}"
            )

        return cls._instance
