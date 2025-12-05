"""Agent orchestration service with real tool integration."""
from typing import Dict, Any, List, Optional, Generator
from datetime import datetime
import json
import logging
import os

from flask import current_app

logger = logging.getLogger(__name__)


class AgentServiceError(Exception):
    """Custom exception for agent service errors."""
    pass


class AgentService:
    """Service for orchestrating the AI agent with real tool execution."""

    def __init__(
        self,
        user_id: str,
        conversation: Optional[Any] = None,
        preferences: Optional[Any] = None,
        ad_account: Optional[Any] = None,
        facebook_connection: Optional[Any] = None
    ):
        """Initialize the agent service."""
        self.user_id = user_id
        self.conversation = conversation
        self.preferences = preferences
        self.ad_account = ad_account
        self.facebook_connection = facebook_connection

        # Track initialization status
        self.llm = None
        self.llm_error = None
        self.tools = []
        self.agent_executor = None

        # Initialize components
        self._init_llm()
        self._init_tools()
        self._init_agent()

    def _init_llm(self):
        """Initialize the LLM based on configuration."""
        provider = os.environ.get('LLM_PROVIDER', 'openai')

        # Check for API keys first
        openai_key = os.environ.get('OPENAI_API_KEY', '').strip()
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '').strip()

        if provider == 'anthropic' and not anthropic_key:
            self.llm_error = "ANTHROPIC_API_KEY not configured"
            logger.error(self.llm_error)
            return
        elif provider == 'openai' and not openai_key:
            self.llm_error = "OPENAI_API_KEY not configured"
            logger.error(self.llm_error)
            return

        try:
            if provider == 'anthropic':
                from langchain_anthropic import ChatAnthropic
                self.llm = ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    anthropic_api_key=anthropic_key,
                    streaming=True,
                    temperature=0.7
                )
                logger.info("Initialized Anthropic Claude LLM")
            else:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model="gpt-4-turbo-preview",
                    openai_api_key=openai_key,
                    streaming=True,
                    temperature=0.7
                )
                logger.info("Initialized OpenAI GPT-4 LLM")

        except Exception as e:
            self.llm_error = f"Failed to initialize LLM: {str(e)}"
            logger.error(self.llm_error, exc_info=True)

    def _init_tools(self):
        """Initialize the agent tools."""
        try:
            from ..agents.tools import get_all_tools

            logger.info(f"Initializing tools for user {self.user_id}...")
            self.tools = get_all_tools(
                user_id=self.user_id,
                ad_account=self.ad_account,
                facebook_connection=self.facebook_connection,
                preferences=self.preferences
            )
            logger.info(f"Successfully initialized {len(self.tools)} agent tools")
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}", exc_info=True)
            self.tools = []

    def _init_agent(self):
        """Initialize the agent executor with tools."""
        logger.info(f"Initializing agent... LLM: {self.llm is not None}, Tools: {len(self.tools) if self.tools else 0}")

        if not self.llm:
            logger.warning("Cannot initialize agent: LLM not available")
            return

        if not self.tools:
            logger.warning("No tools available, using simple chat mode")
            return

        try:
            from langchain.agents import AgentExecutor, create_tool_calling_agent
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_system_prompt()),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # Create the agent with tool calling capability
            agent = create_tool_calling_agent(self.llm, self.tools, prompt)

            # Create the executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=False,  # Disable stdout callback, use file logging instead
                handle_parsing_errors=True,
                max_iterations=10,
                return_intermediate_steps=True
            )
            logger.info(f"Agent executor initialized successfully with {len(self.tools)} tools")

        except Exception as e:
            logger.error(f"Failed to initialize agent executor: {e}", exc_info=True)
            self.agent_executor = None

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        tone = self.preferences.default_tone if self.preferences else 'friendly'
        budget = self.preferences.default_daily_budget if self.preferences else 50
        currency = self.preferences.default_currency if self.preferences else 'USD'
        state = self.conversation.state if self.conversation else 'idle'
        has_account = 'Yes' if self.ad_account else 'No'

        return f"""You are the Daily Ad Agent, an AI Senior Media Buyer and Facebook Ads Strategist.

## Your Persona
- Tone: {tone}
- Style: Professional yet approachable
- Always explain your reasoning
- Be proactive with suggestions

## User Context
- Default Daily Budget: {currency} {budget}
- Current Conversation State: {state}
- Ad Account Connected: {has_account}

## Your Capabilities (Use the tools provided!)

### Performance Analysis Tools
- `get_account_stats`: Get overall account metrics (spend, impressions, clicks, ROAS)
- `get_top_performers`: Find winning ads/campaigns
- `get_underperformers`: Identify poor performers to pause
- `summarize_performance`: Generate plain-language performance summary

### Creative Generation Tools
- `generate_creative_briefs`: Create strategic ad concepts
- `generate_ad_copy`: Write ad copy variants with proper character limits
- `suggest_audiences`: Recommend targeting options

### Execution Tools
- `update_preview_state`: Update the ad preview shown to user
- `save_draft`: Save current ad as a draft
- `publish_campaign`: Publish a draft (requires confirmation!)
- `adjust_budget`: Change campaign budgets
- `pause_items`: Pause underperforming campaigns/ads

## Guidelines

1. **ALWAYS use tools** when the user asks about performance, wants to create ads, or manage campaigns.
   - Don't make up data - use tools to get real information
   - When asked about stats, call `get_account_stats` first

2. **Ad Copy Requirements**:
   - Primary Text: 125-300 characters
   - Headline: max 40 characters
   - Description: 30-60 characters
   - Always suggest an appropriate CTA

3. **Safety First**:
   - Warn if budget exceeds 5x the default (${budget * 5})
   - NEVER publish without explicit user confirmation
   - Check for policy violations before publishing

4. **Be Transparent**:
   - Tell the user what tools you're using
   - Show the data you're basing recommendations on
   - Explain your reasoning

5. **Keep responses concise** but informative. Use markdown for structure."""

    def _get_conversation_history(self) -> list:
        """Get conversation history as LangChain messages."""
        from langchain_core.messages import HumanMessage, AIMessage

        history = []
        if not self.conversation:
            return history

        try:
            from ..models.conversation import Message
            msgs = Message.query.filter_by(
                conversation_id=self.conversation.id,
                is_visible=True
            ).order_by(Message.created_at.asc()).limit(20).all()

            for msg in msgs:
                if msg.role == 'user':
                    history.append(HumanMessage(content=msg.content))
                elif msg.role == 'assistant':
                    history.append(AIMessage(content=msg.content))
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")

        return history

    def chat(self, message: str) -> Generator[str, None, None]:
        """Process a chat message and stream the response with tool execution."""

        # If LLM not available, return error (not silent mock!)
        if not self.llm:
            error_msg = f"""**Configuration Error**

I'm unable to process your request because the AI service is not properly configured.

**Error**: {self.llm_error or 'LLM not initialized'}

**To fix this**, please ensure:
1. `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set in your `.env` file
2. The API key is valid and has available credits
3. `LLM_PROVIDER` is set to either 'openai' or 'anthropic'

Please check your configuration and try again."""

            for char in error_msg:
                yield char
            return

        # Get conversation history
        chat_history = self._get_conversation_history()

        # If we have an agent executor with tools, use it
        if self.agent_executor:
            yield from self._stream_agent_response(message, chat_history)
        else:
            # Fallback to simple chat without tools
            yield from self._stream_simple_chat(message, chat_history)

    def _stream_agent_response(
        self,
        message: str,
        chat_history: list
    ) -> Generator[str, None, None]:
        """Stream response from the agent executor with tool visibility."""

        try:
            logger.info(f"Agent processing message: {message[:100]}...")

            # Signal that we're processing
            yield "**Analyzing your request...**\n\n"

            # Run the agent
            result = self.agent_executor.invoke({
                "input": message,
                "chat_history": chat_history
            })

            # Extract intermediate steps (tool calls)
            intermediate_steps = result.get("intermediate_steps", [])

            # Log and show tool calls
            if intermediate_steps:
                logger.info(f"Agent used {len(intermediate_steps)} tool(s)")
                yield "**Tools Used:**\n"
                for step in intermediate_steps:
                    action, observation = step
                    tool_name = action.tool
                    tool_input = action.tool_input

                    logger.info(f"Tool called: {tool_name} with input: {tool_input}")

                    yield f"- `{tool_name}`: "
                    if isinstance(tool_input, dict):
                        yield f"{json.dumps(tool_input)}\n"
                    else:
                        yield f"{tool_input}\n"

                yield "\n---\n\n"

            # Stream the final output
            output = result.get("output", "")
            logger.info(f"Agent response length: {len(output)} chars")
            for char in output:
                yield char

        except Exception as e:
            logger.error(f"Agent execution error: {e}", exc_info=True)
            error_msg = f"\n\n**Error during processing**: {str(e)}\n\nPlease try rephrasing your request."
            for char in error_msg:
                yield char

    def _stream_simple_chat(
        self,
        message: str,
        chat_history: list
    ) -> Generator[str, None, None]:
        """Stream a simple chat response without tools."""
        from langchain_core.messages import HumanMessage, SystemMessage

        try:
            messages = [SystemMessage(content=self._get_system_prompt())]
            messages.extend(chat_history)
            messages.append(HumanMessage(content=message))

            # Note: Tools are not available in simple mode
            yield "*Note: Running in simple chat mode (tools not available)*\n\n"

            # Stream the response
            for chunk in self.llm.stream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Simple chat error: {e}", exc_info=True)
            yield f"\n\n**Error**: {str(e)}"

    def generate_daily_brief(self) -> Dict[str, Any]:
        """Generate the proactive daily brief."""
        if not self.ad_account:
            return {
                'message': "Welcome! Connect your Facebook Ad Account to get personalized performance insights.",
                'has_data': False,
                'recommendations': []
            }

        # Try to get real data using tools
        try:
            from ..agents.tools.performance_tools import GetAccountStatsTool, GetTopPerformersTool

            # Get stats
            stats_tool = GetAccountStatsTool(
                ad_account=self.ad_account,
                access_token=self._get_access_token()
            )
            stats_json = stats_tool._run(time_range='last_7_days')
            stats = json.loads(stats_json)

            # Get top performers
            top_tool = GetTopPerformersTool(
                ad_account=self.ad_account,
                access_token=self._get_access_token()
            )
            top_json = top_tool._run(metric='roas', limit=3)
            top_data = json.loads(top_json)
            top_performers = top_data.get('top_performers', [])

            # Build message
            message = f"""Good morning! Here's your daily ad performance summary:

**Last 7 Days Performance:**
- Total Spend: ${stats.get('spend', 0):.2f}
- Impressions: {stats.get('impressions', 0):,}
- Clicks: {stats.get('clicks', 0):,}
- CTR: {stats.get('ctr', 0):.2f}%
- Conversions: {stats.get('conversions', 0)}
- ROAS: {stats.get('roas', 0):.1f}x

"""
            if top_performers:
                top = top_performers[0]
                message += f"""**Top Performer:**
"{top.get('name', 'Unknown')}" with ROAS {top.get('roas', 0):.1f}x

"""

            message += "What would you like to focus on today?"

            return {
                'message': message,
                'has_data': True,
                'top_performer': top_performers[0] if top_performers else None,
                'recommendations': self._generate_recommendations(stats, top_performers),
                'summary_stats': stats
            }

        except Exception as e:
            logger.error(f"Error generating daily brief: {e}", exc_info=True)
            return {
                'message': f"Good morning! I had trouble fetching your performance data. Error: {str(e)}",
                'has_data': False,
                'recommendations': []
            }

    def _get_access_token(self) -> Optional[str]:
        """Get the Facebook access token."""
        if self.facebook_connection:
            try:
                return self.facebook_connection.get_access_token()
            except Exception:
                pass
        return os.environ.get('FACEBOOK_PAGE_ACCESS_TOKEN')

    def _generate_recommendations(
        self,
        stats: Dict[str, Any],
        top_performers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on performance data."""
        recommendations = []

        # Check ROAS
        if stats.get('roas', 0) > 3:
            recommendations.append({
                'type': 'scale',
                'action': 'Consider increasing budget',
                'rationale': f'Your ROAS of {stats.get("roas", 0):.1f}x is above target'
            })
        elif stats.get('roas', 0) < 1:
            recommendations.append({
                'type': 'optimize',
                'action': 'Review underperforming campaigns',
                'rationale': f'Your ROAS of {stats.get("roas", 0):.1f}x is below breakeven'
            })

        # Top performer recommendation
        if top_performers:
            top = top_performers[0]
            if top.get('roas', 0) > stats.get('roas', 0) * 1.5:
                recommendations.append({
                    'type': 'scale',
                    'entity': top.get('name'),
                    'action': f'Increase budget on "{top.get("name")}"',
                    'rationale': f'Performing {top.get("roas", 0) / stats.get("roas", 1):.1f}x better than average'
                })

        return recommendations

    def generate_ad_copy(
        self,
        product_info: str,
        tone: str = 'friendly',
        num_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate ad copy variants using the LLM."""
        if not self.llm:
            # Return mock data if no LLM
            return self._mock_ad_copy(product_info, num_variants)

        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            prompt = f"""Generate exactly {num_variants} Facebook ad copy variants for:
Product/Service: {product_info}
Tone: {tone}

For each variant, provide a JSON object with these exact fields:
- variant_number: (1, 2, or 3)
- angle: (the creative angle/approach name)
- primary_text: (125-300 characters)
- headline: (max 40 characters)
- description: (30-60 characters)
- suggested_cta: (one of: shop_now, learn_more, sign_up, book_now, contact_us)

Return ONLY a valid JSON array, no other text."""

            messages = [
                SystemMessage(content="You are an expert Facebook ad copywriter. Always return valid JSON."),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            content = response.content.strip()

            # Try to parse JSON from response
            if content.startswith('```'):
                # Remove markdown code blocks
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            variants = json.loads(content)
            return variants

        except Exception as e:
            logger.error(f"Error generating ad copy: {e}", exc_info=True)
            return self._mock_ad_copy(product_info, num_variants)

    def _mock_ad_copy(self, product_info: str, num_variants: int) -> List[Dict[str, Any]]:
        """Generate mock ad copy as fallback."""
        return [
            {
                'variant_number': 1,
                'angle': 'Urgency + Discount',
                'primary_text': f"Don't miss out! Our {product_info} is now 20% off. Limited stock available - grab yours before they're gone!",
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
        ][:num_variants]

    def analyze_performance(self, time_range: str = 'last_7_days') -> Dict[str, Any]:
        """Analyze account performance using tools."""
        if not self.ad_account:
            return {
                'error': 'No ad account connected',
                'insights': []
            }

        try:
            from ..agents.tools.performance_tools import (
                GetAccountStatsTool,
                GetTopPerformersTool,
                GetUnderperformersTool
            )

            access_token = self._get_access_token()

            # Get stats
            stats_tool = GetAccountStatsTool(
                ad_account=self.ad_account,
                access_token=access_token
            )
            stats = json.loads(stats_tool._run(time_range=time_range))

            # Get top performers
            top_tool = GetTopPerformersTool(
                ad_account=self.ad_account,
                access_token=access_token
            )
            top_data = json.loads(top_tool._run(time_range=time_range, limit=5))

            # Get underperformers
            under_tool = GetUnderperformersTool(
                ad_account=self.ad_account,
                access_token=access_token
            )
            under_data = json.loads(under_tool._run(time_range=time_range))

            # Build insights
            insights = []

            if top_data.get('top_performers'):
                top = top_data['top_performers'][0]
                insights.append({
                    'type': 'winner',
                    'message': f'"{top["name"]}" is your top performer with ROAS {top.get("roas", 0):.1f}x',
                    'recommendation': 'Consider increasing budget by 20-30%'
                })

            if under_data.get('underperformers'):
                for item in under_data['underperformers']:
                    insights.append({
                        'type': 'loser',
                        'message': f'"{item["name"]}" has ROAS {item.get("roas", 0):.1f}x',
                        'recommendation': item.get('recommendation', 'Consider pausing')
                    })

            return {
                'time_range': time_range,
                'summary': stats,
                'insights': insights,
                'top_performers': top_data.get('top_performers', []),
                'underperformers': under_data.get('underperformers', [])
            }

        except Exception as e:
            logger.error(f"Error analyzing performance: {e}", exc_info=True)
            return {
                'error': str(e),
                'insights': []
            }
