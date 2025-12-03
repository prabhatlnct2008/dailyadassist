"""Activity log schemas."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ActivityLogResponse(BaseModel):
    """Response schema for activity log entry."""
    id: str
    user_id: str
    action_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    rationale: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    is_agent_action: bool = False

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Response schema for a recommendation."""
    id: str
    type: str
    description: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    entity_name: str = ""
    suggested_action: str = ""
    impact: str = ""
    created_at: datetime


class CreateActivityLog(BaseModel):
    """Schema for creating an activity log."""
    action_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    rationale: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_agent_action: bool = False
