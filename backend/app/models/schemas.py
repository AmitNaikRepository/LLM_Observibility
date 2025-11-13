"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class RequestStatus(str, Enum):
    """Request status enumeration."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


class SecurityLayer(str, Enum):
    """Security layer enumeration."""
    LLAMA_GUARD = "llama_guard"
    RBAC = "rbac"
    NEMO_GUARDRAILS = "nemo_guardrails"
    PII_FIREWALL = "pii_firewall"


class Component(str, Enum):
    """Component enumeration."""
    API_ROUTER = "api_router"
    SEMANTIC_CACHE = "semantic_cache"
    AI_ROUTER = "ai_router"
    LLAMA_GUARD = "llama_guard"
    RBAC = "rbac"
    NEMO_GUARDRAILS = "nemo_guardrails"
    PII_FIREWALL = "pii_firewall"
    GROQ_CLIENT = "groq_client"


# Metrics Models
class MetricsCreate(BaseModel):
    """Schema for creating a metrics record."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    user_role: UserRole
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    ttft_ms: Optional[int] = None
    tokens_per_second: Optional[float] = None
    cost_usd: float
    status: RequestStatus
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    component: Component
    cache_hit: bool = False
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    request_id: str


class MetricsResponse(BaseModel):
    """Schema for metrics response."""
    id: int
    timestamp: datetime
    user_id: str
    user_role: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    ttft_ms: Optional[int]
    tokens_per_second: Optional[float]
    cost_usd: float
    status: str
    error_type: Optional[str]
    component: str
    cache_hit: bool
    display_status: str

    class Config:
        from_attributes = True


# Security Event Models
class SecurityEventCreate(BaseModel):
    """Schema for creating a security event."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str
    layer: SecurityLayer
    action: str
    user_id: str
    user_role: UserRole
    details: Optional[Dict[str, Any]] = None
    blocked: bool = False
    threat_level: Optional[str] = None


# Routing Decision Models
class RoutingDecisionCreate(BaseModel):
    """Schema for creating a routing decision."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str
    user_id: str
    selected_model: str
    alternative_models: Optional[Dict[str, Any]] = None
    selection_reason: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    cost_savings: Optional[float] = None


# Cache Stats Models
class CacheStatsCreate(BaseModel):
    """Schema for creating cache stats."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str
    user_id: str
    cache_key: Optional[str] = None
    hit: bool
    similarity_score: Optional[float] = None
    tokens_saved: int = 0
    cost_saved: float = 0.0


# PII Event Models
class PIIEventCreate(BaseModel):
    """Schema for creating a PII event."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str
    user_id: str
    pii_types: Dict[str, Any]
    masked_count: int = 0
    confidence_score: Optional[float] = None


# Dashboard KPI Models
class KPIMetrics(BaseModel):
    """KPI metrics for dashboard."""
    avg_latency_ms: float
    p95_latency_ms: int
    total_cost_today: float
    success_rate: float
    total_requests: int
    total_requests_today: int
    cache_hit_rate: float
    cost_savings_today: float


class LatencyDataPoint(BaseModel):
    """Latency data point for charts."""
    timestamp: datetime
    avg_latency: float
    p95_latency: Optional[int] = None


class CostByModel(BaseModel):
    """Cost breakdown by model."""
    model: str
    cost: float
    percentage: float
    request_count: int


class RequestVolume(BaseModel):
    """Request volume by hour."""
    hour: datetime
    request_count: int
    success_count: int
    error_count: int


class TokensPerSecondData(BaseModel):
    """Tokens per second trend data."""
    timestamp: datetime
    avg_tps: float


class ErrorRateData(BaseModel):
    """Error rate data."""
    timestamp: datetime
    error_rate: float
    total_requests: int
    error_count: int


# Filter Models
class MetricsFilter(BaseModel):
    """Filter parameters for metrics queries."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_role: Optional[UserRole] = None
    model: Optional[str] = None
    status: Optional[RequestStatus] = None
    component: Optional[Component] = None
    limit: int = Field(default=20, le=1000)
    offset: int = Field(default=0, ge=0)


# Dashboard Response Model
class DashboardData(BaseModel):
    """Complete dashboard data."""
    kpis: KPIMetrics
    latency_trend: List[LatencyDataPoint]
    cost_by_model: List[CostByModel]
    request_volume: List[RequestVolume]
    tokens_per_second: List[TokensPerSecondData]
    error_rate: List[ErrorRateData]
    recent_requests: List[MetricsResponse]


# Groq Request/Response Models
class GroqChatRequest(BaseModel):
    """Groq chat completion request."""
    messages: List[Dict[str, str]]
    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = False
    user_id: str
    user_role: UserRole


class GroqChatResponse(BaseModel):
    """Groq chat completion response."""
    id: str
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    request_id: str
    latency_ms: int
    cost_usd: float


# Test Traffic Generation
class TestTrafficRequest(BaseModel):
    """Request to generate test traffic."""
    count: int = Field(default=10, ge=1, le=100)
    duration_seconds: int = Field(default=60, ge=1, le=300)
    models: Optional[List[str]] = None
    user_roles: Optional[List[UserRole]] = None


class TestTrafficResponse(BaseModel):
    """Response from test traffic generation."""
    requests_generated: int
    duration_seconds: float
    success_count: int
    error_count: int
