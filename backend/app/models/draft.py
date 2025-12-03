"""Ad draft and published campaign models."""
from datetime import datetime
from ..extensions import db


class AdDraft(db.Model):
    """Ad draft created during conversation."""
    __tablename__ = 'ad_drafts'

    id = db.Column(db.String(36), primary_key=True)
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Campaign structure
    campaign_name = db.Column(db.String(255), nullable=True)
    ad_set_name = db.Column(db.String(255), nullable=True)
    ad_name = db.Column(db.String(255), nullable=True)

    # Ad creative
    primary_text = db.Column(db.Text, nullable=True)
    headline = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    cta = db.Column(db.String(50), default='learn_more')  # learn_more, shop_now, sign_up, contact_us, book_now

    # Media
    media_url = db.Column(db.String(500), nullable=True)
    media_type = db.Column(db.String(20), default='image')  # image, video

    # Targeting
    target_audience = db.Column(db.JSON, nullable=True)

    # Budget
    budget = db.Column(db.Float, nullable=True)
    budget_type = db.Column(db.String(20), default='daily')  # daily, lifetime
    objective = db.Column(db.String(50), default='CONVERSIONS')

    # Status
    status = db.Column(db.String(20), default='draft')  # draft, approved, published, rejected

    # Versioning
    variant_number = db.Column(db.Integer, default=1)
    parent_draft_id = db.Column(db.String(36), db.ForeignKey('ad_drafts.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    variants = db.relationship('AdDraft', backref=db.backref('parent', remote_side=[id]))
    published_campaign = db.relationship('PublishedCampaign', backref='draft', uselist=False)

    # Valid CTAs
    VALID_CTAS = ['learn_more', 'shop_now', 'sign_up', 'contact_us', 'book_now', 'download', 'get_offer']

    # Valid statuses
    VALID_STATUSES = ['draft', 'approved', 'published', 'rejected']

    def to_preview_dict(self):
        """Convert to dictionary for UI preview."""
        return {
            'campaign_name': self.campaign_name,
            'ad_set_name': self.ad_set_name,
            'ad_name': self.ad_name,
            'primary_text': self.primary_text,
            'headline': self.headline,
            'description': self.description,
            'cta': self.cta,
            'media_url': self.media_url,
            'media_type': self.media_type,
            'budget': self.budget,
            'objective': self.objective,
            'variant_number': self.variant_number
        }

    def __repr__(self):
        return f'<AdDraft {self.ad_name or self.id[:8]}... v{self.variant_number}>'


class PublishedCampaign(db.Model):
    """Published campaign on Facebook."""
    __tablename__ = 'published_campaigns'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    ad_draft_id = db.Column(db.String(36), db.ForeignKey('ad_drafts.id'), nullable=False)

    # Facebook IDs
    facebook_campaign_id = db.Column(db.String(100), nullable=False)
    facebook_adset_id = db.Column(db.String(100), nullable=True)
    facebook_ad_id = db.Column(db.String(100), nullable=True)
    ads_manager_url = db.Column(db.String(500), nullable=True)

    # Status
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, paused, deleted

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    performance_snapshots = db.relationship('PerformanceSnapshot', backref='campaign', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PublishedCampaign {self.facebook_campaign_id}>'


class PerformanceSnapshot(db.Model):
    """Daily performance snapshot for a campaign."""
    __tablename__ = 'performance_snapshots'

    id = db.Column(db.String(36), primary_key=True)
    published_campaign_id = db.Column(db.String(36), db.ForeignKey('published_campaigns.id', ondelete='CASCADE'), nullable=False)

    date = db.Column(db.Date, nullable=False)
    spend = db.Column(db.Float, default=0.0)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    ctr = db.Column(db.Float, default=0.0)
    cpc = db.Column(db.Float, default=0.0)
    conversions = db.Column(db.Integer, default=0)
    roas = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PerformanceSnapshot {self.date} spend={self.spend}>'
