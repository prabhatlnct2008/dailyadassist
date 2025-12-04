"""Utility tools for the agent."""
from typing import Any, Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import json
import uuid
from datetime import datetime


class LogDecisionInput(BaseModel):
    """Input for LogDecisionTool."""
    action: str = Field(description="The action taken")
    rationale: str = Field(description="The reasoning behind the action")
    entity_type: Optional[str] = Field(default=None, description="Type of entity affected")
    entity_id: Optional[str] = Field(default=None, description="ID of entity affected")


class LogDecisionTool(BaseTool):
    """Tool to log agent decisions for transparency."""

    name: str = "log_decision"
    description: str = """Log a decision or action for the activity log.
Use this to record important decisions and reasoning for user transparency."""
    args_schema: Type[BaseModel] = LogDecisionInput

    user_id: str = ""

    def _run(
        self,
        action: str,
        rationale: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> str:
        """Execute the tool."""
        from ...extensions import db
        from ...models.activity import ActivityLog

        log_entry = ActivityLog(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            action_type=action,
            entity_type=entity_type,
            entity_id=entity_id,
            rationale=rationale,
            metadata={'logged_by': 'agent'},
            created_at=datetime.utcnow(),
            is_agent_action=True
        )

        try:
            db.session.add(log_entry)
            db.session.commit()

            return json.dumps({
                'success': True,
                'log_id': log_entry.id,
                'message': 'Decision logged'
            })
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e)
            })


class SimulateResultsInput(BaseModel):
    """Input for SimulateResultsTool."""
    budget: float = Field(description="Daily budget for simulation")
    duration_days: int = Field(default=7, description="Number of days to simulate")
    objective: str = Field(default="conversions", description="Campaign objective")


class SimulateResultsTool(BaseTool):
    """Tool to simulate campaign results (heuristic)."""

    name: str = "simulate_results"
    description: str = """Simulate expected results for a campaign.
This is a rough estimate based on historical averages - actual results will vary.
Use for setting expectations only."""
    args_schema: Type[BaseModel] = SimulateResultsInput

    def _run(
        self,
        budget: float,
        duration_days: int = 7,
        objective: str = "conversions"
    ) -> str:
        """Execute the tool."""
        total_budget = budget * duration_days

        # Industry average estimates (these would be refined with actual data)
        avg_cpm = 10.0  # $10 per 1000 impressions
        avg_ctr = 1.5  # 1.5% click-through rate
        avg_cvr = 3.0  # 3% conversion rate

        # Calculate estimates
        estimated_impressions = int((total_budget / avg_cpm) * 1000)
        estimated_clicks = int(estimated_impressions * (avg_ctr / 100))
        estimated_conversions = int(estimated_clicks * (avg_cvr / 100))
        estimated_cpc = total_budget / estimated_clicks if estimated_clicks > 0 else 0
        estimated_cpa = total_budget / estimated_conversions if estimated_conversions > 0 else 0

        simulation = {
            'budget_per_day': budget,
            'duration_days': duration_days,
            'total_budget': total_budget,
            'estimates': {
                'impressions': f"{estimated_impressions:,}",
                'clicks': f"{estimated_clicks:,}",
                'conversions': f"{estimated_conversions:,}",
                'cpc': f"${estimated_cpc:.2f}",
                'cpa': f"${estimated_cpa:.2f}"
            },
            'ranges': {
                'impressions': f"{int(estimated_impressions * 0.7):,} - {int(estimated_impressions * 1.3):,}",
                'clicks': f"{int(estimated_clicks * 0.7):,} - {int(estimated_clicks * 1.3):,}",
                'conversions': f"{int(estimated_conversions * 0.5):,} - {int(estimated_conversions * 1.5):,}"
            },
            'disclaimer': "These are rough estimates based on industry averages. Actual results depend on creative quality, targeting, and market conditions."
        }

        return json.dumps(simulation, indent=2)
