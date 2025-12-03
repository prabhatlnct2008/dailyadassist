"""Execution and management tools for the agent."""
from typing import Any, Optional, Type, List
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import json
import uuid
from datetime import datetime


class UpdatePreviewStateInput(BaseModel):
    """Input for UpdatePreviewStateTool."""
    primary_text: str = Field(description="Primary text for the ad")
    headline: str = Field(description="Headline for the ad")
    description: str = Field(default="", description="Description for the ad")
    cta: str = Field(default="learn_more", description="Call to action button")
    media_url: Optional[str] = Field(default=None, description="Media URL for the ad")


class UpdatePreviewStateTool(BaseTool):
    """Tool to update the ad preview in the UI."""

    name: str = "update_preview_state"
    description: str = """Update the ad preview shown in the War Room interface.
Use this after generating or modifying ad copy to show the user what the ad will look like."""
    args_schema: Type[BaseModel] = UpdatePreviewStateInput

    user_id: str = ""

    def _run(
        self,
        primary_text: str,
        headline: str,
        description: str = "",
        cta: str = "learn_more",
        media_url: Optional[str] = None
    ) -> str:
        """Execute the tool."""
        # In production, this would update a WebSocket/SSE channel
        # or store the state for the frontend to poll

        preview_state = {
            'primary_text': primary_text,
            'headline': headline,
            'description': description,
            'cta': cta,
            'media_url': media_url,
            'updated_at': datetime.utcnow().isoformat()
        }

        # Store in session/cache for frontend (simplified)
        return json.dumps({
            'success': True,
            'preview': preview_state,
            'message': 'Preview updated'
        }, indent=2)


class SaveDraftInput(BaseModel):
    """Input for SaveDraftTool."""
    campaign_name: str = Field(description="Name for the campaign")
    ad_name: str = Field(description="Name for the ad")
    primary_text: str = Field(description="Primary text")
    headline: str = Field(description="Headline")
    description: str = Field(default="", description="Description")
    cta: str = Field(default="learn_more", description="CTA button")
    budget: float = Field(default=50.0, description="Daily budget")
    media_url: Optional[str] = Field(default=None, description="Media URL")


class SaveDraftTool(BaseTool):
    """Tool to save an ad draft."""

    name: str = "save_draft"
    description: str = """Save the current ad as a draft.
Use this to persist the ad before publishing or when the user wants to save progress."""
    args_schema: Type[BaseModel] = SaveDraftInput

    user_id: str = ""

    def _run(
        self,
        campaign_name: str,
        ad_name: str,
        primary_text: str,
        headline: str,
        description: str = "",
        cta: str = "learn_more",
        budget: float = 50.0,
        media_url: Optional[str] = None
    ) -> str:
        """Execute the tool."""
        from ...extensions import db
        from ...models.draft import AdDraft

        draft = AdDraft(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            campaign_name=campaign_name,
            ad_set_name=f"{campaign_name} - Ad Set",
            ad_name=ad_name,
            primary_text=primary_text,
            headline=headline,
            description=description,
            cta=cta,
            budget=budget,
            media_url=media_url,
            status='draft',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        try:
            db.session.add(draft)
            db.session.commit()

            return json.dumps({
                'success': True,
                'draft_id': draft.id,
                'message': f'Draft "{ad_name}" saved successfully'
            }, indent=2)
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e)
            }, indent=2)


class GetCurrentDraftInput(BaseModel):
    """Input for GetCurrentDraftTool."""
    draft_id: Optional[str] = Field(default=None, description="Specific draft ID, or get latest")


class GetCurrentDraftTool(BaseTool):
    """Tool to get the current/latest draft."""

    name: str = "get_current_draft"
    description: str = """Get the current draft being worked on.
Use this to retrieve draft details for modification or publishing."""
    args_schema: Type[BaseModel] = GetCurrentDraftInput

    user_id: str = ""

    def _run(self, draft_id: Optional[str] = None) -> str:
        """Execute the tool."""
        from ...models.draft import AdDraft

        if draft_id:
            draft = AdDraft.query.filter_by(
                id=draft_id,
                user_id=self.user_id
            ).first()
        else:
            # Get the latest draft
            draft = AdDraft.query.filter_by(
                user_id=self.user_id,
                status='draft'
            ).order_by(AdDraft.updated_at.desc()).first()

        if not draft:
            return json.dumps({'error': 'No draft found'})

        return json.dumps({
            'draft': {
                'id': draft.id,
                'campaign_name': draft.campaign_name,
                'ad_name': draft.ad_name,
                'primary_text': draft.primary_text,
                'headline': draft.headline,
                'description': draft.description,
                'cta': draft.cta,
                'budget': draft.budget,
                'media_url': draft.media_url,
                'status': draft.status
            }
        }, indent=2)


class PublishCampaignInput(BaseModel):
    """Input for PublishCampaignTool."""
    draft_id: str = Field(description="ID of the draft to publish")
    confirm: bool = Field(default=False, description="Confirm publishing")


class PublishCampaignTool(BaseTool):
    """Tool to publish a campaign to Facebook."""

    name: str = "publish_campaign"
    description: str = """Publish a draft as a live Facebook campaign.
IMPORTANT: Always ask for user confirmation before publishing.
Returns campaign ID and Ads Manager link on success."""
    args_schema: Type[BaseModel] = PublishCampaignInput

    user_id: str = ""
    ad_account: Optional[Any] = None
    access_token: Optional[str] = None

    def _run(self, draft_id: str, confirm: bool = False) -> str:
        """Execute the tool."""
        if not confirm:
            return json.dumps({
                'requires_confirmation': True,
                'message': 'Publishing requires user confirmation. Please confirm to proceed.'
            })

        from ...models.draft import AdDraft, PublishedCampaign
        from ...models.facebook import FacebookPage
        from ...extensions import db
        from ..execution_agent import ExecutionAgent

        draft = AdDraft.query.filter_by(
            id=draft_id,
            user_id=self.user_id
        ).first()

        if not draft:
            return json.dumps({'error': 'Draft not found'})

        # Get primary page
        page = FacebookPage.query.filter_by(
            user_id=self.user_id,
            is_primary=True
        ).first()

        if not page:
            return json.dumps({'error': 'No Facebook page selected'})

        # Create campaign
        executor = ExecutionAgent(
            ad_account=self.ad_account,
            access_token=self.access_token
        )

        result = executor.create_campaign(
            draft=draft.to_preview_dict(),
            page_id=page.facebook_page_id
        )

        if result.get('success'):
            # Save published campaign record
            published = PublishedCampaign(
                id=str(uuid.uuid4()),
                user_id=self.user_id,
                ad_draft_id=draft.id,
                facebook_campaign_id=result['campaign_id'],
                facebook_adset_id=result.get('adset_id'),
                facebook_ad_id=result.get('ad_id'),
                ads_manager_url=result.get('ads_manager_url'),
                published_at=datetime.utcnow(),
                status='active',
                created_at=datetime.utcnow()
            )

            draft.status = 'published'

            try:
                db.session.add(published)
                db.session.commit()
            except Exception as e:
                return json.dumps({'error': f'Failed to save: {str(e)}'})

            return json.dumps({
                'success': True,
                'campaign_id': result['campaign_id'],
                'ads_manager_url': result.get('ads_manager_url'),
                'message': 'Campaign published successfully!'
            }, indent=2)

        return json.dumps(result)


class AdjustBudgetInput(BaseModel):
    """Input for AdjustBudgetTool."""
    object_id: str = Field(description="Campaign or ad set ID")
    new_budget: float = Field(description="New daily budget amount")


class AdjustBudgetTool(BaseTool):
    """Tool to adjust campaign budget."""

    name: str = "adjust_budget"
    description: str = """Adjust the daily budget for a campaign or ad set.
Use this for budget optimization recommendations."""
    args_schema: Type[BaseModel] = AdjustBudgetInput

    ad_account: Optional[Any] = None
    access_token: Optional[str] = None

    def _run(self, object_id: str, new_budget: float) -> str:
        """Execute the tool."""
        from ..execution_agent import ExecutionAgent

        executor = ExecutionAgent(
            ad_account=self.ad_account,
            access_token=self.access_token
        )

        result = executor.adjust_budget(object_id, new_budget)
        return json.dumps(result, indent=2)


class PauseItemsInput(BaseModel):
    """Input for PauseItemsTool."""
    item_ids: List[str] = Field(description="List of campaign/ad set/ad IDs to pause")


class PauseItemsTool(BaseTool):
    """Tool to pause campaigns or ads."""

    name: str = "pause_items"
    description: str = """Pause one or more campaigns, ad sets, or ads.
Use this for underperforming items or when the user wants to stop spend."""
    args_schema: Type[BaseModel] = PauseItemsInput

    ad_account: Optional[Any] = None
    access_token: Optional[str] = None

    def _run(self, item_ids: List[str]) -> str:
        """Execute the tool."""
        from ..execution_agent import ExecutionAgent

        executor = ExecutionAgent(
            ad_account=self.ad_account,
            access_token=self.access_token
        )

        result = executor.pause_items(item_ids)
        return json.dumps(result, indent=2)
