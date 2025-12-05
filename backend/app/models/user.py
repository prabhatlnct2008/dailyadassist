"""User and preferences models."""
from datetime import datetime
from ..extensions import db


class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    profile_picture_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Active workspace
    active_workspace_id = db.Column(db.String(36), db.ForeignKey('workspaces.id', use_alter=True, name='fk_user_active_workspace'), nullable=True)

    # Relationships
    preferences = db.relationship('UserPreferences', backref='user', uselist=False, cascade='all, delete-orphan')
    facebook_connection = db.relationship('FacebookConnection', backref='user', uselist=False, cascade='all, delete-orphan')
    ad_accounts = db.relationship('AdAccount', backref='user', cascade='all, delete-orphan')
    facebook_pages = db.relationship('FacebookPage', backref='user', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='user', cascade='all, delete-orphan')
    drafts = db.relationship('AdDraft', backref='user', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', cascade='all, delete-orphan')
    past_winners = db.relationship('PastWinner', backref='user', cascade='all, delete-orphan')
    workspaces = db.relationship('Workspace', backref='user', foreign_keys='Workspace.user_id', cascade='all, delete-orphan')
    active_workspace = db.relationship('Workspace', foreign_keys=[active_workspace_id], post_update=True)

    def __repr__(self):
        return f'<User {self.email}>'


class UserPreferences(db.Model):
    """User preferences for agent behavior."""
    __tablename__ = 'user_preferences'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    default_daily_budget = db.Column(db.Float, default=50.0)
    default_currency = db.Column(db.String(10), default='USD')
    default_geo = db.Column(db.String(100), default='US')
    default_tone = db.Column(db.String(50), default='friendly')  # friendly, professional, bold, casual
    default_objective = db.Column(db.String(50), default='conversions')  # conversions, traffic, engagement, awareness
    timezone = db.Column(db.String(100), default='UTC')
    onboarding_completed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserPreferences for user {self.user_id}>'
