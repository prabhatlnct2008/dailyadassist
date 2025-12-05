"""Flask application factory."""
import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv

from .config import config
from .extensions import db, migrate, cors, jwt
from .logging_config import setup_logging


def create_app(config_name=None):
    """Create and configure the Flask application."""
    # Load environment variables first
    load_dotenv()

    # Setup logging early (before anything else logs)
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Starting Daily Ad Agent application...")

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=[app.config['FRONTEND_URL']], supports_credentials=True)
    jwt.init_app(app)

    # Initialize OAuth
    from .api.auth import init_oauth
    init_oauth(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register JWT callbacks
    register_jwt_callbacks(app)

    # Create database tables (for development)
    with app.app_context():
        db.create_all()

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from .api import auth, users, onboarding, conversations, agent, drafts, performance, activity, workspaces

    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(workspaces.bp, url_prefix='/api/workspaces')
    app.register_blueprint(onboarding.bp, url_prefix='/api/onboarding')
    app.register_blueprint(conversations.bp, url_prefix='/api/conversations')
    app.register_blueprint(agent.bp, url_prefix='/api/agent')
    app.register_blueprint(drafts.bp, url_prefix='/api/drafts')
    app.register_blueprint(performance.bp, url_prefix='/api/performance')
    app.register_blueprint(activity.bp, url_prefix='/api/activity')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Daily Ad Agent API is running'})


def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


def register_jwt_callbacks(app):
    """Register JWT callbacks for token handling."""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token Expired',
            'message': 'The access token has expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid Token',
            'message': 'The token is invalid'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Missing Token',
            'message': 'Authorization token is required'
        }), 401
