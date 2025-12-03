"""Conversation API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from ..extensions import db
from ..models.conversation import Conversation, Message
from ..schemas.conversation import (
    ConversationResponse,
    ConversationWithMessages,
    MessageResponse,
    CreateConversation,
    MessageCreate
)

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
