"""Onboarding API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from ..extensions import db
from ..models.user import UserPreferences
from ..models.facebook import FacebookConnection, AdAccount, FacebookPage
from ..services.facebook_service import FacebookService

bp = Blueprint('onboarding', __name__)


@bp.route('/status', methods=['GET'])
@jwt_required()
def get_onboarding_status():
    """Get user's onboarding progress."""
    user_id = get_jwt_identity()

    # Check each step
    fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()
    primary_account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
    primary_page = FacebookPage.query.filter_by(user_id=user_id, is_primary=True).first()
    preferences = UserPreferences.query.filter_by(user_id=user_id).first()

    steps = {
        'facebook_connected': fb_connection is not None,
        'ad_account_selected': primary_account is not None,
        'page_selected': primary_page is not None,
        'defaults_configured': preferences is not None and preferences.onboarding_completed
    }

    current_step = 1
    if steps['facebook_connected']:
        current_step = 2
    if steps['ad_account_selected']:
        current_step = 3
    if steps['page_selected']:
        current_step = 4
    if steps['defaults_configured']:
        current_step = 5  # Completed

    return jsonify({
        'steps': steps,
        'current_step': current_step,
        'is_complete': all(steps.values())
    })


@bp.route('/complete-step', methods=['POST'])
@jwt_required()
def complete_onboarding_step():
    """Complete an onboarding step."""
    user_id = get_jwt_identity()
    data = request.get_json()
    step = data.get('step')

    if step == 'fetch_ad_accounts':
        # Fetch ad accounts from Facebook
        fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()
        if not fb_connection:
            return jsonify({'error': 'Facebook not connected'}), 400

        try:
            fb_service = FacebookService(fb_connection.get_access_token())
            accounts = fb_service.get_ad_accounts()

            # Store accounts
            for acc in accounts:
                existing = AdAccount.query.filter_by(
                    user_id=user_id,
                    facebook_account_id=acc['id']
                ).first()

                if not existing:
                    ad_account = AdAccount(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        facebook_account_id=acc['id'],
                        name=acc['name'],
                        currency=acc.get('currency', 'USD'),
                        timezone=acc.get('timezone_name', 'UTC'),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(ad_account)

            db.session.commit()
            return jsonify({'message': 'Ad accounts fetched', 'count': len(accounts)})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif step == 'fetch_pages':
        # Fetch Facebook pages
        fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()
        if not fb_connection:
            return jsonify({'error': 'Facebook not connected'}), 400

        try:
            fb_service = FacebookService(fb_connection.get_access_token())
            pages = fb_service.get_pages()

            # Store pages
            for pg in pages:
                existing = FacebookPage.query.filter_by(
                    user_id=user_id,
                    facebook_page_id=pg['id']
                ).first()

                if not existing:
                    page = FacebookPage(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        facebook_page_id=pg['id'],
                        name=pg['name'],
                        profile_picture_url=pg.get('picture', {}).get('data', {}).get('url', ''),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(page)

            db.session.commit()
            return jsonify({'message': 'Pages fetched', 'count': len(pages)})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif step == 'complete_onboarding':
        # Mark onboarding as complete
        preferences = UserPreferences.query.filter_by(user_id=user_id).first()
        if preferences:
            preferences.onboarding_completed = True
            preferences.updated_at = datetime.utcnow()
            db.session.commit()

        return jsonify({'message': 'Onboarding completed'})

    return jsonify({'error': 'Unknown step'}), 400


# Import uuid for generating IDs
import uuid
