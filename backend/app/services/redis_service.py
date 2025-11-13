"""Redis service for real-time counters and rate limiting."""

import redis.asyncio as aioredis
from typing import Optional
import logging
from datetime import datetime, timedelta

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisService:
    """Service for Redis operations."""

    def __init__(self):
        """Initialize Redis client."""
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await self.redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis disconnected")

    async def increment_counter(self, key: str, ttl: Optional[int] = None) -> int:
        """Increment a counter and optionally set TTL."""
        if not self.redis:
            return 0

        try:
            value = await self.redis.incr(key)
            if ttl:
                await self.redis.expire(key, ttl)
            return value
        except Exception as e:
            logger.error(f"Failed to increment counter {key}: {e}")
            return 0

    async def get_counter(self, key: str) -> int:
        """Get counter value."""
        if not self.redis:
            return 0

        try:
            value = await self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Failed to get counter {key}: {e}")
            return 0

    async def set_value(self, key: str, value: str, ttl: Optional[int] = None):
        """Set a value with optional TTL."""
        if not self.redis:
            return

        try:
            if ttl:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)
        except Exception as e:
            logger.error(f"Failed to set value {key}: {e}")

    async def get_value(self, key: str) -> Optional[str]:
        """Get a value."""
        if not self.redis:
            return None

        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Failed to get value {key}: {e}")
            return None

    async def check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        limit_per_minute: Optional[int] = None,
        limit_per_hour: Optional[int] = None,
    ) -> tuple[bool, int, int]:
        """
        Check rate limits for a user.

        Returns:
            (allowed, requests_this_minute, requests_this_hour)
        """
        if not self.redis:
            return True, 0, 0

        limit_per_minute = limit_per_minute or settings.RATE_LIMIT_PER_MINUTE
        limit_per_hour = limit_per_hour or settings.RATE_LIMIT_PER_HOUR

        now = datetime.utcnow()
        minute_key = f"rate_limit:{user_id}:{endpoint}:minute:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"rate_limit:{user_id}:{endpoint}:hour:{now.strftime('%Y%m%d%H')}"

        try:
            # Get current counts
            minute_count = await self.get_counter(minute_key)
            hour_count = await self.get_counter(hour_key)

            # Check limits
            if minute_count >= limit_per_minute or hour_count >= limit_per_hour:
                return False, minute_count, hour_count

            # Increment counters
            await self.increment_counter(minute_key, ttl=60)
            await self.increment_counter(hour_key, ttl=3600)

            return True, minute_count + 1, hour_count + 1

        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            # Fail open
            return True, 0, 0

    async def increment_request_counter(self, user_id: str, model: str, status: str):
        """Increment real-time request counters."""
        if not self.redis:
            return

        try:
            today = datetime.utcnow().strftime("%Y%m%d")

            # Global counters
            await self.increment_counter(f"requests:total:{today}", ttl=86400 * 7)
            await self.increment_counter(f"requests:status:{status}:{today}", ttl=86400 * 7)

            # User counters
            await self.increment_counter(f"requests:user:{user_id}:{today}", ttl=86400 * 7)

            # Model counters
            await self.increment_counter(f"requests:model:{model}:{today}", ttl=86400 * 7)

        except Exception as e:
            logger.error(f"Failed to increment request counter: {e}")

    async def get_realtime_stats(self) -> dict:
        """Get real-time statistics from Redis."""
        if not self.redis:
            return {}

        try:
            today = datetime.utcnow().strftime("%Y%m%d")

            total_requests = await self.get_counter(f"requests:total:{today}")
            success_requests = await self.get_counter(f"requests:status:success:{today}")
            error_requests = await self.get_counter(f"requests:status:error:{today}")

            return {
                "total_requests_today": total_requests,
                "success_requests_today": success_requests,
                "error_requests_today": error_requests,
                "success_rate": (success_requests / total_requests * 100) if total_requests > 0 else 0,
            }

        except Exception as e:
            logger.error(f"Failed to get realtime stats: {e}")
            return {}

    async def cache_dashboard_data(self, data: dict, ttl: int = 30):
        """Cache dashboard data."""
        if not self.redis:
            return

        try:
            import json

            await self.set_value("dashboard:data", json.dumps(data), ttl=ttl)
        except Exception as e:
            logger.error(f"Failed to cache dashboard data: {e}")

    async def get_cached_dashboard_data(self) -> Optional[dict]:
        """Get cached dashboard data."""
        if not self.redis:
            return None

        try:
            import json

            data = await self.get_value("dashboard:data")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get cached dashboard data: {e}")
            return None


# Global Redis service instance
redis_service = RedisService()
