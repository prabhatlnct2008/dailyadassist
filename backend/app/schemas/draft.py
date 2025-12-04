"""Draft and campaign schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class CTAEnum(str, Enum):
    learn_more = "learn_more"
    shop_now = "shop_now"
    sign_up = "sign_up"
    contact_us = "contact_us"
    book_now = "book_now"
    download = "download"
    get_offer = "get_offer"


class DraftStatus(str, Enum):
    draft = "draft"
    approved = "approved"
    published = "published"
    rejected = "rejected"


class MediaType(str, Enum):
    image = "image"
    video = "video"


class BudgetType(str, Enum):
    daily = "daily"
    lifetime = "lifetime"


class DraftResponse(BaseModel):
    """Response schema for an ad draft."""
    id: str
    conversation_id: Optional[str] = None
    user_id: str
    campaign_name: Optional[str] = None
    ad_set_name: Optional[str] = None
    ad_name: Optional[str] = None
    primary_text: Optional[str] = None
    headline: Optional[str] = None
    description: Optional[str] = None
    cta: str = "learn_more"
    media_url: Optional[str] = None
    media_type: str = "image"
    target_audience: Optional[Dict[str, Any]] = None
    budget: Optional[float] = None
    budget_type: str = "daily"
    objective: str = "CONVERSIONS"
    status: str = "draft"
    variant_number: int = 1
    parent_draft_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DraftCreate(BaseModel):
    """Schema for creating a draft."""
    conversation_id: Optional[str] = None
    campaign_name: Optional[str] = Field(None, max_length=255)
    ad_set_name: Optional[str] = Field(None, max_length=255)
    ad_name: Optional[str] = Field(None, max_length=255)
    primary_text: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    cta: Optional[CTAEnum] = CTAEnum.learn_more
    media_url: Optional[str] = None
    media_type: Optional[MediaType] = MediaType.image
    target_audience: Optional[Dict[str, Any]] = None
    budget: Optional[float] = Field(None, gt=0)
    budget_type: Optional[BudgetType] = BudgetType.daily
    objective: Optional[str] = "CONVERSIONS"


class DraftUpdate(BaseModel):
    """Schema for updating a draft."""
    campaign_name: Optional[str] = Field(None, max_length=255)
    ad_set_name: Optional[str] = Field(None, max_length=255)
    ad_name: Optional[str] = Field(None, max_length=255)
    primary_text: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    cta: Optional[CTAEnum] = None
    media_url: Optional[str] = None
    media_type: Optional[MediaType] = None
    target_audience: Optional[Dict[str, Any]] = None
    budget: Optional[float] = Field(None, gt=0)
    budget_type: Optional[BudgetType] = None
    objective: Optional[str] = None
    status: Optional[DraftStatus] = None


class PublishedCampaignResponse(BaseModel):
    """Response schema for a published campaign."""
    id: str
    user_id: str
    ad_draft_id: str
    facebook_campaign_id: str
    facebook_adset_id: Optional[str] = None
    facebook_ad_id: Optional[str] = None
    ads_manager_url: Optional[str] = None
    published_at: datetime
    status: str = "active"
    created_at: datetime

    class Config:
        from_attributes = True
