"""Custom decorators."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from ..models.facebook import FacebookConnection, AdAccount


def require_facebook_connection(f):
    """Decorator to require Facebook connection."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        connection = FacebookConnection.query.filter_by(user_id=user_id).first()

        if not connection or not connection.is_token_valid():
            return jsonify({
                'error': 'Facebook connection required',
                'code': 'FACEBOOK_NOT_CONNECTED',
                'message': 'Please connect your Facebook account to continue'
            }), 403

        return f(*args, **kwargs)

    return decorated_function


def require_ad_account(f):
    """Decorator to require a primary ad account."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()

        if not account:
            return jsonify({
                'error': 'Ad account required',
                'code': 'AD_ACCOUNT_NOT_SELECTED',
                'message': 'Please select a primary ad account'
            }), 403

        return f(*args, **kwargs)

    return decorated_function
