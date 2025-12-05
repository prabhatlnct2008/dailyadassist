# Implementation Plan: Page-Based Chat Model

> **Previous Implementation**: The Daily Ad Agent backend and frontend are complete (see phases.md history). This plan covers the architectural refactoring to a **page-centric chat model**.

## 1. System Overview

Transform the Daily Ad Agent from a generic chat model to a **page-centric chat architecture** where:
- **Workspace** = 1 Facebook Ad Account (schema supports multiple, UI starts with 1)
- **Chat Types**: Account Overview (1 per workspace) + Page War Room (1 per page)
- **Products** belong to workspace, optionally tagged to pages
- **Agent memory** is page-scoped for contextual relevance
- **Legacy conversations** archived with pinned summary in Account Overview

### Core Principles
1. Each Facebook Page gets its own dedicated "War Room" chat
2. Account Overview provides cross-page insights and recommendations
3. No "New Chat" button - chats are auto-created based on structure
4. Campaign Threads deferred to V2

### What Changes
| Component | Current State | Required State |
|-----------|--------------|----------------|
| **Workspace** | Missing | 1 per user (schema: multiple), links to 1 Ad Account |
| **Product** | Missing | Multi-product support with 1-3 images, tagged to pages |
| **Conversation** | Generic threads | 3 types: Account Overview, Page War Room, Legacy |
| **FacebookPage** | Basic model | Enhanced via WorkspacePage: tone, CTA style, product tags |
| **Chat Navigation** | Single chat | Sidebar with Account + Pages list |
| **Agent Memory** | Product-based | Page-scoped with fallback hierarchy |
| **Onboarding** | Basic flow | Multi-step wizard with page selection |

---

## 2. Architecture Specification

### 2.1 Database Models (SQLAlchemy)

#### NEW: Workspace Model
```python
# backend/app/models/workspace.py

class Workspace(db.Model):
    __tablename__ = 'workspaces'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., "Red & Co Apparel"

    # Facebook connection (1 ad account per workspace)
    ad_account_id = Column(String(36), ForeignKey('ad_accounts.id'), nullable=True)

    # Defaults
    default_daily_budget = Column(Float, default=500.0)
    default_currency = Column(String(10), default='INR')
    default_objective = Column(String(50), default='CONVERSIONS')
    timezone = Column(String(50), default='Asia/Kolkata')

    # Status
    is_active = Column(Boolean, default=True)
    facebook_connected = Column(Boolean, default=False)
    setup_completed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='workspaces')
    ad_account = relationship('AdAccount', back_populates='workspace')
    products = relationship('Product', back_populates='workspace', cascade='all, delete-orphan')
    pages = relationship('WorkspacePage', back_populates='workspace', cascade='all, delete-orphan')
    conversations = relationship('Conversation', back_populates='workspace', cascade='all, delete-orphan')
```

#### NEW: Product Model
```python
# backend/app/models/product.py

class Product(db.Model):
    __tablename__ = 'products'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey('workspaces.id'), nullable=False)

    # Core fields
    name = Column(String(255), nullable=False)
    short_description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)

    # Pricing
    price = Column(Float, nullable=True)
    price_range_min = Column(Float, nullable=True)
    price_range_max = Column(Float, nullable=True)
    currency = Column(String(10), default='INR')

    # Marketing
    usp = Column(Text, nullable=True)  # Unique Selling Proposition
    target_audience = Column(Text, nullable=True)
    seasonality = Column(String(100), nullable=True)  # e.g., "winter", "all-year", "festive"

    # Media (1-3 images, all optional)
    primary_image_url = Column(String(500), nullable=True)
    image_url_2 = Column(String(500), nullable=True)
    image_url_3 = Column(String(500), nullable=True)

    # Tags for filtering
    tags = Column(JSON, default=list)  # ["hoodie", "winter", "sale"]

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship('Workspace', back_populates='products')
    page_products = relationship('PageProduct', back_populates='product', cascade='all, delete-orphan')
```

#### NEW: WorkspacePage Model (Enhanced Page linkage)
```python
# backend/app/models/workspace.py (continued)

class WorkspacePage(db.Model):
    """Links FacebookPage to Workspace with page-specific settings"""
    __tablename__ = 'workspace_pages'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id = Column(String(36), ForeignKey('workspaces.id'), nullable=False)
    facebook_page_id = Column(String(36), ForeignKey('facebook_pages.id'), nullable=False)

    # Page-specific settings
    default_tone = Column(String(50), default='friendly')  # friendly, professional, bold, casual, playful
    default_cta_style = Column(String(50), nullable=True)  # shop_now, learn_more, sign_up, etc.
    target_markets = Column(JSON, default=list)  # ["India", "US"]

    # Status
    is_included = Column(Boolean, default=True)  # User chose to include this page
    is_primary = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship('Workspace', back_populates='pages')
    facebook_page = relationship('FacebookPage', back_populates='workspace_pages')
    conversation = relationship('Conversation', back_populates='workspace_page', uselist=False)
    page_products = relationship('PageProduct', back_populates='workspace_page', cascade='all, delete-orphan')

    # Unique constraint: one page per workspace
    __table_args__ = (
        UniqueConstraint('workspace_id', 'facebook_page_id', name='uq_workspace_page'),
    )
```

#### NEW: PageProduct Model (Product-Page tagging)
```python
# backend/app/models/product.py (continued)

class PageProduct(db.Model):
    """Associates products with specific pages"""
    __tablename__ = 'page_products'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_page_id = Column(String(36), ForeignKey('workspace_pages.id'), nullable=False)
    product_id = Column(String(36), ForeignKey('products.id'), nullable=False)
    is_default = Column(Boolean, default=False)  # Default product for this page

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workspace_page = relationship('WorkspacePage', back_populates='page_products')
    product = relationship('Product', back_populates='page_products')

    __table_args__ = (
        UniqueConstraint('workspace_page_id', 'product_id', name='uq_page_product'),
    )
```

#### MODIFIED: Conversation Model
```python
# backend/app/models/conversation.py (UPDATED)

class ConversationType(str, Enum):
    ACCOUNT_OVERVIEW = 'account_overview'
    PAGE_WAR_ROOM = 'page_war_room'
    LEGACY = 'legacy'  # For migrated old conversations

class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)

    # NEW: Workspace and Page linkage
    workspace_id = Column(String(36), ForeignKey('workspaces.id'), nullable=True)
    workspace_page_id = Column(String(36), ForeignKey('workspace_pages.id'), nullable=True)

    # NEW: Chat type
    chat_type = Column(SQLEnum(ConversationType), default=ConversationType.LEGACY)

    title = Column(String(255), nullable=True)
    state = Column(String(50), default='idle')
    context = Column(JSON, default=dict)

    # NEW: For legacy migration
    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime, nullable=True)
    archive_summary = Column(Text, nullable=True)  # AI-generated summary

    # NEW: Pinned status (for Account Overview pinned summaries)
    is_pinned = Column(Boolean, default=False)
    pinned_content = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='conversations')
    workspace = relationship('Workspace', back_populates='conversations')
    workspace_page = relationship('WorkspacePage', back_populates='conversation')
    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')
    drafts = relationship('AdDraft', back_populates='conversation')
```

#### MODIFIED: User Model
```python
# Add to existing User model in backend/app/models/user.py

# Add these fields:
active_workspace_id = Column(String(36), ForeignKey('workspaces.id', use_alter=True), nullable=True)

# Add this relationship:
workspaces = relationship('Workspace', back_populates='user', foreign_keys='Workspace.user_id', cascade='all, delete-orphan')
active_workspace = relationship('Workspace', foreign_keys=[active_workspace_id], post_update=True)
```

#### MODIFIED: FacebookPage Model
```python
# Add to existing FacebookPage model in backend/app/models/facebook.py

# Add this relationship:
workspace_pages = relationship('WorkspacePage', back_populates='facebook_page', cascade='all, delete-orphan')
```

#### MODIFIED: AdAccount Model
```python
# Add to existing AdAccount model in backend/app/models/facebook.py

# Add this relationship:
workspace = relationship('Workspace', back_populates='ad_account', uselist=False)
```

---

### 2.2 API Contract (Flask Blueprints)

#### Workspace Endpoints (`/api/workspaces`)
| Method | Endpoint | Request Schema | Response Schema | Description |
|--------|----------|----------------|-----------------|-------------|
| GET | `/` | - | `List[WorkspaceResponse]` | List user's workspaces |
| POST | `/` | `WorkspaceCreate` | `WorkspaceResponse` | Create workspace |
| GET | `/<id>` | - | `WorkspaceDetailResponse` | Get workspace with pages/products |
| PUT | `/<id>` | `WorkspaceUpdate` | `WorkspaceResponse` | Update workspace |
| DELETE | `/<id>` | - | `204` | Delete workspace |
| POST | `/<id>/activate` | - | `WorkspaceResponse` | Set as active workspace |
| POST | `/<id>/connect-facebook` | - | `redirect` | Initiate Facebook OAuth for workspace |
| POST | `/<id>/setup-pages` | `PageSetupRequest` | `WorkspaceResponse` | Configure pages after FB connect |

#### Product Endpoints (`/api/workspaces/<workspace_id>/products`)
| Method | Endpoint | Request Schema | Response Schema | Description |
|--------|----------|----------------|-----------------|-------------|
| GET | `/` | - | `List[ProductResponse]` | List workspace products |
| POST | `/` | `ProductCreate` | `ProductResponse` | Create product |
| GET | `/<id>` | - | `ProductResponse` | Get product |
| PUT | `/<id>` | `ProductUpdate` | `ProductResponse` | Update product |
| DELETE | `/<id>` | - | `204` | Delete product |
| POST | `/<id>/tag-pages` | `PageTagRequest` | `ProductResponse` | Tag product to pages |

#### Page Settings Endpoints (`/api/workspaces/<workspace_id>/pages`)
| Method | Endpoint | Request Schema | Response Schema | Description |
|--------|----------|----------------|-----------------|-------------|
| GET | `/` | - | `List[WorkspacePageResponse]` | List workspace pages with settings |
| GET | `/<id>` | - | `WorkspacePageDetailResponse` | Get page detail with settings |
| PUT | `/<id>/settings` | `PageSettingsUpdate` | `WorkspacePageResponse` | Update page settings (tone, CTA, markets) |
| GET | `/<id>/products` | - | `List[ProductResponse]` | Get products tagged to page |

#### Modified Conversation Endpoints (`/api/conversations`)
| Method | Endpoint | Request Schema | Response Schema | Description |
|--------|----------|----------------|-----------------|-------------|
| GET | `/workspace/<workspace_id>` | - | `ConversationListResponse` | Get all chats for workspace |
| GET | `/workspace/<workspace_id>/overview` | - | `ConversationResponse` | Get Account Overview chat |
| GET | `/page/<page_id>` | - | `ConversationResponse` | Get Page War Room chat |
| GET | `/legacy` | - | `List[ConversationResponse]` | Get archived legacy chats |
| POST | `/<id>/archive` | - | `ConversationResponse` | Archive a conversation |

#### Modified Agent Endpoints (`/api/agent`)
| Method | Endpoint | Request Schema | Response Schema | Description |
|--------|----------|----------------|-----------------|-------------|
| POST | `/chat` | `ChatRequest` (+ workspace_id, page_id) | `SSE Stream` | Page-scoped chat |
| GET | `/daily-brief/<workspace_id>` | - | `DailyBriefResponse` | Workspace daily summary |
| POST | `/generate-copy` | `CopyRequest` (+ page_id) | `CopyResponse` | Page-scoped copy generation |

---

### 2.3 Pydantic Schemas

```python
# backend/app/schemas/workspace.py

class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    default_daily_budget: Optional[float] = 500.0
    default_currency: Optional[str] = 'INR'
    timezone: Optional[str] = 'Asia/Kolkata'

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    default_daily_budget: Optional[float] = None
    default_currency: Optional[str] = None
    default_objective: Optional[str] = None
    timezone: Optional[str] = None

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    facebook_connected: bool
    setup_completed: bool
    ad_account_id: Optional[str]
    default_daily_budget: float
    default_currency: str
    default_objective: str
    timezone: str
    created_at: datetime

    class Config:
        from_attributes = True

class WorkspaceDetailResponse(WorkspaceResponse):
    pages: List['WorkspacePageResponse']
    products: List['ProductResponse']
    ad_account: Optional['AdAccountResponse']
```

```python
# backend/app/schemas/product.py

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price: Optional[float] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    currency: Optional[str] = 'INR'
    usp: Optional[str] = None
    target_audience: Optional[str] = None
    seasonality: Optional[str] = None
    primary_image_url: Optional[str] = None
    image_url_2: Optional[str] = None
    image_url_3: Optional[str] = None
    tags: Optional[List[str]] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price: Optional[float] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    currency: Optional[str] = None
    usp: Optional[str] = None
    target_audience: Optional[str] = None
    seasonality: Optional[str] = None
    primary_image_url: Optional[str] = None
    image_url_2: Optional[str] = None
    image_url_3: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    short_description: Optional[str]
    long_description: Optional[str]
    price: Optional[float]
    price_range_min: Optional[float]
    price_range_max: Optional[float]
    currency: str
    usp: Optional[str]
    target_audience: Optional[str]
    seasonality: Optional[str]
    primary_image_url: Optional[str]
    image_url_2: Optional[str]
    image_url_3: Optional[str]
    tags: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PageTagRequest(BaseModel):
    page_ids: List[str]
    set_default_for: Optional[str] = None  # page_id to set as default
```

```python
# backend/app/schemas/workspace_page.py

class PageSettingsUpdate(BaseModel):
    default_tone: Optional[str] = None
    default_cta_style: Optional[str] = None
    target_markets: Optional[List[str]] = None
    is_included: Optional[bool] = None

class WorkspacePageResponse(BaseModel):
    id: str
    workspace_id: str
    facebook_page_id: str
    facebook_page: 'FacebookPageResponse'
    default_tone: str
    default_cta_style: Optional[str]
    target_markets: List[str]
    is_included: bool
    is_primary: bool
    has_conversation: bool
    conversation_id: Optional[str]

    class Config:
        from_attributes = True

class PageSetupRequest(BaseModel):
    pages: List['PageSetupItem']

class PageSetupItem(BaseModel):
    facebook_page_id: str
    is_included: bool = True
    default_tone: Optional[str] = 'friendly'
```

---

### 2.4 Frontend Modules

#### New Components

**Feature: Workspace Management**
```
src/features/workspace/
├── WorkspaceContext.jsx       # Context for active workspace
├── WorkspaceSwitcher.jsx      # Dropdown (UI hidden for V1, logic ready)
├── WorkspaceSettings.jsx      # Workspace configuration modal
└── hooks/
    ├── useWorkspace.js        # Active workspace hook
    └── useWorkspaces.js       # All workspaces query
```

**Feature: Page-Based Navigation (NEW)**
```
src/features/navigation/
├── Sidebar.jsx                # Left sidebar with Account + Pages
├── AccountOverviewItem.jsx    # "Account Overview" nav item
├── PageListItem.jsx           # Individual page nav item
├── PageSettingsDrawer.jsx     # Page tone/CTA settings drawer
└── hooks/
    └── useNavigation.js       # Navigation state
```

**Feature: Products (NEW)**
```
src/features/products/
├── ProductList.jsx            # Product grid/list view
├── ProductCard.jsx            # Product display card
├── ProductForm.jsx            # Create/edit product form
├── ProductSelector.jsx        # Dropdown in chat header
├── ProductTagManager.jsx      # Tag products to pages
└── hooks/
    ├── useProducts.js         # Products query
    └── useProductMutations.js # CRUD mutations
```

**Feature: War Room (MODIFIED)**
```
src/features/warroom/
├── WarRoom.jsx                # MODIFIED: Add sidebar, page context
├── WarRoomHeader.jsx          # NEW: Active page, product selector
├── ChatPanel.jsx              # MODIFIED: Page-scoped context
├── AccountOverviewChat.jsx    # NEW: Cross-page summary view
├── PageWarRoomChat.jsx        # NEW: Page-specific chat
├── LegacyArchiveViewer.jsx    # NEW: View archived conversations
├── PinnedSummary.jsx          # NEW: Pinned legacy summary
└── ...existing components
```

**Feature: Onboarding (MODIFIED)**
```
src/features/onboarding/
├── SetupWizard.jsx            # MODIFIED: New steps
├── steps/
│   ├── WorkspaceNameStep.jsx  # Step 1: Name workspace
│   ├── FacebookConnectStep.jsx # Step 2: Optional FB connect
│   ├── AdAccountSelectStep.jsx # Step 3: Select ad account
│   ├── PageSelectionStep.jsx  # Step 4: Choose pages (NEW)
│   ├── PageSetupStep.jsx      # Step 4b: Set page tones (NEW)
│   ├── ProductSetupStep.jsx   # Step 5: Add products (NEW)
│   └── CompletionStep.jsx     # Redirect to War Room
└── hooks/
    └── useOnboarding.js
```

#### Modified Components

**API Layer**
```
src/api/
├── workspaces.js              # NEW: Workspace CRUD
├── products.js                # NEW: Product CRUD
├── pages.js                   # NEW: Page settings
├── conversations.js           # MODIFIED: Page-scoped queries
└── agent.js                   # MODIFIED: Page context in chat
```

**Context**
```
src/context/
├── WorkspaceContext.jsx       # NEW: Active workspace state
├── PageContext.jsx            # NEW: Active page state
├── ConversationContext.jsx    # MODIFIED: Chat type awareness
└── AuthContext.jsx            # MODIFIED: Include active workspace
```

---

### 2.5 Agent Memory Architecture

#### Page-Scoped Memory Retrieval

```python
# backend/app/services/memory_service.py

class MemoryRetrievalService:
    """Handles page-scoped memory for agent context"""

    def get_context_for_chat(
        self,
        chat_type: ConversationType,
        workspace_id: str,
        page_id: Optional[str] = None,
        product_id: Optional[str] = None
    ) -> dict:
        """
        Retrieval priority:
        1. Page War Room: page history → page products → page settings
        2. Account Overview: workspace-wide metrics → all pages summary
        """

        if chat_type == ConversationType.PAGE_WAR_ROOM:
            return {
                'page_history': self._get_page_conversation_history(page_id),
                'page_settings': self._get_page_settings(page_id),
                'active_product': self._get_product(product_id) if product_id else None,
                'page_products': self._get_page_products(page_id),
                'page_performance': self._get_page_performance(page_id),
                'past_winners': self._get_page_winners(page_id),
            }

        elif chat_type == ConversationType.ACCOUNT_OVERVIEW:
            return {
                'workspace_summary': self._get_workspace_summary(workspace_id),
                'all_pages_performance': self._get_all_pages_performance(workspace_id),
                'cross_page_recommendations': self._get_recommendations(workspace_id),
                'pinned_legacy_summary': self._get_pinned_summary(workspace_id),
            }

    def _get_page_conversation_history(self, page_id: str, limit: int = 50) -> List[dict]:
        """Get recent messages from page's war room"""
        pass

    def _get_page_settings(self, page_id: str) -> dict:
        """Get page tone, CTA style, target markets"""
        pass

    def _get_page_products(self, page_id: str) -> List[dict]:
        """Get products tagged to this page"""
        pass

    def _get_page_performance(self, page_id: str, days: int = 7) -> dict:
        """Get recent performance metrics for page's campaigns"""
        pass

    def _get_workspace_summary(self, workspace_id: str) -> dict:
        """Get overall workspace stats"""
        pass

    def _get_all_pages_performance(self, workspace_id: str) -> List[dict]:
        """Get performance summary for all pages"""
        pass
```

---

### 2.6 Migration Strategy

#### Legacy Conversation Handling

```python
# backend/app/services/migration_service.py

def migrate_legacy_conversations(user_id: str, workspace_id: str):
    """
    Migration steps:
    1. Find all conversations without workspace_id for this user
    2. Mark as chat_type = LEGACY
    3. Set is_archived = True
    4. Generate AI summary for each (batch)
    5. Create pinned summary in Account Overview
    """

    legacy_convos = Conversation.query.filter(
        Conversation.user_id == user_id,
        Conversation.workspace_id.is_(None),
        Conversation.chat_type != ConversationType.LEGACY
    ).all()

    if not legacy_convos:
        return

    summaries = []
    for convo in legacy_convos:
        # Archive the conversation
        convo.chat_type = ConversationType.LEGACY
        convo.is_archived = True
        convo.archived_at = datetime.utcnow()

        # Generate summary using agent
        convo.archive_summary = generate_conversation_summary(convo)
        summaries.append({
            'title': convo.title,
            'summary': convo.archive_summary,
            'message_count': len(convo.messages),
            'created_at': convo.created_at.isoformat()
        })

    db.session.commit()

    # Create pinned summary in Account Overview
    overview_chat = get_or_create_overview_chat(workspace_id)
    overview_chat.is_pinned = True
    overview_chat.pinned_content = json.dumps({
        'type': 'legacy_archive',
        'message': f'Archived {len(legacy_convos)} previous conversations',
        'conversations': summaries
    })
    db.session.commit()
```

---

## 3. Implementation Details

### 3.1 Auto-Chat Creation Logic

When a workspace completes setup:
```python
def create_workspace_chats(workspace: Workspace):
    """Auto-create required chats for workspace"""

    # 1. Create Account Overview chat
    overview_chat = Conversation(
        user_id=workspace.user_id,
        workspace_id=workspace.id,
        chat_type=ConversationType.ACCOUNT_OVERVIEW,
        title=f"{workspace.name} - Account Overview"
    )
    db.session.add(overview_chat)

    # 2. Create Page War Room for each included page
    for wp in workspace.pages:
        if wp.is_included:
            page_chat = Conversation(
                user_id=workspace.user_id,
                workspace_id=workspace.id,
                workspace_page_id=wp.id,
                chat_type=ConversationType.PAGE_WAR_ROOM,
                title=f"{wp.facebook_page.name} War Room"
            )
            db.session.add(page_chat)

    db.session.commit()

    # 3. If legacy conversations exist, migrate them
    migrate_legacy_conversations(workspace.user_id, workspace.id)
```

### 3.2 Daily Brief Enhancement

```python
def generate_workspace_daily_brief(workspace_id: str) -> str:
    """
    Enhanced daily brief for Account Overview:
    - Yesterday's total spend across all pages
    - Per-page performance summary
    - Top performer identification
    - Cross-page recommendations
    - Suggested actions with page links
    """
    workspace = Workspace.query.get(workspace_id)
    pages = WorkspacePage.query.filter_by(
        workspace_id=workspace_id,
        is_included=True
    ).all()

    # Gather metrics per page
    page_metrics = []
    for page in pages:
        metrics = get_page_performance(page.id, days=1)
        page_metrics.append({
            'page_name': page.facebook_page.name,
            'page_id': page.id,
            **metrics
        })

    # Generate summary using agent
    brief = agent_service.generate_brief(
        workspace_name=workspace.name,
        page_metrics=page_metrics,
        workspace_defaults=workspace.to_dict()
    )

    return brief
```

### 3.3 Frontend Routing

```javascript
// App.jsx routes update
<Route path="/app" element={<WarRoom />}>
  <Route index element={<Navigate to="overview" replace />} />
  <Route path="overview" element={<AccountOverviewChat />} />
  <Route path="page/:pageId" element={<PageWarRoomChat />} />
  <Route path="archive" element={<LegacyArchiveViewer />} />
</Route>
<Route path="/setup" element={<SetupWizard />} />
<Route path="/settings" element={<SettingsPage />} />
```

### 3.4 Sidebar Navigation Structure

```jsx
// Sidebar.jsx structure
<aside className="w-64 bg-gray-900 text-white">
  {/* Account Section */}
  <div className="p-4 border-b border-gray-700">
    <h3 className="text-xs uppercase text-gray-400">Account</h3>
    <NavLink to="/app/overview">
      <AccountOverviewItem />
    </NavLink>
  </div>

  {/* Pages Section */}
  <div className="p-4">
    <h3 className="text-xs uppercase text-gray-400">Pages</h3>
    <nav className="space-y-1 mt-2">
      {pages.map(page => (
        <NavLink key={page.id} to={`/app/page/${page.id}`}>
          <PageListItem page={page} />
        </NavLink>
      ))}
    </nav>
  </div>

  {/* Archive Link (if legacy exists) */}
  {hasLegacyConversations && (
    <div className="p-4 border-t border-gray-700">
      <NavLink to="/app/archive">
        📁 Archived Conversations
      </NavLink>
    </div>
  )}
</aside>
```

---

## 4. Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Workspace-User relation | Many-to-One (schema), One-to-One (UI V1) | Future-proof for multi-workspace |
| Product images | 3 optional URL fields | Simple, no file upload complexity |
| Chat auto-creation | On workspace setup completion | Ensures consistent structure |
| Legacy migration | Archive + summarize + pin | Preserves history without clutter |
| Page settings storage | Separate WorkspacePage model | Flexibility for page-specific config |
| Memory scoping | Service layer abstraction | Clean separation, testable |
| No Campaign Threads | Deferred to V2 | Reduces MVP scope |

---

## 5. External Dependencies

No new packages required. Existing stack sufficient:
- **Backend**: Flask, SQLAlchemy, Flask-Migrate, Pydantic
- **Frontend**: React, React Router, TailwindCSS, React Query

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Legacy data loss | High | Archive instead of delete, generate summaries |
| Performance with many pages | Medium | Pagination, lazy loading in sidebar |
| Complex onboarding | Medium | Skip options, sensible defaults, clear progress |
| Agent context confusion | High | Clear chat type boundaries in system prompts |
| Migration failures | Medium | Batch processing, error recovery, manual fallback |
