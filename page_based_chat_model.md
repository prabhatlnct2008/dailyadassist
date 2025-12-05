Daily Ad Agent – Page-Based Chat Model

This document defines a clean, page-centric chat structure for a single Facebook Ad Account managing multiple Facebook Pages. It includes:
	•	Exact application flow
	•	Updated user stories + acceptance criteria
	•	Detailed screen specs (functional)
	•	Changes required vs your current functional spec

⸻

1) Core Principle

1.1 Workspace-first, Page-centric chat
	•	Workspace = 1 Facebook Ad Account
	•	Inside a Workspace:
	•	Multiple Facebook Pages
	•	Multiple Products
	•	Chat is anchored to Pages

1.2 Chat Types (controlled and simple)
	1.	Account Overview Chat (one per workspace)

	•	Purpose: global daily summary, cross-page recommendations, overall spend/ROAS view.

	2.	Page War Room Chat (one per Facebook Page)

	•	Purpose: day-to-day ideation, drafting, preview, approval, publishing for that page.

	3.	Campaign Threads (optional, auto-created)

	•	Purpose: deep execution threads for big launches.
	•	Hidden by default; surfaced only when created.

1.3 Why this model is best
	•	Each page often has a unique:
	•	audience
	•	tone
	•	product mix
	•	content identity
	•	A dedicated page chat prevents memory pollution across pages.
	•	Keeps UI simple: no ChatGPT-style “infinite thread chaos.”

⸻

2) Application Flow (End-to-End)

2.1 First-time user flow (ideal)
	1.	Login with Google
	2.	Create Workspace
	•	Agent prompt: “What should we call this brand/workspace?”
	3.	Connect Facebook Ad Account (optional but recommended)
	•	Agent: “Want to connect your Facebook Ad Account now? You can still use ideation without connecting.”
	4.	Select Ad Account
	5.	Fetch Pages from Facebook
	6.	Page Setup
	•	For each detected page:
	•	confirm page inclusion
	•	optionally set a page tone
	•	optionally map default products
	7.	Create default chats automatically
	•	System creates:
	•	1 Account Overview Chat
	•	1 Page War Room Chat per selected Page
	8.	Add Products (optional step now or later)
	•	Products are associated to workspace
	•	Optionally tag products to pages

2.2 Returning user daily flow
	1.	User opens app
	2.	Lands on Account Overview Chat (default home)
	3.	Agent sends morning summary:
	•	“Yesterday total spend ₹X across 5 pages. Best ROAS came from Page A…”
	4.	User clicks a page in sidebar
	5.	Lands in that Page War Room
	6.	Agent continues with page-scoped plan:
	•	“On Red & Co Kids, playful short copy performed best. Want 3 new variants for today?”

2.3 Page-only execution flow
	1.	User selects Page: Red & Co Apparel
	2.	Agent header shows:
	•	Active Page
	•	Ad Account
	•	Active Product (if selected)
	3.	User asks:
	•	“Let’s promote red hoodies today.”
	4.	Agent:
	•	checks page history
	•	suggests 2–3 angles
	•	generates draft copy
	•	updates preview
	5.	User:
	•	“Make it shorter and add urgency.”
	6.	Agent iterates preview
	7.	User:
	•	“Approve & publish with ₹2,000/day.”
	8.	Agent asks final confirmation
	9.	Publish flow runs

2.4 If Facebook is not connected
	•	All non-Facebook actions still work:
	•	product setup
	•	ideation
	•	copy generation
	•	mock previews
	•	audience suggestions (generic)
	•	When user tries to publish:
	•	Agent: “To publish for this page, please connect your Facebook Ad Account.”
	•	Primary CTA: “Connect Facebook to publish”

⸻

3) Updated User Stories + Acceptance Criteria

Epic A – Workspace & Account Setup

Story A1: Create Workspace
As a user
I want to create a workspace
So that my ad account, pages, products, and chats stay organized.

Acceptance Criteria
	•	On first login, system prompts for workspace name.
	•	Workspace record created.
	•	User can manage multiple workspaces in future (optional V2).

Story A2: Optional Facebook connect
As a user
I want to connect Facebook optionally during setup
So that I can still explore the app before granting permissions.

Acceptance Criteria
	•	Setup screen offers:
	•	“Connect Facebook”
	•	“Skip for now”
	•	If skipped:
	•	workspace is created
	•	only mock/ideation mode is enabled

Story A3: Select Ad Account
As a user
I want to select which ad account to manage
So that the agent uses the correct data.

Acceptance Criteria
	•	After Facebook OAuth, a dropdown lists ad accounts.
	•	Selected ad account is stored at workspace-level.

⸻

Epic B – Pages

Story B1: Import Pages
As a user
I want the system to fetch my pages automatically
So that setup is fast.

Acceptance Criteria
	•	After ad account selection, system fetches pages linked to user.
	•	UI shows a checklist of pages.
	•	User can choose which pages to include in the workspace.

Story B2: Page-specific defaults
As a user
I want to set a default tone and focus per page
So the agent feels consistent with that page’s brand.

Acceptance Criteria
	•	Each page can store:
	•	default tone
	•	default CTA style (optional)
	•	default product tags (optional)

⸻

Epic C – Chat Structure

Story C1: Auto-create chats
As a user
I want default chats created automatically
So I don’t have to manage threads.

Acceptance Criteria
	•	System creates:
	•	1 Account Overview Chat per workspace
	•	1 Page War Room Chat per included Page
	•	No “New Chat” button is shown by default.

Story C2: One chat per page
As a user
I want one dedicated chat per page
So that each page’s strategy stays focused.

Acceptance Criteria
	•	Sidebar lists pages.
	•	Clicking a page opens its Page War Room.
	•	The agent’s memory retrieval defaults to page-scoped history.

Story C3: Account Overview chat
As a user
I want an overall ad-account chat
So I can see cross-page performance and guidance.

Acceptance Criteria
	•	Account Overview appears above Pages in sidebar.
	•	The agent summarizes yesterday/last 7 days across all pages.

⸻

Epic D – Products (within Page chats)

Story D1: Add products to workspace
As a user
I want to add multiple products
So the agent can draft ads without me repeating context.

Acceptance Criteria
	•	Products are created under the workspace.
	•	Product fields include:
	•	name
	•	short description
	•	price range
	•	USP
	•	seasonality
	•	optional default page

Story D2: Product selector inside page chat
As a user
I want to select an active product inside the page chat
So the agent drafts correctly for that page.

Acceptance Criteria
	•	Page War Room header shows:
	•	“Active Product: ____ ▼”
	•	option “+ Add Product”
	•	Selecting a product updates agent context immediately.

⸻

Epic E – Publishing & Guardrails

Story E1: Connect-to-publish
As a user
I want clear prompts when Facebook isn’t connected
So I understand what’s blocked.

Acceptance Criteria
	•	In mock mode, “Approve & publish” button becomes:
	•	“Connect Facebook to publish”
	•	Agent messages explain publish dependency.

Story E2: Page-scoped publish
As a user
I want the agent to publish for the active page
So I don’t need to reselect identity each time.

Acceptance Criteria
	•	Publishing uses:
	•	active workspace ad account
	•	active page as identity
	•	active product if selected
	•	Agent confirms:
	•	budget
	•	page
	•	product
	•	audience

⸻

4) Screen Specifications (Functional)

Screen 1 – Login

Purpose: Secure entry.

Elements
	•	Logo + name: “Daily Ad Agent”
	•	Tagline: “Your AI media buyer for Facebook Ads.”
	•	Primary button: “Continue with Google”
	•	Reassurance text:
	•	“We only use Google for login.”
	•	“You control all publishing.”

⸻

Screen 2 – Workspace Setup Wizard

Step 1: Name your workspace
	•	Input label: “Workspace name”
	•	Placeholder: “e.g., Red & Co Apparel”
	•	Button: “Continue”

Step 2: Connect Facebook (optional)
	•	Two buttons:
	•	“Connect Facebook”
	•	“Skip for now”
	•	Helper text:
	•	“You can still use ideation and previews without connecting.”

Step 3: Select Ad Account (if connected)
	•	Dropdown of ad accounts
	•	Button: “Use this ad account”

Step 4: Choose Pages
	•	Checklist of pages
	•	For each page line item:
	•	Page name
	•	small preview avatar
	•	optional “Set tone (later)” link
	•	Button: “Add selected pages”

Step 5: Add Products (optional)
	•	Quick add form:
	•	product name
	•	one-line USP
	•	price range
	•	optional default page
	•	Button:
	•	“Add product”
	•	“Skip”

Completion redirects to War Room.

⸻

Screen 3 – War Room (New Navigation)

Top Bar
	•	Left: Logo + “Daily Ad Agent”
	•	Center tabs:
	•	“War Room”
	•	“Performance” (optional V2)
	•	“Settings”
	•	Right: Help + user avatar

Left Sidebar (NEW)

Section header:
	•	“Account”
Item:
	•	“Account Overview”

Section header:
	•	“Pages”
List:
	•	“Red & Co Apparel”
	•	“Red & Co Kids”
	•	“Red & Co Clearance”
	•	etc.

Main area (two columns)

Left column (Chat)
	•	Header displays:
	•	“Daily Ad Agent”
	•	“Active Page: Red & Co Apparel” (hidden when in account overview)
	•	Status dot: Online

Right column (Live Stage)
Tabs:
	•	“Current draft”
	•	“Past performance”
	•	“Activity log”

⸻

Screen 4 – Account Overview Chat View

Purpose: Cross-page summary.

Agent’s first daily message example:
	•	“Yesterday across 5 pages: Spend ₹X, average ROAS Y.”
	•	“Top performer: Red & Co Kids – ‘Winter Bundle’ ROAS 3.9.”
	•	“Recommended today: Scale kids page by 20% and test urgency copy for Apparel page.”

Buttons in chat suggestions (optional):
	•	“Open Red & Co Kids plan”
	•	“Apply budget suggestion”

⸻

Screen 5 – Page War Room Chat View

Purpose: Page-specific ideation, drafting, approval.

Page header strip (above chat input)
	•	“Active Page: Red & Co Apparel”
	•	“Active Product: Red Hoodie ▼”
	•	Quick action link: “Change page settings”

Agent message pattern
	1.	Page summary
	2.	2–3 angles
	3.	Draft variants
	4.	Preview updated

⸻

Screen 6 – Page Settings Drawer

Accessible from page header.

Fields:
	•	Page tone dropdown
	•	Default CTA style
	•	Default products tags (multi-select)
	•	Target markets (optional)

Button:
	•	“Save page defaults”

⸻

Screen 7 – Settings (Workspace)

Facebook connection block
	•	Status: Connected / Not connected
	•	Buttons:
	•	“Reconnect Facebook”
	•	“Change Ad Account”

Defaults
	•	Default test budget
	•	Default objective
	•	Timezone

⸻

5) What changes are needed in your existing functional spec (Functional only)

Your current spec is strong, but it assumes a more generic chat model. You’ll need these changes:

5.1 Update the Information Architecture

Before
	•	Dashboard split UI
	•	One main chat with product context

After
	•	Add a left sidebar with:
	•	Account Overview chat
	•	Pages list
	•	This becomes the primary navigation.

5.2 Redefine chat rules

Add explicit constraints
	•	1 Account Overview thread per workspace
	•	1 Page War Room thread per page
	•	Campaign threads are auto-created only when needed

Remove / avoid
	•	A generic “New Chat” button

5.3 Shift memory defaults

Before
	•	Agent memory mainly product-based

After
	•	Agent memory retrieval should prioritize:
	1.	active page history
	2.	active product within that page
	3.	global account signals only when in Account Overview

5.4 Clarify reporting scope in UI copy

Add new microcopy in Past Performance tab:
	•	When in Page War Room:
	•	“Showing results for campaigns linked to this Page.”
	•	When in Account Overview:
	•	“Showing results across the full Ad Account.”

5.5 Adjust onboarding/Setup Wizard

Add new step: “Choose Pages”
Add new behavior: auto-create chats based on pages.

5.6 Publish confirmation updates

Update publish confirmation text to include page explicitly:
	•	“Publishing under Page: Red & Co Apparel with budget ₹X/day. Proceed?”

5.7 Add Page Settings (lightweight)

Introduce a simple drawer or modal to store:
	•	page tone
	•	default product tags

⸻

6) Recommended MVP cut (so you don’t overbuild)

Must-have
	•	Workspace = 1 ad account
	•	Optional Facebook connect
	•	Import pages
	•	Auto-create chats
	•	Sidebar with Account Overview + Page chats
	•	Page War Room chat + live preview
	•	Publish guardrail “connect-to-publish”

Nice-to-have later
	•	Campaign sub-threads
	•	Page-specific audience templates
	•	Cross-page budget automation

⸻

7) The clean final rule set (copy-paste)
	1.	A user creates a Workspace.
	2.	A Workspace connects to one Facebook Ad Account.
	3.	The system imports Pages and the user selects which to include.
	4.	The system auto-creates:
	•	1 Account Overview Chat
	•	1 Page War Room Chat per Page
	5.	Products belong to the workspace and can be optionally tagged to pages.
	6.	Inside each Page War Room:
	•	the agent defaults to page-scoped memory and performance.
	7.	If Facebook isn’t connected:
	•	ideation + draft + preview works
	•	publishing is blocked with clear “Connect to publish” UX.

⸻

8) Success criteria for this model
	•	Users can visually understand the structure in 5 seconds:
	•	“Account summary here.”
	•	“Each page has its own AI war room.”
	•	The agent never mixes tones across pages.
	•	The primary workflow stays one screen deep:
	•	click page → chat → preview → approve.