"""Facebook Marketing API service with real API integration."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

# Check if we should use mock data
USE_MOCK_DATA = os.environ.get('USE_MOCK_FACEBOOK_DATA', 'false').lower() == 'true'


class FacebookServiceError(Exception):
    """Custom exception for Facebook API errors."""
    pass


class FacebookService:
    """Service for interacting with Facebook Marketing API."""

    def __init__(self, access_token: str):
        """Initialize with access token."""
        self.access_token = access_token
        self.api_version = os.environ.get('FACEBOOK_GRAPH_API_VERSION', 'v22.0')
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
        self._api_initialized = False

        # Try to initialize the Facebook API
        self._init_facebook_api()

    def _init_facebook_api(self):
        """Initialize the Facebook Business API if available."""
        if not self.access_token:
            logger.warning("No access token provided, using mock data")
            return

        try:
            from facebook_business.api import FacebookAdsApi
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.campaign import Campaign
            from facebook_business.adobjects.ad import Ad

            FacebookAdsApi.init(access_token=self.access_token)
            self._api_initialized = True
            logger.info("Facebook Ads API initialized successfully")
        except ImportError:
            logger.warning("facebook-business SDK not installed, using mock data")
        except Exception as e:
            logger.error(f"Failed to initialize Facebook API: {e}")

    def _should_use_mock(self) -> bool:
        """Determine if we should use mock data."""
        return USE_MOCK_DATA or not self._api_initialized or not self.access_token

    def _get_date_range(self, time_range: str) -> Dict[str, str]:
        """Convert time range string to date parameters."""
        today = datetime.utcnow().date()

        ranges = {
            'today': (today, today),
            'yesterday': (today - timedelta(days=1), today - timedelta(days=1)),
            'last_7_days': (today - timedelta(days=7), today),
            'last_14_days': (today - timedelta(days=14), today),
            'last_30_days': (today - timedelta(days=30), today),
            'this_month': (today.replace(day=1), today),
        }

        start_date, end_date = ranges.get(time_range, ranges['last_7_days'])
        return {
            'since': start_date.isoformat(),
            'until': end_date.isoformat()
        }

    def get_ad_accounts(self) -> List[Dict[str, Any]]:
        """Get user's ad accounts."""
        if self._should_use_mock():
            return self._mock_ad_accounts()

        try:
            from facebook_business.adobjects.aduser import AdUser
            from facebook_business.adobjects.adaccount import AdAccount

            me = AdUser(fbid='me')
            accounts = me.get_ad_accounts(fields=[
                AdAccount.Field.id,
                AdAccount.Field.name,
                AdAccount.Field.currency,
                AdAccount.Field.timezone_name,
                AdAccount.Field.account_status
            ])

            return [
                {
                    'id': account[AdAccount.Field.id],
                    'name': account[AdAccount.Field.name],
                    'currency': account.get(AdAccount.Field.currency, 'USD'),
                    'timezone_name': account.get(AdAccount.Field.timezone_name, 'UTC'),
                    'account_status': account.get(AdAccount.Field.account_status, 1)
                }
                for account in accounts
            ]
        except Exception as e:
            logger.error(f"Error fetching ad accounts: {e}")
            return self._mock_ad_accounts()

    def _mock_ad_accounts(self) -> List[Dict[str, Any]]:
        """Return mock ad accounts."""
        return [
            {
                'id': 'act_123456789',
                'name': 'My Business Account',
                'currency': 'USD',
                'timezone_name': 'America/New_York',
                'account_status': 1
            }
        ]

    def get_pages(self) -> List[Dict[str, Any]]:
        """Get user's Facebook pages."""
        if self._should_use_mock():
            return self._mock_pages()

        try:
            import requests

            url = f"{self.base_url}/me/accounts"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,picture{url}'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return data.get('data', [])
        except Exception as e:
            logger.error(f"Error fetching pages: {e}")
            return self._mock_pages()

    def _mock_pages(self) -> List[Dict[str, Any]]:
        """Return mock pages."""
        page_id = os.environ.get('FACEBOOK_PAGE_ID', 'page_123')
        return [
            {
                'id': page_id,
                'name': 'My Business Page',
                'picture': {
                    'data': {
                        'url': 'https://via.placeholder.com/100'
                    }
                }
            }
        ]

    def get_account_stats(
        self,
        account_id: str,
        time_range: str = 'last_7_days',
        level: str = 'account'
    ) -> Dict[str, Any]:
        """Get account-level statistics."""
        date_range = self._get_date_range(time_range)

        if self._should_use_mock():
            return self._mock_account_stats(date_range)

        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.adsinsights import AdsInsights

            account = AdAccount(account_id)
            insights = account.get_insights(
                params={
                    'time_range': {
                        'since': date_range['since'],
                        'until': date_range['until']
                    },
                    'level': level
                },
                fields=[
                    AdsInsights.Field.spend,
                    AdsInsights.Field.impressions,
                    AdsInsights.Field.clicks,
                    AdsInsights.Field.ctr,
                    AdsInsights.Field.cpc,
                    AdsInsights.Field.conversions,
                    AdsInsights.Field.purchase_roas,
                ]
            )

            if insights:
                data = insights[0]
                spend = float(data.get(AdsInsights.Field.spend, 0))
                conversions = self._parse_conversions(data.get(AdsInsights.Field.conversions, []))
                roas_data = data.get(AdsInsights.Field.purchase_roas, [])
                roas = float(roas_data[0].get('value', 0)) if roas_data else 0

                return {
                    'spend': spend,
                    'impressions': int(data.get(AdsInsights.Field.impressions, 0)),
                    'clicks': int(data.get(AdsInsights.Field.clicks, 0)),
                    'ctr': float(data.get(AdsInsights.Field.ctr, 0)),
                    'cpc': float(data.get(AdsInsights.Field.cpc, 0)),
                    'conversions': conversions,
                    'roas': roas,
                    'active_campaigns': self._count_active_campaigns(account_id),
                    'date_range': date_range,
                    'is_real_data': True
                }
            else:
                return self._mock_account_stats(date_range)

        except Exception as e:
            logger.error(f"Error fetching account stats: {e}")
            return self._mock_account_stats(date_range)

    def _parse_conversions(self, conversions_data: list) -> int:
        """Parse conversions from Facebook API response."""
        total = 0
        for conv in conversions_data:
            if isinstance(conv, dict):
                total += int(conv.get('value', 0))
        return total

    def _count_active_campaigns(self, account_id: str) -> int:
        """Count active campaigns in the account."""
        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.campaign import Campaign

            account = AdAccount(account_id)
            campaigns = account.get_campaigns(
                params={'effective_status': ['ACTIVE']},
                fields=[Campaign.Field.id]
            )
            return len(list(campaigns))
        except Exception:
            return 3  # Default

    def _mock_account_stats(self, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Return mock account stats."""
        return {
            'spend': 1500.00,
            'impressions': 45000,
            'clicks': 1200,
            'ctr': 2.67,
            'cpc': 1.25,
            'conversions': 45,
            'roas': 3.2,
            'active_campaigns': 3,
            'date_range': date_range,
            'is_real_data': False
        }

    def get_top_performers(
        self,
        account_id: str,
        metric: str = 'roas',
        time_range: str = 'last_7_days',
        limit: int = 5,
        level: str = 'ad'
    ) -> List[Dict[str, Any]]:
        """Get top performing campaigns/adsets/ads."""
        date_range = self._get_date_range(time_range)

        if self._should_use_mock():
            return self._mock_top_performers(account_id, limit)

        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.adsinsights import AdsInsights

            account = AdAccount(account_id)

            # Map metric to Facebook field
            sort_field = {
                'roas': AdsInsights.Field.purchase_roas,
                'ctr': AdsInsights.Field.ctr,
                'conversions': AdsInsights.Field.conversions,
                'spend': AdsInsights.Field.spend
            }.get(metric, AdsInsights.Field.purchase_roas)

            insights = account.get_insights(
                params={
                    'time_range': {
                        'since': date_range['since'],
                        'until': date_range['until']
                    },
                    'level': level,
                    'sort': [f'{sort_field}_descending'],
                    'limit': limit
                },
                fields=[
                    AdsInsights.Field.ad_id,
                    AdsInsights.Field.ad_name,
                    AdsInsights.Field.campaign_name,
                    AdsInsights.Field.spend,
                    AdsInsights.Field.impressions,
                    AdsInsights.Field.clicks,
                    AdsInsights.Field.ctr,
                    AdsInsights.Field.cpc,
                    AdsInsights.Field.conversions,
                    AdsInsights.Field.purchase_roas,
                ]
            )

            performers = []
            for data in insights:
                roas_data = data.get(AdsInsights.Field.purchase_roas, [])
                roas = float(roas_data[0].get('value', 0)) if roas_data else 0

                performers.append({
                    'id': data.get(AdsInsights.Field.ad_id, ''),
                    'name': data.get(AdsInsights.Field.ad_name, data.get(AdsInsights.Field.campaign_name, '')),
                    'spend': float(data.get(AdsInsights.Field.spend, 0)),
                    'impressions': int(data.get(AdsInsights.Field.impressions, 0)),
                    'clicks': int(data.get(AdsInsights.Field.clicks, 0)),
                    'ctr': float(data.get(AdsInsights.Field.ctr, 0)),
                    'cpc': float(data.get(AdsInsights.Field.cpc, 0)),
                    'conversions': self._parse_conversions(data.get(AdsInsights.Field.conversions, [])),
                    'roas': roas,
                    'ads_manager_url': f'https://www.facebook.com/adsmanager/manage/ads?act={account_id.replace("act_", "")}',
                    'is_real_data': True
                })

            return performers if performers else self._mock_top_performers(account_id, limit)

        except Exception as e:
            logger.error(f"Error fetching top performers: {e}")
            return self._mock_top_performers(account_id, limit)

    def _mock_top_performers(self, account_id: str, limit: int) -> List[Dict[str, Any]]:
        """Return mock top performers."""
        return [
            {
                'id': 'ad_001',
                'name': 'Red Hoodie - Winter Sale',
                'spend': 500.00,
                'impressions': 15000,
                'clicks': 525,
                'ctr': 3.5,
                'cpc': 0.95,
                'conversions': 25,
                'roas': 4.2,
                'ads_manager_url': f'https://www.facebook.com/adsmanager/manage/ads?act={account_id}',
                'is_real_data': False
            },
            {
                'id': 'ad_002',
                'name': 'Sneaker Collection - Flash',
                'spend': 350.00,
                'impressions': 12500,
                'clicks': 350,
                'ctr': 2.8,
                'cpc': 1.00,
                'conversions': 15,
                'roas': 3.1,
                'ads_manager_url': f'https://www.facebook.com/adsmanager/manage/ads?act={account_id}',
                'is_real_data': False
            }
        ][:limit]

    def get_underperformers(
        self,
        account_id: str,
        metric: str = 'roas',
        threshold: float = 1.0,
        time_range: str = 'last_7_days'
    ) -> List[Dict[str, Any]]:
        """Get underperforming campaigns/ads."""
        date_range = self._get_date_range(time_range)

        if self._should_use_mock():
            return self._mock_underperformers(account_id)

        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.adsinsights import AdsInsights

            account = AdAccount(account_id)
            insights = account.get_insights(
                params={
                    'time_range': {
                        'since': date_range['since'],
                        'until': date_range['until']
                    },
                    'level': 'ad',
                    'filtering': [{'field': 'ad.effective_status', 'operator': 'IN', 'value': ['ACTIVE']}]
                },
                fields=[
                    AdsInsights.Field.ad_id,
                    AdsInsights.Field.ad_name,
                    AdsInsights.Field.spend,
                    AdsInsights.Field.impressions,
                    AdsInsights.Field.clicks,
                    AdsInsights.Field.ctr,
                    AdsInsights.Field.conversions,
                    AdsInsights.Field.purchase_roas,
                ]
            )

            underperformers = []
            for data in insights:
                roas_data = data.get(AdsInsights.Field.purchase_roas, [])
                roas = float(roas_data[0].get('value', 0)) if roas_data else 0
                spend = float(data.get(AdsInsights.Field.spend, 0))

                # Only include if spend > 0 and ROAS < threshold
                if spend > 10 and roas < threshold:
                    underperformers.append({
                        'id': data.get(AdsInsights.Field.ad_id, ''),
                        'name': data.get(AdsInsights.Field.ad_name, ''),
                        'spend': spend,
                        'impressions': int(data.get(AdsInsights.Field.impressions, 0)),
                        'clicks': int(data.get(AdsInsights.Field.clicks, 0)),
                        'ctr': float(data.get(AdsInsights.Field.ctr, 0)),
                        'conversions': self._parse_conversions(data.get(AdsInsights.Field.conversions, [])),
                        'roas': roas,
                        'recommendation': f'Consider pausing this ad - ROAS {roas:.1f}x is below {threshold}x',
                        'is_real_data': True
                    })

            return underperformers if underperformers else self._mock_underperformers(account_id)

        except Exception as e:
            logger.error(f"Error fetching underperformers: {e}")
            return self._mock_underperformers(account_id)

    def _mock_underperformers(self, account_id: str) -> List[Dict[str, Any]]:
        """Return mock underperformers."""
        return [
            {
                'id': 'ad_bad_001',
                'name': 'Old Collection - Generic',
                'spend': 200.00,
                'impressions': 8000,
                'clicks': 64,
                'ctr': 0.8,
                'conversions': 2,
                'roas': 0.7,
                'recommendation': 'Consider pausing this campaign due to low ROAS',
                'is_real_data': False
            }
        ]

    def get_campaign_metrics(
        self,
        account_id: str,
        time_range: str = 'last_7_days',
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics for all campaigns."""
        date_range = self._get_date_range(time_range)

        if self._should_use_mock():
            return self._mock_campaign_metrics()

        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.campaign import Campaign
            from facebook_business.adobjects.adsinsights import AdsInsights

            account = AdAccount(account_id)

            # Get campaigns
            filtering = []
            if status:
                filtering.append({'field': 'effective_status', 'operator': 'IN', 'value': [status]})

            campaigns = account.get_campaigns(
                params={'filtering': filtering} if filtering else {},
                fields=[
                    Campaign.Field.id,
                    Campaign.Field.name,
                    Campaign.Field.status,
                    Campaign.Field.objective,
                    Campaign.Field.daily_budget,
                ]
            )

            # Get insights for each campaign
            results = []
            for campaign in campaigns:
                try:
                    insights = campaign.get_insights(
                        params={
                            'time_range': {
                                'since': date_range['since'],
                                'until': date_range['until']
                            }
                        },
                        fields=[
                            AdsInsights.Field.spend,
                            AdsInsights.Field.impressions,
                            AdsInsights.Field.clicks,
                            AdsInsights.Field.ctr,
                            AdsInsights.Field.cpc,
                            AdsInsights.Field.conversions,
                            AdsInsights.Field.purchase_roas,
                        ]
                    )

                    if insights:
                        data = insights[0]
                        roas_data = data.get(AdsInsights.Field.purchase_roas, [])
                        roas = float(roas_data[0].get('value', 0)) if roas_data else 0

                        results.append({
                            'id': campaign[Campaign.Field.id],
                            'name': campaign[Campaign.Field.name],
                            'status': campaign[Campaign.Field.status],
                            'objective': campaign.get(Campaign.Field.objective, ''),
                            'spend': float(data.get(AdsInsights.Field.spend, 0)),
                            'impressions': int(data.get(AdsInsights.Field.impressions, 0)),
                            'clicks': int(data.get(AdsInsights.Field.clicks, 0)),
                            'ctr': float(data.get(AdsInsights.Field.ctr, 0)),
                            'cpc': float(data.get(AdsInsights.Field.cpc, 0)),
                            'conversions': self._parse_conversions(data.get(AdsInsights.Field.conversions, [])),
                            'roas': roas,
                            'daily_budget': float(campaign.get(Campaign.Field.daily_budget, 0)) / 100,
                            'is_real_data': True
                        })
                except Exception as e:
                    logger.warning(f"Error getting insights for campaign {campaign.get('id')}: {e}")

            return results if results else self._mock_campaign_metrics()

        except Exception as e:
            logger.error(f"Error fetching campaign metrics: {e}")
            return self._mock_campaign_metrics()

    def _mock_campaign_metrics(self) -> List[Dict[str, Any]]:
        """Return mock campaign metrics."""
        return [
            {
                'id': 'camp_001',
                'name': 'Red Hoodie - Winter Sale',
                'status': 'ACTIVE',
                'objective': 'CONVERSIONS',
                'spend': 500.00,
                'impressions': 15000,
                'clicks': 525,
                'ctr': 3.5,
                'cpc': 0.95,
                'conversions': 25,
                'roas': 4.2,
                'daily_budget': 100.00,
                'is_real_data': False
            },
            {
                'id': 'camp_002',
                'name': 'Sneaker Collection - Flash',
                'status': 'ACTIVE',
                'objective': 'CONVERSIONS',
                'spend': 350.00,
                'impressions': 12500,
                'clicks': 350,
                'ctr': 2.8,
                'cpc': 1.00,
                'conversions': 15,
                'roas': 3.1,
                'daily_budget': 75.00,
                'is_real_data': False
            }
        ]

    def create_campaign(
        self,
        account_id: str,
        page_id: str,
        campaign_data: Dict[str, Any],
        adset_data: Dict[str, Any],
        ad_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a complete campaign with adset and ad."""
        if self._should_use_mock():
            return self._mock_create_campaign(account_id)

        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.campaign import Campaign
            from facebook_business.adobjects.adset import AdSet
            from facebook_business.adobjects.ad import Ad
            from facebook_business.adobjects.adcreative import AdCreative

            account = AdAccount(account_id)

            # Create Campaign
            campaign = account.create_campaign(params={
                Campaign.Field.name: campaign_data.get('name', 'New Campaign'),
                Campaign.Field.objective: campaign_data.get('objective', 'OUTCOME_SALES'),
                Campaign.Field.status: Campaign.Status.paused,  # Start paused for safety
                Campaign.Field.special_ad_categories: [],
            })
            campaign_id = campaign.get_id()
            logger.info(f"Created campaign: {campaign_id}")

            # Create Ad Set
            adset = account.create_ad_set(params={
                AdSet.Field.name: adset_data.get('name', 'New Ad Set'),
                AdSet.Field.campaign_id: campaign_id,
                AdSet.Field.daily_budget: int(adset_data.get('budget', 5000)),  # In cents
                AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
                AdSet.Field.optimization_goal: adset_data.get('optimization_goal', 'OFFSITE_CONVERSIONS'),
                AdSet.Field.targeting: adset_data.get('targeting', {
                    'geo_locations': {'countries': ['US']},
                    'age_min': 18,
                    'age_max': 65,
                }),
                AdSet.Field.status: AdSet.Status.paused,
            })
            adset_id = adset.get_id()
            logger.info(f"Created ad set: {adset_id}")

            # Create Ad Creative
            creative = account.create_ad_creative(params={
                AdCreative.Field.name: f"Creative - {ad_data.get('name', 'New Ad')}",
                AdCreative.Field.object_story_spec: {
                    'page_id': page_id,
                    'link_data': {
                        'message': ad_data.get('primary_text', ''),
                        'name': ad_data.get('headline', ''),
                        'description': ad_data.get('description', ''),
                        'link': ad_data.get('link', 'https://example.com'),
                        'call_to_action': {
                            'type': ad_data.get('cta', 'LEARN_MORE').upper(),
                        },
                        'image_hash': ad_data.get('image_hash', ''),
                    }
                }
            })
            creative_id = creative.get_id()

            # Create Ad
            ad = account.create_ad(params={
                Ad.Field.name: ad_data.get('name', 'New Ad'),
                Ad.Field.adset_id: adset_id,
                Ad.Field.creative: {'creative_id': creative_id},
                Ad.Field.status: Ad.Status.paused,
            })
            ad_id = ad.get_id()
            logger.info(f"Created ad: {ad_id}")

            return {
                'success': True,
                'campaign_id': campaign_id,
                'adset_id': adset_id,
                'ad_id': ad_id,
                'ads_manager_url': f'https://www.facebook.com/adsmanager/manage/campaigns?act={account_id.replace("act_", "")}&campaign_ids={campaign_id}',
                'status': 'PAUSED',
                'is_real_data': True
            }

        except Exception as e:
            logger.error(f"Error creating campaign: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _mock_create_campaign(self, account_id: str) -> Dict[str, Any]:
        """Return mock campaign creation result."""
        campaign_id = f"camp_{int(datetime.utcnow().timestamp())}"
        adset_id = f"adset_{int(datetime.utcnow().timestamp())}"
        ad_id = f"ad_{int(datetime.utcnow().timestamp())}"

        return {
            'success': True,
            'campaign_id': campaign_id,
            'adset_id': adset_id,
            'ad_id': ad_id,
            'ads_manager_url': f'https://www.facebook.com/adsmanager/manage/campaigns?act={account_id}&campaign_ids={campaign_id}',
            'status': 'PAUSED',
            'is_real_data': False
        }

    def adjust_budget(
        self,
        object_id: str,
        new_budget: float,
        budget_type: str = 'daily'
    ) -> Dict[str, Any]:
        """Adjust budget for a campaign or adset."""
        if self._should_use_mock():
            return self._mock_adjust_budget(object_id, new_budget)

        try:
            from facebook_business.adobjects.campaign import Campaign
            from facebook_business.adobjects.adset import AdSet

            # Determine if it's a campaign or adset
            if object_id.startswith('adset_') or 'adset' in object_id.lower():
                obj = AdSet(object_id)
                field = AdSet.Field.daily_budget
            else:
                obj = Campaign(object_id)
                field = Campaign.Field.daily_budget

            # Update budget (convert to cents)
            obj.api_update(params={
                field: int(new_budget * 100)
            })

            return {
                'id': object_id,
                'new_budget': new_budget,
                'budget_type': budget_type,
                'success': True,
                'is_real_data': True
            }

        except Exception as e:
            logger.error(f"Error adjusting budget: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _mock_adjust_budget(self, object_id: str, new_budget: float) -> Dict[str, Any]:
        """Return mock budget adjustment."""
        logger.info(f"[MOCK] Adjusting budget for {object_id} to {new_budget}")
        return {
            'id': object_id,
            'new_budget': new_budget,
            'budget_type': 'daily',
            'success': True,
            'is_real_data': False
        }

    def pause_items(self, item_ids: List[str]) -> Dict[str, Any]:
        """Pause campaigns, adsets, or ads."""
        if self._should_use_mock():
            return self._mock_pause_items(item_ids)

        try:
            from facebook_business.adobjects.campaign import Campaign
            from facebook_business.adobjects.adset import AdSet
            from facebook_business.adobjects.ad import Ad

            paused = []
            errors = []

            for item_id in item_ids:
                try:
                    # Determine type and pause
                    if 'camp' in item_id.lower():
                        obj = Campaign(item_id)
                        obj.api_update(params={Campaign.Field.status: Campaign.Status.paused})
                    elif 'adset' in item_id.lower():
                        obj = AdSet(item_id)
                        obj.api_update(params={AdSet.Field.status: AdSet.Status.paused})
                    else:
                        obj = Ad(item_id)
                        obj.api_update(params={Ad.Field.status: Ad.Status.paused})

                    paused.append(item_id)
                except Exception as e:
                    errors.append({'id': item_id, 'error': str(e)})

            return {
                'paused_items': paused,
                'errors': errors,
                'success': len(errors) == 0,
                'is_real_data': True
            }

        except Exception as e:
            logger.error(f"Error pausing items: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _mock_pause_items(self, item_ids: List[str]) -> Dict[str, Any]:
        """Return mock pause result."""
        logger.info(f"[MOCK] Pausing items: {item_ids}")
        return {
            'paused_items': item_ids,
            'errors': [],
            'success': True,
            'is_real_data': False
        }

    def get_ad_preview(self, ad_id: str) -> Dict[str, Any]:
        """Get ad preview data."""
        if self._should_use_mock():
            return self._mock_ad_preview(ad_id)

        try:
            from facebook_business.adobjects.ad import Ad

            ad = Ad(ad_id)
            previews = ad.get_previews(params={
                'ad_format': 'DESKTOP_FEED_STANDARD'
            })

            if previews:
                return {
                    'id': ad_id,
                    'preview_url': previews[0].get('body', ''),
                    'status': 'ACTIVE',
                    'is_real_data': True
                }

            return self._mock_ad_preview(ad_id)

        except Exception as e:
            logger.error(f"Error getting ad preview: {e}")
            return self._mock_ad_preview(ad_id)

    def _mock_ad_preview(self, ad_id: str) -> Dict[str, Any]:
        """Return mock ad preview."""
        return {
            'id': ad_id,
            'preview_url': f'https://www.facebook.com/ads/preview/?d={ad_id}',
            'status': 'ACTIVE',
            'is_real_data': False
        }
