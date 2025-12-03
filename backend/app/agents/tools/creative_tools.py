"""Creative generation tools for the agent."""
from typing import Any, Optional, Type, List
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import json
import os
import requests


class GenerateCreativeBriefsInput(BaseModel):
    """Input for GenerateCreativeBriefsTool."""
    product_info: str = Field(description="Description of the product or service")
    num_briefs: int = Field(default=3, description="Number of briefs to generate")


class GenerateCreativeBriefsTool(BaseTool):
    """Tool to generate creative briefs/angles."""

    name: str = "generate_creative_briefs"
    description: str = """Generate creative briefs and angles for ad campaigns.
Use this when starting to create new ads to explore different approaches.
Returns multiple angle options with hooks, value props, and target emotions."""
    args_schema: Type[BaseModel] = GenerateCreativeBriefsInput

    preferences: Optional[Any] = None

    def _run(self, product_info: str, num_briefs: int = 3) -> str:
        """Execute the tool."""
        from ..creative_strategist import CreativeStrategistAgent

        strategist = CreativeStrategistAgent(preferences=self.preferences)
        briefs = strategist.generate_briefs(
            product_info=product_info,
            num_briefs=num_briefs
        )

        return json.dumps({'briefs': briefs}, indent=2)


class GenerateAdCopyInput(BaseModel):
    """Input for GenerateAdCopyTool."""
    brief: str = Field(description="Creative brief or angle to use")
    tone: str = Field(default="friendly", description="Tone: friendly, professional, bold, casual")
    num_variants: int = Field(default=3, description="Number of copy variants")


class GenerateAdCopyTool(BaseTool):
    """Tool to generate ad copy variants."""

    name: str = "generate_ad_copy"
    description: str = """Generate ad copy variants including Primary Text, Headline, and Description.
Use after selecting a creative brief to create actual ad text.
All copy respects Facebook character limits."""
    args_schema: Type[BaseModel] = GenerateAdCopyInput

    preferences: Optional[Any] = None

    def _run(
        self,
        brief: str,
        tone: str = "friendly",
        num_variants: int = 3
    ) -> str:
        """Execute the tool."""
        from ..copywriter import CopywriterAgent

        copywriter = CopywriterAgent(preferences=self.preferences)

        # Parse brief if it's a string
        brief_dict = {'angle_name': brief, 'hook': brief, 'value_proposition': brief}

        variants = copywriter.generate_copy(
            brief=brief_dict,
            tone=tone,
            num_variants=num_variants
        )

        return json.dumps({'variants': variants}, indent=2)


class SuggestAudiencesInput(BaseModel):
    """Input for SuggestAudiencesTool."""
    product_info: str = Field(description="Product or service description")
    region: str = Field(default="US", description="Target region")


class SuggestAudiencesTool(BaseTool):
    """Tool to suggest target audiences."""

    name: str = "suggest_audiences"
    description: str = """Suggest target audiences for a product or campaign.
Returns audience segments including interests, demographics, and lookalike options."""
    args_schema: Type[BaseModel] = SuggestAudiencesInput

    preferences: Optional[Any] = None

    def _run(self, product_info: str, region: str = "US") -> str:
        """Execute the tool."""
        from ..creative_strategist import CreativeStrategistAgent

        strategist = CreativeStrategistAgent(preferences=self.preferences)
        audiences = strategist.suggest_audiences(
            product_info=product_info,
            region=region
        )

        return json.dumps({'audiences': audiences}, indent=2)


class SearchStockImagesInput(BaseModel):
    """Input for SearchStockImagesTool."""
    query: str = Field(description="Search query for images")
    count: int = Field(default=5, description="Number of images to return")


class SearchStockImagesTool(BaseTool):
    """Tool to search for stock images."""

    name: str = "search_stock_images"
    description: str = """Search for stock images from Unsplash or Pexels.
Use when the user needs images for their ad creative."""
    args_schema: Type[BaseModel] = SearchStockImagesInput

    def _run(self, query: str, count: int = 5) -> str:
        """Execute the tool."""
        images = []

        # Try Unsplash first
        unsplash_key = os.environ.get('UNSPLASH_ACCESS_KEY')
        if unsplash_key:
            try:
                response = requests.get(
                    'https://api.unsplash.com/search/photos',
                    params={'query': query, 'per_page': count},
                    headers={'Authorization': f'Client-ID {unsplash_key}'}
                )
                if response.status_code == 200:
                    data = response.json()
                    for photo in data.get('results', []):
                        images.append({
                            'source': 'unsplash',
                            'id': photo['id'],
                            'url': photo['urls']['regular'],
                            'thumb': photo['urls']['thumb'],
                            'description': photo.get('description', ''),
                            'photographer': photo['user']['name'],
                            'download_url': photo['links']['download']
                        })
            except Exception as e:
                pass

        # Try Pexels as fallback
        if not images:
            pexels_key = os.environ.get('PEXELS_API_KEY')
            if pexels_key:
                try:
                    response = requests.get(
                        'https://api.pexels.com/v1/search',
                        params={'query': query, 'per_page': count},
                        headers={'Authorization': pexels_key}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        for photo in data.get('photos', []):
                            images.append({
                                'source': 'pexels',
                                'id': photo['id'],
                                'url': photo['src']['large'],
                                'thumb': photo['src']['tiny'],
                                'description': photo.get('alt', ''),
                                'photographer': photo['photographer'],
                                'download_url': photo['src']['original']
                            })
                except Exception as e:
                    pass

        # Return mock data if no API keys
        if not images:
            images = [
                {
                    'source': 'placeholder',
                    'id': f'mock_{i}',
                    'url': f'https://via.placeholder.com/1200x628?text={query.replace(" ", "+")}+{i}',
                    'thumb': f'https://via.placeholder.com/200x200?text={query.replace(" ", "+")}',
                    'description': f'Placeholder image for {query}',
                    'photographer': 'Placeholder',
                    'is_mock': True
                }
                for i in range(count)
            ]

        return json.dumps({'images': images, 'query': query}, indent=2)
