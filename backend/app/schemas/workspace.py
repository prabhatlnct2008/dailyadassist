"""Workspace schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WorkspaceCreate(BaseModel):
    """Schema for creating a workspace."""
    name: str = Field(..., min_length=1, max_length=255)
    default_daily_budget: Optional[float] = Field(500.0, gt=0)
    default_currency: Optional[str] = Field('INR', max_length=10)
    timezone: Optional[str] = Field('Asia/Kolkata', max_length=50)


class WorkspaceUpdate(BaseModel):
    """Schema for updating a workspace."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    default_daily_budget: Optional[float] = Field(None, gt=0)
    default_currency: Optional[str] = Field(None, max_length=10)
    default_objective: Optional[str] = Field(None, max_length=50)
    timezone: Optional[str] = Field(None, max_length=50)


class WorkspaceResponse(BaseModel):
    """Response schema for workspace."""
    id: str
    name: str
    facebook_connected: bool
    setup_completed: bool
    ad_account_id: Optional[str] = None
    default_daily_budget: float
    default_currency: str
    default_objective: str
    timezone: str
    created_at: datetime

    class Config:
        from_attributes = True


class WorkspaceDetailResponse(WorkspaceResponse):
    """Detailed response schema for workspace with related data."""
    pages: List['WorkspacePageResponse'] = []
    products: List['ProductResponse'] = []
    ad_account: Optional['AdAccountResponse'] = None

    class Config:
        from_attributes = True


# Forward references will be resolved when other schemas are imported
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .workspace_page import WorkspacePageResponse
    from .product import ProductResponse
    from .user import AdAccountResponse
