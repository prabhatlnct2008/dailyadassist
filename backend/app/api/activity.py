"""Activity log API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from ..extensions import db
from ..models.activity import ActivityLog
from ..schemas.activity import ActivityLogResponse, RecommendationResponse

bp = Blueprint('activity', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def list_activity():
    """List activity log entries."""
    user_id = get_jwt_identity()

    # Filters
    action_type = request.args.get('action_type')
    entity_type = request.args.get('entity_type')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = ActivityLog.query.filter_by(user_id=user_id)

    if action_type:
        query = query.filter_by(action_type=action_type)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)

    activities = query.order_by(ActivityLog.created_at.desc())\
        .paginate(page=page, per_page=per_page)

    return jsonify({
        'activities': [
            ActivityLogResponse.model_validate(a).model_dump()
            for a in activities.items
        ],
        'total': activities.total,
        'page': page,
        'per_page': per_page,
        'pages': activities.pages
    })


@bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get pending recommendations from the agent."""
    user_id = get_jwt_identity()

    # Get recommendations (stored as activity logs with specific type)
    recommendations = ActivityLog.query.filter_by(
        user_id=user_id,
        action_type='recommendation_made'
    ).filter(
        ActivityLog.extra_data['applied'].astext != 'true'
    ).order_by(ActivityLog.created_at.desc()).limit(10).all()

    return jsonify({
        'recommendations': [
            {
                'id': r.id,
                'type': r.extra_data.get('recommendation_type', 'unknown'),
                'description': r.rationale,
                'entity_type': r.entity_type,
                'entity_id': r.entity_id,
                'entity_name': r.extra_data.get('entity_name', ''),
                'suggested_action': r.extra_data.get('suggested_action', ''),
                'impact': r.extra_data.get('expected_impact', ''),
                'created_at': r.created_at.isoformat()
            }
            for r in recommendations
        ]
    })


@bp.route('/recommendations/<recommendation_id>/apply', methods=['POST'])
@jwt_required()
def apply_recommendation(recommendation_id):
    """Apply a recommendation."""
    user_id = get_jwt_identity()

    recommendation = ActivityLog.query.filter_by(
        id=recommendation_id,
        user_id=user_id,
        action_type='recommendation_made'
    ).first()

    if not recommendation:
        return jsonify({'error': 'Recommendation not found'}), 404

    try:
        # Execute the recommendation based on type
        rec_type = recommendation.extra_data.get('recommendation_type')
        entity_id = recommendation.entity_id

        result = {'success': True, 'message': 'Recommendation applied'}

        if rec_type == 'increase_budget':
            # Call budget adjustment
            from ..services.facebook_service import FacebookService
            from ..models.facebook import AdAccount, FacebookConnection

            account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
            fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()

            if account and fb_connection:
                fb_service = FacebookService(fb_connection.get_access_token())
                new_budget = recommendation.extra_data.get('new_budget')
                fb_service.adjust_budget(entity_id, new_budget)
                result['message'] = f'Budget increased to {new_budget}'

        elif rec_type == 'pause_campaign':
            # Pause the campaign
            from ..services.facebook_service import FacebookService
            from ..models.facebook import AdAccount, FacebookConnection

            account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
            fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()

            if account and fb_connection:
                fb_service = FacebookService(fb_connection.get_access_token())
                fb_service.pause_items([entity_id])
                result['message'] = 'Campaign paused'

        # Mark recommendation as applied
        recommendation.extra_data['applied'] = True
        recommendation.extra_data['applied_at'] = datetime.utcnow().isoformat()

        # Log the application
        applied_log = ActivityLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action_type='recommendation_applied',
            entity_type=recommendation.entity_type,
            entity_id=entity_id,
            rationale=f"Applied recommendation: {recommendation.rationale}",
            extra_data={'recommendation_id': recommendation_id},
            created_at=datetime.utcnow(),
            is_agent_action=False
        )
        db.session.add(applied_log)
        db.session.commit()

        return jsonify(result)

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to apply recommendation: {str(e)}'}), 500
