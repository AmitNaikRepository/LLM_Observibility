"""Metrics API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta

from app.database.connection import db_pool
from app.models.schemas import (
    MetricsResponse,
    MetricsFilter,
    KPIMetrics,
    DashboardData,
    LatencyDataPoint,
    CostByModel,
    RequestVolume,
    TokensPerSecondData,
    ErrorRateData,
)
from app.services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/kpis", response_model=KPIMetrics)
async def get_kpis():
    """Get KPI metrics for dashboard."""
    try:
        # Get today's date
        today = datetime.utcnow().date()

        # Query for today's metrics
        kpi_query = """
            SELECT
                AVG(latency_ms) as avg_latency_ms,
                SUM(cost_usd) as total_cost_today,
                COUNT(*) as total_requests_today,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) * 100 as success_rate,
                AVG(CASE WHEN cache_hit THEN 1.0 ELSE 0.0 END) * 100 as cache_hit_rate
            FROM llm_metrics
            WHERE DATE(timestamp) = $1
        """

        kpi_data = await db_pool.fetchrow(kpi_query, today)

        # Get P95 latency for last 24 hours
        p95_query = """
            SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)::INT as p95_latency
            FROM llm_metrics
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """
        p95_data = await db_pool.fetchrow(p95_query)

        # Get total requests (all time)
        total_query = "SELECT COUNT(*) as total FROM llm_metrics"
        total_data = await db_pool.fetchrow(total_query)

        # Get cost savings from cache
        savings_query = """
            SELECT COALESCE(SUM(cost_saved), 0) as savings
            FROM cache_stats
            WHERE DATE(timestamp) = $1
        """
        savings_data = await db_pool.fetchrow(savings_query, today)

        # Get Redis real-time stats
        redis_stats = await redis_service.get_realtime_stats()

        return KPIMetrics(
            avg_latency_ms=float(kpi_data["avg_latency_ms"] or 0),
            p95_latency_ms=p95_data["p95_latency"] or 0,
            total_cost_today=float(kpi_data["total_cost_today"] or 0),
            success_rate=float(kpi_data["success_rate"] or 0),
            total_requests=total_data["total"] or 0,
            total_requests_today=kpi_data["total_requests_today"] or 0,
            cache_hit_rate=float(kpi_data["cache_hit_rate"] or 0),
            cost_savings_today=float(savings_data["savings"] or 0),
        )

    except Exception as e:
        logger.error(f"Failed to get KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latency-trend", response_model=List[LatencyDataPoint])
async def get_latency_trend(hours: int = Query(default=24, le=168)):
    """Get latency trend for the last N hours."""
    try:
        query = """
            SELECT
                DATE_TRUNC('hour', timestamp) as hour,
                AVG(latency_ms) as avg_latency,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)::INT as p95_latency
            FROM llm_metrics
            WHERE timestamp > NOW() - INTERVAL '1 hour' * $1
            GROUP BY DATE_TRUNC('hour', timestamp)
            ORDER BY hour ASC
        """

        rows = await db_pool.fetch(query, hours)

        return [
            LatencyDataPoint(
                timestamp=row["hour"],
                avg_latency=float(row["avg_latency"]),
                p95_latency=row["p95_latency"],
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"Failed to get latency trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cost-by-model", response_model=List[CostByModel])
async def get_cost_by_model(days: int = Query(default=7, le=90)):
    """Get cost breakdown by model."""
    try:
        query = """
            SELECT
                model,
                SUM(cost_usd) as total_cost,
                COUNT(*) as request_count
            FROM llm_metrics
            WHERE timestamp > NOW() - INTERVAL '1 day' * $1
            GROUP BY model
            ORDER BY total_cost DESC
        """

        rows = await db_pool.fetch(query, days)

        # Calculate total cost
        total_cost = sum(float(row["total_cost"]) for row in rows)

        return [
            CostByModel(
                model=row["model"],
                cost=float(row["total_cost"]),
                percentage=(float(row["total_cost"]) / total_cost * 100) if total_cost > 0 else 0,
                request_count=row["request_count"],
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"Failed to get cost by model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/request-volume", response_model=List[RequestVolume])
async def get_request_volume(hours: int = Query(default=24, le=168)):
    """Get request volume by hour."""
    try:
        query = """
            SELECT
                DATE_TRUNC('hour', timestamp) as hour,
                COUNT(*) as request_count,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count
            FROM llm_metrics
            WHERE timestamp > NOW() - INTERVAL '1 hour' * $1
            GROUP BY DATE_TRUNC('hour', timestamp)
            ORDER BY hour ASC
        """

        rows = await db_pool.fetch(query, hours)

        return [
            RequestVolume(
                hour=row["hour"],
                request_count=row["request_count"],
                success_count=row["success_count"],
                error_count=row["error_count"],
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"Failed to get request volume: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tokens-per-second", response_model=List[TokensPerSecondData])
async def get_tokens_per_second(hours: int = Query(default=24, le=168)):
    """Get tokens per second trend."""
    try:
        query = """
            SELECT
                DATE_TRUNC('hour', timestamp) as hour,
                AVG(tokens_per_second) as avg_tps
            FROM llm_metrics
            WHERE timestamp > NOW() - INTERVAL '1 hour' * $1
              AND tokens_per_second IS NOT NULL
            GROUP BY DATE_TRUNC('hour', timestamp)
            ORDER BY hour ASC
        """

        rows = await db_pool.fetch(query, hours)

        return [
            TokensPerSecondData(
                timestamp=row["hour"],
                avg_tps=float(row["avg_tps"] or 0),
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"Failed to get tokens per second: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/error-rate", response_model=List[ErrorRateData])
async def get_error_rate(hours: int = Query(default=24, le=168)):
    """Get error rate over time."""
    try:
        query = """
            SELECT
                DATE_TRUNC('hour', timestamp) as hour,
                COUNT(*) as total_requests,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) * 100 as error_rate
            FROM llm_metrics
            WHERE timestamp > NOW() - INTERVAL '1 hour' * $1
            GROUP BY DATE_TRUNC('hour', timestamp)
            ORDER BY hour ASC
        """

        rows = await db_pool.fetch(query, hours)

        return [
            ErrorRateData(
                timestamp=row["hour"],
                error_rate=float(row["error_rate"] or 0),
                total_requests=row["total_requests"],
                error_count=row["error_count"],
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"Failed to get error rate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-requests", response_model=List[MetricsResponse])
async def get_recent_requests(
    limit: int = Query(default=20, le=100),
    status: Optional[str] = None,
    model: Optional[str] = None,
):
    """Get recent requests with optional filters."""
    try:
        # Build query with filters
        conditions = ["1=1"]
        params = []
        param_count = 0

        if status:
            param_count += 1
            conditions.append(f"status = ${param_count}")
            params.append(status)

        if model:
            param_count += 1
            conditions.append(f"model = ${param_count}")
            params.append(model)

        param_count += 1
        params.append(limit)

        query = f"""
            SELECT * FROM v_recent_requests
            WHERE {' AND '.join(conditions)}
            ORDER BY timestamp DESC
            LIMIT ${param_count}
        """

        rows = await db_pool.fetch(query, *params)

        return [
            MetricsResponse(
                id=row["id"],
                timestamp=row["timestamp"],
                user_id=row["user_id"],
                user_role=row["user_role"],
                model=row["model"],
                input_tokens=row["input_tokens"],
                output_tokens=row["output_tokens"],
                total_tokens=row["total_tokens"],
                latency_ms=row["latency_ms"],
                ttft_ms=row.get("ttft_ms"),
                tokens_per_second=float(row["tokens_per_second"]) if row.get("tokens_per_second") else None,
                cost_usd=float(row["cost_usd"]),
                status=row["status"],
                error_type=row.get("error_type"),
                component=row["component"],
                cache_hit=row["cache_hit"],
                display_status=row["display_status"],
            )
            for row in rows
        ]

    except Exception as e:
        logger.error(f"Failed to get recent requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data():
    """Get all dashboard data in a single request."""
    try:
        # Check cache first
        cached_data = await redis_service.get_cached_dashboard_data()
        if cached_data:
            return cached_data

        # Fetch all data
        kpis = await get_kpis()
        latency_trend = await get_latency_trend(hours=24)
        cost_by_model = await get_cost_by_model(days=7)
        request_volume = await get_request_volume(hours=24)
        tokens_per_second = await get_tokens_per_second(hours=24)
        error_rate = await get_error_rate(hours=24)
        recent_requests = await get_recent_requests(limit=20)

        dashboard_data = DashboardData(
            kpis=kpis,
            latency_trend=latency_trend,
            cost_by_model=cost_by_model,
            request_volume=request_volume,
            tokens_per_second=tokens_per_second,
            error_rate=error_rate,
            recent_requests=recent_requests,
        )

        # Cache the data
        await redis_service.cache_dashboard_data(dashboard_data.model_dump(), ttl=30)

        return dashboard_data

    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[str])
async def get_models():
    """Get list of all models used."""
    try:
        query = "SELECT DISTINCT model FROM llm_metrics ORDER BY model"
        rows = await db_pool.fetch(query)
        return [row["model"] for row in rows]
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-roles", response_model=List[str])
async def get_user_roles():
    """Get list of all user roles."""
    try:
        query = "SELECT DISTINCT user_role FROM llm_metrics ORDER BY user_role"
        rows = await db_pool.fetch(query)
        return [row["user_role"] for row in rows]
    except Exception as e:
        logger.error(f"Failed to get user roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))
