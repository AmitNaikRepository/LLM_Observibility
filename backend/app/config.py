"""Configuration management for the LLM Observability system."""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/llm_observability"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/llm_observability"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Groq API
    GROQ_API_KEY: str

    # LangFuse
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Groq Pricing (per 1M tokens)
    GROQ_LLAMA3_8B_INPUT_COST: float = 0.05
    GROQ_LLAMA3_8B_OUTPUT_COST: float = 0.08
    GROQ_LLAMA3_70B_INPUT_COST: float = 0.59
    GROQ_LLAMA3_70B_OUTPUT_COST: float = 0.79
    GROQ_MIXTRAL_8X7B_INPUT_COST: float = 0.24
    GROQ_MIXTRAL_8X7B_OUTPUT_COST: float = 0.24
    GROQ_GEMMA_7B_INPUT_COST: float = 0.07
    GROQ_GEMMA_7B_OUTPUT_COST: float = 0.07
    GROQ_GEMMA2_9B_INPUT_COST: float = 0.20
    GROQ_GEMMA2_9B_OUTPUT_COST: float = 0.20

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Async Processing
    METRICS_QUEUE_SIZE: int = 1000
    METRICS_BATCH_SIZE: int = 10
    METRICS_FLUSH_INTERVAL: int = 5  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def get_model_costs(self, model: str) -> tuple[float, float]:
        """Get input and output costs for a model (per 1M tokens)."""
        model_lower = model.lower()

        if "llama-3.1-8b" in model_lower or "llama3-8b" in model_lower:
            return self.GROQ_LLAMA3_8B_INPUT_COST, self.GROQ_LLAMA3_8B_OUTPUT_COST
        elif "llama-3.1-70b" in model_lower or "llama3-70b" in model_lower:
            return self.GROQ_LLAMA3_70B_INPUT_COST, self.GROQ_LLAMA3_70B_OUTPUT_COST
        elif "mixtral" in model_lower:
            return self.GROQ_MIXTRAL_8X7B_INPUT_COST, self.GROQ_MIXTRAL_8X7B_OUTPUT_COST
        elif "gemma-7b" in model_lower:
            return self.GROQ_GEMMA_7B_INPUT_COST, self.GROQ_GEMMA_7B_OUTPUT_COST
        elif "gemma2-9b" in model_lower:
            return self.GROQ_GEMMA2_9B_INPUT_COST, self.GROQ_GEMMA2_9B_OUTPUT_COST
        else:
            # Default fallback
            return 0.10, 0.10

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request."""
        input_cost_per_m, output_cost_per_m = self.get_model_costs(model)

        input_cost = (input_tokens / 1_000_000) * input_cost_per_m
        output_cost = (output_tokens / 1_000_000) * output_cost_per_m

        return round(input_cost + output_cost, 8)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
