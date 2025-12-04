"""Authentication schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: str
    email: EmailStr
    name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime
    last_login_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response schema for JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class GoogleAuthCallback(BaseModel):
    """Schema for Google OAuth callback data."""
    code: str
    state: Optional[str] = None


class FacebookAuthCallback(BaseModel):
    """Schema for Facebook OAuth callback data."""
    code: str
    state: Optional[str] = None
