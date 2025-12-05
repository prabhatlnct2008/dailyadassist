# Project Status: Page-Based Chat Model

## Current Phase: Not Started

---

## Previous Implementation (Complete)

The initial Daily Ad Agent implementation is complete. See git history for details:
- Backend scaffolding (Flask, SQLAlchemy, JWT auth)
- Database models (User, Conversation, Message, AdDraft, etc.)
- Authentication (Google OAuth, Facebook OAuth)
- Multi-agent system (Orchestrator, Performance Analyst, Copywriter, etc.)
- War Room UI (Chat, Live Stage, Performance tabs)
- Settings and Onboarding

---

## Page-Based Chat Model Implementation

### Overview

Transform from generic chat to page-centric architecture:
- **Workspace** model (1 per user in UI, multiple in schema)
- **Product** catalog with images
- **Page-scoped War Room** chats
- **Account Overview** cross-page chat
- **Legacy conversation** archival with pinned summaries

---

## Phase 1: Database Foundation
**Goal:** Create new models and migrations

### Backend Models
- [ ] Create `Workspace` model (`backend/app/models/workspace.py`)
- [ ] Create `WorkspacePage` model (page-workspace linkage with settings)
- [ ] Create `Product` model (`backend/app/models/product.py`)
- [ ] Create `PageProduct` model (product-page tagging)
- [ ] Add `ConversationType` enum to conversation model
- [ ] Modify `Conversation` model (add chat_type, workspace_id, page_id, archive fields)
- [ ] Modify `User` model (add workspaces relationship, active_workspace_id)
- [ ] Modify `FacebookPage` model (add workspace_pages relationship)
- [ ] Modify `AdAccount` model (add workspace relationship)
- [ ] Update `models/__init__.py` to export new models

### Database Migrations
- [ ] Create Alembic migration for new tables (workspaces, products, workspace_pages, page_products)
- [ ] Create Alembic migration for Conversation modifications
- [ ] Create Alembic migration for User modifications
- [ ] Test migrations (upgrade/downgrade)

### Schemas
- [ ] Create `WorkspaceCreate`, `WorkspaceUpdate`, `WorkspaceResponse` schemas
- [ ] Create `ProductCreate`, `ProductUpdate`, `ProductResponse` schemas
- [ ] Create `WorkspacePageResponse`, `PageSettingsUpdate` schemas
- [ ] Create `PageSetupRequest`, `PageSetupItem` schemas
- [ ] Update `ConversationResponse` schema with new fields

---

## Phase 2: Backend API - Workspaces
**Goal:** Implement workspace CRUD endpoints

### Workspace Blueprint (`/api/workspaces`)
- [ ] Create `backend/app/api/workspaces.py` blueprint
- [ ] GET `/` - List user workspaces
- [ ] POST `/` - Create workspace
- [ ] GET `/<id>` - Get workspace detail (with pages, products)
- [ ] PUT `/<id>` - Update workspace
- [ ] DELETE `/<id>` - Delete workspace
- [ ] POST `/<id>/activate` - Set active workspace
- [ ] Register blueprint in app factory

### Workspace-Facebook Integration
- [ ] POST `/<id>/connect-facebook` - Initiate FB OAuth for workspace
- [ ] Update Facebook callback to link to workspace
- [ ] POST `/<id>/setup-pages` - Configure pages after FB connect

---

## Phase 3: Backend API - Products
**Goal:** Implement product CRUD endpoints

### Product Endpoints (`/api/workspaces/<workspace_id>/products`)
- [ ] Create `backend/app/api/products.py` blueprint
- [ ] GET `/` - List workspace products
- [ ] POST `/` - Create product
- [ ] GET `/<id>` - Get product
- [ ] PUT `/<id>` - Update product
- [ ] DELETE `/<id>` - Delete product
- [ ] POST `/<id>/tag-pages` - Tag product to pages
- [ ] Register blueprint in app factory

---

## Phase 4: Backend API - Page Settings
**Goal:** Implement page settings endpoints

### Page Settings Endpoints (`/api/workspaces/<workspace_id>/pages`)
- [ ] Create `backend/app/api/workspace_pages.py` blueprint
- [ ] GET `/` - List workspace pages with settings
- [ ] GET `/<id>` - Get page detail with settings
- [ ] PUT `/<id>/settings` - Update page settings (tone, CTA, markets)
- [ ] GET `/<id>/products` - Get products tagged to page
- [ ] Register blueprint in app factory

---

## Phase 5: Backend API - Conversations Update
**Goal:** Implement page-scoped conversation system

### Conversation Endpoint Updates
- [ ] GET `/workspace/<workspace_id>` - Get all workspace chats
- [ ] GET `/workspace/<workspace_id>/overview` - Get Account Overview chat
- [ ] GET `/page/<page_id>` - Get Page War Room chat
- [ ] GET `/legacy` - Get archived legacy chats
- [ ] POST `/<id>/archive` - Archive a conversation

### Chat Auto-Creation Service
- [ ] Create `backend/app/services/chat_service.py`
- [ ] Implement `create_workspace_chats()` function
- [ ] Implement `create_page_war_room()` for new pages
- [ ] Implement `get_or_create_overview_chat()`
- [ ] Hook into workspace setup completion

---

## Phase 6: Backend - Agent & Memory Updates
**Goal:** Implement page-scoped agent context

### Memory Service
- [ ] Create `backend/app/services/memory_service.py`
- [ ] Implement `MemoryRetrievalService` class
- [ ] Implement page-scoped context retrieval
- [ ] Implement workspace-scoped context retrieval

### Agent Updates
- [ ] Modify `/api/agent/chat` to accept workspace_id, page_id
- [ ] Update `agent_service.py` to use MemoryRetrievalService
- [ ] Update `/api/agent/daily-brief/<workspace_id>` for workspace scope
- [ ] Update `/api/agent/generate-copy` for page scope
- [ ] Update agent system prompts for page context awareness

### Legacy Migration
- [ ] Create `backend/app/services/migration_service.py`
- [ ] Implement `migrate_legacy_conversations()` function
- [ ] Implement `generate_conversation_summary()` helper
- [ ] Create pinned summary for Account Overview

---

## Phase 7: Frontend - Core Infrastructure
**Goal:** Set up workspace and page context

### Context & State
- [ ] Create `src/features/workspace/WorkspaceContext.jsx`
- [ ] Create `src/context/PageContext.jsx`
- [ ] Update `AuthContext.jsx` to include active workspace
- [ ] Update `ConversationContext.jsx` for chat types

### API Client
- [ ] Create `src/api/workspaces.js`
- [ ] Create `src/api/products.js`
- [ ] Create `src/api/pages.js`
- [ ] Update `src/api/conversations.js` for new endpoints
- [ ] Update `src/api/agent.js` for page context

### Routing
- [ ] Update `App.jsx` with new routes
- [ ] Add `/app/overview` route for Account Overview
- [ ] Add `/app/page/:pageId` route for Page War Room
- [ ] Add `/app/archive` route for legacy viewer
- [ ] Update default redirect after login

---

## Phase 8: Frontend - Navigation & Layout
**Goal:** Implement sidebar navigation

### Sidebar Component
- [ ] Create `src/features/navigation/Sidebar.jsx`
- [ ] Create `AccountOverviewItem.jsx`
- [ ] Create `PageListItem.jsx`
- [ ] Add page selection highlight (active state)
- [ ] Add workspace name header

### War Room Layout Updates
- [ ] Modify `WarRoom.jsx` to include Sidebar
- [ ] Create `WarRoomHeader.jsx` with page/product context
- [ ] Add responsive sidebar toggle for mobile
- [ ] Update grid layout for sidebar

### Page Settings Drawer
- [ ] Create `PageSettingsDrawer.jsx`
- [ ] Implement tone selector dropdown
- [ ] Implement CTA style selector
- [ ] Implement target markets multi-select
- [ ] Hook up to page settings API
- [ ] Add trigger from page header

---

## Phase 9: Frontend - Chat Views
**Goal:** Implement page-scoped chat experiences

### Account Overview Chat
- [ ] Create `AccountOverviewChat.jsx`
- [ ] Display pinned legacy summary (if exists)
- [ ] Implement cross-page summary display
- [ ] Add "Open Page Plan" quick action buttons
- [ ] Style for overview context

### Page War Room Chat
- [ ] Create `PageWarRoomChat.jsx`
- [ ] Add page header strip (active page, product)
- [ ] Create `ProductSelector.jsx` dropdown
- [ ] Integrate page context into chat messages
- [ ] Update preview panel scope text ("Showing for this Page")

### Legacy Archive Viewer
- [ ] Create `LegacyArchiveViewer.jsx`
- [ ] Display archived conversations list
- [ ] Show conversation summaries
- [ ] Allow read-only viewing of old messages
- [ ] Add "back to overview" navigation

### Chat Panel Updates
- [ ] Update `ChatPanel.jsx` for chat type awareness
- [ ] Modify agent message context for page scope
- [ ] Update typing indicators per chat

---

## Phase 10: Frontend - Onboarding Flow
**Goal:** Implement enhanced setup wizard

### Setup Wizard Structure
- [ ] Refactor `SetupWizard.jsx` for new steps
- [ ] Add step progress indicator with labels
- [ ] Implement step navigation (back/next)

### Individual Steps
- [ ] Create `WorkspaceNameStep.jsx` (Step 1)
  - [ ] Workspace name input
  - [ ] Validation
- [ ] Create `FacebookConnectStep.jsx` (Step 2 - optional)
  - [ ] "Connect Facebook" button
  - [ ] "Skip for now" option
  - [ ] Helper text about ideation mode
- [ ] Create `AdAccountSelectStep.jsx` (Step 3)
  - [ ] Ad account dropdown
  - [ ] Account details preview
- [ ] Create `PageSelectionStep.jsx` (Step 4)
  - [ ] Checklist of available pages
  - [ ] Page avatar preview
  - [ ] Select all / deselect all
- [ ] Create `PageSetupStep.jsx` (Step 4b - tone per page)
  - [ ] Loop through selected pages
  - [ ] Tone dropdown per page
  - [ ] Optional: CTA style per page
- [ ] Create `ProductSetupStep.jsx` (Step 5 - optional)
  - [ ] Quick add product form
  - [ ] Product name, USP, price, image
  - [ ] "Add another" / "Skip" buttons
- [ ] Update `CompletionStep.jsx`
  - [ ] Trigger workspace setup completion
  - [ ] Trigger chat auto-creation
  - [ ] Redirect to War Room

### Onboarding API Integration
- [ ] Hook workspace creation to Step 1
- [ ] Hook Facebook OAuth to Step 2
- [ ] Hook ad account selection to Step 3
- [ ] Hook page setup to Steps 4/4b
- [ ] Hook product creation to Step 5
- [ ] Call setup-pages endpoint on completion

---

## Phase 11: Frontend - Products
**Goal:** Implement product management

### Product Components
- [ ] Create `src/features/products/ProductList.jsx`
- [ ] Create `ProductCard.jsx`
- [ ] Create `ProductForm.jsx` (create/edit modal)
- [ ] Create `ProductTagManager.jsx` (tag to pages)
- [ ] Create `ProductSelector.jsx` (dropdown for chat header)

### Product Hooks
- [ ] Create `useProducts.js` query hook
- [ ] Create `useProductMutations.js` mutation hooks

### Integration Points
- [ ] Add product management to Settings page
- [ ] Integrate `ProductSelector` in WarRoomHeader
- [ ] Show active product context in chat
- [ ] Pre-fill product in copy generation

---

## Phase 12: Integration & Polish
**Goal:** End-to-end testing and refinements

### Integration Testing
- [ ] Test complete onboarding flow (with FB connect)
- [ ] Test onboarding flow (skip FB connect)
- [ ] Test page switching in War Room
- [ ] Test product selection in chat
- [ ] Test Account Overview daily brief
- [ ] Test Page War Room ideation flow
- [ ] Test legacy conversation archival
- [ ] Test publish flow with page context

### UI/UX Polish
- [ ] Add loading states to sidebar
- [ ] Add empty states (no pages, no products)
- [ ] Improve mobile responsiveness
- [ ] Add tooltips and help text
- [ ] Ensure consistent styling across views
- [ ] Add keyboard shortcuts (optional)

### Error Handling
- [ ] Add error boundaries
- [ ] Handle Facebook connection failures gracefully
- [ ] Handle missing workspace redirect
- [ ] Add retry logic for failed requests
- [ ] Show user-friendly error messages

### Performance
- [ ] Optimize sidebar rendering
- [ ] Lazy load archive viewer
- [ ] Cache workspace/pages data
- [ ] Debounce page settings updates

---

## Phase 13: Documentation & Cleanup
**Goal:** Finalize implementation

### Documentation
- [ ] Update API documentation (add new endpoints)
- [ ] Add inline code comments for complex logic
- [ ] Update README with new features

### Code Cleanup
- [ ] Remove unused code/components
- [ ] Consolidate duplicate logic
- [ ] Run linter and fix issues
- [ ] Review and fix TypeScript/prop types (if applicable)

### Final Testing
- [ ] Full regression test
- [ ] Test with multiple users
- [ ] Test edge cases (empty states, errors)
- [ ] Security review (token handling, auth checks)

---

## Completion Checklist

### Must-Have (MVP)
- [ ] Workspace model in schema (1 per user in UI)
- [ ] Optional Facebook connect during setup
- [ ] Import pages from Facebook
- [ ] Auto-create chats (Account Overview + Page War Rooms)
- [ ] Sidebar with Account + Pages navigation
- [ ] Page War Room chat + live preview
- [ ] Product management with images (1-3)
- [ ] Product selector in chat header
- [ ] Publish guardrail "connect-to-publish"
- [ ] Legacy conversation archival with summary
- [ ] Pinned summary in Account Overview

### Deferred to V2
- [ ] Multi-workspace UI (switcher)
- [ ] Campaign sub-threads
- [ ] Page-specific audience templates
- [ ] Cross-page budget automation
- [ ] Advanced analytics dashboard

---

## Notes & Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2024-12-05 | Multiple workspaces in schema, single in UI | Future-proof without UI complexity |
| 2024-12-05 | 3 product image fields (URLs) | Simple, no file upload needed |
| 2024-12-05 | Archive legacy conversations, don't delete | Preserve user history |
| 2024-12-05 | No Campaign Threads in MVP | Reduce scope for faster delivery |
| 2024-12-05 | Pin legacy summary to Account Overview | Clean UX, easy access |

---

## Blockers & Issues

_None currently_

---

## Session Log

| Session | Phase | Tasks Completed | Notes |
|---------|-------|-----------------|-------|
| 2024-12-05 | Planning | Created plan.md, phases.md | Initial architecture design |
| - | - | - | Implementation not started |
