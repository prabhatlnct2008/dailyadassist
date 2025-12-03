# Implementation Plan: Daily Ad Agent

## 1. System Overview

Daily Ad Agent is a conversational AI assistant that acts as a Senior Media Buyer for Facebook Ads. The system proactively analyzes past performance, suggests creative & copy, and manages Facebook ad campaigns through a chat-based "War Room" interface.

### Core Capabilities:
- **Proactive Daily Engagement**: Agent initiates conversations based on performance data
- **Multi-Agent Architecture**: Orchestrator + specialized sub-agents for different tasks
- **Facebook Integration**: Full campaign creation, management, and analysis
- **War Room Interface**: Split-screen chat + live ad preview

### Tech Stack:
- **Backend**: Python/Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: React with Tailwind CSS
- **AI/LLM**: LangChain with OpenAI/Claude for agentic reasoning
- **Authentication**: Google OAuth + Facebook OAuth

---

## 2. Architecture Specification

### 2.1 Database Models (SQLAlchemy)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Database Schema                           │
└─────────────────────────────────────────────────────────────────┘

User
├── id: String (UUID, PK)
├── email: String (unique, indexed)
├── google_id: String (unique)
├── name: String
├── profile_picture_url: String (nullable)
├── created_at: DateTime
├── last_login_at: DateTime
└── is_active: Boolean (default=True)

FacebookConnection
├── id: String (UUID, PK)
├── user_id: String (FK -> User.id, cascade delete)
├── access_token: String (encrypted)
├── token_expires_at: DateTime
├── facebook_user_id: String
├── created_at: DateTime
└── updated_at: DateTime

AdAccount
├── id: String (UUID, PK)
├── user_id: String (FK -> User.id, cascade delete)
├── facebook_account_id: String
├── name: String
├── currency: String
├── timezone: String
├── is_primary: Boolean (default=False)
├── created_at: DateTime
└── updated_at: DateTime

FacebookPage
├── id: String (UUID, PK)
├── user_id: String (FK -> User.id, cascade delete)
├── facebook_page_id: String
├── name: String
├── profile_picture_url: String
├── is_primary: Boolean (default=False)
├── created_at: DateTime
└── updated_at: DateTime

UserPreferences
├── id: String (UUID, PK)
├── user_id: String (FK -> User.id, unique, cascade delete)
├── default_daily_budget: Float
├── default_currency: String (default='USD')
├── default_geo: String (default='US')
├── default_tone: Enum('friendly', 'professional', 'bold', 'casual')
├── default_objective: Enum('conversions', 'traffic', 'engagement', 'awareness')
├── timezone: String (default='UTC')
├── onboarding_completed: Boolean (default=False)
├── created_at: DateTime
└── updated_at: DateTime

Conversation
├── id: String (UUID, PK)
├── user_id: String (FK -> User.id, cascade delete)
├── title: String (nullable)
├── state: Enum('idle', 'discovery', 'ideation', 'drafting', 'review', 'ready_to_publish', 'published')
├── context: JSON (stores current campaign context)
├── created_at: DateTime
└── updated_at: DateTime

Message
├── id: String (UUID, PK)
├── conversation_id: String (FK -> Conversation.id, cascade delete)
├── role: Enum('user', 'assistant', 'system')
├── content: Text
├── metadata: JSON (nullable, stores tool calls, etc.)
├── created_at: DateTime
└── is_visible: Boolean (default=True)

AdDraft
├── id: String (UUID, PK)
├── conversation_id: String (FK -> Conversation.id, cascade delete)
├── user_id: String (FK -> User.id)
├── campaign_name: String
├── ad_set_name: String
├── ad_name: String
├── primary_text: Text
├── headline: String
├── description: String
├── cta: Enum('learn_more', 'shop_now', 'sign_up', 'contact_us', 'book_now')
├── media_url: String (nullable)
├── media_type: Enum('image', 'video')
├── target_audience: JSON
├── budget: Float
├── budget_type: Enum('daily', 'lifetime')
├── objective: String
├── status: Enum('draft', 'approved', 'published', 'rejected')
├── variant_number: Integer (default=1)
├── parent_draft_id: String (FK -> AdDraft.id, nullable)
├── created_at: DateTime
└── updated_at: DateTime

PublishedCampaign
├── id: String (UUID, PK)
├── user_id: String (FK -> User.id)
├── ad_draft_id: String (FK -> AdDraft.id)
├── facebook_campaign_id: String
├── facebook_adset_id: String
├── facebook_ad_id: String
├── ads_manager_url: String
├── published_at: DateTime
├── status: Enum('active', 'paused', 'deleted')
└── created_at: DateTime

PerformanceSnapshot
├── id: String (UUID, PK)
├── published_campaign_id: String (FK -> PublishedCampaign.id)
├── date: Date
├── spend: Float
├── impressions: Integer
├── clicks: Integer
├── ctr: Float
├── cpc: Float
├── conversions: Integer
├── roas: Float
├── created_at: DateTime
└── updated_at: DateTime

ActivityLog
├── id: String (UUID, PK)
├── user_id: String (FK -> User.id)
├── action_type: Enum('draft_created', 'draft_updated', 'campaign_published', 'budget_changed', 'campaign_paused', 'recommendation_made', 'recommendation_applied')
├── entity_type: String (e.g., 'campaign', 'adset', 'ad', 'draft')
├── entity_id: String
├── rationale: Text (nullable)
├── metadata: JSON (nullable)
├── created_at: DateTime
└── is_agent_action: Boolean (default=False)

PastWinner
├── id: String (UUID, PK)
├── user_id: String (FK -> User.id)
├── campaign_name: String
├── ad_content: JSON (stores full ad details)
├── metrics: JSON (spend, roas, ctr, etc.)
├── winning_factors: Text (agent analysis)
├── created_at: DateTime
└── updated_at: DateTime
```

### 2.2 API Contract (Flask Blueprints)

#### Authentication Routes (`/api/auth`)

| Method | Endpoint | Request | Response | Description |
|--------|----------|---------|----------|-------------|
| GET | `/google/login` | - | Redirect | Initiates Google OAuth flow |
| GET | `/google/callback` | OAuth code | JWT Token | Handles Google OAuth callback |
| GET | `/facebook/connect` | JWT | Redirect | Initiates Facebook OAuth flow |
| GET | `/facebook/callback` | OAuth code | Connection Status | Handles Facebook callback |
| POST | `/logout` | JWT | Success | Invalidates session |
| GET | `/me` | JWT | UserResponse | Returns current user info |

#### User Routes (`/api/users`)

| Method | Endpoint | Request | Response | Description |
|--------|----------|---------|----------|-------------|
| GET | `/preferences` | JWT | PreferencesResponse | Get user preferences |
| PUT | `/preferences` | PreferencesUpdate | PreferencesResponse | Update preferences |
| GET | `/ad-accounts` | JWT | List[AdAccountResponse] | Get linked ad accounts |
| PUT | `/ad-accounts/{id}/primary` | JWT | AdAccountResponse | Set primary ad account |
| GET | `/pages` | JWT | List[PageResponse] | Get linked Facebook pages |
| PUT | `/pages/{id}/primary` | JWT | PageResponse | Set primary page |

#### Onboarding Routes (`/api/onboarding`)

| Method | Endpoint | Request | Response | Description |
|--------|----------|---------|----------|-------------|
| GET | `/status` | JWT | OnboardingStatus | Get onboarding progress |
| POST | `/complete-step` | StepData | OnboardingStatus | Complete onboarding step |

#### Conversation Routes (`/api/conversations`)

| Method | Endpoint | Request | Response | Description |
|--------|----------|---------|----------|-------------|
| GET | `/` | JWT | List[ConversationResponse] | List user conversations |
| POST | `/` | CreateConversation | ConversationResponse | Start new conversation |
| GET | `/{id}` | JWT | ConversationWithMessages | Get conversation with messages |
| POST | `/{id}/messages` | MessageCreate | MessageResponse | Send message to agent |
| GET | `/{id}/messages` | JWT, pagination | List[MessageResponse] | Get conversation messages |

#### Agent Routes (`/api/agent`)

| Method | Endpoint | Request | Response | Description |
|--------|----------|---------|----------|-------------|
| POST | `/chat` | ChatRequest | StreamingResponse | Send message, get streaming response |
| GET | `/daily-brief` | JWT | DailyBriefResponse | Get proactive daily brief |
| POST | `/generate-copy` | CopyRequest | CopyVariants | Generate ad copy variants |
| POST | `/analyze-performance` | TimeRange | PerformanceAnalysis | Analyze account performance |

#### Draft Routes (`/api/drafts`)

| Method | Endpoint | Request | Response | Description |
|--------|----------|---------|----------|-------------|
| GET | `/` | JWT | List[DraftResponse] | List user drafts |
| GET | `/{id}` | JWT | DraftResponse | Get draft details |
| PUT | `/{id}` | DraftUpdate | DraftResponse | Update draft manually |
| POST | `/{id}/publish` | PublishRequest | PublishedCampaignResponse | Publish draft to Facebook |
| GET | `/{id}/variants` | JWT | List[DraftResponse] | Get draft variants |

#### Performance Routes (`/api/performance`)

| Method | Endpoint | Request | Response | Description |
|--------|----------|---------|----------|-------------|
| GET | `/summary` | TimeRange | PerformanceSummary | Get performance summary |
| GET | `/top-performers` | Metric, TimeRange | List[TopPerformer] | Get top performing ads |
| GET | `/underperformers` | Threshold | List[UnderPerformer] | Get underperforming ads |
| GET | `/campaigns` | Filters | List[CampaignMetrics] | Get campaign metrics |

#### Activity Routes (`/api/activity`)

| Method | Endpoint | Request | Response | Description |
|--------|----------|---------|----------|-------------|
| GET | `/` | JWT, Filters | List[ActivityLogResponse] | Get activity log |
| GET | `/recommendations` | JWT | List[Recommendation] | Get pending recommendations |
| POST | `/recommendations/{id}/apply` | JWT | ApplyResult | Apply a recommendation |

### 2.3 Frontend Modules (React)

```
src/
├── api/
│   ├── client.ts              # Axios instance with interceptors
│   ├── auth.ts                # Auth API calls
│   ├── conversations.ts       # Conversation API calls
│   ├── drafts.ts              # Draft API calls
│   ├── performance.ts         # Performance API calls
│   └── user.ts                # User/preferences API calls
│
├── features/
│   ├── auth/
│   │   ├── LoginPage.tsx      # Google Sign-In page
│   │   ├── AuthProvider.tsx   # Auth context provider
│   │   └── useAuth.ts         # Auth hook
│   │
│   ├── onboarding/
│   │   ├── SetupWizard.tsx    # Multi-step wizard container
│   │   ├── ConnectFacebook.tsx
│   │   ├── SelectAdAccount.tsx
│   │   ├── SelectPage.tsx
│   │   └── SetDefaults.tsx
│   │
│   ├── warroom/
│   │   ├── WarRoom.tsx        # Main split-screen layout
│   │   ├── ChatPanel.tsx      # Left panel - chat interface
│   │   ├── MessageList.tsx    # Chat message list
│   │   ├── MessageInput.tsx   # Chat input with attachments
│   │   ├── AgentMessage.tsx   # Agent message bubble
│   │   ├── UserMessage.tsx    # User message bubble
│   │   ├── TypingIndicator.tsx
│   │   ├── LiveStage.tsx      # Right panel container
│   │   ├── CurrentDraft.tsx   # Draft preview tab
│   │   ├── AdMockup.tsx       # Facebook ad mockup component
│   │   ├── VariantSelector.tsx
│   │   ├── DraftEditor.tsx    # Manual edit mode
│   │   ├── PastPerformance.tsx # Performance table tab
│   │   └── ActivityLog.tsx    # Activity timeline tab
│   │
│   ├── settings/
│   │   ├── SettingsPage.tsx
│   │   ├── AccountSection.tsx
│   │   ├── FacebookSection.tsx
│   │   └── PreferencesSection.tsx
│   │
│   └── shared/
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Select.tsx
│       ├── Modal.tsx
│       ├── Toast.tsx
│       ├── Tabs.tsx
│       ├── Table.tsx
│       ├── Loader.tsx
│       └── ProgressBar.tsx
│
├── hooks/
│   ├── useConversation.ts
│   ├── useDrafts.ts
│   ├── usePerformance.ts
│   └── useWebSocket.ts
│
├── context/
│   ├── AuthContext.tsx
│   ├── ConversationContext.tsx
│   └── DraftContext.tsx
│
├── utils/
│   ├── formatters.ts
│   ├── validators.ts
│   └── constants.ts
│
├── App.tsx
├── main.tsx
└── index.css                   # Tailwind imports
```

---

## 3. Agentic Architecture

### 3.1 Agent Hierarchy

```
┌────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                       │
│            (Persona: Senior Media Buyer)                    │
│                                                             │
│  Responsibilities:                                          │
│  - Understand user intent                                   │
│  - Break work into tasks                                    │
│  - Coordinate sub-agents                                    │
│  - Maintain conversation state                              │
│  - Make final decisions                                     │
└─────────────────────┬──────────────────────────────────────┘
                      │
         ┌────────────┼────────────┬────────────┬────────────┐
         │            │            │            │            │
         ▼            ▼            ▼            ▼            ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Performance │ │ Creative │ │Copywriter│ │Execution │ │ QA/Safety│
│   Analyst   │ │Strategist│ │  Agent   │ │  Agent   │ │  Agent   │
└─────────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

### 3.2 Agent Tools

```python
# Tool definitions for LangChain

AGENT_TOOLS = [
    # Performance Analysis
    "get_ad_account_stats",      # Get metrics for time range
    "get_top_performers",        # Find winning ads
    "get_underperformers",       # Find losing ads
    "summarize_performance",     # Plain-language summary

    # Creative Generation
    "generate_creative_briefs",  # Create ad angles/concepts
    "generate_ad_copy",          # Write copy variants
    "suggest_audiences",         # Recommend targeting
    "search_stock_images",       # Find images (Unsplash/Pexels)

    # Preview & State
    "update_preview_state",      # Update UI preview
    "save_draft",                # Persist draft to DB
    "get_current_draft",         # Retrieve current draft

    # Execution
    "publish_campaign",          # Create FB campaign
    "adjust_budget",             # Change campaign budget
    "pause_items",               # Pause campaigns/ads

    # Logging
    "log_decision",              # Record agent reasoning

    # Simulation
    "simulate_results",          # Rough predictions
]
```

### 3.3 State Machine

```
States:
  IDLE          → Initial state, waiting for user
  DISCOVERY     → Gathering info about what user wants
  IDEATION      → Generating creative concepts
  DRAFTING      → Writing ad copy/selecting media
  REVIEW        → User reviewing draft
  READY_TO_PUBLISH → Draft approved, awaiting publish command
  PUBLISHED     → Campaign live

Transitions:
  IDLE → DISCOVERY: User initiates conversation / Daily trigger
  DISCOVERY → IDEATION: User provides product/goal
  IDEATION → DRAFTING: Brief selected
  DRAFTING → REVIEW: Draft complete
  REVIEW → DRAFTING: User requests changes
  REVIEW → READY_TO_PUBLISH: User approves
  READY_TO_PUBLISH → PUBLISHED: publish_campaign() succeeds
  PUBLISHED → IDLE: Conversation complete
  * → IDLE: User explicitly ends / New conversation
```

### 3.4 Memory Architecture

```python
class AgentMemory:
    # Short-term (per conversation)
    conversation_history: List[Message]
    current_draft: Optional[AdDraft]
    current_state: ConversationState
    pending_tool_calls: List[ToolCall]

    # Long-term (per user, persisted in DB)
    past_winners: List[PastWinner]        # Top performing ads
    user_preferences: UserPreferences     # Tone, budget, etc.
    account_config: AdAccount             # Selected account
    learned_patterns: Dict                # What works for this user
```

---

## 4. Implementation Details

### 4.1 Backend Structure

```
backend/
├── app/
│   ├── __init__.py            # Flask app factory
│   ├── config.py              # Configuration classes
│   ├── extensions.py          # SQLAlchemy, etc.
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── facebook.py
│   │   ├── conversation.py
│   │   ├── draft.py
│   │   ├── performance.py
│   │   └── activity.py
│   │
│   ├── api/
│   │   ├── __init__.py        # Blueprint registration
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── onboarding.py
│   │   ├── conversations.py
│   │   ├── agent.py
│   │   ├── drafts.py
│   │   ├── performance.py
│   │   └── activity.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── facebook_service.py
│   │   ├── agent_service.py
│   │   └── performance_service.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Main agent
│   │   ├── performance_analyst.py
│   │   ├── creative_strategist.py
│   │   ├── copywriter.py
│   │   ├── execution_agent.py
│   │   ├── qa_safety_agent.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── performance_tools.py
│   │   │   ├── creative_tools.py
│   │   │   ├── execution_tools.py
│   │   │   └── utility_tools.py
│   │   └── prompts/
│   │       ├── orchestrator.txt
│   │       ├── analyst.txt
│   │       ├── strategist.txt
│   │       ├── copywriter.txt
│   │       └── qa.txt
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   ├── draft.py
│   │   └── performance.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── security.py
│       ├── decorators.py
│       └── helpers.py
│
├── migrations/                 # Flask-Migrate
├── tests/
├── requirements.txt
├── run.py
└── .env.example
```

### 4.2 Key Libraries

**Backend:**
- Flask 3.x
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-CORS
- Flask-JWT-Extended
- Authlib (OAuth)
- LangChain
- OpenAI / Anthropic SDK
- facebook-business SDK
- Pydantic (validation)
- python-dotenv

**Frontend:**
- React 18
- React Router v6
- Tailwind CSS
- Axios
- React Query (TanStack Query)
- Socket.io-client (real-time)
- React Hook Form
- Zustand (state management)

### 4.3 Security Considerations

1. **Token Storage**: Facebook access tokens encrypted at rest (Fernet)
2. **JWT**: Short-lived access tokens (15 min) + refresh tokens
3. **CORS**: Strict origin checking
4. **Rate Limiting**: Per-user rate limits on agent endpoints
5. **Input Validation**: Pydantic schemas for all inputs
6. **Budget Guardrails**: Max budget limits in agent logic
7. **Content Filtering**: QA agent checks for policy violations

### 4.4 Facebook API Integration

```python
# Required permissions
FACEBOOK_PERMISSIONS = [
    'ads_read',           # Read ad data
    'ads_management',     # Create/manage ads
    'pages_read_engagement',  # Read page data
    'business_management',    # Access Business Manager
]

# Key API endpoints used
FACEBOOK_API_ENDPOINTS = {
    'ad_accounts': '/me/adaccounts',
    'pages': '/me/accounts',
    'campaigns': '/{ad_account_id}/campaigns',
    'adsets': '/{ad_account_id}/adsets',
    'ads': '/{ad_account_id}/ads',
    'insights': '/{object_id}/insights',
}
```

---

## 5. Environment Variables

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///dailyadagent.db

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Facebook OAuth
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# AI/LLM
OPENAI_API_KEY=your-openai-key
# or
ANTHROPIC_API_KEY=your-anthropic-key

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Stock Images (optional)
UNSPLASH_ACCESS_KEY=your-unsplash-key
PEXELS_API_KEY=your-pexels-key
```

---

## 6. Deployment Notes

### PythonAnywhere Specific:
- Use WSGI configuration for Flask
- SQLite file stored in persistent storage
- Scheduled tasks for daily triggers
- Static files served separately

### Frontend Hosting:
- Can be hosted on PythonAnywhere static files
- Or separate hosting (Vercel, Netlify)
