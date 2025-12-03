"""Agent orchestration service."""
from typing import Dict, Any, List, Optional, Generator
from datetime import datetime
import json
import logging
import os

from flask import current_app

logger = logging.getLogger(__name__)


class AgentService:
    """Service for orchestrating the AI agent."""

    def __init__(
        self,
        user_id: str,
        conversation: Optional[Any] = None,
        preferences: Optional[Any] = None,
        ad_account: Optional[Any] = None
    ):
        """Initialize the agent service."""
        self.user_id = user_id
        self.conversation = conversation
        self.preferences = preferences
        self.ad_account = ad_account

        # Initialize LLM based on config
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize the LLM based on configuration."""
        provider = os.environ.get('LLM_PROVIDER', 'openai')

        try:
            if provider == 'anthropic':
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY')
                )
            else:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model="gpt-4-turbo-preview",
                    openai_api_key=os.environ.get('OPENAI_API_KEY'),
                    streaming=True
                )
        except Exception as e:
            logger.warning(f"Failed to initialize LLM: {e}. Using mock responses.")
            return None

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the orchestrator agent."""
        tone = self.preferences.default_tone if self.preferences else 'friendly'
        budget = self.preferences.default_daily_budget if self.preferences else 50

        return f"""You are a Senior Media Buyer and Facebook Ads Strategist AI assistant named "Daily Ad Agent".

Your persona is {tone} and professional. You help busy marketers and founders manage their Facebook ads efficiently.

Your capabilities:
1. Analyze past ad performance and identify winners/losers
2. Generate creative briefs and ad copy
3. Suggest target audiences based on product info
4. Create and manage Facebook ad campaigns
5. Provide daily performance summaries and recommendations

User's default daily budget: ${budget}

Current conversation state: {self.conversation.state if self.conversation else 'idle'}

Guidelines:
- Be proactive and suggest next steps
- Always explain your reasoning
- Ask for confirmation before publishing ads
- Warn about budgets that exceed 5x the default
- Check for policy violations before publishing
- Reference past winners when suggesting new ads
- Keep responses concise but informative

When drafting ads:
- Primary Text: 125-300 characters
- Headline: max 40 characters
- Description: 30-60 characters
- Always suggest a CTA

You have access to tools for:
- get_account_stats: Get performance metrics
- get_top_performers: Find winning ads
- get_underperformers: Find poor performers
- generate_creative_briefs: Create ad concepts
- generate_ad_copy: Write ad text variants
- suggest_audiences: Recommend targeting
- update_preview: Update the ad preview UI
- publish_campaign: Create Facebook campaign
- adjust_budget: Change campaign budget
- pause_items: Pause campaigns/ads
"""

    def chat(self, message: str) -> Generator[str, None, None]:
        """Process a chat message and stream the response."""
        if not self.llm:
            # Mock response when LLM is not available
            yield from self._mock_chat_response(message)
            return

        try:
            from langchain.schema import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content=self._get_system_prompt()),
            ]

            # Add conversation history if available
            if self.conversation:
                from ..models.conversation import Message
                history = Message.query.filter_by(
                    conversation_id=self.conversation.id,
                    is_visible=True
                ).order_by(Message.created_at.asc()).limit(20).all()

                for msg in history:
                    if msg.role == 'user':
                        messages.append(HumanMessage(content=msg.content))
                    elif msg.role == 'assistant':
                        from langchain.schema import AIMessage
                        messages.append(AIMessage(content=msg.content))

            messages.append(HumanMessage(content=message))

            # Stream the response
            for chunk in self.llm.stream(messages):
                if hasattr(chunk, 'content'):
                    yield chunk.content

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            yield f"I apologize, but I encountered an error: {str(e)}. Please try again."

    def _mock_chat_response(self, message: str) -> Generator[str, None, None]:
        """Generate mock responses when LLM is not available."""
        message_lower = message.lower()

        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            response = """Hello! I'm your Daily Ad Agent, ready to help you create and manage Facebook ads.

Here's what I can help you with today:
1. **Analyze Performance** - Review your recent ad performance
2. **Create New Ads** - Generate copy and creatives for new campaigns
3. **Optimize Existing Campaigns** - Adjust budgets and pause underperformers

What would you like to focus on?"""

        elif 'performance' in message_lower or 'stats' in message_lower:
            response = """Based on your recent performance data:

**Last 7 Days Summary:**
- Total Spend: $1,500
- Impressions: 45,000
- Clicks: 1,200 (CTR: 2.67%)
- Conversions: 45
- Average ROAS: 3.2x

**Top Performer:**
"Red Hoodie - Winter Sale" with ROAS 4.2x

**Recommendation:** Consider increasing budget on "Red Hoodie - Winter Sale" by 30% to capitalize on its strong performance.

Would you like me to apply this recommendation?"""

        elif 'create' in message_lower or 'new ad' in message_lower or 'draft' in message_lower:
            response = """I'd be happy to help create a new ad! Let me gather some information:

1. **What product or service** are you promoting?
2. **What's your target audience** (age, interests, location)?
3. **What's your campaign objective** (sales, traffic, awareness)?

Once you share these details, I'll generate 3 creative variants for you to review."""

        elif any(word in message_lower for word in ['hoodie', 'product', 'sell']):
            response = """Great! Let me create some ad variants for you.

**Creative Brief: Product Launch**

I've generated 3 variants based on successful patterns:

**Variant 1 - Urgency + Discount**
- Primary: "Don't miss out! Our best-selling hoodie is back with 20% off. Limited stock available - grab yours before they're gone!"
- Headline: "20% Off - Limited Time"
- CTA: Shop Now

**Variant 2 - Social Proof**
- Primary: "Join 10,000+ happy customers who love our ultra-soft hoodies. Premium comfort, unbeatable style."
- Headline: "Customer Favorite"
- CTA: Shop Now

**Variant 3 - Quality Focus**
- Primary: "Premium cotton. Perfect fit. Made to last. Experience the hoodie that's changing the game."
- Headline: "Quality You Can Feel"
- CTA: Learn More

I've updated the preview panel with Variant 1. Which version would you like to publish, or should I make adjustments?"""

        elif 'publish' in message_lower or 'launch' in message_lower or 'go ahead' in message_lower:
            response = """Before I publish, let me confirm the details:

**Campaign: "Red Hoodie - Winter Sale"**
- Objective: Conversions
- Daily Budget: $50
- Target: US, Ages 18-34, Interests: Fashion, Streetwear
- CTA: Shop Now

**Safety Checks:**
- Budget is within your usual range
- No policy violations detected
- Ad copy meets character limits

Reply "Yes" to confirm and publish, or let me know if you'd like to make changes."""

        elif message_lower in ['yes', 'confirm', 'approved']:
            response = """Your campaign has been published successfully!

**Campaign Details:**
- Campaign ID: camp_123456
- Status: Active (will start delivering shortly)
- Ads Manager Link: [View in Ads Manager]

I'll monitor performance and send you a summary tomorrow. Would you like to create another ad or review anything else?"""

        else:
            response = f"""I understand you're asking about: "{message}"

As your AI Media Buyer, I can help you with:
- **Performance Analysis** - "Show me my stats"
- **Create New Ads** - "Let's create an ad for [product]"
- **Optimize Campaigns** - "What should I improve?"
- **Publish Ads** - "Launch this campaign"

What would you like to do?"""

        # Yield character by character to simulate streaming
        for char in response:
            yield char

    def generate_daily_brief(self) -> Dict[str, Any]:
        """Generate the proactive daily brief."""
        if not self.ad_account:
            return {
                'message': "Welcome! Connect your Facebook Ad Account to get started with daily performance insights.",
                'has_data': False,
                'recommendations': []
            }

        # In production, this would use actual Facebook data
        # For now, return mock data
        return {
            'message': """Good morning! Here's your daily ad performance summary:

**Yesterday's Highlights:**
- Total Spend: $250
- Best ROAS: 4.2x on "Red Hoodie - Winter Sale"
- 3 active campaigns running

**Today's Recommendations:**
1. Increase budget on "Red Hoodie - Winter Sale" by 30% - it's been consistently outperforming
2. Consider pausing "Old Collection - Generic" (ROAS 0.7)

Would you like me to apply any of these recommendations?""",
            'has_data': True,
            'top_performer': {
                'name': 'Red Hoodie - Winter Sale',
                'roas': 4.2,
                'spend': 100.00
            },
            'recommendations': [
                {
                    'type': 'increase_budget',
                    'entity': 'Red Hoodie - Winter Sale',
                    'action': 'Increase budget by 30%',
                    'rationale': 'Consistent ROAS above 4.0 for 5 days'
                },
                {
                    'type': 'pause_campaign',
                    'entity': 'Old Collection - Generic',
                    'action': 'Pause campaign',
                    'rationale': 'ROAS below 1.0, burning budget'
                }
            ],
            'summary_stats': {
                'total_spend': 250.00,
                'total_conversions': 12,
                'average_roas': 2.8,
                'active_campaigns': 3
            }
        }

    def generate_ad_copy(
        self,
        product_info: str,
        tone: str = 'friendly',
        num_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate ad copy variants."""
        if self.llm:
            try:
                from langchain.schema import HumanMessage, SystemMessage

                prompt = f"""Generate {num_variants} Facebook ad copy variants for:
Product: {product_info}
Tone: {tone}

For each variant provide:
1. An angle/approach name
2. Primary text (125-300 chars)
3. Headline (max 40 chars)
4. Description (30-60 chars)
5. Suggested CTA

Format as JSON array."""

                messages = [
                    SystemMessage(content="You are an expert Facebook ad copywriter."),
                    HumanMessage(content=prompt)
                ]

                response = self.llm.invoke(messages)
                # Parse response and return structured data
                # For now, fall through to mock data

            except Exception as e:
                logger.error(f"Error generating copy: {e}")

        # Mock data
        return [
            {
                'variant_number': 1,
                'angle': 'Urgency + Discount',
                'primary_text': f"Don't miss out! Our best-selling product is now 20% off. Limited stock available - grab yours before they're gone!",
                'headline': '20% Off - Limited Time',
                'description': 'Premium quality, unbeatable price',
                'suggested_cta': 'shop_now'
            },
            {
                'variant_number': 2,
                'angle': 'Social Proof',
                'primary_text': f"Join thousands of happy customers who love our {product_info}. See why everyone's talking about it!",
                'headline': 'Customer Favorite',
                'description': 'Rated 5 stars by our community',
                'suggested_cta': 'learn_more'
            },
            {
                'variant_number': 3,
                'angle': 'Quality Focus',
                'primary_text': f"Premium quality meets exceptional design. Experience the difference with our {product_info}.",
                'headline': 'Quality You Can Trust',
                'description': 'Made with care, built to last',
                'suggested_cta': 'shop_now'
            }
        ]

    def analyze_performance(self, time_range: str = 'last_7_days') -> Dict[str, Any]:
        """Analyze account performance and provide insights."""
        from .facebook_service import FacebookService

        if not self.ad_account:
            return {
                'error': 'No ad account connected',
                'insights': []
            }

        # Mock analysis
        return {
            'time_range': time_range,
            'summary': {
                'total_spend': 1500.00,
                'total_conversions': 45,
                'average_roas': 3.2,
                'trend': 'improving'
            },
            'insights': [
                {
                    'type': 'winner',
                    'message': '"Red Hoodie - Winter Sale" is your top performer with ROAS 4.2x',
                    'recommendation': 'Consider increasing budget by 30%'
                },
                {
                    'type': 'loser',
                    'message': '"Old Collection - Generic" has ROAS 0.7x',
                    'recommendation': 'Consider pausing this campaign'
                },
                {
                    'type': 'opportunity',
                    'message': 'Your CTR is above industry average',
                    'recommendation': 'Your ad creative is working well'
                }
            ],
            'top_performers': [
                {'name': 'Red Hoodie - Winter Sale', 'roas': 4.2, 'spend': 500},
                {'name': 'Sneaker Collection - Flash', 'roas': 3.1, 'spend': 350}
            ],
            'underperformers': [
                {'name': 'Old Collection - Generic', 'roas': 0.7, 'spend': 200}
            ]
        }
