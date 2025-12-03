"""Orchestrator Agent - The main agent that coordinates sub-agents."""
from typing import Dict, Any, List, Optional, Generator
import logging
import os

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    The main orchestrator agent that acts as a Senior Media Buyer.

    Responsibilities:
    - Understand user intent
    - Break work into tasks
    - Coordinate sub-agents
    - Maintain conversation state
    - Make final decisions
    """

    def __init__(
        self,
        user_id: str,
        conversation: Optional[Any] = None,
        preferences: Optional[Any] = None,
        ad_account: Optional[Any] = None,
        facebook_connection: Optional[Any] = None
    ):
        """Initialize the orchestrator agent."""
        self.user_id = user_id
        self.conversation = conversation
        self.preferences = preferences
        self.ad_account = ad_account
        self.facebook_connection = facebook_connection

        # Initialize sub-agents
        self._init_sub_agents()

        # Initialize LLM
        self.llm = self._init_llm()

        # Initialize tools
        self.tools = self._init_tools()

    def _init_llm(self):
        """Initialize the language model."""
        provider = os.environ.get('LLM_PROVIDER', 'openai')

        try:
            if provider == 'anthropic':
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model="claude-3-sonnet-20240229",
                    anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY'),
                    streaming=True
                )
            else:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model="gpt-4-turbo-preview",
                    openai_api_key=os.environ.get('OPENAI_API_KEY'),
                    streaming=True,
                    temperature=0.7
                )
        except Exception as e:
            logger.warning(f"Failed to initialize LLM: {e}")
            return None

    def _init_sub_agents(self):
        """Initialize specialized sub-agents."""
        from .performance_analyst import PerformanceAnalystAgent
        from .creative_strategist import CreativeStrategistAgent
        from .copywriter import CopywriterAgent
        from .execution_agent import ExecutionAgent
        from .qa_safety_agent import QASafetyAgent

        access_token = None
        if self.facebook_connection:
            access_token = self.facebook_connection.get_access_token()

        self.performance_analyst = PerformanceAnalystAgent(
            ad_account=self.ad_account,
            access_token=access_token
        )

        self.creative_strategist = CreativeStrategistAgent(
            preferences=self.preferences
        )

        self.copywriter = CopywriterAgent(
            preferences=self.preferences
        )

        self.execution_agent = ExecutionAgent(
            ad_account=self.ad_account,
            access_token=access_token
        )

        self.qa_safety_agent = QASafetyAgent(
            preferences=self.preferences
        )

    def _init_tools(self) -> List:
        """Initialize LangChain tools."""
        from .tools import get_all_tools

        return get_all_tools(
            user_id=self.user_id,
            ad_account=self.ad_account,
            facebook_connection=self.facebook_connection,
            preferences=self.preferences
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the orchestrator."""
        tone = self.preferences.default_tone if self.preferences else 'friendly'
        budget = self.preferences.default_daily_budget if self.preferences else 50
        currency = self.preferences.default_currency if self.preferences else 'USD'

        state = self.conversation.state if self.conversation else 'idle'

        return f"""You are the Daily Ad Agent, an AI Senior Media Buyer and Facebook Ads Strategist.

## Your Persona
- Tone: {tone}
- Style: Professional yet approachable
- Always explain your reasoning
- Be proactive with suggestions

## User Context
- Default Daily Budget: {currency} {budget}
- Current Conversation State: {state}
- Account Connected: {'Yes' if self.ad_account else 'No'}

## Your Capabilities

### Performance Analysis
- Analyze historical ad performance
- Identify top performers and underperformers
- Provide data-driven recommendations

### Creative Generation
- Generate creative briefs and angles
- Write ad copy variants (Primary Text, Headline, Description)
- Suggest target audiences

### Campaign Management
- Create new campaigns
- Adjust budgets
- Pause underperforming ads
- All actions require user confirmation

## Guidelines

1. **Always Start with Context**: When the user first messages, check if there's recent performance data to discuss.

2. **Multi-Step Workflows**: For complex tasks:
   - First, gather information
   - Then, present a plan
   - Get confirmation before executing

3. **Ad Copy Requirements**:
   - Primary Text: 125-300 characters
   - Headline: max 40 characters
   - Description: 30-60 characters
   - Always suggest an appropriate CTA

4. **Safety Guardrails**:
   - Warn if budget exceeds 5x the default
   - Check for policy violations before publishing
   - Never publish without explicit confirmation

5. **State Transitions**:
   - IDLE → DISCOVERY: User starts a task
   - DISCOVERY → IDEATION: Gathering complete
   - IDEATION → DRAFTING: Brief approved
   - DRAFTING → REVIEW: Draft ready
   - REVIEW → READY_TO_PUBLISH: User approves
   - READY_TO_PUBLISH → PUBLISHED: Campaign live

6. **Response Format**:
   - Keep responses concise but informative
   - Use markdown for structure
   - Include clear action items or questions
"""

    def chat(self, message: str) -> Generator[str, None, None]:
        """Process a user message and stream the response."""
        if not self.llm:
            yield from self._mock_response(message)
            return

        try:
            from langchain.schema import HumanMessage, SystemMessage, AIMessage
            from langchain.agents import AgentExecutor, create_openai_tools_agent
            from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

            # Build conversation history
            history = []
            if self.conversation:
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

            # Create the agent with tools
            if self.tools:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self._get_system_prompt()),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ])

                agent = create_openai_tools_agent(self.llm, self.tools, prompt)
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    handle_parsing_errors=True
                )

                # Execute with streaming
                for chunk in agent_executor.stream({
                    "input": message,
                    "chat_history": history
                }):
                    if 'output' in chunk:
                        yield chunk['output']

            else:
                # Simple chat without tools
                messages = [SystemMessage(content=self._get_system_prompt())]
                messages.extend(history)
                messages.append(HumanMessage(content=message))

                for chunk in self.llm.stream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content

        except Exception as e:
            logger.error(f"Error in orchestrator chat: {e}")
            yield f"I apologize, but I encountered an error processing your request. Error: {str(e)}"

    def _mock_response(self, message: str) -> Generator[str, None, None]:
        """Generate mock responses when LLM is unavailable."""
        message_lower = message.lower()

        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            response = self._get_greeting_response()
        elif 'performance' in message_lower or 'stats' in message_lower:
            response = self._get_performance_response()
        elif 'create' in message_lower or 'new ad' in message_lower:
            response = self._get_create_ad_response()
        elif any(word in message_lower for word in ['publish', 'launch', 'go ahead']):
            response = self._get_publish_response()
        elif message_lower in ['yes', 'confirm', 'approved']:
            response = self._get_confirmation_response()
        else:
            response = self._get_default_response(message)

        for char in response:
            yield char

    def _get_greeting_response(self) -> str:
        return """Hello! I'm your Daily Ad Agent, ready to help you create and manage Facebook ads.

**Today's Quick Stats** (if connected):
- 3 active campaigns running
- Top performer: "Red Hoodie - Winter Sale" (ROAS 4.2x)

**How can I help you today?**
1. Review your ad performance
2. Create a new ad campaign
3. Optimize existing campaigns
4. Get recommendations

Just tell me what you'd like to focus on!"""

    def _get_performance_response(self) -> str:
        return """**Performance Summary - Last 7 Days**

| Metric | Value |
|--------|-------|
| Total Spend | $1,500 |
| Impressions | 45,000 |
| Clicks | 1,200 |
| CTR | 2.67% |
| Conversions | 45 |
| ROAS | 3.2x |

**Top Performer:**
"Red Hoodie - Winter Sale"
- ROAS: 4.2x
- Spend: $500
- Conversions: 25

**Underperformer:**
"Old Collection - Generic"
- ROAS: 0.7x
- Spend: $200
- Conversions: 2

**Recommendations:**
1. Increase "Red Hoodie" budget by 30%
2. Pause "Old Collection - Generic"

Would you like me to apply any of these recommendations?"""

    def _get_create_ad_response(self) -> str:
        return """Great! Let's create a new ad campaign.

I'll need a few details:

1. **Product/Service**: What are you promoting?
2. **Goal**: Sales, traffic, or brand awareness?
3. **Target Audience**: Who should see this ad?
4. **Budget**: Daily budget for this campaign?

Share what you can, and I'll generate creative options for you!"""

    def _get_publish_response(self) -> str:
        return """Before I publish, let me confirm the details:

**Campaign Summary**
- Name: "New Campaign"
- Objective: Conversions
- Daily Budget: $50
- Target: US, Ages 18-34

**Ad Creative**
- Primary Text: "Your compelling ad copy here..."
- Headline: "Your Headline"
- CTA: Shop Now

**Safety Checks:**
- Budget within normal range
- No policy violations detected
- Copy meets character limits

Reply **"Yes"** to confirm and publish."""

    def _get_confirmation_response(self) -> str:
        return """**Campaign Published Successfully!**

- Campaign ID: camp_12345
- Status: Active
- [View in Ads Manager](https://facebook.com/adsmanager)

I'll monitor performance and update you tomorrow.

What else would you like to do?"""

    def _get_default_response(self, message: str) -> str:
        return f"""I understand you're asking about: "{message}"

Here's how I can help:
- **"Show my stats"** - View performance data
- **"Create a new ad"** - Start a new campaign
- **"Optimize my ads"** - Get improvement recommendations
- **"Pause [campaign]"** - Stop an underperformer

What would you like to do?"""

    def generate_daily_brief(self) -> Dict[str, Any]:
        """Generate the proactive daily brief."""
        if not self.ad_account:
            return {
                'message': "Welcome! Connect your Facebook Ad Account to get personalized performance insights.",
                'has_data': False,
                'recommendations': []
            }

        # Use performance analyst to get data
        stats = self.performance_analyst.get_summary('last_7_days')
        top_performers = self.performance_analyst.get_top_performers(limit=3)
        recommendations = self.performance_analyst.get_recommendations()

        message = f"""Good morning! Here's your daily ad performance summary:

**Yesterday's Performance:**
- Spend: ${stats.get('spend', 0):.2f}
- Conversions: {stats.get('conversions', 0)}
- ROAS: {stats.get('roas', 0):.1f}x

**Top Performer:**
{top_performers[0]['name'] if top_performers else 'No data'} ({top_performers[0].get('roas', 0):.1f}x ROAS)

**Today's Recommendations:**
"""
        for i, rec in enumerate(recommendations[:3], 1):
            message += f"\n{i}. {rec.get('action', '')} - {rec.get('rationale', '')}"

        return {
            'message': message,
            'has_data': True,
            'top_performer': top_performers[0] if top_performers else None,
            'recommendations': recommendations,
            'summary_stats': stats
        }
