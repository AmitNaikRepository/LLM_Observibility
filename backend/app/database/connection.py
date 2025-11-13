"""Database connection management."""

import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# SQLAlchemy setup
Base = declarative_base()

# Sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Async engine for API
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    echo=settings.DEBUG,
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Database connection pool for raw queries
class DatabasePool:
    """Manages asyncpg connection pool."""

    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        """Create connection pool."""
        if self.pool is None:
            try:
                # Parse DATABASE_URL to get connection params
                url = settings.ASYNC_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
                self.pool = await asyncpg.create_pool(
                    url,
                    min_size=10,
                    max_size=50,
                    command_timeout=60,
                )
                logger.info("Database connection pool created")
            except Exception as e:
                logger.error(f"Failed to create database pool: {e}")
                raise

    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def execute(self, query: str, *args):
        """Execute a query without returning results."""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch multiple rows."""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch a single row."""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Fetch a single value."""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global pool instance
db_pool = DatabasePool()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db():
    """Dependency for FastAPI routes."""
    async with get_db_session() as session:
        yield session


async def init_db():
    """Initialize database connection."""
    try:
        await db_pool.connect()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """Close database connection."""
    try:
        await db_pool.close()
        await async_engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
