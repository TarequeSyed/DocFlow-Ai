import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """
    Sets up the central logger configurations for the FastAPI application.
    """
    log_level = logging.INFO
    if settings.ENVIRONMENT == "development":
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format=(
            "%(asctime)s [%(levelname)s] %(name)s "
            "(%(filename)s:%(lineno)d) - %(message)s"
        ),
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger instance.
    """
    return logging.getLogger(name)
