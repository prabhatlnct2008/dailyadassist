"""Memory Retrieval Service for page-scoped agent context."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from ..extensions import db
from ..models.conversation import Conversation, Message, ConversationType
from ..models.workspace import Workspace, WorkspacePage
from ..models.product import Product, PageProduct
from ..models.facebook import FacebookPage
from .facebook_service import FacebookService

logger = logging.getLogger(__name__)


class MemoryRetrievalService:
    """Handles page-scoped memory for agent context."""

    def __init__(self, facebook_service: Optional[FacebookService] = None):
        """Initialize the memory retrieval service.

        Args:
            facebook_service: Optional FacebookService for performance data
        """
        self.facebook_service = facebook_service

    def get_context_for_chat(
        self,
        chat_type: ConversationType,
        workspace_id: str,
        page_id: Optional[str] = None,
        product_id: Optional[str] = None
    ) -> dict:
        """
        Returns context dict based on chat type:
        - PAGE_WAR_ROOM: page history, page settings, active product, page products, page performance
        - ACCOUNT_OVERVIEW: workspace summary, all pages performance, recommendations

        Args:
            chat_type: Type of conversation (PAGE_WAR_ROOM or ACCOUNT_OVERVIEW)
            workspace_id: ID of the workspace
            page_id: Optional ID of the workspace page (required for PAGE_WAR_ROOM)
            product_id: Optional ID of the active product

        Returns:
            Dictionary with context data appropriate for the chat type
        """
        try:
            if chat_type == ConversationType.PAGE_WAR_ROOM:
                if not page_id:
                    logger.warning("PAGE_WAR_ROOM chat requires page_id")
                    return {}

                return {
                    'chat_type': 'page_war_room',
                    'page_history': self._get_page_conversation_history(page_id),
                    'page_settings': self._get_page_settings(page_id),
                    'active_product': self._get_product_context(product_id) if product_id else None,
                    'page_products': self._get_page_products(page_id),
                    'page_performance': self._get_page_performance(page_id),
                }

            elif chat_type == ConversationType.ACCOUNT_OVERVIEW:
                return {
                    'chat_type': 'account_overview',
                    'workspace_summary': self._get_workspace_summary(workspace_id),
                    'all_pages_performance': self._get_all_pages_performance(workspace_id),
                    'pinned_legacy_summary': self._get_pinned_summary(workspace_id),
                }

            else:
                # Legacy or unknown type
                return {
                    'chat_type': str(chat_type),
                    'workspace_summary': self._get_workspace_summary(workspace_id)
                }

        except Exception as e:
            logger.error(f"Error retrieving chat context: {e}", exc_info=True)
            return {'error': str(e)}

    def _get_page_conversation_history(self, page_id: str, limit: int = 50) -> List[dict]:
        """Get recent messages from page's war room.

        Args:
            page_id: ID of the workspace page
            limit: Maximum number of messages to retrieve

        Returns:
            List of message dictionaries
        """
        try:
            # Find the conversation for this page
            conversation = Conversation.query.filter_by(
                workspace_page_id=page_id,
                chat_type=ConversationType.PAGE_WAR_ROOM,
                is_archived=False
            ).first()

            if not conversation:
                return []

            # Get recent messages
            messages = Message.query.filter_by(
                conversation_id=conversation.id,
                is_visible=True
            ).order_by(Message.created_at.desc()).limit(limit).all()

            # Reverse to get chronological order
            messages.reverse()

            return [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ]

        except Exception as e:
            logger.error(f"Error fetching page conversation history: {e}", exc_info=True)
            return []

    def _get_page_settings(self, page_id: str) -> dict:
        """Get page tone, CTA style, target markets.

        Args:
            page_id: ID of the workspace page

        Returns:
            Dictionary with page settings
        """
        try:
            workspace_page = WorkspacePage.query.get(page_id)

            if not workspace_page:
                return {}

            # Get the Facebook page info too
            fb_page = workspace_page.facebook_page if hasattr(workspace_page, 'facebook_page') else None

            return {
                'page_id': workspace_page.id,
                'page_name': fb_page.name if fb_page else 'Unknown Page',
                'default_tone': workspace_page.default_tone,
                'default_cta_style': workspace_page.default_cta_style,
                'target_markets': workspace_page.target_markets or [],
                'is_primary': workspace_page.is_primary,
            }

        except Exception as e:
            logger.error(f"Error fetching page settings: {e}", exc_info=True)
            return {}

    def _get_page_products(self, page_id: str) -> List[dict]:
        """Get products tagged to this page.

        Args:
            page_id: ID of the workspace page

        Returns:
            List of product dictionaries
        """
        try:
            # Get page-product associations
            page_products = PageProduct.query.filter_by(
                workspace_page_id=page_id
            ).all()

            products = []
            for pp in page_products:
                product = pp.product if hasattr(pp, 'product') else None
                if product and product.is_active:
                    products.append({
                        'id': product.id,
                        'name': product.name,
                        'short_description': product.short_description,
                        'price': product.price,
                        'price_range_min': product.price_range_min,
                        'price_range_max': product.price_range_max,
                        'currency': product.currency,
                        'usp': product.usp,
                        'target_audience': product.target_audience,
                        'seasonality': product.seasonality,
                        'tags': product.tags or [],
                        'is_default': pp.is_default,
                    })

            return products

        except Exception as e:
            logger.error(f"Error fetching page products: {e}", exc_info=True)
            return []

    def _get_page_performance(self, page_id: str, days: int = 7) -> dict:
        """Get recent performance metrics for page's campaigns.

        Args:
            page_id: ID of the workspace page
            days: Number of days to look back

        Returns:
            Dictionary with performance metrics
        """
        try:
            # Get workspace page to find the ad account
            workspace_page = WorkspacePage.query.get(page_id)
            if not workspace_page:
                return {'error': 'Page not found'}

            workspace = workspace_page.workspace if hasattr(workspace_page, 'workspace') else None
            if not workspace or not workspace.ad_account_id:
                return {'message': 'No ad account connected'}

            # If we have a Facebook service, get real performance data
            if self.facebook_service:
                try:
                    # Get page-specific performance
                    # Note: This would need page-specific filtering in production
                    time_range = 'last_7_days' if days == 7 else f'last_{days}_days'
                    stats = self.facebook_service.get_account_stats(
                        workspace.ad_account.facebook_account_id,
                        time_range=time_range
                    )
                    return stats
                except Exception as e:
                    logger.warning(f"Error fetching real performance data: {e}")

            # Return placeholder if no service available
            return {
                'message': 'Performance data not available',
                'period_days': days
            }

        except Exception as e:
            logger.error(f"Error fetching page performance: {e}", exc_info=True)
            return {'error': str(e)}

    def _get_workspace_summary(self, workspace_id: str) -> dict:
        """Get overall workspace stats.

        Args:
            workspace_id: ID of the workspace

        Returns:
            Dictionary with workspace summary
        """
        try:
            workspace = Workspace.query.get(workspace_id)
            if not workspace:
                return {}

            # Count pages and products
            pages_count = WorkspacePage.query.filter_by(
                workspace_id=workspace_id,
                is_included=True
            ).count()

            products_count = Product.query.filter_by(
                workspace_id=workspace_id,
                is_active=True
            ).count()

            # Get active conversations count
            conversations_count = Conversation.query.filter_by(
                workspace_id=workspace_id,
                is_archived=False
            ).count()

            return {
                'workspace_id': workspace.id,
                'workspace_name': workspace.name,
                'default_daily_budget': workspace.default_daily_budget,
                'default_currency': workspace.default_currency,
                'default_objective': workspace.default_objective,
                'timezone': workspace.timezone,
                'facebook_connected': workspace.facebook_connected,
                'setup_completed': workspace.setup_completed,
                'pages_count': pages_count,
                'products_count': products_count,
                'conversations_count': conversations_count,
            }

        except Exception as e:
            logger.error(f"Error fetching workspace summary: {e}", exc_info=True)
            return {}

    def _get_all_pages_performance(self, workspace_id: str) -> List[dict]:
        """Get performance summary for all pages.

        Args:
            workspace_id: ID of the workspace

        Returns:
            List of page performance dictionaries
        """
        try:
            pages = WorkspacePage.query.filter_by(
                workspace_id=workspace_id,
                is_included=True
            ).all()

            results = []
            for page in pages:
                fb_page = page.facebook_page if hasattr(page, 'facebook_page') else None
                page_info = {
                    'page_id': page.id,
                    'page_name': fb_page.name if fb_page else 'Unknown Page',
                    'is_primary': page.is_primary,
                    'default_tone': page.default_tone,
                }

                # Get performance for this page
                perf = self._get_page_performance(page.id, days=7)
                page_info['performance'] = perf

                results.append(page_info)

            return results

        except Exception as e:
            logger.error(f"Error fetching all pages performance: {e}", exc_info=True)
            return []

    def _get_product_context(self, product_id: str) -> dict:
        """Get context for a specific product.

        Args:
            product_id: ID of the product

        Returns:
            Dictionary with product context
        """
        try:
            product = Product.query.get(product_id)
            if not product or not product.is_active:
                return {}

            return {
                'id': product.id,
                'name': product.name,
                'short_description': product.short_description,
                'long_description': product.long_description,
                'price': product.price,
                'price_range_min': product.price_range_min,
                'price_range_max': product.price_range_max,
                'currency': product.currency,
                'usp': product.usp,
                'target_audience': product.target_audience,
                'seasonality': product.seasonality,
                'tags': product.tags or [],
                'has_images': bool(product.primary_image_url),
            }

        except Exception as e:
            logger.error(f"Error fetching product context: {e}", exc_info=True)
            return {}

    def _get_pinned_summary(self, workspace_id: str) -> Optional[dict]:
        """Get pinned legacy summary for Account Overview.

        Args:
            workspace_id: ID of the workspace

        Returns:
            Pinned summary data or None
        """
        try:
            # Find pinned conversation in this workspace
            pinned_convo = Conversation.query.filter_by(
                workspace_id=workspace_id,
                is_pinned=True
            ).first()

            if not pinned_convo or not pinned_convo.pinned_content:
                return None

            import json
            try:
                pinned_data = json.loads(pinned_convo.pinned_content)
                return pinned_data
            except json.JSONDecodeError:
                return {
                    'type': 'text',
                    'content': pinned_convo.pinned_content
                }

        except Exception as e:
            logger.error(f"Error fetching pinned summary: {e}", exc_info=True)
            return None
