Functional Specification – Daily Facebook Ad Agent (Agentic Ad Assistant)

1. Product Overview

Name (working): Daily Ad Agent
Platform: Python/Flask backend (PythonAnywhere), React (or plain JS) frontend
Core Idea:
A conversational, “agentic” AI that plans, drafts, tests, and launches Facebook ads daily for small marketers and founders. Instead of forcing users into complex dashboards, the system acts like a Senior Media Buyer in chat form, connected to the Facebook Marketing API.

The agent:
	•	Proactively opens conversations every day.
	•	Analyzes past performance.
	•	Suggests creative & copy.
	•	Previews everything in a “War Room” interface.
	•	Launches / adjusts campaigns when the user approves.

⸻

2. Personas & Goals

Primary Persona: Busy Marketer / Founder
	•	Runs or manages 1–5 Facebook Ad accounts.
	•	Hates spending time inside Ads Manager.
	•	Wants: “Tell me what to do today” + “Make ads that work, fast.”

Top Jobs-To-Be-Done:
	1.	“Give me a ready-to-launch ad every day.”
	2.	“Let me approve/edit from one screen.”
	3.	“Learn what works and double down automatically.”

⸻

3. High-Level Epics
	1.	Epic A – Authentication & Integration
	2.	Epic B – Onboarding & Settings
	3.	Epic C – Agentic Core (AI Brain & Tools)
	4.	Epic D – War Room Interface (Chat + Preview)
	5.	Epic E – Campaign Execution & Safety
	6.	Epic F – Reporting, Learning Loop & Notifications

⸻

4. Agentic Architecture (Core Concept)

4.1 Agent Types

Orchestrator Agent (Main Agent)
	•	Persona: Senior Media Buyer & Strategist.
	•	Responsibilities: Understand user intent, break work into tasks, call sub-agents/tools, keep state.

Sub-Agents (optional but conceptually important):
	1.	Performance Analyst Agent
	•	Reads historical stats.
	•	Identifies “winners”, “losers”, trends.
	2.	Creative Strategist Agent
	•	Generates angles, hooks, and concepts.
	3.	Copywriter Agent
	•	Writes Primary Text, Headline, Description variants.
	4.	Execution Agent
	•	Maps structured plan to Facebook Campaign → Ad Set → Ad.
	5.	QA / Safety Agent
	•	Checks policies, budgets, and constraints before publishing.

4.2 Memory & State
	•	Short-term memory: Current conversation, current draft, current campaign context.
	•	Long-term memory:
	•	“Past winners” (top campaigns/ads).
	•	User preferences (tone, audiences, default budget, typical CTA).
	•	Account configuration (selected account, page, default daily budget, timezone).
	•	State Machine (examples):
	•	IDLE → DISCOVERY → IDEATION → DRAFTING → REVIEW → READY_TO_PUBLISH → PUBLISHED.

⸻

5. Agent Tools (LangChain-style)

Below is a richer list of tools the agent can call. (Names are conceptual; implementation via Flask APIs.)
	1.	get_ad_account_stats(time_range, level, filters)
	•	Input: time_range ('last_7_days' | 'yesterday' | 'last_30_days'), level ('campaign'|'adset'|'ad'), filters (optional)
	•	Output: JSON with spend, impressions, CTR, CPC, ROAS, etc.
	2.	get_top_performers(metric, time_range, limit)
	•	Input: e.g. metric='roas', time_range='last_7_days', limit=5
	•	Output: Top campaigns/adsets/ads sorted by the metric.
	3.	get_underperformers(metric, threshold, time_range)
	•	Output: List of bad performers for pausing or improvement suggestions.
	4.	generate_creative_briefs(product_info, past_winners)
	•	Output: 2–3 “angles” with hooks, value props, and suggested audiences.
	5.	generate_ad_copy(brief, tone, variants)
	•	Output: For each variant: primary text, headline, description, suggested CTA.
	6.	suggest_audiences(product_info, region, past_winners)
	•	Output: Audience segments (interests, lookalike hints, demographic hints).
	7.	search_stock_images(query)
	•	Integration with Unsplash/Pexels API.
	•	Output: URLs + metadata.
	8.	analyze_image(image_url) (optional Vision API)
	•	Output: Tags/objects detected; used to shape copy.
	9.	update_preview_state(ad_structure)
	•	Input: { page_name, profile_pic_url, primary_text, media_url, headline, description, CTA }.
	•	Action: Update right-panel preview via WebSocket/REST.
	10.	simulate_results(draft_campaign, budget, time_range) (heuristic)
	•	Output: Rough prediction (for messaging only, not real performance).
	11.	publish_campaign(campaign_structure)
	•	Action: Create Campaign → Ad Set → Ad via Facebook Marketing API.
	•	Output: IDs and link to Ads Manager.
	12.	adjust_budget(campaign_id_or_adset_id, new_budget)
	•	For incremental optimization.
	13.	pause_items(item_ids)
	•	Pause campaigns/adsets/ads.
	14.	summarize_performance(time_range)
	•	Output: Plain-language summary (“Yesterday: 3 campaigns ran, best ROAS 3.4…”).
	15.	log_decision(action, rationale)
	•	For internal tracking / future explanation to user (“We doubled budget because ROAS > 3 for 7 days.”).

⸻

6. Detailed Epics, User Stories, and Acceptance Criteria

Epic A – Authentication & Integration

Story A1: Google Sign-In
As a busy marketer, I want to log in with my Google account so that I don’t have to remember another password.

Acceptance Criteria
	•	“Continue with Google” button on home page.
	•	On successful OAuth, user lands on Dashboard (or Setup Wizard if first time).
	•	New User record created with:
	•	email, google_id, created_at, last_login_at.
	•	Subsequent logins reuse the same user.

Story A2: Facebook Ad Account Connection
As a user, I want to connect my Facebook Ad Account so that the agent can manage campaigns on my behalf.

Acceptance Criteria
	•	“Connect Facebook” button on Setup Wizard and in Settings.
	•	Facebook OAuth requests ads_read, ads_management, pages_read_engagement.
	•	If user has multiple ad accounts:
	•	Dropdown lists available Ad Accounts.
	•	User selects one (required step).
	•	System securely stores:
	•	Long-lived access token.
	•	Selected Ad Account ID.
	•	Associated Facebook Page IDs.
	•	Error handling:
	•	If token expired, user sees a clear “Reconnect Facebook” message.

⸻

Epic B – Onboarding & Settings

Story B1: First-Time Setup Wizard
As a new user, I want a guided setup so that the agent has everything it needs to start running ads.

Acceptance Criteria
	•	Steps:
	1.	Connect Facebook.
	2.	Select Ad Account.
	3.	Select Primary Facebook Page.
	4.	Set default daily budget (with currency).
	5.	Choose default tone of voice (e.g., “Friendly”, “Professional”, “Bold”).
	•	Progress indicator (Step 1 of 4, etc.).
	•	Completion leads to Dashboard with a welcome message from the Agent.

Story B2: Configurable Defaults
As a user, I want to adjust my default settings so that the agent behaves according to my preferences.

Acceptance Criteria
	•	Settings page contains:
	•	Default daily budget.
	•	Default geo (e.g., country/region).
	•	Default tone of copy.
	•	Default campaign objective (e.g., Conversions / Traffic).
	•	Timezone for daily summaries & triggers.
	•	Changes are persisted and used by the Agent for future suggestions.

⸻

Epic C – Agentic Core (AI Brain & Tools)

Story C1: Daily Proactive Trigger
As a user, I want the agent to start the conversation each day with context so I don’t have to think what to do.

Acceptance Criteria
	•	On first visit of the day to Dashboard OR via scheduled cron hitting the agent:
	•	Agent sends an opening message based on recent performance, e.g.
“Good morning! Yesterday’s ‘Sneaker – Flash Sale’ ad had a 3.1 ROAS with ₹1,500 spend. Should we raise the budget or test a new creative today?”
	•	Message must be based on actual data from get_ad_account_stats() / get_top_performers().
	•	If no campaigns exist:
	•	Agent says: “We don’t have any active campaigns yet. Want to set up your first ad for [Product X]?”

Story C2: Historical Analysis Tool
As a user, I want the agent to understand what has worked or failed so it doesn’t repeat mistakes.

Acceptance Criteria
	•	Tool get_top_performers() implemented and callable by agent.
	•	User can ask: “What was my best ad last week?” and get:
	•	Ad name, spend, ROAS, CTR, link to Ad in Ads Manager.
	•	Agent automatically uses historical performance in:
	•	Its proactive morning message.
	•	Suggestions (“This looks similar to last week’s winner about free shipping.”).

Story C3: Creative & Copy Generation
As a user, I want the agent to propose ad text so I can quickly approve or tweak it.

Acceptance Criteria
	•	For a given product/idea, agent generates:
	•	2–3 angles/briefs (e.g., “Urgency + Discount”, “Social Proof + Quality”).
	•	For each angle: 2–3 variants of:
	•	Primary Text (125–300 characters).
	•	Headline (<= 40 characters).
	•	Description (<= 30–60 characters).
	•	All text respects Facebook character limits and basic ad policies.
	•	Text is structured so UI can render each variant clearly.

Story C4: Multi-Tool Reasoning
As a system, the agent should chain tools together to handle a full workflow.

Acceptance Criteria
	•	Example flow:
	•	User: “Let’s sell the red hoodie again.”
	•	Agent:
	1.	Calls get_top_performers() to see if “red hoodie” performed well earlier.
	2.	Calls generate_creative_briefs() based on history.
	3.	Calls generate_ad_copy() with chosen brief.
	4.	Calls update_preview_state() to refresh UI.
	•	Output to user: “I’ve drafted 3 variants based on last month’s winner. Here’s Variant A…”

⸻

Epic D – War Room Interface (Chat + Preview)

Story D1: Split-Screen Workflow
As a user, I want the chat on the left and ad preview on the right so I can visualize what we’re discussing.

Acceptance Criteria
	•	Left panel:
	•	Chat bubbles (User vs Agent).
	•	Message timestamps.
	•	Typing indicator for Agent.
	•	Text input area + send button + optional “Attach Image” icon.
	•	Right panel:
	•	Tabs: Current Draft, Past Performance, Activity Log.
	•	When Agent proposes or updates a draft, right panel auto-refreshes with latest version via update_preview_state.

Story D2: Edit & Feedback Loop
As a user, I want to say things like “Make it punchier” and get improved versions.

Acceptance Criteria
	•	User gives free-text feedback:
	•	“Shorter please”, “More benefit-driven”, “Make it funny”.
	•	Agent:
	•	Acknowledges feedback.
	•	Generates Version 2 (or 3, etc.) annotated as “Variant 2”, “Variant 3”.
	•	Right panel shows:
	•	Selected variant in the mockup.
	•	Option to switch between Variant 1/2/3.

Story D3: Manual Edit
As a user, I want to manually tweak the text before publishing.

Acceptance Criteria
	•	“Edit Manually” button near the preview.
	•	On click:
	•	Primary Text, Headline, Description, CTA become editable fields.
	•	Changes auto-refresh preview.
	•	Agent acknowledges manual edits:
	•	“Got it, I’ll remember this tone for future ads.”

Story D4: Past Performance View
As a user, I want a quick view of historical performance without leaving the War Room.

Acceptance Criteria
	•	Right panel → “Past Performance” tab shows table:
	•	Date, Campaign Name, Ad Name, Spend, ROAS, CTR, Status.
	•	Sorting options: by Date, Spend, ROAS.
	•	Clicking a row:
	•	Opens a small detail side drawer (or modal) with deeper stats + link to Ads Manager.

⸻

Epic E – Campaign Execution & Safety

Story E1: Approve & Publish Command
As a user, I want a simple “Go ahead” or button to publish the ad so that it goes live.

Acceptance Criteria
	•	“Approve & Publish” button under the preview.
	•	User can also type: “Go ahead”, “Launch this with ₹2,000 budget today.”
	•	Before publishing, agent must confirm:
	•	“Publishing Campaign ‘Red Hoodie – Winter Sale’ with daily budget ₹2,000 and targeting [India, Age 18–34, Interests: Streetwear]. Proceed?”
	•	On “Yes”:
	•	publish_campaign() is called.
	•	On success:
	•	UI shows success toast.
	•	Agent message: “Done. Here’s the link to view it in Ads Manager: [link].”

Story E2: Safety Guardrails
As a system owner, I want guardrails so accidental high budgets or illegal content are avoided.

Acceptance Criteria
	•	Budget limits:
	•	If requested budget > default budget * 5:
	•	Agent asks: “This is significantly higher than your usual daily budget. Are you sure?”
	•	Content checks:
	•	QA Agent (or pre-publish step) scans for disallowed words (e.g., “cure”, discriminatory language).
	•	If found:
	•	Agent: “This copy may violate ad policies because of [reason]. Suggest I rephrase it?”
	•	No campaign is published without explicit user confirmation in-chat or via button.

Story E3: Post-Publish Summary
As a user, I want a confirmation summary after publish.

Acceptance Criteria
	•	Agent sends:
	•	Campaign Name.
	•	Objective.
	•	Daily budget.
	•	Targeting summary.
	•	Direct Ads Manager link.
	•	System logs:
	•	PublishedBy (user), PublishedAt, and DecisionLog.

⸻

Epic F – Reporting, Learning Loop & Notifications

Story F1: Daily Performance Summary
As a user, I want a simple daily recap so I know if things are working.

Acceptance Criteria
	•	Once per day (configurable time):
	•	Agent can generate summary upon user entering Dashboard or via prompt:
	•	“Yesterday: 3 active campaigns, total spend ₹4,500, average ROAS 2.6. Best performer: ‘Red Hoodie – Winter Sale’ with ROAS 4.1.”
	•	Uses summarize_performance() + stats tools.

Story F2: Recommendations Based on Learnings
As a user, I want the agent to suggest concrete next steps based on my data.

Acceptance Criteria
	•	After summary, agent proposes actions:
	•	“Recommendation 1: Increase budget by 30% on ‘Red Hoodie – Winter Sale.’”
	•	“Recommendation 2: Pause ‘Old Collection – Generic’ (ROAS 0.7).”
	•	Each recommendation is actionable:
	•	“Apply this now” button in chat or commands like “Yes, apply rec 1.”

Story F3: Activity Log
As a user, I want to see what the agent has done over time.

Acceptance Criteria
	•	“Activity Log” tab shows:
	•	Time, Action, Campaign/Ad, short rationale (from log_decision()).
	•	Examples:
	•	“2025-12-03 10:45 – Published Campaign ‘Red Hoodie – Winter Sale’ (user approved).”
	•	“2025-12-02 09:15 – Suggested budget increase (not applied).”

⸻

7. Screen Specifications / Wireframes

Screen 1 – Gate (Login)

Purpose: Simple entry point to the product.

Layout:
	•	Centered card on clean background (light or dark theme).
	•	Elements:
	•	Logo / Product name.
	•	Tagline: “Your AI Media Buyer for Facebook Ads.”
	•	Primary button: “Continue with Google”.
	•	Small text: “We only use your Google account for login. No spam, ever.”

⸻

Screen 2 – Setup Wizard (First-Time User)

Layout: Full-screen stepped wizard.

Step 1: Connect Facebook
	•	Title: “Connect your Facebook Account”
	•	Description: “We’ll sync your ad data and manage campaigns for you.”
	•	Button: “Connect Facebook”
	•	Status indicator: Connected / Not connected.

Step 2: Select Ad Account
	•	Title: “Choose Your Ad Account”
	•	Dropdown listing Account Name (ID) from API.
	•	Helper text: “We’ll focus on this account for now. You can change it later.”

Step 3: Select Facebook Page
	•	Title: “Choose Your Facebook Page”
	•	Dropdown of pages user manages.
	•	Preview: Page profile picture + name.

Step 4: Set Defaults
	•	Fields:
	•	Default daily test budget (number + currency).
	•	Default objective (dropdown).
	•	Tone of voice (dropdown).
	•	Button: “Finish Setup”
	•	On completion, redirect to Dashboard.

⸻

Screen 3 – Dashboard (War Room)

User spends 90% of time here.

Layout: 2-column split.

Left Column – Agent Chat
	•	Header:
	•	“Daily Ad Agent” + status indicator (Online / Syncing…).
	•	Subtitle: “Context: Drafting Campaign #45” or “Idle”.
	•	Chat area:
	•	Scrollable history.
	•	Clear grouping of days.
	•	Input area:
	•	Textbox.
	•	“Send” button.
	•	Attachment (image upload) button.

Right Column – Live Stage
Tabs:
	1.	Current Draft
	2.	Past Performance
	3.	Activity Log

Current Draft Tab
	•	“Facebook Ad Mockup Card”:
	•	Page profile picture + page name.
	•	“Sponsored” label.
	•	Primary text block.
	•	Media (image/video placeholder).
	•	Headline.
	•	Description.
	•	CTA button.
	•	Controls:
	•	Variant selector: “Variant 1 / 2 / 3”.
	•	Buttons: [Edit Manually] [Approve & Publish].

Past Performance Tab
	•	Table:
	•	Date | Campaign | Spend | ROAS | Status.
	•	Interactions:
	•	Sort by columns.
	•	Click row → detail drawer with metrics.

Activity Log Tab
	•	Timeline list:
	•	Timestamp + short description.
	•	Filter by action type (Publish, Budget Change, Suggestion).

⸻

Screen 4 – Settings

Sections:
	•	Account:
	•	Google email (readonly).
	•	“Disconnect Google” (optional).
	•	Facebook:
	•	Connected account summary.
	•	“Reconnect Facebook” / “Change Ad Account”.
	•	Preferences:
	•	Default daily budget.
	•	Default tone.
	•	Default objective.
	•	Timezone.
	•	Actions:
	•	“Save Changes”.

⸻

8. Technical Flow Example (End-to-End)
	1.	User: “Let’s sell the red hoodie again.”
	2.	Flask Backend:
	•	Receives message from frontend.
	•	Calls Orchestrator Agent via LangChain.
	3.	Agent:
	•	Calls get_top_performers() with filter “red hoodie” over last 30 days.
	•	If past winner exists:
	•	Summarizes what worked.
	•	Calls generate_creative_briefs() using those insights.
	•	Calls generate_ad_copy() for 2–3 variants.
	•	Calls update_preview_state() with Variant 1.
	•	Sends chat message with explanation:
“Your red hoodie ad from last month had ROAS 4.2. I’ve created 3 new variants based on that angle. Here’s Variant 1…”
	4.	Frontend:
	•	Renders Agent message in chat.
	•	Updates preview on right.
	5.	User: “Shorten the primary text and launch with ₹2,000/day.”
	6.	Agent:
	•	Interprets feedback.
	•	Shortens copy (new Variant 2).
	•	Updates preview via update_preview_state().
	•	Asks for confirmation:
	•	“Publishing with ₹2,000/day and same audience as last winner. Proceed?”
	7.	User: “Yes.”
	8.	Agent:
	•	Calls publish_campaign() with full structure.
	•	On success, logs action via log_decision().
	•	Sends message with Ads Manager link.
	9.	Frontend:
	•	Shows success toast + updates Activity Log.
