"""Workspace and workspace page models."""
from datetime import datetime
from uuid import uuid4
from ..extensions import db


class Workspace(db.Model):
    """Workspace model representing a business workspace linked to one Facebook Ad Account."""
    __tablename__ = 'workspaces'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    # Facebook connection (1 ad account per workspace)
    ad_account_id = db.Column(db.String(36), db.ForeignKey('ad_accounts.id'), nullable=True)

    # Defaults
    default_daily_budget = db.Column(db.Float, default=500.0)
    default_currency = db.Column(db.String(10), default='INR')
    default_objective = db.Column(db.String(50), default='CONVERSIONS')
    timezone = db.Column(db.String(50), default='Asia/Kolkata')

    # Status
    is_active = db.Column(db.Boolean, default=True)
    facebook_connected = db.Column(db.Boolean, default=False)
    setup_completed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', backref='workspace', cascade='all, delete-orphan')
    pages = db.relationship('WorkspacePage', backref='workspace', cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='workspace', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Workspace {self.name}>'


class WorkspacePage(db.Model):
    """Links FacebookPage to Workspace with page-specific settings."""
    __tablename__ = 'workspace_pages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False)
    facebook_page_id = db.Column(db.String(36), db.ForeignKey('facebook_pages.id', ondelete='CASCADE'), nullable=False)

    # Page-specific settings
    default_tone = db.Column(db.String(50), default='friendly')
    default_cta_style = db.Column(db.String(50), nullable=True)
    target_markets = db.Column(db.JSON, default=list)

    # Status
    is_included = db.Column(db.Boolean, default=True)
    is_primary = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversation = db.relationship('Conversation', backref='workspace_page', uselist=False)
    page_products = db.relationship('PageProduct', backref='workspace_page', cascade='all, delete-orphan')

    # Unique constraint: one page per workspace
    __table_args__ = (
        db.UniqueConstraint('workspace_id', 'facebook_page_id', name='uq_workspace_page'),
    )

    def __repr__(self):
        return f'<WorkspacePage workspace={self.workspace_id[:8]} page={self.facebook_page_id[:8]}>'
