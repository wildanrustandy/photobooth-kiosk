from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models with async support."""

    pass


# Create async engine
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.
    Automatically handles session cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables (use only in development/testing)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db():
    """Dispose of the engine and close all connections."""
    await async_engine.dispose()
