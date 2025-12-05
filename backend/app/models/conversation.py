"""Conversation and message models."""
from datetime import datetime
from enum import Enum
from ..extensions import db


class ConversationType(str, Enum):
    """Types of conversations in the system."""
    ACCOUNT_OVERVIEW = 'account_overview'
    PAGE_WAR_ROOM = 'page_war_room'
    LEGACY = 'legacy'


class Conversation(db.Model):
    """Chat conversation with the agent."""
    __tablename__ = 'conversations'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Workspace and Page linkage
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=True)
    workspace_page_id = db.Column(db.String(36), db.ForeignKey('workspace_pages.id', ondelete='CASCADE'), nullable=True)

    # Chat type
    chat_type = db.Column(db.Enum(ConversationType), default=ConversationType.LEGACY)

    title = db.Column(db.String(255), nullable=True)
    state = db.Column(db.String(50), default='idle')  # idle, discovery, ideation, drafting, review, ready_to_publish, published
    context = db.Column(db.JSON, default=dict)  # Stores current campaign context

    # For legacy migration
    is_archived = db.Column(db.Boolean, default=False)
    archived_at = db.Column(db.DateTime, nullable=True)
    archive_summary = db.Column(db.Text, nullable=True)

    # Pinned status (for Account Overview pinned summaries)
    is_pinned = db.Column(db.Boolean, default=False)
    pinned_content = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = db.relationship('Message', backref='conversation', cascade='all, delete-orphan', order_by='Message.created_at')
    drafts = db.relationship('AdDraft', backref='conversation', cascade='all, delete-orphan')

    # Valid states
    VALID_STATES = ['idle', 'discovery', 'ideation', 'drafting', 'review', 'ready_to_publish', 'published']

    def set_state(self, new_state):
        """Set conversation state with validation."""
        if new_state not in self.VALID_STATES:
            raise ValueError(f"Invalid state: {new_state}")
        self.state = new_state

    def __repr__(self):
        return f'<Conversation {self.id[:8]}... type={self.chat_type} state={self.state}>'


class Message(db.Model):
    """Individual message in a conversation."""
    __tablename__ = 'messages'

    id = db.Column(db.String(36), primary_key=True)
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    extra_data = db.Column(db.JSON, nullable=True)  # Tool calls, attachments, etc.

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_visible = db.Column(db.Boolean, default=True)

    # Valid roles
    VALID_ROLES = ['user', 'assistant', 'system']

    def __repr__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f'<Message {self.role}: {preview}>'
