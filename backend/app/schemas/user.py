"""User and preferences schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ToneEnum(str, Enum):
    friendly = "friendly"
    professional = "professional"
    bold = "bold"
    casual = "casual"


class ObjectiveEnum(str, Enum):
    conversions = "conversions"
    traffic = "traffic"
    engagement = "engagement"
    awareness = "awareness"


class PreferencesResponse(BaseModel):
    """Response schema for user preferences."""
    id: str
    user_id: str
    default_daily_budget: float = 50.0
    default_currency: str = "USD"
    default_geo: str = "US"
    default_tone: str = "friendly"
    default_objective: str = "conversions"
    timezone: str = "UTC"
    onboarding_completed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    default_daily_budget: Optional[float] = Field(None, gt=0)
    default_currency: Optional[str] = Field(None, max_length=10)
    default_geo: Optional[str] = Field(None, max_length=100)
    default_tone: Optional[ToneEnum] = None
    default_objective: Optional[ObjectiveEnum] = None
    timezone: Optional[str] = Field(None, max_length=100)
    onboarding_completed: Optional[bool] = None


class AdAccountResponse(BaseModel):
    """Response schema for ad account."""
    id: str
    user_id: str
    facebook_account_id: str
    name: Optional[str] = None
    currency: str = "USD"
    timezone: str = "UTC"
    is_primary: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class FacebookPageResponse(BaseModel):
    """Response schema for Facebook page."""
    id: str
    user_id: str
    facebook_page_id: str
    name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    is_primary: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
