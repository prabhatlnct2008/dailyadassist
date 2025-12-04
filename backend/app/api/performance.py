"""Performance analytics API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from ..extensions import db
from ..models.facebook import AdAccount, FacebookConnection
from ..models.draft import PublishedCampaign, PerformanceSnapshot
from ..services.facebook_service import FacebookService
from ..schemas.performance import (
    PerformanceSummary,
    TopPerformer,
    CampaignMetrics
)

bp = Blueprint('performance', __name__)


@bp.route('/summary', methods=['GET'])
@jwt_required()
def get_performance_summary():
    """Get performance summary for a time range."""
    user_id = get_jwt_identity()
    time_range = request.args.get('time_range', 'last_7_days')

    # Get user's primary account
    account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
    if not account:
        return jsonify({'error': 'No ad account connected'}), 400

    fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()
    if not fb_connection:
        return jsonify({'error': 'Facebook not connected'}), 400

    try:
        fb_service = FacebookService(fb_connection.get_access_token())
        stats = fb_service.get_account_stats(
            account_id=account.facebook_account_id,
            time_range=time_range
        )

        return jsonify({
            'time_range': time_range,
            'total_spend': stats.get('spend', 0),
            'total_impressions': stats.get('impressions', 0),
            'total_clicks': stats.get('clicks', 0),
            'average_ctr': stats.get('ctr', 0),
            'average_cpc': stats.get('cpc', 0),
            'total_conversions': stats.get('conversions', 0),
            'average_roas': stats.get('roas', 0),
            'active_campaigns': stats.get('active_campaigns', 0)
        })

    except Exception as e:
        # Return mock data for development
        return jsonify({
            'time_range': time_range,
            'total_spend': 1500.00,
            'total_impressions': 45000,
            'total_clicks': 1200,
            'average_ctr': 2.67,
            'average_cpc': 1.25,
            'total_conversions': 45,
            'average_roas': 3.2,
            'active_campaigns': 3,
            'is_mock_data': True
        })


@bp.route('/top-performers', methods=['GET'])
@jwt_required()
def get_top_performers():
    """Get top performing campaigns/ads."""
    user_id = get_jwt_identity()
    metric = request.args.get('metric', 'roas')
    time_range = request.args.get('time_range', 'last_7_days')
    limit = request.args.get('limit', 5, type=int)
    level = request.args.get('level', 'ad')  # campaign, adset, or ad

    account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
    if not account:
        return jsonify({'error': 'No ad account connected'}), 400

    fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()
    if not fb_connection:
        return jsonify({'error': 'Facebook not connected'}), 400

    try:
        fb_service = FacebookService(fb_connection.get_access_token())
        top_performers = fb_service.get_top_performers(
            account_id=account.facebook_account_id,
            metric=metric,
            time_range=time_range,
            limit=limit,
            level=level
        )

        return jsonify({
            'metric': metric,
            'time_range': time_range,
            'level': level,
            'performers': top_performers
        })

    except Exception as e:
        # Return mock data for development
        return jsonify({
            'metric': metric,
            'time_range': time_range,
            'level': level,
            'performers': [
                {
                    'id': 'mock_1',
                    'name': 'Red Hoodie - Winter Sale',
                    'spend': 500.00,
                    'roas': 4.2,
                    'ctr': 3.5,
                    'conversions': 25
                },
                {
                    'id': 'mock_2',
                    'name': 'Sneaker Collection - Flash',
                    'spend': 350.00,
                    'roas': 3.1,
                    'ctr': 2.8,
                    'conversions': 15
                }
            ],
            'is_mock_data': True
        })


@bp.route('/underperformers', methods=['GET'])
@jwt_required()
def get_underperformers():
    """Get underperforming campaigns/ads."""
    user_id = get_jwt_identity()
    metric = request.args.get('metric', 'roas')
    threshold = request.args.get('threshold', 1.0, type=float)
    time_range = request.args.get('time_range', 'last_7_days')

    account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
    if not account:
        return jsonify({'error': 'No ad account connected'}), 400

    fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()
    if not fb_connection:
        return jsonify({'error': 'Facebook not connected'}), 400

    try:
        fb_service = FacebookService(fb_connection.get_access_token())
        underperformers = fb_service.get_underperformers(
            account_id=account.facebook_account_id,
            metric=metric,
            threshold=threshold,
            time_range=time_range
        )

        return jsonify({
            'metric': metric,
            'threshold': threshold,
            'time_range': time_range,
            'underperformers': underperformers
        })

    except Exception as e:
        # Return mock data for development
        return jsonify({
            'metric': metric,
            'threshold': threshold,
            'time_range': time_range,
            'underperformers': [
                {
                    'id': 'mock_under_1',
                    'name': 'Old Collection - Generic',
                    'spend': 200.00,
                    'roas': 0.7,
                    'ctr': 0.8,
                    'conversions': 2,
                    'recommendation': 'Consider pausing this campaign'
                }
            ],
            'is_mock_data': True
        })


@bp.route('/campaigns', methods=['GET'])
@jwt_required()
def get_campaign_metrics():
    """Get metrics for all campaigns."""
    user_id = get_jwt_identity()
    time_range = request.args.get('time_range', 'last_7_days')
    status_filter = request.args.get('status')

    account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
    if not account:
        return jsonify({'error': 'No ad account connected'}), 400

    fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()
    if not fb_connection:
        return jsonify({'error': 'Facebook not connected'}), 400

    try:
        fb_service = FacebookService(fb_connection.get_access_token())
        campaigns = fb_service.get_campaign_metrics(
            account_id=account.facebook_account_id,
            time_range=time_range,
            status=status_filter
        )

        return jsonify({
            'time_range': time_range,
            'campaigns': campaigns
        })

    except Exception as e:
        # Return mock data for development
        return jsonify({
            'time_range': time_range,
            'campaigns': [
                {
                    'id': 'camp_1',
                    'name': 'Red Hoodie - Winter Sale',
                    'status': 'ACTIVE',
                    'objective': 'CONVERSIONS',
                    'spend': 500.00,
                    'impressions': 15000,
                    'clicks': 525,
                    'ctr': 3.5,
                    'conversions': 25,
                    'roas': 4.2,
                    'daily_budget': 100.00
                },
                {
                    'id': 'camp_2',
                    'name': 'Sneaker Collection - Flash',
                    'status': 'ACTIVE',
                    'objective': 'CONVERSIONS',
                    'spend': 350.00,
                    'impressions': 12500,
                    'clicks': 350,
                    'ctr': 2.8,
                    'conversions': 15,
                    'roas': 3.1,
                    'daily_budget': 75.00
                }
            ],
            'is_mock_data': True
        })
