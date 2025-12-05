"""Agent API endpoints."""
from flask import Blueprint, jsonify, request, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
import json

from ..extensions import db
from ..models.conversation import Conversation, Message, ConversationType
from ..models.user import UserPreferences
from ..models.facebook import AdAccount
from ..models.workspace import Workspace, WorkspacePage
from ..services.agent_service import AgentService
from ..schemas.agent import ChatRequest, DailyBriefResponse

bp = Blueprint('agent', __name__)


@bp.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """Send a message to the agent and get a streaming response."""
    user_id = get_jwt_identity()
    data = request.get_json()

    conversation_id = data.get('conversation_id')
    message_content = data.get('message', '')

    # NEW: Page-based chat context
    workspace_id = data.get('workspace_id')
    page_id = data.get('page_id')  # workspace_page_id
    product_id = data.get('product_id')

    # Get or create conversation
    if conversation_id:
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
    else:
        # Create new conversation with workspace/page context
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            workspace_id=workspace_id,
            workspace_page_id=page_id,
            chat_type=ConversationType.PAGE_WAR_ROOM if page_id else ConversationType.ACCOUNT_OVERVIEW if workspace_id else ConversationType.LEGACY,
            state='idle',
            context={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(conversation)
        db.session.commit()

    # Store user message
    user_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation.id,
        role='user',
        content=message_content,
        created_at=datetime.utcnow()
    )
    db.session.add(user_message)
    db.session.commit()

    # Get user context
    from ..models.facebook import FacebookConnection

    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    primary_account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
    facebook_connection = FacebookConnection.query.filter_by(user_id=user_id).first()

    # Initialize agent service with full context (including page context)
    agent_service = AgentService(
        user_id=user_id,
        conversation=conversation,
        preferences=preferences,
        ad_account=primary_account,
        facebook_connection=facebook_connection,
        workspace_id=workspace_id or (conversation.workspace_id if conversation else None),
        page_id=page_id or (conversation.workspace_page_id if conversation else None),
        product_id=product_id
    )

    def generate():
        """Generate streaming response."""
        full_response = ""

        try:
            for chunk in agent_service.chat(message_content):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"

            # Store assistant message
            assistant_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                role='assistant',
                content=full_response,
                created_at=datetime.utcnow()
            )
            db.session.add(assistant_message)
            conversation.updated_at = datetime.utcnow()
            db.session.commit()

            yield f"data: {json.dumps({'content': '', 'done': True, 'conversation_id': conversation.id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@bp.route('/daily-brief', methods=['GET'])
@bp.route('/daily-brief/<workspace_id>', methods=['GET'])
@jwt_required()
def get_daily_brief(workspace_id=None):
    """Get the proactive daily brief from the agent.

    Args:
        workspace_id: Optional workspace ID for workspace-scoped brief
    """
    user_id = get_jwt_identity()

    # If no workspace_id provided, try to get user's active workspace
    if not workspace_id:
        from ..models.user import User
        user = User.query.get(user_id)
        if user and hasattr(user, 'active_workspace_id') and user.active_workspace_id:
            workspace_id = user.active_workspace_id
        else:
            # Fall back to first workspace
            workspace = Workspace.query.filter_by(user_id=user_id, is_active=True).first()
            if workspace:
                workspace_id = workspace.id

    # Get user context
    from ..models.facebook import FacebookConnection

    preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    primary_account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
    facebook_connection = FacebookConnection.query.filter_by(user_id=user_id).first()

    if not primary_account:
        return jsonify({
            'message': "Welcome! I see you haven't connected a Facebook Ad Account yet. Would you like to set one up so I can start managing your ads?",
            'has_data': False,
            'recommendations': []
        })

    # Initialize agent service with full context (including workspace)
    agent_service = AgentService(
        user_id=user_id,
        conversation=None,
        preferences=preferences,
        ad_account=primary_account,
        facebook_connection=facebook_connection,
        workspace_id=workspace_id
    )

    try:
        if workspace_id:
            brief = agent_service.generate_workspace_daily_brief(workspace_id, user_id)
        else:
            brief = agent_service.generate_daily_brief()
        return jsonify(brief)
    except Exception as e:
        return jsonify({
            'message': f"Good morning! I had trouble fetching your performance data. Error: {str(e)}",
            'has_data': False,
            'recommendations': []
        })


@bp.route('/generate-copy', methods=['POST'])
@jwt_required()
def generate_copy():
    """Generate ad copy variants."""
    user_id = get_jwt_identity()
    data = request.get_json()

    preferences = UserPreferences.query.filter_by(user_id=user_id).first()

    agent_service = AgentService(
        user_id=user_id,
        conversation=None,
        preferences=preferences,
        ad_account=None
    )

    try:
        variants = agent_service.generate_ad_copy(
            product_info=data.get('product_info', ''),
            tone=data.get('tone', preferences.default_tone if preferences else 'friendly'),
            num_variants=data.get('num_variants', 3)
        )
        return jsonify({'variants': variants})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/analyze-performance', methods=['POST'])
@jwt_required()
def analyze_performance():
    """Analyze account performance."""
    user_id = get_jwt_identity()
    data = request.get_json()

    primary_account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()

    if not primary_account:
        return jsonify({'error': 'No ad account connected'}), 400

    agent_service = AgentService(
        user_id=user_id,
        conversation=None,
        preferences=None,
        ad_account=primary_account
    )

    try:
        analysis = agent_service.analyze_performance(
            time_range=data.get('time_range', 'last_7_days')
        )
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
