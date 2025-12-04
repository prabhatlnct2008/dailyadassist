"""Performance Analyst Agent - Analyzes historical ad performance."""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class PerformanceAnalystAgent:
    """
    Specialized agent for analyzing ad performance.

    Responsibilities:
    - Read historical stats
    - Identify winners and losers
    - Detect trends
    - Generate performance summaries
    """

    def __init__(
        self,
        ad_account: Optional[Any] = None,
        access_token: Optional[str] = None
    ):
        """Initialize the performance analyst."""
        self.ad_account = ad_account
        self.access_token = access_token

        if access_token:
            from ..services.facebook_service import FacebookService
            self.fb_service = FacebookService(access_token)
        else:
            self.fb_service = None

    def get_summary(self, time_range: str = 'last_7_days') -> Dict[str, Any]:
        """Get performance summary for a time range."""
        if self.fb_service and self.ad_account:
            try:
                return self.fb_service.get_account_stats(
                    account_id=self.ad_account.facebook_account_id,
                    time_range=time_range
                )
            except Exception as e:
                logger.error(f"Error fetching stats: {e}")

        # Mock data
        return {
            'spend': 1500.00,
            'impressions': 45000,
            'clicks': 1200,
            'ctr': 2.67,
            'cpc': 1.25,
            'conversions': 45,
            'roas': 3.2,
            'active_campaigns': 3
        }

    def get_top_performers(
        self,
        metric: str = 'roas',
        limit: int = 5,
        time_range: str = 'last_7_days'
    ) -> List[Dict[str, Any]]:
        """Get top performing ads."""
        if self.fb_service and self.ad_account:
            try:
                return self.fb_service.get_top_performers(
                    account_id=self.ad_account.facebook_account_id,
                    metric=metric,
                    limit=limit,
                    time_range=time_range
                )
            except Exception as e:
                logger.error(f"Error fetching top performers: {e}")

        # Mock data
        return [
            {
                'id': 'ad_001',
                'name': 'Red Hoodie - Winter Sale',
                'spend': 500.00,
                'roas': 4.2,
                'ctr': 3.5,
                'conversions': 25
            },
            {
                'id': 'ad_002',
                'name': 'Sneaker Collection - Flash',
                'spend': 350.00,
                'roas': 3.1,
                'ctr': 2.8,
                'conversions': 15
            }
        ]

    def get_underperformers(
        self,
        metric: str = 'roas',
        threshold: float = 1.0,
        time_range: str = 'last_7_days'
    ) -> List[Dict[str, Any]]:
        """Get underperforming ads."""
        if self.fb_service and self.ad_account:
            try:
                return self.fb_service.get_underperformers(
                    account_id=self.ad_account.facebook_account_id,
                    metric=metric,
                    threshold=threshold,
                    time_range=time_range
                )
            except Exception as e:
                logger.error(f"Error fetching underperformers: {e}")

        # Mock data
        return [
            {
                'id': 'ad_bad_001',
                'name': 'Old Collection - Generic',
                'spend': 200.00,
                'roas': 0.7,
                'ctr': 0.8,
                'conversions': 2
            }
        ]

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on performance data."""
        top_performers = self.get_top_performers(limit=3)
        underperformers = self.get_underperformers()

        recommendations = []

        # Recommend scaling winners
        for perf in top_performers:
            if perf.get('roas', 0) > 3.0:
                recommendations.append({
                    'type': 'increase_budget',
                    'entity_id': perf['id'],
                    'entity_name': perf['name'],
                    'action': f"Increase budget by 30%",
                    'rationale': f"Consistent ROAS of {perf['roas']:.1f}x",
                    'expected_impact': 'More conversions at similar efficiency'
                })

        # Recommend pausing losers
        for perf in underperformers:
            if perf.get('roas', 0) < 1.0:
                recommendations.append({
                    'type': 'pause_campaign',
                    'entity_id': perf['id'],
                    'entity_name': perf['name'],
                    'action': "Pause this campaign",
                    'rationale': f"ROAS of {perf['roas']:.1f}x is below breakeven",
                    'expected_impact': 'Save budget for better performers'
                })

        return recommendations

    def analyze_trends(self, time_range: str = 'last_30_days') -> Dict[str, Any]:
        """Analyze performance trends."""
        # In production, this would analyze day-over-day changes
        return {
            'spend_trend': 'increasing',
            'spend_change_pct': 15.5,
            'roas_trend': 'stable',
            'roas_change_pct': 2.3,
            'ctr_trend': 'improving',
            'ctr_change_pct': 8.7,
            'insights': [
                "Your CTR has improved 8.7% over the past month",
                "Spend is up 15.5%, but ROAS remains stable",
                "Weekend performance is 20% better than weekdays"
            ]
        }

    def compare_performance(
        self,
        period1: str,
        period2: str
    ) -> Dict[str, Any]:
        """Compare performance between two periods."""
        stats1 = self.get_summary(period1)
        stats2 = self.get_summary(period2)

        def calc_change(old, new):
            if old == 0:
                return 0
            return ((new - old) / old) * 100

        return {
            'period1': period1,
            'period2': period2,
            'spend_change': calc_change(stats1['spend'], stats2['spend']),
            'roas_change': calc_change(stats1['roas'], stats2['roas']),
            'ctr_change': calc_change(stats1['ctr'], stats2['ctr']),
            'conversions_change': calc_change(stats1['conversions'], stats2['conversions'])
        }

    def generate_summary_text(self, time_range: str = 'last_7_days') -> str:
        """Generate a plain-language performance summary."""
        stats = self.get_summary(time_range)
        top = self.get_top_performers(limit=1)
        under = self.get_underperformers()

        summary = f"""Performance Summary ({time_range.replace('_', ' ').title()}):

- Total Spend: ${stats['spend']:,.2f}
- Impressions: {stats['impressions']:,}
- Clicks: {stats['clicks']:,} (CTR: {stats['ctr']:.2f}%)
- Conversions: {stats['conversions']}
- Average ROAS: {stats['roas']:.1f}x
- Active Campaigns: {stats['active_campaigns']}

Top Performer: "{top[0]['name']}" with ROAS {top[0]['roas']:.1f}x
"""
        if under:
            summary += f"\nUnderperformer: \"{under[0]['name']}\" with ROAS {under[0]['roas']:.1f}x (consider pausing)"

        return summary
