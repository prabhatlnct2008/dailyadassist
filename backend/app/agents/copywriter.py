"""Copywriter Agent - Generates ad copy."""
from typing import Dict, Any, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class CopywriterAgent:
    """
    Specialized agent for writing ad copy.

    Responsibilities:
    - Write Primary Text, Headlines, Descriptions
    - Generate multiple variants
    - Respect character limits
    - Match tone preferences
    """

    # Facebook ad character limits
    LIMITS = {
        'primary_text': {'min': 50, 'max': 300, 'recommended': 125},
        'headline': {'min': 5, 'max': 40, 'recommended': 27},
        'description': {'min': 10, 'max': 90, 'recommended': 30}
    }

    def __init__(self, preferences: Optional[Any] = None):
        """Initialize the copywriter agent."""
        self.preferences = preferences
        self.default_tone = preferences.default_tone if preferences else 'friendly'
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize LLM for copy generation."""
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
                    temperature=0.7
                )
        except Exception as e:
            logger.warning(f"Failed to initialize LLM for copywriter: {e}")
            return None

    def generate_copy(
        self,
        brief: Dict[str, Any],
        tone: Optional[str] = None,
        num_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate ad copy variants from a brief."""
        tone = tone or self.default_tone

        if self.llm:
            try:
                return self._generate_with_llm(brief, tone, num_variants)
            except Exception as e:
                logger.error(f"Error generating copy with LLM: {e}")

        return self._generate_mock_copy(brief, tone, num_variants)

    def _generate_with_llm(
        self,
        brief: Dict[str, Any],
        tone: str,
        num_variants: int
    ) -> List[Dict[str, Any]]:
        """Generate copy using LLM."""
        from langchain.schema import HumanMessage, SystemMessage

        system = f"""You are an expert Facebook ad copywriter. Write compelling ad copy that:
- Is {tone} in tone
- Creates urgency and drives action
- Respects character limits:
  - Primary Text: 125-300 characters
  - Headline: max 40 characters
  - Description: 30-60 characters

Always suggest an appropriate CTA from: Learn More, Shop Now, Sign Up, Contact Us, Book Now, Download, Get Offer"""

        prompt = f"""Write {num_variants} ad copy variants for this brief:

Angle: {brief.get('angle_name', 'General')}
Hook: {brief.get('hook', '')}
Value Proposition: {brief.get('value_proposition', '')}
Target Emotion: {brief.get('target_emotion', '')}

For each variant, provide:
1. Primary Text (125-300 chars)
2. Headline (max 40 chars)
3. Description (30-60 chars)
4. CTA"""

        response = self.llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=prompt)
        ])

        return self._parse_copy_response(response.content, brief, num_variants)

    def _parse_copy_response(
        self,
        response: str,
        brief: Dict[str, Any],
        num_variants: int
    ) -> List[Dict[str, Any]]:
        """Parse LLM response into structured copy."""
        # Simplified parsing - in production use more robust parsing
        variants = []
        for i in range(num_variants):
            variants.append({
                'variant_number': i + 1,
                'angle': brief.get('angle_name', f'Variant {i+1}'),
                'primary_text': f"Variant {i+1} primary text from LLM",
                'headline': f"Headline {i+1}",
                'description': f"Description {i+1}",
                'suggested_cta': 'shop_now'
            })
        return variants

    def _generate_mock_copy(
        self,
        brief: Dict[str, Any],
        tone: str,
        num_variants: int
    ) -> List[Dict[str, Any]]:
        """Generate mock copy variants."""
        angle = brief.get('angle_name', 'General')

        templates = {
            'Urgency + Scarcity': [
                {
                    'primary_text': "Don't miss out! Our best-selling product is back with 20% off. Limited stock available - grab yours before they're gone!",
                    'headline': '20% Off - Limited Time',
                    'description': 'While supplies last',
                    'cta': 'shop_now'
                },
                {
                    'primary_text': "Last chance! Only a few left in stock. Get yours now before it's too late. Free shipping on orders today only.",
                    'headline': 'Almost Sold Out',
                    'description': 'Order now, ships today',
                    'cta': 'shop_now'
                },
                {
                    'primary_text': "Flash sale ends tonight! Save big on our most popular items. Don't wait - these deals won't last.",
                    'headline': 'Flash Sale - Today Only',
                    'description': 'Ends at midnight',
                    'cta': 'get_offer'
                }
            ],
            'Social Proof': [
                {
                    'primary_text': "Join 10,000+ happy customers who love our products. See why everyone's talking about it. Rated 5 stars!",
                    'headline': 'Customer Favorite',
                    'description': 'Trusted by thousands',
                    'cta': 'learn_more'
                },
                {
                    'primary_text': "See what the hype is about! Our community can't stop raving about their experience. Join them today.",
                    'headline': 'Join the Community',
                    'description': '5-star rated by customers',
                    'cta': 'shop_now'
                },
                {
                    'primary_text': "Thousands of 5-star reviews can't be wrong. Discover what makes our product the #1 choice.",
                    'headline': '#1 Customer Choice',
                    'description': 'Read the reviews',
                    'cta': 'learn_more'
                }
            ],
            'Quality + Premium': [
                {
                    'primary_text': "Premium quality meets exceptional design. Experience the difference with our handcrafted products.",
                    'headline': 'Quality You Can Feel',
                    'description': 'Crafted with care',
                    'cta': 'shop_now'
                },
                {
                    'primary_text': "Invest in the best. Our premium materials and attention to detail set us apart. You deserve quality.",
                    'headline': 'Premium Collection',
                    'description': 'Built to last',
                    'cta': 'shop_now'
                },
                {
                    'primary_text': "Excellence in every detail. From materials to finish, we obsess over quality so you don't have to.",
                    'headline': 'Uncompromising Quality',
                    'description': 'The difference is clear',
                    'cta': 'learn_more'
                }
            ]
        }

        # Get templates for the angle or use default
        angle_templates = templates.get(angle, templates['Quality + Premium'])

        variants = []
        for i in range(min(num_variants, len(angle_templates))):
            t = angle_templates[i]
            variants.append({
                'variant_number': i + 1,
                'angle': angle,
                'primary_text': t['primary_text'],
                'headline': t['headline'],
                'description': t['description'],
                'suggested_cta': t['cta']
            })

        return variants

    def refine_copy(
        self,
        original: Dict[str, Any],
        feedback: str
    ) -> Dict[str, Any]:
        """Refine copy based on user feedback."""
        if self.llm:
            try:
                from langchain.schema import HumanMessage, SystemMessage

                prompt = f"""Refine this ad copy based on the feedback:

Original:
- Primary Text: {original['primary_text']}
- Headline: {original['headline']}
- Description: {original['description']}

Feedback: {feedback}

Provide the refined version maintaining character limits."""

                response = self.llm.invoke([
                    SystemMessage(content="You are an expert ad copywriter."),
                    HumanMessage(content=prompt)
                ])

                # Parse and return refined copy
                return {
                    **original,
                    'primary_text': response.content,  # Simplified
                    'is_refined': True
                }

            except Exception as e:
                logger.error(f"Error refining copy: {e}")

        # Return original with note
        return {
            **original,
            'note': f'Refinement requested: {feedback}'
        }

    def validate_copy(self, copy: Dict[str, Any]) -> Dict[str, Any]:
        """Validate copy against character limits and policies."""
        issues = []

        primary_text = copy.get('primary_text', '')
        headline = copy.get('headline', '')
        description = copy.get('description', '')

        # Check character limits
        if len(primary_text) > self.LIMITS['primary_text']['max']:
            issues.append(f"Primary text too long ({len(primary_text)} chars, max {self.LIMITS['primary_text']['max']})")

        if len(headline) > self.LIMITS['headline']['max']:
            issues.append(f"Headline too long ({len(headline)} chars, max {self.LIMITS['headline']['max']})")

        if len(description) > self.LIMITS['description']['max']:
            issues.append(f"Description too long ({len(description)} chars, max {self.LIMITS['description']['max']})")

        # Check for policy violations (simplified)
        forbidden_words = ['cure', 'guarantee', 'miracle', 'risk-free']
        all_text = f"{primary_text} {headline} {description}".lower()

        for word in forbidden_words:
            if word in all_text:
                issues.append(f"Potential policy violation: '{word}' may not be allowed")

        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'character_counts': {
                'primary_text': len(primary_text),
                'headline': len(headline),
                'description': len(description)
            }
        }
