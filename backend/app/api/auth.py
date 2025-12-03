"""Authentication API endpoints."""
from flask import Blueprint, jsonify, request, redirect, current_app, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from authlib.integrations.flask_client import OAuth
from datetime import datetime
import uuid

from ..extensions import db
from ..models.user import User
from ..models.facebook import FacebookConnection
from ..schemas.auth import UserResponse

bp = Blueprint('auth', __name__)
oauth = OAuth()


def init_oauth(app):
    """Initialize OAuth with app context."""
    oauth.init_app(app)

    # Google OAuth
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # Facebook OAuth
    oauth.register(
        name='facebook',
        client_id=app.config['FACEBOOK_APP_ID'],
        client_secret=app.config['FACEBOOK_APP_SECRET'],
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={
            'scope': 'ads_read ads_management pages_read_engagement business_management'
        }
    )


@bp.route('/google/login')
def google_login():
    """Initiate Google OAuth login."""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            return jsonify({'error': 'Failed to get user info'}), 400

        # Find or create user
        user = User.query.filter_by(google_id=user_info['sub']).first()

        if not user:
            user = User(
                id=str(uuid.uuid4()),
                email=user_info['email'],
                google_id=user_info['sub'],
                name=user_info.get('name', ''),
                profile_picture_url=user_info.get('picture', ''),
                created_at=datetime.utcnow(),
                last_login_at=datetime.utcnow()
            )
            db.session.add(user)
        else:
            user.last_login_at = datetime.utcnow()

        db.session.commit()

        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Redirect to frontend with tokens
        frontend_url = current_app.config['FRONTEND_URL']
        return redirect(f"{frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}")

    except Exception as e:
        current_app.logger.error(f"Google OAuth error: {str(e)}")
        frontend_url = current_app.config['FRONTEND_URL']
        return redirect(f"{frontend_url}/auth/error?message=Authentication failed")


@bp.route('/facebook/connect')
@jwt_required()
def facebook_connect():
    """Initiate Facebook OAuth to connect ad account."""
    redirect_uri = url_for('auth.facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)


@bp.route('/facebook/callback')
@jwt_required()
def facebook_callback():
    """Handle Facebook OAuth callback."""
    try:
        user_id = get_jwt_identity()
        token = oauth.facebook.authorize_access_token()

        # Get Facebook user ID
        resp = oauth.facebook.get('me?fields=id,name')
        fb_user_info = resp.json()

        # Store or update Facebook connection
        connection = FacebookConnection.query.filter_by(user_id=user_id).first()

        if not connection:
            connection = FacebookConnection(
                id=str(uuid.uuid4()),
                user_id=user_id,
                facebook_user_id=fb_user_info['id'],
                created_at=datetime.utcnow()
            )
            db.session.add(connection)

        # Encrypt and store the access token
        connection.set_access_token(token['access_token'])
        connection.token_expires_at = datetime.fromtimestamp(token.get('expires_at', 0)) if token.get('expires_at') else None
        connection.updated_at = datetime.utcnow()

        db.session.commit()

        frontend_url = current_app.config['FRONTEND_URL']
        return redirect(f"{frontend_url}/onboarding/facebook-connected")

    except Exception as e:
        current_app.logger.error(f"Facebook OAuth error: {str(e)}")
        frontend_url = current_app.config['FRONTEND_URL']
        return redirect(f"{frontend_url}/onboarding/facebook-error?message=Connection failed")


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token})


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (invalidate token on client side)."""
    # In a production app, you might want to blacklist the token
    return jsonify({'message': 'Successfully logged out'})


@bp.route('/me')
@jwt_required()
def get_current_user():
    """Get current user information."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(UserResponse.from_orm(user).model_dump())
