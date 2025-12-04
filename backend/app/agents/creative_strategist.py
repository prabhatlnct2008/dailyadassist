"""Creative Strategist Agent - Generates ad concepts and briefs."""
from typing import Dict, Any, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class CreativeStrategistAgent:
    """
    Specialized agent for creative strategy.

    Responsibilities:
    - Generate creative angles
    - Create campaign briefs
    - Suggest audiences based on product info
    - Analyze past winners for patterns
    """

    def __init__(self, preferences: Optional[Any] = None):
        """Initialize the creative strategist."""
        self.preferences = preferences
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize LLM for creative generation."""
        try:
            provider = os.environ.get('LLM_PROVIDER', 'openai')
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
                    temperature=0.8  # Higher temperature for creativity
                )
        except Exception as e:
            logger.warning(f"Failed to initialize LLM for creative: {e}")
            return None

    def generate_briefs(
        self,
        product_info: str,
        past_winners: Optional[List[Dict]] = None,
        num_briefs: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate creative briefs/angles for a product."""
        if self.llm:
            try:
                from langchain.schema import HumanMessage, SystemMessage

                system = """You are an expert Facebook ad creative strategist.
Generate compelling creative briefs for Facebook ads.
Each brief should have a unique angle that resonates with the target audience."""

                prompt = f"""Generate {num_briefs} creative briefs for this product:

Product: {product_info}

{"Past Winners: " + str(past_winners) if past_winners else ""}

For each brief, provide:
1. Angle Name (2-3 words)
2. Hook (the attention-grabbing element)
3. Value Proposition
4. Target Emotion (what feeling to evoke)
5. Suggested Audiences (2-3 interest/demographic targets)

Format as a structured response."""

                response = self.llm.invoke([
                    SystemMessage(content=system),
                    HumanMessage(content=prompt)
                ])

                # Parse and return (simplified for now)
                return self._parse_briefs(response.content, num_briefs)

            except Exception as e:
                logger.error(f"Error generating briefs with LLM: {e}")

        # Return mock briefs
        return self._get_mock_briefs(product_info)

    def _parse_briefs(self, response: str, num_briefs: int) -> List[Dict[str, Any]]:
        """Parse LLM response into structured briefs."""
        # Simplified parsing - in production, use more robust parsing
        briefs = []
        for i in range(num_briefs):
            briefs.append({
                'angle_name': f'Angle {i+1}',
                'hook': 'Attention-grabbing hook',
                'value_proposition': 'Key benefit for customer',
                'target_emotion': 'Excitement',
                'suggested_audiences': ['Interest 1', 'Interest 2']
            })
        return briefs

    def _get_mock_briefs(self, product_info: str) -> List[Dict[str, Any]]:
        """Generate mock creative briefs."""
        return [
            {
                'angle_name': 'Urgency + Scarcity',
                'hook': 'Limited time offer that creates FOMO',
                'value_proposition': 'Get it before it\'s gone at this special price',
                'target_emotion': 'Fear of missing out',
                'suggested_audiences': [
                    'Deal seekers',
                    'Impulse buyers',
                    'Brand followers'
                ]
            },
            {
                'angle_name': 'Social Proof',
                'hook': 'Join thousands of happy customers',
                'value_proposition': 'Trusted by the community, loved by users',
                'target_emotion': 'Trust and belonging',
                'suggested_audiences': [
                    'Review readers',
                    'Community-oriented',
                    'Risk-averse buyers'
                ]
            },
            {
                'angle_name': 'Quality + Premium',
                'hook': 'Premium quality that speaks for itself',
                'value_proposition': 'Invest in the best, enjoy lasting value',
                'target_emotion': 'Pride and satisfaction',
                'suggested_audiences': [
                    'Quality seekers',
                    'Premium shoppers',
                    'Brand conscious'
                ]
            }
        ]

    def suggest_audiences(
        self,
        product_info: str,
        region: str = 'US',
        past_winners: Optional[List[Dict]] = None
    ) -> List[Dict[str, Any]]:
        """Suggest target audiences for a product."""
        if self.llm:
            try:
                from langchain.schema import HumanMessage, SystemMessage

                prompt = f"""Suggest 5 target audiences for Facebook ads:

Product: {product_info}
Region: {region}

For each audience, provide:
1. Name
2. Type (interest, demographic, behavior, lookalike)
3. Details (specific interests or demographics)
4. Rationale"""

                response = self.llm.invoke([
                    SystemMessage(content="You are a Facebook ads targeting expert."),
                    HumanMessage(content=prompt)
                ])

                # Parse response
                return self._parse_audiences(response.content)

            except Exception as e:
                logger.error(f"Error suggesting audiences: {e}")

        # Mock audiences
        return [
            {
                'name': 'Fashion Enthusiasts',
                'type': 'interest',
                'details': {
                    'interests': ['Fashion', 'Online Shopping', 'Streetwear']
                },
                'rationale': 'Core audience interested in fashion products'
            },
            {
                'name': 'Young Professionals',
                'type': 'demographic',
                'details': {
                    'age_range': '25-34',
                    'education': 'College educated',
                    'income': 'Above average'
                },
                'rationale': 'Purchasing power and style-conscious'
            },
            {
                'name': 'Engaged Shoppers',
                'type': 'behavior',
                'details': {
                    'behaviors': ['Engaged shoppers', 'Online buyers']
                },
                'rationale': 'High purchase intent audience'
            },
            {
                'name': 'Competitor Audiences',
                'type': 'interest',
                'details': {
                    'interests': ['Nike', 'Adidas', 'H&M']
                },
                'rationale': 'Already interested in similar brands'
            },
            {
                'name': 'Lookalike - Past Buyers',
                'type': 'lookalike',
                'details': {
                    'source': 'Customer list',
                    'percentage': '1%'
                },
                'rationale': 'Similar to your best customers'
            }
        ]

    def _parse_audiences(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into audience suggestions."""
        # Simplified - return mock for now
        return self.suggest_audiences.__wrapped__(self, "", "US", None)

    def analyze_winning_patterns(
        self,
        past_winners: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze patterns in past winning ads."""
        if not past_winners:
            return {
                'patterns': [],
                'recommendations': []
            }

        # Analyze common elements
        patterns = {
            'common_hooks': [],
            'effective_ctas': [],
            'winning_audiences': [],
            'best_performing_times': [],
            'optimal_budget_range': {}
        }

        # In production, this would do real analysis
        return {
            'patterns': [
                'Urgency-based messaging performs 40% better',
                'Video ads have 2x higher CTR',
                'Weekend campaigns have better ROAS'
            ],
            'recommendations': [
                'Use time-limited offers in primary text',
                'Consider video creative for next campaign',
                'Schedule campaigns for weekend delivery'
            ]
        }
