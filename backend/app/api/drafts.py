"""Draft management API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from ..extensions import db
from ..models.draft import AdDraft, PublishedCampaign
from ..models.facebook import AdAccount, FacebookPage
from ..services.facebook_service import FacebookService
from ..schemas.draft import DraftResponse, DraftUpdate, PublishedCampaignResponse

bp = Blueprint('drafts', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def list_drafts():
    """List user's ad drafts."""
    user_id = get_jwt_identity()

    status_filter = request.args.get('status')
    query = AdDraft.query.filter_by(user_id=user_id)

    if status_filter:
        query = query.filter_by(status=status_filter)

    drafts = query.order_by(AdDraft.updated_at.desc()).all()

    return jsonify([
        DraftResponse.model_validate(draft).model_dump()
        for draft in drafts
    ])


@bp.route('/<draft_id>', methods=['GET'])
@jwt_required()
def get_draft(draft_id):
    """Get a specific draft."""
    user_id = get_jwt_identity()

    draft = AdDraft.query.filter_by(id=draft_id, user_id=user_id).first()
    if not draft:
        return jsonify({'error': 'Draft not found'}), 404

    return jsonify(DraftResponse.model_validate(draft).model_dump())


@bp.route('/<draft_id>', methods=['PUT'])
@jwt_required()
def update_draft(draft_id):
    """Update a draft manually."""
    user_id = get_jwt_identity()
    data = request.get_json()

    draft = AdDraft.query.filter_by(id=draft_id, user_id=user_id).first()
    if not draft:
        return jsonify({'error': 'Draft not found'}), 404

    # Update fields
    update_data = DraftUpdate(**data)
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(draft, field, value)

    draft.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(DraftResponse.model_validate(draft).model_dump())


@bp.route('/<draft_id>/publish', methods=['POST'])
@jwt_required()
def publish_draft(draft_id):
    """Publish a draft to Facebook."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    draft = AdDraft.query.filter_by(id=draft_id, user_id=user_id).first()
    if not draft:
        return jsonify({'error': 'Draft not found'}), 404

    # Get user's primary account and page
    account = AdAccount.query.filter_by(user_id=user_id, is_primary=True).first()
    page = FacebookPage.query.filter_by(user_id=user_id, is_primary=True).first()

    if not account:
        return jsonify({'error': 'No ad account selected'}), 400
    if not page:
        return jsonify({'error': 'No Facebook page selected'}), 400

    try:
        # Get Facebook access token
        from ..models.facebook import FacebookConnection
        fb_connection = FacebookConnection.query.filter_by(user_id=user_id).first()
        if not fb_connection:
            return jsonify({'error': 'Facebook not connected'}), 400

        fb_service = FacebookService(fb_connection.get_access_token())

        # Create campaign structure
        campaign_data = {
            'name': draft.campaign_name,
            'objective': draft.objective or 'CONVERSIONS',
            'status': 'PAUSED',  # Start paused for safety
        }

        adset_data = {
            'name': draft.ad_set_name,
            'daily_budget': int(draft.budget * 100),  # Convert to cents
            'targeting': draft.target_audience or {},
            'billing_event': 'IMPRESSIONS',
            'optimization_goal': 'CONVERSIONS',
        }

        ad_data = {
            'name': draft.ad_name,
            'creative': {
                'primary_text': draft.primary_text,
                'headline': draft.headline,
                'description': draft.description,
                'cta': draft.cta,
                'image_url': draft.media_url,
            }
        }

        # Publish to Facebook
        result = fb_service.create_campaign(
            account_id=account.facebook_account_id,
            page_id=page.facebook_page_id,
            campaign_data=campaign_data,
            adset_data=adset_data,
            ad_data=ad_data
        )

        # Create published campaign record
        published = PublishedCampaign(
            id=str(uuid.uuid4()),
            user_id=user_id,
            ad_draft_id=draft.id,
            facebook_campaign_id=result['campaign_id'],
            facebook_adset_id=result['adset_id'],
            facebook_ad_id=result['ad_id'],
            ads_manager_url=result['ads_manager_url'],
            published_at=datetime.utcnow(),
            status='active',
            created_at=datetime.utcnow()
        )
        db.session.add(published)

        # Update draft status
        draft.status = 'published'
        draft.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify(PublishedCampaignResponse.model_validate(published).model_dump())

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to publish: {str(e)}'}), 500


@bp.route('/<draft_id>/variants', methods=['GET'])
@jwt_required()
def get_draft_variants(draft_id):
    """Get all variants of a draft."""
    user_id = get_jwt_identity()

    # Get the base draft
    draft = AdDraft.query.filter_by(id=draft_id, user_id=user_id).first()
    if not draft:
        return jsonify({'error': 'Draft not found'}), 404

    # Find the root draft (if this is a variant)
    root_id = draft.parent_draft_id or draft.id

    # Get all drafts in this variant tree
    variants = AdDraft.query.filter(
        AdDraft.user_id == user_id,
        (AdDraft.id == root_id) | (AdDraft.parent_draft_id == root_id)
    ).order_by(AdDraft.variant_number.asc()).all()

    return jsonify([
        DraftResponse.model_validate(v).model_dump()
        for v in variants
    ])
