"""Pydantic schemas package."""
from .auth import UserResponse, TokenResponse
from .user import PreferencesResponse, PreferencesUpdate, AdAccountResponse, FacebookPageResponse
from .conversation import (
    ConversationResponse,
    ConversationWithMessages,
    MessageResponse,
    CreateConversation,
    MessageCreate
)
from .draft import DraftResponse, DraftUpdate, DraftCreate, PublishedCampaignResponse
from .performance import PerformanceSummary, TopPerformer, CampaignMetrics
from .activity import ActivityLogResponse, RecommendationResponse
from .agent import ChatRequest, DailyBriefResponse, CopyVariant

__all__ = [
    'UserResponse',
    'TokenResponse',
    'PreferencesResponse',
    'PreferencesUpdate',
    'AdAccountResponse',
    'FacebookPageResponse',
    'ConversationResponse',
    'ConversationWithMessages',
    'MessageResponse',
    'CreateConversation',
    'MessageCreate',
    'DraftResponse',
    'DraftUpdate',
    'DraftCreate',
    'PublishedCampaignResponse',
    'PerformanceSummary',
    'TopPerformer',
    'CampaignMetrics',
    'ActivityLogResponse',
    'RecommendationResponse',
    'ChatRequest',
    'DailyBriefResponse',
    'CopyVariant'
]
