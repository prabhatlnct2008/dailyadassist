"""User management API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from ..extensions import db
from ..models.user import User, UserPreferences
from ..models.facebook import AdAccount, FacebookPage
from ..schemas.user import (
    PreferencesResponse,
    PreferencesUpdate,
    AdAccountResponse,
    FacebookPageResponse
)

bp = Blueprint('users', __name__)


@bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get user preferences."""
    user_id = get_jwt_identity()
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()

    if not preferences:
        # Create default preferences
        preferences = UserPreferences(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.session.add(preferences)
        db.session.commit()

    return jsonify(PreferencesResponse.model_validate(preferences).model_dump())


@bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update user preferences."""
    user_id = get_jwt_identity()
    data = request.get_json()

    preferences = UserPreferences.query.filter_by(user_id=user_id).first()

    if not preferences:
        preferences = UserPreferences(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.session.add(preferences)

    # Update fields
    update_data = PreferencesUpdate(**data)
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(preferences, field, value)

    preferences.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(PreferencesResponse.model_validate(preferences).model_dump())


@bp.route('/ad-accounts', methods=['GET'])
@jwt_required()
def get_ad_accounts():
    """Get user's linked ad accounts."""
    user_id = get_jwt_identity()
    accounts = AdAccount.query.filter_by(user_id=user_id).all()

    return jsonify([
        AdAccountResponse.model_validate(account).model_dump()
        for account in accounts
    ])


@bp.route('/ad-accounts/<account_id>/primary', methods=['PUT'])
@jwt_required()
def set_primary_ad_account(account_id):
    """Set primary ad account."""
    user_id = get_jwt_identity()

    # Unset all as primary
    AdAccount.query.filter_by(user_id=user_id).update({'is_primary': False})

    # Set the selected one as primary
    account = AdAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return jsonify({'error': 'Ad account not found'}), 404

    account.is_primary = True
    account.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(AdAccountResponse.model_validate(account).model_dump())


@bp.route('/pages', methods=['GET'])
@jwt_required()
def get_facebook_pages():
    """Get user's linked Facebook pages."""
    user_id = get_jwt_identity()
    pages = FacebookPage.query.filter_by(user_id=user_id).all()

    return jsonify([
        FacebookPageResponse.model_validate(page).model_dump()
        for page in pages
    ])


@bp.route('/pages/<page_id>/primary', methods=['PUT'])
@jwt_required()
def set_primary_page(page_id):
    """Set primary Facebook page."""
    user_id = get_jwt_identity()

    # Unset all as primary
    FacebookPage.query.filter_by(user_id=user_id).update({'is_primary': False})

    # Set the selected one as primary
    page = FacebookPage.query.filter_by(id=page_id, user_id=user_id).first()
    if not page:
        return jsonify({'error': 'Facebook page not found'}), 404

    page.is_primary = True
    page.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(FacebookPageResponse.model_validate(page).model_dump())
