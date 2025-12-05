"""Workspace management API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from ..extensions import db
from ..models.workspace import Workspace, WorkspacePage
from ..models.conversation import Conversation, ConversationType
from ..models.facebook import FacebookPage
from ..models.user import User
from ..schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceDetailResponse
)
from ..schemas.workspace_page import (
    PageSetupRequest,
    PageSetupItem,
    WorkspacePageResponse
)

bp = Blueprint('workspaces', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def list_workspaces():
    """List all workspaces for the current user."""
    user_id = get_jwt_identity()
    workspaces = Workspace.query.filter_by(user_id=user_id).order_by(Workspace.created_at.desc()).all()

    return jsonify([
        WorkspaceResponse.model_validate(workspace).model_dump()
        for workspace in workspaces
    ]), 200


@bp.route('/', methods=['POST'])
@jwt_required()
def create_workspace():
    """Create a new workspace."""
    user_id = get_jwt_identity()
    data = request.get_json()

    try:
        # Validate input
        workspace_data = WorkspaceCreate(**data)
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400

    # Create workspace
    workspace = Workspace(
        id=str(uuid4()),
        user_id=user_id,
        name=workspace_data.name,
        default_daily_budget=workspace_data.default_daily_budget,
        default_currency=workspace_data.default_currency,
        timezone=workspace_data.timezone,
        created_at=datetime.utcnow()
    )

    db.session.add(workspace)
    db.session.commit()

    return jsonify(WorkspaceResponse.model_validate(workspace).model_dump()), 201


@bp.route('/<workspace_id>', methods=['GET'])
@jwt_required()
def get_workspace(workspace_id):
    """Get workspace detail with pages, products, and ad account."""
    user_id = get_jwt_identity()

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first()
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    # Build detailed response with related data
    response_data = {
        'id': workspace.id,
        'name': workspace.name,
        'facebook_connected': workspace.facebook_connected,
        'setup_completed': workspace.setup_completed,
        'ad_account_id': workspace.ad_account_id,
        'default_daily_budget': workspace.default_daily_budget,
        'default_currency': workspace.default_currency,
        'default_objective': workspace.default_objective,
        'timezone': workspace.timezone,
        'created_at': workspace.created_at,
        'pages': [],
        'products': [],
        'ad_account': None
    }

    # Add pages with their Facebook page data
    for wp in workspace.pages:
        page_data = {
            'id': wp.id,
            'workspace_id': wp.workspace_id,
            'facebook_page_id': wp.facebook_page_id,
            'facebook_page': {
                'id': wp.facebook_page.id,
                'facebook_page_id': wp.facebook_page.facebook_page_id,
                'name': wp.facebook_page.name,
                'profile_picture_url': wp.facebook_page.profile_picture_url,
                'is_primary': wp.facebook_page.is_primary,
            },
            'default_tone': wp.default_tone,
            'default_cta_style': wp.default_cta_style,
            'target_markets': wp.target_markets or [],
            'is_included': wp.is_included,
            'is_primary': wp.is_primary,
            'has_conversation': wp.conversation is not None,
            'conversation_id': wp.conversation.id if wp.conversation else None
        }
        response_data['pages'].append(page_data)

    # Add products
    for product in workspace.products:
        product_data = {
            'id': product.id,
            'workspace_id': product.workspace_id,
            'name': product.name,
            'short_description': product.short_description,
            'long_description': product.long_description,
            'price': product.price,
            'price_range_min': product.price_range_min,
            'price_range_max': product.price_range_max,
            'currency': product.currency,
            'usp': product.usp,
            'target_audience': product.target_audience,
            'seasonality': product.seasonality,
            'primary_image_url': product.primary_image_url,
            'image_url_2': product.image_url_2,
            'image_url_3': product.image_url_3,
            'tags': product.tags or [],
            'is_active': product.is_active,
            'created_at': product.created_at
        }
        response_data['products'].append(product_data)

    # Add ad account if exists
    if workspace.ad_account:
        response_data['ad_account'] = {
            'id': workspace.ad_account.id,
            'facebook_account_id': workspace.ad_account.facebook_account_id,
            'name': workspace.ad_account.name,
            'currency': workspace.ad_account.currency,
            'timezone': workspace.ad_account.timezone,
            'is_primary': workspace.ad_account.is_primary,
        }

    return jsonify(response_data), 200


@bp.route('/<workspace_id>', methods=['PUT'])
@jwt_required()
def update_workspace(workspace_id):
    """Update workspace details."""
    user_id = get_jwt_identity()
    data = request.get_json()

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first()
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    try:
        # Validate input
        update_data = WorkspaceUpdate(**data)
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400

    # Update fields
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(workspace, field, value)

    workspace.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(WorkspaceResponse.model_validate(workspace).model_dump()), 200


@bp.route('/<workspace_id>', methods=['DELETE'])
@jwt_required()
def delete_workspace(workspace_id):
    """Delete a workspace and all related data."""
    user_id = get_jwt_identity()

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first()
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    # Check if this is the user's active workspace
    user = User.query.get(user_id)
    if user and user.active_workspace_id == workspace_id:
        user.active_workspace_id = None

    db.session.delete(workspace)
    db.session.commit()

    return '', 204


@bp.route('/<workspace_id>/activate', methods=['POST'])
@jwt_required()
def activate_workspace(workspace_id):
    """Set a workspace as the user's active workspace."""
    user_id = get_jwt_identity()

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first()
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    # Update user's active workspace
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.active_workspace_id = workspace_id
    db.session.commit()

    return jsonify(WorkspaceResponse.model_validate(workspace).model_dump()), 200


@bp.route('/<workspace_id>/setup-pages', methods=['POST'])
@jwt_required()
def setup_pages(workspace_id):
    """Configure pages for a workspace after Facebook connection.

    This endpoint:
    1. Creates WorkspacePage entries for each selected page
    2. Auto-creates conversations (Account Overview + Page War Rooms)
    3. Marks workspace as setup_completed
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first()
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404

    try:
        # Validate input
        setup_request = PageSetupRequest(**data)
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.errors()}), 400

    # Verify all Facebook pages exist and belong to user
    for page_item in setup_request.pages:
        fb_page = FacebookPage.query.filter_by(
            id=page_item.facebook_page_id,
            user_id=user_id
        ).first()
        if not fb_page:
            return jsonify({
                'error': 'Invalid Facebook page',
                'message': f'Page {page_item.facebook_page_id} not found or does not belong to user'
            }), 400

    # Create WorkspacePage entries
    workspace_pages = []
    for page_item in setup_request.pages:
        # Check if workspace page already exists
        existing = WorkspacePage.query.filter_by(
            workspace_id=workspace_id,
            facebook_page_id=page_item.facebook_page_id
        ).first()

        if existing:
            # Update existing
            existing.is_included = page_item.is_included
            existing.default_tone = page_item.default_tone or 'friendly'
            existing.updated_at = datetime.utcnow()
            workspace_pages.append(existing)
        else:
            # Create new
            wp = WorkspacePage(
                id=str(uuid4()),
                workspace_id=workspace_id,
                facebook_page_id=page_item.facebook_page_id,
                default_tone=page_item.default_tone or 'friendly',
                is_included=page_item.is_included,
                created_at=datetime.utcnow()
            )
            db.session.add(wp)
            workspace_pages.append(wp)

    db.session.flush()  # Flush to get IDs for conversation creation

    # Create Account Overview conversation (only if it doesn't exist)
    overview_conv = Conversation.query.filter_by(
        workspace_id=workspace_id,
        chat_type=ConversationType.ACCOUNT_OVERVIEW
    ).first()

    if not overview_conv:
        overview_conv = Conversation(
            id=str(uuid4()),
            user_id=user_id,
            workspace_id=workspace_id,
            chat_type=ConversationType.ACCOUNT_OVERVIEW,
            title=f"{workspace.name} - Account Overview",
            created_at=datetime.utcnow()
        )
        db.session.add(overview_conv)

    # Create Page War Room conversations for each included page
    for wp in workspace_pages:
        if wp.is_included:
            # Check if conversation already exists
            existing_conv = Conversation.query.filter_by(
                workspace_page_id=wp.id,
                chat_type=ConversationType.PAGE_WAR_ROOM
            ).first()

            if not existing_conv:
                page_conv = Conversation(
                    id=str(uuid4()),
                    user_id=user_id,
                    workspace_id=workspace_id,
                    workspace_page_id=wp.id,
                    chat_type=ConversationType.PAGE_WAR_ROOM,
                    title=f"{wp.facebook_page.name} War Room",
                    created_at=datetime.utcnow()
                )
                db.session.add(page_conv)

    # Mark workspace setup as completed
    workspace.setup_completed = True
    workspace.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify(WorkspaceResponse.model_validate(workspace).model_dump()), 200
