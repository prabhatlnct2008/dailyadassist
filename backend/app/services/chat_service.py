"""Chat service for managing conversations and chats."""
from datetime import datetime
from uuid import uuid4
from typing import Optional

from ..extensions import db
from ..models.conversation import Conversation, ConversationType
from ..models.workspace import Workspace, WorkspacePage


class ChatService:
    """Service for managing chat conversations."""

    @staticmethod
    def get_or_create_overview_chat(workspace_id: str, user_id: str) -> Conversation:
        """
        Get or create the Account Overview chat for a workspace.

        Args:
            workspace_id: The workspace ID
            user_id: The user ID

        Returns:
            The Account Overview conversation

        Raises:
            ValueError: If workspace not found or doesn't belong to user
        """
        # Verify workspace exists and belongs to user
        workspace = Workspace.query.filter_by(
            id=workspace_id,
            user_id=user_id
        ).first()

        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found or access denied")

        # Check if overview chat already exists
        overview_chat = Conversation.query.filter_by(
            workspace_id=workspace_id,
            chat_type=ConversationType.ACCOUNT_OVERVIEW
        ).first()

        if overview_chat:
            return overview_chat

        # Create new overview chat
        overview_chat = Conversation(
            id=str(uuid4()),
            user_id=user_id,
            workspace_id=workspace_id,
            chat_type=ConversationType.ACCOUNT_OVERVIEW,
            title=f"{workspace.name} - Account Overview",
            state='idle',
            context={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(overview_chat)
        db.session.commit()

        return overview_chat

    @staticmethod
    def get_or_create_page_chat(
        workspace_page_id: str,
        user_id: str,
        workspace_id: str
    ) -> Conversation:
        """
        Get or create a Page War Room chat for a workspace page.

        Args:
            workspace_page_id: The workspace page ID
            user_id: The user ID
            workspace_id: The workspace ID

        Returns:
            The Page War Room conversation

        Raises:
            ValueError: If workspace page not found or doesn't belong to user's workspace
        """
        # Verify workspace page exists and belongs to workspace
        workspace_page = WorkspacePage.query.filter_by(
            id=workspace_page_id,
            workspace_id=workspace_id
        ).first()

        if not workspace_page:
            raise ValueError(f"Workspace page {workspace_page_id} not found or access denied")

        # Verify workspace belongs to user
        workspace = Workspace.query.filter_by(
            id=workspace_id,
            user_id=user_id
        ).first()

        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found or access denied")

        # Check if page chat already exists
        page_chat = Conversation.query.filter_by(
            workspace_page_id=workspace_page_id,
            chat_type=ConversationType.PAGE_WAR_ROOM
        ).first()

        if page_chat:
            return page_chat

        # Get Facebook page name for title
        from ..models.facebook import FacebookPage
        facebook_page = FacebookPage.query.get(workspace_page.facebook_page_id)
        page_name = facebook_page.name if facebook_page else "Page"

        # Create new page chat
        page_chat = Conversation(
            id=str(uuid4()),
            user_id=user_id,
            workspace_id=workspace_id,
            workspace_page_id=workspace_page_id,
            chat_type=ConversationType.PAGE_WAR_ROOM,
            title=f"{page_name} War Room",
            state='idle',
            context={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(page_chat)
        db.session.commit()

        return page_chat

    @staticmethod
    def create_workspace_chats(workspace: Workspace) -> None:
        """
        Auto-create required chats for a workspace.
        Called when a workspace completes setup.

        Args:
            workspace: The workspace object
        """
        # 1. Create Account Overview chat
        overview_chat = Conversation.query.filter_by(
            workspace_id=workspace.id,
            chat_type=ConversationType.ACCOUNT_OVERVIEW
        ).first()

        if not overview_chat:
            overview_chat = Conversation(
                id=str(uuid4()),
                user_id=workspace.user_id,
                workspace_id=workspace.id,
                chat_type=ConversationType.ACCOUNT_OVERVIEW,
                title=f"{workspace.name} - Account Overview",
                state='idle',
                context={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(overview_chat)

        # 2. Create Page War Room for each included page
        from ..models.facebook import FacebookPage

        for workspace_page in workspace.pages:
            if workspace_page.is_included:
                # Check if chat already exists
                existing_chat = Conversation.query.filter_by(
                    workspace_page_id=workspace_page.id,
                    chat_type=ConversationType.PAGE_WAR_ROOM
                ).first()

                if not existing_chat:
                    facebook_page = FacebookPage.query.get(workspace_page.facebook_page_id)
                    page_name = facebook_page.name if facebook_page else "Page"

                    page_chat = Conversation(
                        id=str(uuid4()),
                        user_id=workspace.user_id,
                        workspace_id=workspace.id,
                        workspace_page_id=workspace_page.id,
                        chat_type=ConversationType.PAGE_WAR_ROOM,
                        title=f"{page_name} War Room",
                        state='idle',
                        context={},
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(page_chat)

        db.session.commit()

    @staticmethod
    def archive_conversation(conversation_id: str, user_id: str) -> Conversation:
        """
        Archive a conversation.

        Args:
            conversation_id: The conversation ID to archive
            user_id: The user ID (for authorization)

        Returns:
            The archived conversation

        Raises:
            ValueError: If conversation not found or doesn't belong to user
        """
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found or access denied")

        # Mark as archived
        conversation.is_archived = True
        conversation.archived_at = datetime.utcnow()

        db.session.commit()

        return conversation


# Create singleton instance
chat_service = ChatService()
