"""Script to seed the database with realistic test data."""

import asyncio
import random
from datetime import datetime, timedelta
import asyncpg
from typing import List
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import get_settings

settings = get_settings()

# Test data configuration
MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
    "gemma2-9b-it",
]

USER_ROLES = ["employee", "manager", "admin"]

COMPONENTS = [
    "groq_client",
    "ai_router",
    "semantic_cache",
    "llama_guard",
    "nemo_guardrails",
    "pii_firewall",
]

STATUSES = ["success", "error", "timeout"]

USER_IDS = [f"user_{i}" for i in range(1, 51)]  # 50 users


def generate_realistic_metrics(count: int = 500, days: int = 7) -> List[dict]:
    """Generate realistic metrics data."""
    metrics = []
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    for i in range(count):
        # Random timestamp within the range
        timestamp = start_time + timedelta(
            seconds=random.randint(0, int((end_time - start_time).total_seconds()))
        )

        # Select random attributes
        model = random.choice(MODELS)
        user_id = random.choice(USER_IDS)
        user_role = random.choice(USER_ROLES)
        component = random.choice(COMPONENTS)

        # Status distribution: 90% success, 8% error, 2% timeout
        status_roll = random.random()
        if status_roll < 0.90:
            status = "success"
        elif status_roll < 0.98:
            status = "error"
        else:
            status = "timeout"

        # Generate realistic token counts based on model
        if "8b" in model.lower():
            input_tokens = random.randint(50, 500)
            output_tokens = random.randint(50, 800) if status == "success" else 0
            base_latency = random.randint(200, 800)
        elif "70b" in model.lower():
            input_tokens = random.randint(100, 1000)
            output_tokens = random.randint(100, 1500) if status == "success" else 0
            base_latency = random.randint(800, 2000)
        else:
            input_tokens = random.randint(75, 750)
            output_tokens = random.randint(75, 1000) if status == "success" else 0
            base_latency = random.randint(400, 1200)

        # Add some variance to latency
        latency_ms = base_latency + random.randint(-100, 300)
        latency_ms = max(100, latency_ms)  # Minimum 100ms

        # Calculate TTFT (Time To First Token) - roughly 20-40% of total latency
        ttft_ms = int(latency_ms * random.uniform(0.2, 0.4)) if status == "success" else None

        # Calculate tokens per second
        if status == "success" and output_tokens > 0:
            tokens_per_second = (output_tokens / (latency_ms / 1000))
        else:
            tokens_per_second = None

        # Cache hit: 30% chance
        cache_hit = random.random() < 0.30

        # Calculate cost
        input_cost, output_cost = settings.get_model_costs(model)
        cost_usd = ((input_tokens / 1_000_000) * input_cost) + (
            (output_tokens / 1_000_000) * output_cost
        )

        # Error details
        error_type = None
        error_message = None
        if status == "error":
            error_types = [
                "APIError",
                "TimeoutError",
                "RateLimitError",
                "ValidationError",
                "InvalidRequestError",
            ]
            error_type = random.choice(error_types)
            error_message = f"Simulated {error_type} for testing"
        elif status == "timeout":
            error_type = "TimeoutError"
            error_message = "Request timed out after 30 seconds"

        metric = {
            "timestamp": timestamp,
            "user_id": user_id,
            "user_role": user_role,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
            "ttft_ms": ttft_ms,
            "tokens_per_second": tokens_per_second,
            "cost_usd": cost_usd,
            "status": status,
            "error_type": error_type,
            "error_message": error_message,
            "component": component,
            "cache_hit": cache_hit,
            "request_id": f"req_{i}_{timestamp.timestamp()}",
        }

        metrics.append(metric)

    return metrics


async def seed_metrics(pool: asyncpg.Pool, metrics: List[dict]):
    """Insert metrics into database."""
    async with pool.acquire() as conn:
        async with conn.transaction():
            for metric in metrics:
                await conn.execute(
                    """
                    INSERT INTO llm_metrics (
                        timestamp, user_id, user_role, model, input_tokens, output_tokens,
                        latency_ms, ttft_ms, tokens_per_second, cost_usd, status,
                        error_type, error_message, component, cache_hit, request_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    """,
                    metric["timestamp"],
                    metric["user_id"],
                    metric["user_role"],
                    metric["model"],
                    metric["input_tokens"],
                    metric["output_tokens"],
                    metric["latency_ms"],
                    metric["ttft_ms"],
                    metric["tokens_per_second"],
                    metric["cost_usd"],
                    metric["status"],
                    metric["error_type"],
                    metric["error_message"],
                    metric["component"],
                    metric["cache_hit"],
                    metric["request_id"],
                )


async def seed_cache_stats(pool: asyncpg.Pool, count: int = 150):
    """Seed cache statistics."""
    metrics = await pool.fetch(
        "SELECT request_id, user_id, input_tokens, cost_usd FROM llm_metrics ORDER BY RANDOM() LIMIT $1",
        count,
    )

    async with pool.acquire() as conn:
        async with conn.transaction():
            for metric in metrics:
                hit = random.random() < 0.30  # 30% hit rate
                similarity_score = random.uniform(0.85, 0.99) if hit else random.uniform(0.50, 0.84)
                tokens_saved = metric["input_tokens"] if hit else 0
                cost_saved = metric["cost_usd"] * 0.8 if hit else 0  # 80% cost savings on cache hit

                await conn.execute(
                    """
                    INSERT INTO cache_stats (
                        request_id, user_id, cache_key, hit, similarity_score,
                        tokens_saved, cost_saved
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    metric["request_id"],
                    metric["user_id"],
                    f"cache_key_{random.randint(1, 100)}",
                    hit,
                    similarity_score,
                    tokens_saved,
                    cost_saved,
                )


async def seed_routing_decisions(pool: asyncpg.Pool, count: int = 200):
    """Seed routing decisions."""
    metrics = await pool.fetch(
        "SELECT request_id, user_id, model, cost_usd FROM llm_metrics ORDER BY RANDOM() LIMIT $1",
        count,
    )

    async with pool.acquire() as conn:
        async with conn.transaction():
            for metric in metrics:
                # Calculate cost savings from routing
                selected_model = metric["model"]
                alternative_models = [m for m in MODELS if m != selected_model]

                # Simulate savings by comparing with most expensive alternative
                expensive_model = "llama-3.1-70b-versatile"
                if selected_model != expensive_model:
                    expensive_cost = metric["cost_usd"] * 2.5  # Simulate higher cost
                    cost_savings = expensive_cost - metric["cost_usd"]
                else:
                    cost_savings = 0

                await conn.execute(
                    """
                    INSERT INTO routing_decisions (
                        request_id, user_id, selected_model, alternative_models,
                        selection_reason, estimated_cost, actual_cost, cost_savings
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    metric["request_id"],
                    metric["user_id"],
                    selected_model,
                    {"alternatives": alternative_models[:2]},
                    random.choice(
                        [
                            "Lowest cost for task",
                            "Fastest response time",
                            "Best for complexity",
                            "User preference",
                        ]
                    ),
                    metric["cost_usd"],
                    metric["cost_usd"],
                    cost_savings,
                )


async def seed_security_events(pool: asyncpg.Pool, count: int = 50):
    """Seed security events."""
    metrics = await pool.fetch(
        "SELECT request_id, user_id, user_role FROM llm_metrics ORDER BY RANDOM() LIMIT $1",
        count,
    )

    layers = ["llama_guard", "rbac", "nemo_guardrails", "pii_firewall"]

    async with pool.acquire() as conn:
        async with conn.transaction():
            for metric in metrics:
                layer = random.choice(layers)
                blocked = random.random() < 0.20  # 20% blocked

                await conn.execute(
                    """
                    INSERT INTO security_events (
                        request_id, layer, action, user_id, user_role,
                        details, blocked, threat_level
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    metric["request_id"],
                    layer,
                    "blocked" if blocked else "allowed",
                    metric["user_id"],
                    metric["user_role"],
                    {"reason": f"Security check by {layer}"},
                    blocked,
                    random.choice(["low", "medium", "high"]) if blocked else "low",
                )


async def seed_pii_events(pool: asyncpg.Pool, count: int = 30):
    """Seed PII detection events."""
    metrics = await pool.fetch(
        "SELECT request_id, user_id FROM llm_metrics ORDER BY RANDOM() LIMIT $1",
        count,
    )

    pii_types_list = [
        {"email": 1},
        {"phone": 1},
        {"ssn": 1},
        {"credit_card": 1},
        {"email": 2, "phone": 1},
    ]

    async with pool.acquire() as conn:
        async with conn.transaction():
            for metric in metrics:
                pii_types = random.choice(pii_types_list)
                masked_count = sum(pii_types.values())

                await conn.execute(
                    """
                    INSERT INTO pii_events (
                        request_id, user_id, pii_types, masked_count, confidence_score
                    ) VALUES ($1, $2, $3, $4, $5)
                    """,
                    metric["request_id"],
                    metric["user_id"],
                    pii_types,
                    masked_count,
                    random.uniform(0.85, 0.99),
                )


async def main():
    """Main seeding function."""
    print("Starting database seeding...")

    # Connect to database
    try:
        url = settings.ASYNC_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        pool = await asyncpg.create_pool(url)
        print("Connected to database")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    try:
        # Generate and insert metrics
        print("Generating 500 realistic metrics over 7 days...")
        metrics = generate_realistic_metrics(count=500, days=7)
        print(f"Inserting {len(metrics)} metrics...")
        await seed_metrics(pool, metrics)
        print("Metrics inserted successfully")

        # Seed cache stats
        print("Seeding cache statistics...")
        await seed_cache_stats(pool, count=150)
        print("Cache stats inserted")

        # Seed routing decisions
        print("Seeding routing decisions...")
        await seed_routing_decisions(pool, count=200)
        print("Routing decisions inserted")

        # Seed security events
        print("Seeding security events...")
        await seed_security_events(pool, count=50)
        print("Security events inserted")

        # Seed PII events
        print("Seeding PII events...")
        await seed_pii_events(pool, count=30)
        print("PII events inserted")

        # Update daily stats
        print("Updating daily stats...")
        await pool.execute("SELECT update_daily_stats()")
        print("Daily stats updated")

        print("\n✅ Database seeding completed successfully!")

        # Print some statistics
        total_metrics = await pool.fetchval("SELECT COUNT(*) FROM llm_metrics")
        total_cost = await pool.fetchval("SELECT SUM(cost_usd) FROM llm_metrics")
        success_rate = await pool.fetchval(
            "SELECT SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 FROM llm_metrics"
        )

        print(f"\nDatabase Statistics:")
        print(f"  Total Metrics: {total_metrics}")
        print(f"  Total Cost: ${total_cost:.4f}")
        print(f"  Success Rate: {success_rate:.2f}%")

    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await pool.close()
        print("Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())
