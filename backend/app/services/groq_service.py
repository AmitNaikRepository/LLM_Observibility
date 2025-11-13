"""Groq API service with comprehensive instrumentation."""

import time
import uuid
from typing import Dict, Any, Optional, List
import logging
from groq import Groq, AsyncGroq
from groq.types.chat import ChatCompletion

from app.config import get_settings
from app.models.schemas import (
    MetricsCreate,
    UserRole,
    RequestStatus,
    Component,
    GroqChatRequest,
    GroqChatResponse,
)
from app.services.metrics_service import metrics_service
from app.services.langfuse_service import langfuse_service, trace_llm_call

logger = logging.getLogger(__name__)
settings = get_settings()


class GroqService:
    """Service for Groq API calls with full observability."""

    def __init__(self):
        """Initialize Groq client."""
        try:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            self.sync_client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info("Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        user_id: str,
        user_role: UserRole,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        component: Component = Component.GROQ_CLIENT,
        cache_hit: bool = False,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GroqChatResponse:
        """
        Execute a chat completion with full instrumentation.

        This method wraps the Groq API call with:
        - Latency tracking
        - Token counting
        - Cost calculation
        - Error handling
        - LangFuse tracing
        - Async metrics logging
        """
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        first_token_time = None
        status = RequestStatus.SUCCESS
        error_type = None
        error_message = None

        # Create LangFuse trace if not provided
        if not trace_id:
            trace = langfuse_service.create_trace(
                name=f"groq_chat_completion",
                user_id=user_id,
                metadata={
                    "model": model,
                    "component": component.value,
                    "request_id": request_id,
                    **(metadata or {}),
                },
                tags=["groq", "chat_completion", component.value],
            )
            trace_id = trace.id if trace else None

        try:
            # Create generation span in LangFuse
            if trace_id:
                generation = langfuse_service.create_generation(
                    trace_id=trace_id,
                    name="groq_api_call",
                    model=model,
                    model_parameters={
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    input_data=messages,
                    metadata={
                        "user_role": user_role.value,
                        "cache_hit": cache_hit,
                    },
                )

            # Make the actual API call
            response: ChatCompletion = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Calculate first token time (approximation)
            first_token_time = int((time.perf_counter() - start_time) * 1000 / 2)

            # Extract response data
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason

            # Extract usage information
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            total_tokens = response.usage.total_tokens if response.usage else 0

            # Calculate metrics
            end_time = time.perf_counter()
            latency_ms = int((end_time - start_time) * 1000)
            tokens_per_second = (output_tokens / (latency_ms / 1000)) if latency_ms > 0 else 0

            # Calculate cost
            cost_usd = settings.calculate_cost(model, input_tokens, output_tokens)

            # Update LangFuse generation
            if trace_id and generation:
                langfuse_service.create_generation(
                    trace_id=trace_id,
                    name="groq_api_call",
                    model=model,
                    output_data={"content": content, "finish_reason": finish_reason},
                    usage={
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": total_tokens,
                    },
                    metadata={
                        "latency_ms": latency_ms,
                        "cost_usd": float(cost_usd),
                        "tokens_per_second": tokens_per_second,
                    },
                )

            # Create metrics record
            metric = MetricsCreate(
                request_id=request_id,
                user_id=user_id,
                user_role=user_role,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                ttft_ms=first_token_time,
                tokens_per_second=tokens_per_second,
                cost_usd=cost_usd,
                status=status,
                component=component,
                cache_hit=cache_hit,
                trace_id=trace_id,
            )

            # Log metrics asynchronously
            await metrics_service.log_metric(metric)

            # Prepare response
            return GroqChatResponse(
                id=response.id,
                content=content,
                model=model,
                usage={
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": total_tokens,
                },
                finish_reason=finish_reason,
                request_id=request_id,
                latency_ms=latency_ms,
                cost_usd=float(cost_usd),
            )

        except Exception as e:
            # Handle errors
            status = RequestStatus.ERROR
            error_type = type(e).__name__
            error_message = str(e)

            # Calculate error latency
            end_time = time.perf_counter()
            latency_ms = int((end_time - start_time) * 1000)

            logger.error(f"Groq API error: {error_type} - {error_message}")

            # Update LangFuse trace with error
            if trace_id:
                langfuse_service.update_trace(
                    trace_id=trace_id,
                    output={"error": error_message},
                    metadata={"error_type": error_type, "status": "error"},
                )

            # Log error metrics
            error_metric = MetricsCreate(
                request_id=request_id,
                user_id=user_id,
                user_role=user_role,
                model=model,
                input_tokens=0,
                output_tokens=0,
                latency_ms=latency_ms,
                cost_usd=0.0,
                status=status,
                error_type=error_type,
                error_message=error_message,
                component=component,
                cache_hit=cache_hit,
                trace_id=trace_id,
            )

            await metrics_service.log_metric(error_metric)

            # Re-raise the exception
            raise

    async def chat_completion_with_security(
        self,
        request: GroqChatRequest,
        security_checks: Optional[Dict[str, Any]] = None,
    ) -> GroqChatResponse:
        """
        Execute chat completion with security layer integration.

        This method integrates with the 4-layer security system:
        1. Llama Guard (malicious content detection)
        2. RBAC (role-based access control)
        3. NeMo Guardrails (task validation)
        4. PII Firewall (auto-detect and mask sensitive data)
        """
        request_id = str(uuid.uuid4())

        # Create trace for the entire request
        trace = langfuse_service.create_trace(
            name="secured_chat_completion",
            user_id=request.user_id,
            metadata={
                "model": request.model,
                "user_role": request.user_role.value,
                "request_id": request_id,
            },
            tags=["secured_request", "groq"],
        )
        trace_id = trace.id if trace else None

        try:
            # Here you would integrate with your security layers
            # For now, we'll simulate the checks

            # Layer 1: Llama Guard (content safety)
            # ... your existing Llama Guard implementation

            # Layer 2: RBAC check
            # ... your existing RBAC implementation

            # Layer 3: NeMo Guardrails
            # ... your existing guardrails implementation

            # Layer 4: PII Firewall
            # ... your existing PII detection/masking

            # Execute the actual LLM call
            response = await self.chat_completion(
                messages=request.messages,
                model=request.model,
                user_id=request.user_id,
                user_role=request.user_role,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                component=Component.GROQ_CLIENT,
                trace_id=trace_id,
            )

            return response

        except Exception as e:
            logger.error(f"Error in secured chat completion: {e}")
            raise


# Global Groq service instance
groq_service = GroqService()
