# Agent Refactor Plan

## Current Issues

### 1. LLM Package Version Mismatch
- **Current versions**: `langchain==0.1.0`, `langchain-openai==0.0.2`, `langchain-anthropic==0.1.1`
- **Problem**: These old versions don't properly support the `.stream()` method and modern tool calling
- **Result**: LLM initialization likely fails silently, triggering mock fallbacks

### 2. AgentService Doesn't Use Tools
- **File**: `backend/app/services/agent_service.py`
- **Problem**: The chat endpoint uses `AgentService` which does simple LLM chat without tool bindings
- **Note**: `OrchestratorAgent` exists with tools wired, but isn't used by the API!

### 3. Silent Mock Fallbacks
- When LLM init fails, code silently falls back to `_mock_chat_response()`
- No errors surfaced to help diagnose configuration issues
- User sees canned responses without knowing the real agent isn't working

### 4. Facebook API Not Integrated
- `FacebookService` returns hardcoded mock data
- Real Facebook Page Access Token exists in `.env` but isn't used
- `facebook-business` SDK installed but not utilized

### 5. No Tool Output in Chat Loop
- Agent doesn't report what tools were called or their results
- No state transitions or multi-step reasoning visible to user

---

## Implementation Plan

### Phase 1: Upgrade LangChain Stack
**Files**: `requirements.txt`

Update to compatible modern versions:
```
langchain>=0.2.0
langchain-openai>=0.1.0
langchain-anthropic>=0.1.15
langchain-core>=0.2.0
```

### Phase 2: Refactor Agent API to Use Orchestrator
**Files**: `backend/app/api/agent.py`, `backend/app/services/agent_service.py`

1. Replace `AgentService` usage with `OrchestratorAgent`
2. Pass proper context (conversation, preferences, ad_account, facebook_connection)
3. Ensure tools are properly bound to the agent

### Phase 3: Implement ReAct Agent with Tool Calling
**Files**: `backend/app/agents/orchestrator.py`

1. Use `create_react_agent` or `create_tool_calling_agent` from langchain
2. Implement proper streaming with intermediate steps
3. Surface tool calls and results in the response stream

### Phase 4: Real Facebook API Integration
**Files**: `backend/app/services/facebook_service.py`

1. Use `facebook-business` SDK for real API calls
2. Implement proper error handling for API failures
3. Add rate limiting and retry logic
4. Keep mock data as fallback for development without valid token

### Phase 5: Proper Error Handling
**Files**: All agent/service files

1. Remove silent fallbacks - surface errors to user
2. Add detailed logging for debugging
3. Distinguish between "no API key" vs "API error" vs "mock mode"
4. Add configuration validation on startup

### Phase 6: Enhanced Chat Response Format
**Files**: `backend/app/api/agent.py`

Stream structured events:
```json
{"type": "thinking", "content": "Analyzing your request..."}
{"type": "tool_call", "tool": "get_account_stats", "args": {...}}
{"type": "tool_result", "tool": "get_account_stats", "result": {...}}
{"type": "message", "content": "Based on the data..."}
{"type": "done", "conversation_id": "..."}
```

---

## Files to Modify

1. `backend/requirements.txt` - Upgrade packages
2. `backend/app/services/agent_service.py` - Complete rewrite to use Orchestrator
3. `backend/app/agents/orchestrator.py` - Modern agent implementation
4. `backend/app/api/agent.py` - Enhanced streaming with tool visibility
5. `backend/app/services/facebook_service.py` - Real API integration
6. `backend/app/agents/tools/*.py` - Ensure tools work with new agent

---

## Expected Outcome

After implementation:
1. Agent will actually call OpenAI/Anthropic API (no more mock by default)
2. Tools will be executed and results shown to user
3. Real Facebook data will be fetched when valid token exists
4. Errors will be surfaced clearly instead of hidden
5. User will see agent "thinking" and tool usage in real-time
