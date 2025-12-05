"""Workspace pages API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from ..extensions import db
from ..models.workspace import Workspace, WorkspacePage
from ..models.product import Product, PageProduct
from ..models.facebook import FacebookPage
from ..schemas.workspace_page import PageSettingsUpdate, WorkspacePageResponse
from ..schemas.product import ProductResponse
from ..schemas.user import FacebookPageResponse

bp = Blueprint('workspace_pages', __name__)


def validate_workspace_access(workspace_id, user_id):
    """Validate that the user owns the workspace."""
    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first()
    if not workspace:
        return None
    return workspace


@bp.route('/', methods=['GET'])
@jwt_required()
def list_workspace_pages(workspace_id):
    """List all pages in a workspace with their settings."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace = validate_workspace_access(workspace_id, user_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found or access denied'}), 404

    # Get all workspace pages
    workspace_pages = WorkspacePage.query.filter_by(workspace_id=workspace_id).all()

    # Build response with facebook_page details
    result = []
    for wp in workspace_pages:
        # Get the associated conversation
        conversation_id = wp.conversation.id if wp.conversation else None
        has_conversation = wp.conversation is not None

        # Build response object
        page_data = {
            'id': wp.id,
            'workspace_id': wp.workspace_id,
            'facebook_page_id': wp.facebook_page_id,
            'facebook_page': FacebookPageResponse.model_validate(wp.facebook_page).model_dump(),
            'default_tone': wp.default_tone,
            'default_cta_style': wp.default_cta_style,
            'target_markets': wp.target_markets or [],
            'is_included': wp.is_included,
            'is_primary': wp.is_primary,
            'has_conversation': has_conversation,
            'conversation_id': conversation_id
        }
        result.append(page_data)

    return jsonify(result)


@bp.route('/<page_id>', methods=['GET'])
@jwt_required()
def get_workspace_page(workspace_id, page_id):
    """Get a specific workspace page with details."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace = validate_workspace_access(workspace_id, user_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found or access denied'}), 404

    # Get the workspace page
    workspace_page = WorkspacePage.query.filter_by(
        id=page_id,
        workspace_id=workspace_id
    ).first()

    if not workspace_page:
        return jsonify({'error': 'Page not found in this workspace'}), 404

    # Get the associated conversation
    conversation_id = workspace_page.conversation.id if workspace_page.conversation else None
    has_conversation = workspace_page.conversation is not None

    # Build response
    page_data = {
        'id': workspace_page.id,
        'workspace_id': workspace_page.workspace_id,
        'facebook_page_id': workspace_page.facebook_page_id,
        'facebook_page': FacebookPageResponse.model_validate(workspace_page.facebook_page).model_dump(),
        'default_tone': workspace_page.default_tone,
        'default_cta_style': workspace_page.default_cta_style,
        'target_markets': workspace_page.target_markets or [],
        'is_included': workspace_page.is_included,
        'is_primary': workspace_page.is_primary,
        'has_conversation': has_conversation,
        'conversation_id': conversation_id
    }

    return jsonify(page_data)


@bp.route('/<page_id>/settings', methods=['PUT'])
@jwt_required()
def update_page_settings(workspace_id, page_id):
    """Update page-specific settings (tone, CTA style, target markets, etc.)."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace = validate_workspace_access(workspace_id, user_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found or access denied'}), 404

    # Get the workspace page
    workspace_page = WorkspacePage.query.filter_by(
        id=page_id,
        workspace_id=workspace_id
    ).first()

    if not workspace_page:
        return jsonify({'error': 'Page not found in this workspace'}), 404

    # Parse and validate request data
    data = request.get_json()
    try:
        settings_update = PageSettingsUpdate(**data)
    except Exception as e:
        return jsonify({'error': f'Invalid request data: {str(e)}'}), 400

    # Update only provided fields (partial update)
    for field, value in settings_update.model_dump(exclude_unset=True).items():
        setattr(workspace_page, field, value)

    workspace_page.updated_at = datetime.utcnow()
    db.session.commit()

    # Get the associated conversation
    conversation_id = workspace_page.conversation.id if workspace_page.conversation else None
    has_conversation = workspace_page.conversation is not None

    # Build response
    page_data = {
        'id': workspace_page.id,
        'workspace_id': workspace_page.workspace_id,
        'facebook_page_id': workspace_page.facebook_page_id,
        'facebook_page': FacebookPageResponse.model_validate(workspace_page.facebook_page).model_dump(),
        'default_tone': workspace_page.default_tone,
        'default_cta_style': workspace_page.default_cta_style,
        'target_markets': workspace_page.target_markets or [],
        'is_included': workspace_page.is_included,
        'is_primary': workspace_page.is_primary,
        'has_conversation': has_conversation,
        'conversation_id': conversation_id
    }

    return jsonify(page_data)


@bp.route('/<page_id>/products', methods=['GET'])
@jwt_required()
def get_page_products(workspace_id, page_id):
    """Get all products tagged to this page."""
    user_id = get_jwt_identity()

    # Validate workspace access
    workspace = validate_workspace_access(workspace_id, user_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found or access denied'}), 404

    # Get the workspace page
    workspace_page = WorkspacePage.query.filter_by(
        id=page_id,
        workspace_id=workspace_id
    ).first()

    if not workspace_page:
        return jsonify({'error': 'Page not found in this workspace'}), 404

    # Get all page-product associations for this page
    page_products = PageProduct.query.filter_by(workspace_page_id=page_id).all()

    # Build response with product details and is_default flag
    result = []
    for pp in page_products:
        product = pp.product
        product_data = ProductResponse.model_validate(product).model_dump()
        # Add the is_default flag from the association
        product_data['is_default'] = pp.is_default
        result.append(product_data)

    return jsonify(result)
