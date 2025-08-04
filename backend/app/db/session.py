"""
Database session management with async SQLAlchemy.
Provides database engine, session factory, and dependency injection.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from ..core.config import settings


# Create async engine with optimized connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool if "postgresql" in settings.DATABASE_URL else NullPool,
    pool_size=settings.DATABASE_POOL_SIZE if "postgresql" in settings.DATABASE_URL else 0,
    max_overflow=settings.DATABASE_MAX_OVERFLOW if "postgresql" in settings.DATABASE_URL else 0,
    pool_pre_ping=True,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """
    Get a new database session (for use outside of FastAPI dependency injection).
    
    Returns:
        AsyncSession: Database session
    """
    return AsyncSessionLocal()