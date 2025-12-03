"""Execution Agent - Handles campaign creation and management."""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ExecutionAgent:
    """
    Specialized agent for campaign execution.

    Responsibilities:
    - Create campaigns, ad sets, and ads
    - Adjust budgets
    - Pause/unpause items
    - Map draft structure to Facebook API
    """

    def __init__(
        self,
        ad_account: Optional[Any] = None,
        access_token: Optional[str] = None
    ):
        """Initialize the execution agent."""
        self.ad_account = ad_account
        self.access_token = access_token

        if access_token:
            from ..services.facebook_service import FacebookService
            self.fb_service = FacebookService(access_token)
        else:
            self.fb_service = None

    def create_campaign(
        self,
        draft: Dict[str, Any],
        page_id: str
    ) -> Dict[str, Any]:
        """Create a complete campaign from a draft."""
        if not self.fb_service or not self.ad_account:
            return self._mock_create_campaign(draft)

        try:
            # Prepare campaign data
            campaign_data = {
                'name': draft.get('campaign_name', 'New Campaign'),
                'objective': draft.get('objective', 'CONVERSIONS'),
                'status': 'PAUSED',  # Always start paused for safety
                'special_ad_categories': []
            }

            # Prepare ad set data
            adset_data = {
                'name': draft.get('ad_set_name', 'New Ad Set'),
                'daily_budget': int(draft.get('budget', 50) * 100),  # Cents
                'billing_event': 'IMPRESSIONS',
                'optimization_goal': 'CONVERSIONS',
                'targeting': self._prepare_targeting(draft.get('target_audience', {})),
                'status': 'PAUSED'
            }

            # Prepare ad data
            ad_data = {
                'name': draft.get('ad_name', 'New Ad'),
                'creative': {
                    'primary_text': draft.get('primary_text', ''),
                    'headline': draft.get('headline', ''),
                    'description': draft.get('description', ''),
                    'cta': self._map_cta(draft.get('cta', 'learn_more')),
                    'image_url': draft.get('media_url', '')
                }
            }

            # Create via Facebook API
            result = self.fb_service.create_campaign(
                account_id=self.ad_account.facebook_account_id,
                page_id=page_id,
                campaign_data=campaign_data,
                adset_data=adset_data,
                ad_data=ad_data
            )

            return {
                'success': True,
                **result
            }

        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _mock_create_campaign(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """Mock campaign creation for development."""
        campaign_id = f"camp_{uuid.uuid4().hex[:12]}"
        adset_id = f"adset_{uuid.uuid4().hex[:12]}"
        ad_id = f"ad_{uuid.uuid4().hex[:12]}"

        return {
            'success': True,
            'campaign_id': campaign_id,
            'adset_id': adset_id,
            'ad_id': ad_id,
            'status': 'PAUSED',
            'ads_manager_url': f'https://www.facebook.com/adsmanager/manage/campaigns?campaign_ids={campaign_id}',
            'is_mock': True
        }

    def _prepare_targeting(self, audience: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare targeting spec for Facebook API."""
        targeting = {
            'geo_locations': {
                'countries': audience.get('countries', ['US'])
            }
        }

        if 'age_min' in audience:
            targeting['age_min'] = audience['age_min']
        if 'age_max' in audience:
            targeting['age_max'] = audience['age_max']
        if 'genders' in audience:
            targeting['genders'] = audience['genders']
        if 'interests' in audience:
            targeting['flexible_spec'] = [{
                'interests': [{'name': i} for i in audience['interests']]
            }]

        return targeting

    def _map_cta(self, cta: str) -> str:
        """Map CTA to Facebook API format."""
        cta_map = {
            'learn_more': 'LEARN_MORE',
            'shop_now': 'SHOP_NOW',
            'sign_up': 'SIGN_UP',
            'contact_us': 'CONTACT_US',
            'book_now': 'BOOK_NOW',
            'download': 'DOWNLOAD',
            'get_offer': 'GET_OFFER'
        }
        return cta_map.get(cta, 'LEARN_MORE')

    def adjust_budget(
        self,
        object_id: str,
        new_budget: float,
        object_type: str = 'adset'
    ) -> Dict[str, Any]:
        """Adjust budget for a campaign or ad set."""
        if not self.fb_service:
            return {
                'success': True,
                'object_id': object_id,
                'new_budget': new_budget,
                'is_mock': True
            }

        try:
            result = self.fb_service.adjust_budget(
                object_id=object_id,
                new_budget=new_budget
            )
            return {'success': True, **result}

        except Exception as e:
            logger.error(f"Error adjusting budget: {e}")
            return {'success': False, 'error': str(e)}

    def pause_items(self, item_ids: List[str]) -> Dict[str, Any]:
        """Pause campaigns, ad sets, or ads."""
        if not self.fb_service:
            return {
                'success': True,
                'paused_items': item_ids,
                'is_mock': True
            }

        try:
            result = self.fb_service.pause_items(item_ids)
            return {'success': True, **result}

        except Exception as e:
            logger.error(f"Error pausing items: {e}")
            return {'success': False, 'error': str(e)}

    def unpause_items(self, item_ids: List[str]) -> Dict[str, Any]:
        """Unpause (activate) campaigns, ad sets, or ads."""
        # Similar to pause, but set status to ACTIVE
        if not self.fb_service:
            return {
                'success': True,
                'activated_items': item_ids,
                'is_mock': True
            }

        # In production, update status to ACTIVE via API
        return {
            'success': True,
            'activated_items': item_ids
        }

    def duplicate_campaign(
        self,
        campaign_id: str,
        new_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Duplicate an existing campaign."""
        # In production, use Facebook's campaign copy API
        return {
            'success': True,
            'original_campaign_id': campaign_id,
            'new_campaign_id': f"camp_{uuid.uuid4().hex[:12]}",
            'new_name': new_name or f"Copy of Campaign",
            'is_mock': True
        }

    def update_creative(
        self,
        ad_id: str,
        creative_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update ad creative."""
        # In production, update via Facebook API
        return {
            'success': True,
            'ad_id': ad_id,
            'updates_applied': creative_updates,
            'is_mock': True
        }

    def get_delivery_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign delivery status."""
        # Mock status
        return {
            'campaign_id': campaign_id,
            'status': 'ACTIVE',
            'delivery_status': 'DELIVERING',
            'effective_status': 'ACTIVE',
            'issues': [],
            'is_mock': True
        }
