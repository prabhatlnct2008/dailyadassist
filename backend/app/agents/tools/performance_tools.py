"""Performance analysis tools for the agent."""
from typing import Any, Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import json


class GetAccountStatsInput(BaseModel):
    """Input for GetAccountStatsTool."""
    time_range: str = Field(
        default="last_7_days",
        description="Time range for stats: today, yesterday, last_7_days, last_14_days, last_30_days"
    )
    level: str = Field(
        default="account",
        description="Level of aggregation: account, campaign, adset, ad"
    )


class GetAccountStatsTool(BaseTool):
    """Tool to get ad account statistics."""

    name: str = "get_account_stats"
    description: str = """Get performance statistics for the ad account.
Use this to understand overall account performance including spend, impressions, clicks, CTR, CPC, conversions, and ROAS.
Input should specify time_range (e.g., 'last_7_days') and level (e.g., 'account', 'campaign')."""
    args_schema: Type[BaseModel] = GetAccountStatsInput

    ad_account: Optional[Any] = None
    access_token: Optional[str] = None

    def _run(self, time_range: str = "last_7_days", level: str = "account") -> str:
        """Execute the tool."""
        from ...services.facebook_service import FacebookService

        if self.access_token and self.ad_account:
            fb_service = FacebookService(self.access_token)
            stats = fb_service.get_account_stats(
                account_id=self.ad_account.facebook_account_id,
                time_range=time_range,
                level=level
            )
        else:
            # Mock data
            stats = {
                'spend': 1500.00,
                'impressions': 45000,
                'clicks': 1200,
                'ctr': 2.67,
                'cpc': 1.25,
                'conversions': 45,
                'roas': 3.2,
                'active_campaigns': 3,
                'time_range': time_range
            }

        return json.dumps(stats, indent=2)


class GetTopPerformersInput(BaseModel):
    """Input for GetTopPerformersTool."""
    metric: str = Field(
        default="roas",
        description="Metric to sort by: roas, ctr, conversions, spend"
    )
    time_range: str = Field(
        default="last_7_days",
        description="Time range for analysis"
    )
    limit: int = Field(
        default=5,
        description="Number of top performers to return"
    )


class GetTopPerformersTool(BaseTool):
    """Tool to get top performing ads."""

    name: str = "get_top_performers"
    description: str = """Get the top performing campaigns or ads.
Use this to identify what's working well and worth scaling.
Returns ads sorted by the specified metric (roas, ctr, conversions)."""
    args_schema: Type[BaseModel] = GetTopPerformersInput

    ad_account: Optional[Any] = None
    access_token: Optional[str] = None

    def _run(
        self,
        metric: str = "roas",
        time_range: str = "last_7_days",
        limit: int = 5
    ) -> str:
        """Execute the tool."""
        from ...services.facebook_service import FacebookService

        if self.access_token and self.ad_account:
            fb_service = FacebookService(self.access_token)
            performers = fb_service.get_top_performers(
                account_id=self.ad_account.facebook_account_id,
                metric=metric,
                time_range=time_range,
                limit=limit
            )
        else:
            # Mock data
            performers = [
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

        return json.dumps({'top_performers': performers, 'metric': metric}, indent=2)


class GetUnderperformersInput(BaseModel):
    """Input for GetUnderperformersTool."""
    metric: str = Field(default="roas", description="Metric to evaluate")
    threshold: float = Field(default=1.0, description="Threshold below which is underperforming")
    time_range: str = Field(default="last_7_days", description="Time range for analysis")


class GetUnderperformersTool(BaseTool):
    """Tool to get underperforming ads."""

    name: str = "get_underperformers"
    description: str = """Get underperforming campaigns or ads that should be paused or improved.
Use this to identify budget-wasting ads below a performance threshold."""
    args_schema: Type[BaseModel] = GetUnderperformersInput

    ad_account: Optional[Any] = None
    access_token: Optional[str] = None

    def _run(
        self,
        metric: str = "roas",
        threshold: float = 1.0,
        time_range: str = "last_7_days"
    ) -> str:
        """Execute the tool."""
        from ...services.facebook_service import FacebookService

        if self.access_token and self.ad_account:
            fb_service = FacebookService(self.access_token)
            underperformers = fb_service.get_underperformers(
                account_id=self.ad_account.facebook_account_id,
                metric=metric,
                threshold=threshold,
                time_range=time_range
            )
        else:
            # Mock data
            underperformers = [
                {
                    'id': 'ad_bad_001',
                    'name': 'Old Collection - Generic',
                    'spend': 200.00,
                    'roas': 0.7,
                    'ctr': 0.8,
                    'conversions': 2,
                    'recommendation': 'Consider pausing this campaign'
                }
            ]

        return json.dumps({
            'underperformers': underperformers,
            'threshold': threshold,
            'metric': metric
        }, indent=2)


class SummarizePerformanceInput(BaseModel):
    """Input for SummarizePerformanceTool."""
    time_range: str = Field(default="last_7_days", description="Time range for summary")


class SummarizePerformanceTool(BaseTool):
    """Tool to generate a plain-language performance summary."""

    name: str = "summarize_performance"
    description: str = """Generate a plain-language summary of account performance.
Use this to give the user an easy-to-understand overview of how their ads are doing."""
    args_schema: Type[BaseModel] = SummarizePerformanceInput

    ad_account: Optional[Any] = None
    access_token: Optional[str] = None

    def _run(self, time_range: str = "last_7_days") -> str:
        """Execute the tool."""
        from ..performance_analyst import PerformanceAnalystAgent

        analyst = PerformanceAnalystAgent(
            ad_account=self.ad_account,
            access_token=self.access_token
        )

        summary = analyst.generate_summary_text(time_range)
        return summary
