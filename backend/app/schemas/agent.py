"""Agent-related schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    """Response schema for chat (non-streaming)."""
    conversation_id: str
    message: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class StreamChunk(BaseModel):
    """Schema for streaming response chunk."""
    content: str
    done: bool = False
    conversation_id: Optional[str] = None
    error: Optional[str] = None


class CopyVariant(BaseModel):
    """A single ad copy variant."""
    variant_number: int
    angle: str
    primary_text: str
    headline: str
    description: str
    suggested_cta: str = "learn_more"


class CreativeBrief(BaseModel):
    """A creative brief/angle."""
    angle_name: str
    hook: str
    value_proposition: str
    target_emotion: str
    suggested_audiences: List[str] = []


class DailyBriefResponse(BaseModel):
    """Response for daily brief."""
    message: str
    has_data: bool = False
    top_performer: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = []
    summary_stats: Optional[Dict[str, Any]] = None


class GenerateCopyRequest(BaseModel):
    """Request for generating ad copy."""
    product_info: str = Field(..., min_length=10)
    tone: Optional[str] = "friendly"
    num_variants: int = Field(default=3, ge=1, le=5)
    past_winners: Optional[List[Dict[str, Any]]] = None


class AnalyzePerformanceRequest(BaseModel):
    """Request for analyzing performance."""
    time_range: str = "last_7_days"
    focus_metric: Optional[str] = None


class AudienceSuggestion(BaseModel):
    """Suggested target audience."""
    name: str
    type: str  # interest, demographic, lookalike
    details: Dict[str, Any] = {}
    rationale: str = ""
