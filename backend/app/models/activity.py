"""Activity log and past winners models."""
from datetime import datetime
from ..extensions import db


class ActivityLog(db.Model):
    """Log of agent and user actions."""
    __tablename__ = 'activity_logs'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    action_type = db.Column(db.String(50), nullable=False)
    # Types: draft_created, draft_updated, campaign_published, budget_changed,
    #        campaign_paused, recommendation_made, recommendation_applied

    entity_type = db.Column(db.String(50), nullable=True)  # campaign, adset, ad, draft
    entity_id = db.Column(db.String(100), nullable=True)
    rationale = db.Column(db.Text, nullable=True)
    extra_data = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_agent_action = db.Column(db.Boolean, default=False)

    # Valid action types
    VALID_ACTION_TYPES = [
        'draft_created',
        'draft_updated',
        'campaign_published',
        'budget_changed',
        'campaign_paused',
        'recommendation_made',
        'recommendation_applied',
        'copy_generated',
        'brief_generated'
    ]

    def __repr__(self):
        return f'<ActivityLog {self.action_type} on {self.entity_type}>'


class PastWinner(db.Model):
    """Record of past winning ads for learning."""
    __tablename__ = 'past_winners'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    campaign_name = db.Column(db.String(255), nullable=False)
    ad_content = db.Column(db.JSON, nullable=False)  # Full ad details
    metrics = db.Column(db.JSON, nullable=False)  # spend, roas, ctr, etc.
    winning_factors = db.Column(db.Text, nullable=True)  # Agent analysis

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PastWinner {self.campaign_name}>'
