import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.embeddings.factory import EmbeddingProviderFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("docuflow-backend")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An AI-powered Document Intelligence Platform API",
    version="1.0.0",
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """
    Triggers on backend launch. Validates configuration and verifies that
    the configured embedding provider loads successfully.
    """
    logger.info("Verifying system configuration...")
    try:
        provider = EmbeddingProviderFactory.get_provider()
        logger.info(
            f"Embedding Provider loaded successfully: {provider.__class__.__name__}"
        )
    except Exception as e:
        logger.critical(f"Failed to load embedding provider: {e}", exc_info=True)
        raise e


@app.get("/", tags=["General"])
async def read_root() -> dict[str, str]:
    """
    Branding and welcome index route.
    """
    logger.info("Welcome route accessed.")
    return {
        "project": settings.PROJECT_NAME,
        "description": "An AI-powered Document Intelligence Platform",
        "status": "online",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health", tags=["General"])
async def health_check() -> dict[str, Any]:
    """
    Basic application health checker detailing the active embedding model.
    """
    logger.info("Health check endpoint queried.")
    try:
        provider = EmbeddingProviderFactory.get_provider()
        provider_name = provider.__class__.__name__
    except Exception as e:
        provider_name = f"ERROR: {e}"

    return {
        "status": "healthy",
        "services": {"api": "healthy"},
        "embeddings": {
            "active_provider": settings.EMBEDDING_PROVIDER,
            "provider_class": provider_name,
            "model_name": (
                settings.FASTEMBED_MODEL
                if settings.EMBEDDING_PROVIDER == "fastembed"
                else settings.OPENAI_EMBEDDING_MODEL
            ),
        },
    }
