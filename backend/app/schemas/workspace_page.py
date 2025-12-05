"""Workspace page schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from .user import FacebookPageResponse


class PageSettingsUpdate(BaseModel):
    """Schema for updating page settings."""
    default_tone: Optional[str] = Field(None, max_length=50)
    default_cta_style: Optional[str] = Field(None, max_length=50)
    target_markets: Optional[List[str]] = None
    is_included: Optional[bool] = None


class WorkspacePageResponse(BaseModel):
    """Response schema for workspace page."""
    id: str
    workspace_id: str
    facebook_page_id: str
    facebook_page: FacebookPageResponse
    default_tone: str
    default_cta_style: Optional[str] = None
    target_markets: List[str] = []
    is_included: bool
    is_primary: bool
    has_conversation: bool = False
    conversation_id: Optional[str] = None

    class Config:
        from_attributes = True


class PageSetupItem(BaseModel):
    """Schema for individual page setup item."""
    facebook_page_id: str
    is_included: bool = True
    default_tone: Optional[str] = 'friendly'


class PageSetupRequest(BaseModel):
    """Schema for setting up pages during workspace creation."""
    pages: List[PageSetupItem]
