"""Conversation and message schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ConversationState(str, Enum):
    idle = "idle"
    discovery = "discovery"
    ideation = "ideation"
    drafting = "drafting"
    review = "review"
    ready_to_publish = "ready_to_publish"
    published = "published"


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class MessageResponse(BaseModel):
    """Response schema for a message."""
    id: str
    conversation_id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    is_visible: bool = True

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response schema for a conversation."""
    id: str
    user_id: str
    title: Optional[str] = None
    state: str = "idle"
    context: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Conversation with its messages."""
    messages: List[MessageResponse] = []


class CreateConversation(BaseModel):
    """Schema for creating a conversation."""
    title: Optional[str] = Field(None, max_length=255)


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None
