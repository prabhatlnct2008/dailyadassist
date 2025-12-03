"""Performance and metrics schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class PerformanceSummary(BaseModel):
    """Summary of account performance."""
    time_range: str
    total_spend: float = 0.0
    total_impressions: int = 0
    total_clicks: int = 0
    average_ctr: float = 0.0
    average_cpc: float = 0.0
    total_conversions: int = 0
    average_roas: float = 0.0
    active_campaigns: int = 0
    is_mock_data: bool = False


class TopPerformer(BaseModel):
    """A top performing campaign/ad."""
    id: str
    name: str
    spend: float = 0.0
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    cpc: float = 0.0
    conversions: int = 0
    roas: float = 0.0
    ads_manager_url: Optional[str] = None


class UnderPerformer(BaseModel):
    """An underperforming campaign/ad."""
    id: str
    name: str
    spend: float = 0.0
    roas: float = 0.0
    ctr: float = 0.0
    conversions: int = 0
    recommendation: str = ""


class CampaignMetrics(BaseModel):
    """Metrics for a single campaign."""
    id: str
    name: str
    status: str
    objective: str
    spend: float = 0.0
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    cpc: float = 0.0
    conversions: int = 0
    roas: float = 0.0
    daily_budget: float = 0.0


class DailySnapshot(BaseModel):
    """Daily performance snapshot."""
    date: date
    spend: float = 0.0
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    conversions: int = 0
    roas: float = 0.0
