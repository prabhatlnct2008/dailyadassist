"""Migration service for handling legacy conversations."""
from datetime import datetime
import json
from typing import Dict, List, Optional

from ..extensions import db
from ..models.conversation import Conversation, ConversationType, Message
from ..models.workspace import Workspace
from .chat_service import chat_service


class MigrationService:
    """Service for migrating legacy conversations."""

    @staticmethod
    def migrate_legacy_conversations(user_id: str, workspace_id: str) -> dict:
        """
        Migrate legacy conversations for a user when they create a workspace.

        Migration steps:
        1. Find all conversations without workspace_id for this user
        2. Mark as chat_type = LEGACY
        3. Set is_archived = True
        4. Generate AI summary for each
        5. Pin summary in Account Overview

        Args:
            user_id: The user ID
            workspace_id: The workspace ID to associate legacy summaries with

        Returns:
            Dictionary with migration summary
        """
        # Verify workspace exists and belongs to user
        workspace = Workspace.query.filter_by(
            id=workspace_id,
            user_id=user_id
        ).first()

        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found or access denied")

        # Find all conversations without workspace_id for this user
        # that aren't already marked as legacy
        legacy_convos = Conversation.query.filter(
            Conversation.user_id == user_id,
            Conversation.workspace_id.is_(None),
            Conversation.chat_type != ConversationType.LEGACY
        ).all()

        if not legacy_convos:
            return {
                'migrated_count': 0,
                'message': 'No legacy conversations to migrate'
            }

        summaries = []
        migrated_count = 0

        for convo in legacy_convos:
            # Archive the conversation
            convo.chat_type = ConversationType.LEGACY
            convo.is_archived = True
            convo.archived_at = datetime.utcnow()

            # Generate summary
            summary = MigrationService.generate_conversation_summary(convo)
            convo.archive_summary = summary

            summaries.append({
                'id': convo.id,
                'title': convo.title or 'Untitled Conversation',
                'summary': summary,
                'message_count': len(convo.messages),
                'created_at': convo.created_at.isoformat() if convo.created_at else None,
                'last_updated': convo.updated_at.isoformat() if convo.updated_at else None
            })
            migrated_count += 1

        db.session.commit()

        # Get or create Account Overview chat
        overview_chat = chat_service.get_or_create_overview_chat(workspace_id, user_id)

        # Create pinned content
        pinned_data = {
            'type': 'legacy_archive',
            'message': f'Archived {migrated_count} previous conversation{"s" if migrated_count != 1 else ""}',
            'migrated_at': datetime.utcnow().isoformat(),
            'conversations': summaries
        }

        overview_chat.is_pinned = True
        overview_chat.pinned_content = json.dumps(pinned_data)

        db.session.commit()

        return {
            'migrated_count': migrated_count,
            'message': f'Successfully migrated {migrated_count} conversation{"s" if migrated_count != 1 else ""}',
            'summaries': summaries
        }

    @staticmethod
    def generate_conversation_summary(conversation: Conversation) -> str:
        """
        Generate a simple summary for a conversation.

        Args:
            conversation: The conversation to summarize

        Returns:
            A text summary of the conversation
        """
        messages = Message.query.filter_by(
            conversation_id=conversation.id,
            is_visible=True
        ).order_by(Message.created_at.asc()).all()

        if not messages:
            return "Empty conversation with no messages"

        message_count = len(messages)
        user_messages = [m for m in messages if m.role == 'user']
        assistant_messages = [m for m in messages if m.role == 'assistant']

        # Get date range
        first_message_date = messages[0].created_at.strftime('%Y-%m-%d') if messages[0].created_at else 'Unknown'
        last_message_date = messages[-1].created_at.strftime('%Y-%m-%d') if messages[-1].created_at else 'Unknown'

        # Try to extract topics from first few user messages
        topics = []
        for msg in user_messages[:3]:
            # Extract first few words as topic hint
            words = msg.content.strip().split()[:10]
            if words:
                topic_hint = ' '.join(words)
                if len(msg.content) > 50:
                    topic_hint += '...'
                topics.append(topic_hint)

        # Build summary
        summary_parts = [
            f"Total messages: {message_count} ({len(user_messages)} from you, {len(assistant_messages)} from assistant)",
            f"Date range: {first_message_date} to {last_message_date}"
        ]

        if topics:
            summary_parts.append(f"Topics discussed: {'; '.join(topics)}")

        # Check for any drafts
        if conversation.drafts:
            summary_parts.append(f"Generated {len(conversation.drafts)} ad draft(s)")

        return '. '.join(summary_parts)


# Create singleton instance
migration_service = MigrationService()
