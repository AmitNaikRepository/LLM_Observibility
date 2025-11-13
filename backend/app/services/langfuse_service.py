"""LangFuse integration service for distributed tracing."""

from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from typing import Optional, Dict, Any
import logging
from functools import wraps
from contextlib import asynccontextmanager

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LangFuseService:
    """Service for LangFuse integration."""

    def __init__(self):
        """Initialize LangFuse client."""
        try:
            self.client = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST,
            )
            self.enabled = True
            logger.info("LangFuse client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LangFuse: {e}")
            self.client = None
            self.enabled = False

    def create_trace(
        self,
        name: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
    ):
        """Create a new trace."""
        if not self.enabled:
            return None

        try:
            return self.client.trace(
                name=name,
                user_id=user_id,
                metadata=metadata or {},
                tags=tags or [],
            )
        except Exception as e:
            logger.error(f"Failed to create trace: {e}")
            return None

    def create_span(
        self,
        trace_id: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
    ):
        """Create a span within a trace."""
        if not self.enabled:
            return None

        try:
            return self.client.span(
                trace_id=trace_id,
                name=name,
                metadata=metadata or {},
                input=input_data,
                output=output_data,
            )
        except Exception as e:
            logger.error(f"Failed to create span: {e}")
            return None

    def create_generation(
        self,
        trace_id: str,
        name: str,
        model: str,
        model_parameters: Optional[Dict[str, Any]] = None,
        input_data: Optional[Any] = None,
        output_data: Optional[Any] = None,
        usage: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Create a generation (LLM call) within a trace."""
        if not self.enabled:
            return None

        try:
            return self.client.generation(
                trace_id=trace_id,
                name=name,
                model=model,
                model_parameters=model_parameters or {},
                input=input_data,
                output=output_data,
                usage=usage,
                metadata=metadata or {},
            )
        except Exception as e:
            logger.error(f"Failed to create generation: {e}")
            return None

    def update_trace(
        self,
        trace_id: str,
        output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Update an existing trace."""
        if not self.enabled:
            return

        try:
            self.client.trace(
                id=trace_id,
                output=output,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Failed to update trace: {e}")

    def score_trace(
        self,
        trace_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ):
        """Add a score to a trace."""
        if not self.enabled:
            return

        try:
            self.client.score(
                trace_id=trace_id,
                name=name,
                value=value,
                comment=comment,
            )
        except Exception as e:
            logger.error(f"Failed to score trace: {e}")

    def flush(self):
        """Flush pending traces to LangFuse."""
        if not self.enabled:
            return

        try:
            self.client.flush()
        except Exception as e:
            logger.error(f"Failed to flush LangFuse: {e}")

    def shutdown(self):
        """Shutdown LangFuse client."""
        if self.enabled:
            try:
                self.client.flush()
                logger.info("LangFuse client shut down successfully")
            except Exception as e:
                logger.error(f"Error during LangFuse shutdown: {e}")


# Global LangFuse service instance
langfuse_service = LangFuseService()


def trace_llm_call(component: str):
    """Decorator to trace LLM calls with LangFuse."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract user_id from kwargs if available
            user_id = kwargs.get("user_id", "unknown")
            model = kwargs.get("model", "unknown")

            # Create trace
            trace = langfuse_service.create_trace(
                name=f"{component}.{func.__name__}",
                user_id=user_id,
                metadata={"component": component, "model": model},
                tags=[component, "llm_call"],
            )

            trace_id = trace.id if trace else None

            try:
                # Call the function
                result = await func(*args, **kwargs)

                # Update trace with success
                if trace_id:
                    langfuse_service.update_trace(
                        trace_id=trace_id,
                        output={"status": "success"},
                        metadata={"completed": True},
                    )

                # Add trace_id to result if it's a dict
                if isinstance(result, dict) and trace_id:
                    result["trace_id"] = trace_id

                return result

            except Exception as e:
                # Update trace with error
                if trace_id:
                    langfuse_service.update_trace(
                        trace_id=trace_id,
                        output={"status": "error", "error": str(e)},
                        metadata={"error": True},
                    )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id", "unknown")
            model = kwargs.get("model", "unknown")

            trace = langfuse_service.create_trace(
                name=f"{component}.{func.__name__}",
                user_id=user_id,
                metadata={"component": component, "model": model},
                tags=[component, "llm_call"],
            )

            trace_id = trace.id if trace else None

            try:
                result = func(*args, **kwargs)

                if trace_id:
                    langfuse_service.update_trace(
                        trace_id=trace_id,
                        output={"status": "success"},
                        metadata={"completed": True},
                    )

                if isinstance(result, dict) and trace_id:
                    result["trace_id"] = trace_id

                return result

            except Exception as e:
                if trace_id:
                    langfuse_service.update_trace(
                        trace_id=trace_id,
                        output={"status": "error", "error": str(e)},
                        metadata={"error": True},
                    )
                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
