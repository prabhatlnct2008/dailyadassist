"""Product schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductCreate(BaseModel):
    """Schema for creating a product."""
    name: str = Field(..., min_length=1, max_length=255)
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    price_range_min: Optional[float] = Field(None, gt=0)
    price_range_max: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field('INR', max_length=10)
    usp: Optional[str] = None
    target_audience: Optional[str] = None
    seasonality: Optional[str] = Field(None, max_length=100)
    primary_image_url: Optional[str] = Field(None, max_length=500)
    image_url_2: Optional[str] = Field(None, max_length=500)
    image_url_3: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = []


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    price_range_min: Optional[float] = Field(None, gt=0)
    price_range_max: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=10)
    usp: Optional[str] = None
    target_audience: Optional[str] = None
    seasonality: Optional[str] = Field(None, max_length=100)
    primary_image_url: Optional[str] = Field(None, max_length=500)
    image_url_2: Optional[str] = Field(None, max_length=500)
    image_url_3: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Response schema for product."""
    id: str
    workspace_id: str
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price: Optional[float] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    currency: str
    usp: Optional[str] = None
    target_audience: Optional[str] = None
    seasonality: Optional[str] = None
    primary_image_url: Optional[str] = None
    image_url_2: Optional[str] = None
    image_url_3: Optional[str] = None
    tags: List[str] = []
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PageTagRequest(BaseModel):
    """Schema for tagging products to pages."""
    page_ids: List[str]
    set_default_for: Optional[str] = None  # page_id to set as default
