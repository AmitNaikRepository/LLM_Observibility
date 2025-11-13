"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database.connection import init_db, close_db
from app.services.redis_service import redis_service
from app.services.metrics_service import metrics_service
from app.services.langfuse_service import langfuse_service
from app.routers import metrics, groq
from app.middleware.observability import ObservabilityMiddleware, RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for startup and shutdown."""
    # Startup
    logger.info("Starting LLM Observability API...")

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Connect Redis
        await redis_service.connect()
        logger.info("Redis connected")

        # Start metrics service
        await metrics_service.start()
        logger.info("Metrics service started")

        logger.info("LLM Observability API started successfully")

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down LLM Observability API...")

    try:
        # Stop metrics service
        await metrics_service.stop()
        logger.info("Metrics service stopped")

        # Flush LangFuse
        langfuse_service.shutdown()
        logger.info("LangFuse flushed")

        # Close Redis
        await redis_service.disconnect()
        logger.info("Redis disconnected")

        # Close database
        await close_db()
        logger.info("Database closed")

        logger.info("LLM Observability API shut down successfully")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="LLM Observability API",
    description="Comprehensive observability platform for LLM systems",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(ObservabilityMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(metrics.router)
app.include_router(groq.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "LLM Observability API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        # Check database
        await init_db()  # This is safe to call multiple times

        # Check Redis
        if redis_service.redis:
            await redis_service.redis.ping()

        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "metrics_service": "running" if metrics_service.running else "stopped",
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
