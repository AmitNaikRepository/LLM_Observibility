"""Metrics service for async logging to PostgreSQL."""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from queue import Queue
import logging
from threading import Thread
import uuid

from app.database.connection import db_pool
from app.models.schemas import (
    MetricsCreate,
    SecurityEventCreate,
    RoutingDecisionCreate,
    CacheStatsCreate,
    PIIEventCreate,
)
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MetricsService:
    """Service for async metrics logging."""

    def __init__(self):
        """Initialize metrics service."""
        self.metrics_queue: asyncio.Queue = asyncio.Queue(maxsize=settings.METRICS_QUEUE_SIZE)
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the metrics worker."""
        if not self.running:
            self.running = True
            self.worker_task = asyncio.create_task(self._process_metrics())
            logger.info("Metrics service started")

    async def stop(self):
        """Stop the metrics worker."""
        if self.running:
            self.running = False
            if self.worker_task:
                await self.worker_task
            # Flush remaining metrics
            await self._flush_queue()
            logger.info("Metrics service stopped")

    async def log_metric(self, metric: MetricsCreate) -> bool:
        """Add a metric to the queue for async processing."""
        try:
            await self.metrics_queue.put(metric)
            return True
        except asyncio.QueueFull:
            logger.error("Metrics queue is full, dropping metric")
            return False

    async def log_security_event(self, event: SecurityEventCreate) -> bool:
        """Log a security event."""
        try:
            await self._insert_security_event(event)
            return True
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            return False

    async def log_routing_decision(self, decision: RoutingDecisionCreate) -> bool:
        """Log a routing decision."""
        try:
            await self._insert_routing_decision(decision)
            return True
        except Exception as e:
            logger.error(f"Failed to log routing decision: {e}")
            return False

    async def log_cache_stats(self, stats: CacheStatsCreate) -> bool:
        """Log cache statistics."""
        try:
            await self._insert_cache_stats(stats)
            return True
        except Exception as e:
            logger.error(f"Failed to log cache stats: {e}")
            return False

    async def log_pii_event(self, event: PIIEventCreate) -> bool:
        """Log a PII detection event."""
        try:
            await self._insert_pii_event(event)
            return True
        except Exception as e:
            logger.error(f"Failed to log PII event: {e}")
            return False

    async def _process_metrics(self):
        """Worker task to process metrics from queue."""
        logger.info("Metrics worker started")
        batch = []
        last_flush = datetime.utcnow()

        while self.running:
            try:
                # Check if we should flush based on time
                if (datetime.utcnow() - last_flush).total_seconds() >= settings.METRICS_FLUSH_INTERVAL:
                    if batch:
                        await self._flush_batch(batch)
                        batch = []
                        last_flush = datetime.utcnow()

                # Get metric from queue with timeout
                try:
                    metric = await asyncio.wait_for(
                        self.metrics_queue.get(),
                        timeout=1.0,
                    )
                    batch.append(metric)

                    # Flush if batch is full
                    if len(batch) >= settings.METRICS_BATCH_SIZE:
                        await self._flush_batch(batch)
                        batch = []
                        last_flush = datetime.utcnow()

                except asyncio.TimeoutError:
                    continue

            except Exception as e:
                logger.error(f"Error processing metrics: {e}")
                await asyncio.sleep(1)

        # Flush remaining batch
        if batch:
            await self._flush_batch(batch)

        logger.info("Metrics worker stopped")

    async def _flush_batch(self, batch: list[MetricsCreate]):
        """Flush a batch of metrics to database."""
        if not batch:
            return

        try:
            # Prepare batch insert query
            query = """
                INSERT INTO llm_metrics (
                    timestamp, user_id, user_role, model, input_tokens, output_tokens,
                    latency_ms, ttft_ms, tokens_per_second, cost_usd, status,
                    error_type, error_message, component, cache_hit, trace_id,
                    span_id, request_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
            """

            # Execute batch insert
            async with db_pool.pool.acquire() as conn:
                async with conn.transaction():
                    for metric in batch:
                        await conn.execute(
                            query,
                            metric.timestamp,
                            metric.user_id,
                            metric.user_role.value,
                            metric.model,
                            metric.input_tokens,
                            metric.output_tokens,
                            metric.latency_ms,
                            metric.ttft_ms,
                            metric.tokens_per_second,
                            metric.cost_usd,
                            metric.status.value,
                            metric.error_type,
                            metric.error_message,
                            metric.component.value,
                            metric.cache_hit,
                            metric.trace_id,
                            metric.span_id,
                            metric.request_id,
                        )

            logger.info(f"Flushed {len(batch)} metrics to database")

        except Exception as e:
            logger.error(f"Failed to flush metrics batch: {e}")
            # Optionally: implement retry logic or dead letter queue

    async def _flush_queue(self):
        """Flush all remaining metrics in queue."""
        batch = []
        while not self.metrics_queue.empty():
            try:
                metric = self.metrics_queue.get_nowait()
                batch.append(metric)
            except asyncio.QueueEmpty:
                break

        if batch:
            await self._flush_batch(batch)

    async def _insert_security_event(self, event: SecurityEventCreate):
        """Insert a security event into database."""
        query = """
            INSERT INTO security_events (
                timestamp, request_id, layer, action, user_id, user_role,
                details, blocked, threat_level
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """

        await db_pool.execute(
            query,
            event.timestamp,
            event.request_id,
            event.layer.value,
            event.action,
            event.user_id,
            event.user_role.value,
            event.details,
            event.blocked,
            event.threat_level,
        )

    async def _insert_routing_decision(self, decision: RoutingDecisionCreate):
        """Insert a routing decision into database."""
        query = """
            INSERT INTO routing_decisions (
                timestamp, request_id, user_id, selected_model, alternative_models,
                selection_reason, estimated_cost, actual_cost, cost_savings
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """

        await db_pool.execute(
            query,
            decision.timestamp,
            decision.request_id,
            decision.user_id,
            decision.selected_model,
            decision.alternative_models,
            decision.selection_reason,
            decision.estimated_cost,
            decision.actual_cost,
            decision.cost_savings,
        )

    async def _insert_cache_stats(self, stats: CacheStatsCreate):
        """Insert cache stats into database."""
        query = """
            INSERT INTO cache_stats (
                timestamp, request_id, user_id, cache_key, hit,
                similarity_score, tokens_saved, cost_saved
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """

        await db_pool.execute(
            query,
            stats.timestamp,
            stats.request_id,
            stats.user_id,
            stats.cache_key,
            stats.hit,
            stats.similarity_score,
            stats.tokens_saved,
            stats.cost_saved,
        )

    async def _insert_pii_event(self, event: PIIEventCreate):
        """Insert PII event into database."""
        query = """
            INSERT INTO pii_events (
                timestamp, request_id, user_id, pii_types, masked_count, confidence_score
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """

        await db_pool.execute(
            query,
            event.timestamp,
            event.request_id,
            event.user_id,
            event.pii_types,
            event.masked_count,
            event.confidence_score,
        )


# Global metrics service instance
metrics_service = MetricsService()
