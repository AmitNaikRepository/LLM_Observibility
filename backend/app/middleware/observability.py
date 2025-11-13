"""Observability middleware for FastAPI."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from typing import Callable

from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware to track API requests."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track metrics."""
        start_time = time.perf_counter()

        # Extract user info from request (if available)
        user_id = request.headers.get("X-User-ID", "anonymous")
        user_role = request.headers.get("X-User-Role", "employee")

        # Add request context
        request.state.user_id = user_id
        request.state.user_role = user_role
        request.state.start_time = start_time

        try:
            # Process request
            response = await call_next(request)

            # Calculate latency
            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Add custom headers
            response.headers["X-Request-Time"] = str(latency_ms)

            # Log to stdout for debugging
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Latency: {latency_ms}ms - "
                f"User: {user_id}"
            )

            return response

        except Exception as e:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error(
                f"{request.method} {request.url.path} - "
                f"Error: {str(e)} - "
                f"Latency: {latency_ms}ms - "
                f"User: {user_id}"
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limits before processing request."""
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        user_id = request.headers.get("X-User-ID", "anonymous")
        endpoint = request.url.path

        # Check rate limit
        allowed, minute_count, hour_count = await redis_service.check_rate_limit(
            user_id=user_id,
            endpoint=endpoint,
        )

        if not allowed:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={
                    "X-RateLimit-Limit-Minute": str(60),
                    "X-RateLimit-Limit-Hour": str(1000),
                    "X-RateLimit-Remaining-Minute": str(max(0, 60 - minute_count)),
                    "X-RateLimit-Remaining-Hour": str(max(0, 1000 - hour_count)),
                },
            )

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(60)
        response.headers["X-RateLimit-Limit-Hour"] = str(1000)
        response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, 60 - minute_count))
        response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, 1000 - hour_count))

        return response
