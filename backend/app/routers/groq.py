"""Groq API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List

from app.models.schemas import (
    GroqChatRequest,
    GroqChatResponse,
    TestTrafficRequest,
    TestTrafficResponse,
)
from app.services.groq_service import groq_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/groq", tags=["groq"])


@router.post("/chat/completions", response_model=GroqChatResponse)
async def chat_completion(request: GroqChatRequest):
    """
    Execute a chat completion with full observability.

    This endpoint wraps the Groq API with:
    - Automatic metrics tracking
    - LangFuse tracing
    - Cost calculation
    - Error handling
    """
    try:
        response = await groq_service.chat_completion(
            messages=request.messages,
            model=request.model,
            user_id=request.user_id,
            user_role=request.user_role,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return response

    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/completions/secured", response_model=GroqChatResponse)
async def secured_chat_completion(request: GroqChatRequest):
    """
    Execute a chat completion with security layers.

    This endpoint integrates with the 4-layer security system:
    1. Llama Guard
    2. RBAC
    3. NeMo Guardrails
    4. PII Firewall
    """
    try:
        response = await groq_service.chat_completion_with_security(request)
        return response

    except Exception as e:
        logger.error(f"Secured chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
