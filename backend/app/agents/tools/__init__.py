"""Agent tools package."""
from typing import List, Any, Optional
from langchain.tools import BaseTool

from .performance_tools import (
    GetAccountStatsTool,
    GetTopPerformersTool,
    GetUnderperformersTool,
    SummarizePerformanceTool
)
from .creative_tools import (
    GenerateCreativeBriefsTool,
    GenerateAdCopyTool,
    SuggestAudiencesTool,
    SearchStockImagesTool
)
from .execution_tools import (
    UpdatePreviewStateTool,
    SaveDraftTool,
    GetCurrentDraftTool,
    PublishCampaignTool,
    AdjustBudgetTool,
    PauseItemsTool
)
from .utility_tools import (
    LogDecisionTool,
    SimulateResultsTool
)


def get_all_tools(
    user_id: str,
    ad_account: Optional[Any] = None,
    facebook_connection: Optional[Any] = None,
    preferences: Optional[Any] = None
) -> List[BaseTool]:
    """Get all available tools for the agent."""

    access_token = None
    if facebook_connection:
        access_token = facebook_connection.get_access_token()

    tools = [
        # Performance tools
        GetAccountStatsTool(ad_account=ad_account, access_token=access_token),
        GetTopPerformersTool(ad_account=ad_account, access_token=access_token),
        GetUnderperformersTool(ad_account=ad_account, access_token=access_token),
        SummarizePerformanceTool(ad_account=ad_account, access_token=access_token),

        # Creative tools
        GenerateCreativeBriefsTool(preferences=preferences),
        GenerateAdCopyTool(preferences=preferences),
        SuggestAudiencesTool(preferences=preferences),
        SearchStockImagesTool(),

        # Execution tools
        UpdatePreviewStateTool(user_id=user_id),
        SaveDraftTool(user_id=user_id),
        GetCurrentDraftTool(user_id=user_id),
        PublishCampaignTool(
            user_id=user_id,
            ad_account=ad_account,
            access_token=access_token
        ),
        AdjustBudgetTool(ad_account=ad_account, access_token=access_token),
        PauseItemsTool(ad_account=ad_account, access_token=access_token),

        # Utility tools
        LogDecisionTool(user_id=user_id),
        SimulateResultsTool()
    ]

    return tools


__all__ = [
    'get_all_tools',
    'GetAccountStatsTool',
    'GetTopPerformersTool',
    'GetUnderperformersTool',
    'SummarizePerformanceTool',
    'GenerateCreativeBriefsTool',
    'GenerateAdCopyTool',
    'SuggestAudiencesTool',
    'SearchStockImagesTool',
    'UpdatePreviewStateTool',
    'SaveDraftTool',
    'GetCurrentDraftTool',
    'PublishCampaignTool',
    'AdjustBudgetTool',
    'PauseItemsTool',
    'LogDecisionTool',
    'SimulateResultsTool'
]
