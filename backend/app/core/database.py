from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Create async database engine
# We use NullPool in Serverless or custom settings (like pool_size) for container scale
engine = create_async_engine(
    settings.DATABASE_URL, echo=False, future=True, pool_pre_ping=True
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """
    Subclass DeclarativeBase to initialize declarative models.
    """

    pass
