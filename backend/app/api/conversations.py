"""Conversation API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from ..extensions import db
from ..models.conversation import Conversation, Message, ConversationType
from ..models.workspace import WorkspacePage
from ..schemas.conversation import (
    ConversationResponse,
    ConversationWithMessages,
    MessageResponse,
    CreateConversation,
    MessageCreate
)
from ..services.chat_service import chat_service

bp = Blueprint('conversations', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def list_conversations():
    """List user's conversations."""
    user_id = get_jwt_identity()

    conversations = Conversation.query.filter_by(user_id=user_id)\
        .order_by(Conversation.updated_at.desc())\
        .all()

    return jsonify([
        ConversationResponse.model_validate(conv).model_dump()
        for conv in conversations
    ])


@bp.route('/', methods=['POST'])
@jwt_required()
def create_conversation():
    """Create a new conversation."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=data.get('title'),
        state='idle',
        context={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(conversation)
    db.session.commit()

    return jsonify(ConversationResponse.model_validate(conversation).model_dump()), 201


@bp.route('/<conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """Get a conversation with its messages."""
    user_id = get_jwt_identity()

    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=user_id
    ).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    messages = Message.query.filter_by(
        conversation_id=conversation_id,
        is_visible=True
    ).order_by(Message.created_at.asc()).all()

    response = ConversationWithMessages.model_validate({
        **conversation.__dict__,
        'messages': [m.__dict__ for m in messages]
    })

    return jsonify(response.model_dump())


@bp.route('/<conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    """Get conversation messages with pagination."""
    user_id = get_jwt_identity()

    # Verify conversation belongs to user
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=user_id
    ).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    messages = Message.query.filter_by(
        conversation_id=conversation_id,
        is_visible=True
    ).order_by(Message.created_at.asc())\
        .paginate(page=page, per_page=per_page)

    return jsonify({
        'messages': [
            MessageResponse.model_validate(m).model_dump()
            for m in messages.items
        ],
        'total': messages.total,
        'page': page,
        'per_page': per_page,
        'pages': messages.pages
    })


@bp.route('/<conversation_id>/messages', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    """Send a message in a conversation."""
    user_id = get_jwt_identity()
    data = request.get_json()

    # Verify conversation belongs to user
    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=user_id
    ).first()

    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    # Create user message
    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role='user',
        content=data.get('content', ''),
        metadata=data.get('metadata'),
        created_at=datetime.utcnow()
    )
    db.session.add(message)

    # Update conversation
    conversation.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(MessageResponse.model_validate(message).model_dump()), 201


# NEW ENDPOINTS FOR PHASE 5

@bp.route('/workspace/<workspace_id>', methods=['GET'])
@jwt_required()
def get_workspace_conversations(workspace_id):
    """Get all chats for a workspace (Account Overview + Page War Rooms)."""
    user_id = get_jwt_identity()

    # Get all conversations for this workspace
    conversations = Conversation.query.filter_by(
        workspace_id=workspace_id,
        user_id=user_id,
        is_archived=False
    ).order_by(
        # Account Overview first, then by updated_at
        Conversation.chat_type.desc(),
        Conversation.updated_at.desc()
    ).all()

    return jsonify({
        'conversations': [
            ConversationResponse.model_validate(conv).model_dump()
            for conv in conversations
        ],
        'count': len(conversations)
    })


@bp.route('/workspace/<workspace_id>/overview', methods=['GET'])
@jwt_required()
def get_workspace_overview_chat(workspace_id):
    """Get or create the Account Overview chat for a workspace."""
    user_id = get_jwt_identity()

    try:
        overview_chat = chat_service.get_or_create_overview_chat(workspace_id, user_id)

        # Get messages for this conversation
        messages = Message.query.filter_by(
            conversation_id=overview_chat.id,
            is_visible=True
        ).order_by(Message.created_at.asc()).all()

        response = ConversationWithMessages.model_validate({
            **overview_chat.__dict__,
            'messages': [m.__dict__ for m in messages]
        })

        return jsonify(response.model_dump())

    except ValueError as e:
        return jsonify({'error': str(e)}), 403


@bp.route('/page/<page_id>', methods=['GET'])
@jwt_required()
def get_page_chat(page_id):
    """Get or create the Page War Room chat for a workspace page."""
    user_id = get_jwt_identity()

    # Get workspace page to verify access and get workspace_id
    workspace_page = WorkspacePage.query.get(page_id)

    if not workspace_page:
        return jsonify({'error': 'Page not found'}), 404

    # Verify workspace belongs to user
    from ..models.workspace import Workspace
    workspace = Workspace.query.filter_by(
        id=workspace_page.workspace_id,
        user_id=user_id
    ).first()

    if not workspace:
        return jsonify({'error': 'Access denied'}), 403

    try:
        page_chat = chat_service.get_or_create_page_chat(
            workspace_page_id=page_id,
            user_id=user_id,
            workspace_id=workspace_page.workspace_id
        )

        # Get messages for this conversation
        messages = Message.query.filter_by(
            conversation_id=page_chat.id,
            is_visible=True
        ).order_by(Message.created_at.asc()).all()

        response = ConversationWithMessages.model_validate({
            **page_chat.__dict__,
            'messages': [m.__dict__ for m in messages]
        })

        return jsonify(response.model_dump())

    except ValueError as e:
        return jsonify({'error': str(e)}), 403


@bp.route('/legacy', methods=['GET'])
@jwt_required()
def get_legacy_conversations():
    """Get archived legacy chats for the user."""
    user_id = get_jwt_identity()

    legacy_convos = Conversation.query.filter_by(
        user_id=user_id,
        chat_type=ConversationType.LEGACY,
        is_archived=True
    ).order_by(Conversation.archived_at.desc()).all()

    return jsonify({
        'conversations': [
            {
                **ConversationResponse.model_validate(conv).model_dump(),
                'archive_summary': conv.archive_summary,
                'archived_at': conv.archived_at.isoformat() if conv.archived_at else None
            }
            for conv in legacy_convos
        ],
        'count': len(legacy_convos)
    })


@bp.route('/<conversation_id>/archive', methods=['POST'])
@jwt_required()
def archive_conversation(conversation_id):
    """Archive a conversation."""
    user_id = get_jwt_identity()

    try:
        conversation = chat_service.archive_conversation(conversation_id, user_id)

        return jsonify({
            **ConversationResponse.model_validate(conversation).model_dump(),
            'is_archived': conversation.is_archived,
            'archived_at': conversation.archived_at.isoformat() if conversation.archived_at else None
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
