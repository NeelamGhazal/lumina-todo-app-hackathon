# Quickstart: OpenAI Agent with MCP Integration

**Feature Branch**: `006-openai-agent-mcp`
**Prerequisites**: Part 1 MCP Server running on port 8001

## Setup

### 1. Environment Variables

Add to `chatbot/.env`:

```bash
# OpenRouter Configuration (REQUIRED)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Agent Configuration
AGENT_MODEL=gpt-4o-mini  # or gpt-4o for complex reasoning

# MCP Server (from Part 1)
MCP_SERVER_URL=http://localhost:8001

# Database (same as Part 1)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```

### 2. Install Dependencies

```bash
cd chatbot
uv sync
```

### 3. Verify MCP Server (Part 1)

```bash
# Check MCP server is running
curl http://localhost:8001/health
# Expected: {"status": "healthy", ...}

# Check tools are available
curl http://localhost:8001/mcp/tools
# Expected: {"tools": [...5 tools...]}
```

## Usage

### Start the Agent Server

```bash
cd chatbot
uv run uvicorn mcp_server.main:app --port 8001 --reload
```

### Send Chat Messages

#### Add a Task
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response:
```json
{
  "message": "I've added 'buy groceries' to your tasks.",
  "conversation_id": "660e8400-e29b-41d4-a716-446655440001",
  "tool_calls": [
    {"tool": "add_task", "success": true, "result_preview": "Created task: buy groceries"}
  ]
}
```

#### List Tasks
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my tasks",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "conversation_id": "660e8400-e29b-41d4-a716-446655440001"
  }'
```

Response:
```json
{
  "message": "Here are your tasks:\n\n1. [ID: abc123] Buy groceries (pending)\n2. [ID: def456] Call dentist (completed)",
  "conversation_id": "660e8400-e29b-41d4-a716-446655440001",
  "tool_calls": [
    {"tool": "list_tasks", "success": true, "result_preview": "Found 2 tasks"}
  ]
}
```

#### Complete a Task
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mark buy groceries as done",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "conversation_id": "660e8400-e29b-41d4-a716-446655440001"
  }'
```

#### Delete a Task
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Delete the groceries task",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

#### Multi-turn Context
```bash
# First: list tasks
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my pending tasks",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'

# Then: use context (same conversation)
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Complete the first one",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "conversation_id": "CONVERSATION_ID_FROM_ABOVE"
  }'
```

### View Conversation History

#### List Conversations
```bash
curl "http://localhost:8001/conversations?user_id=550e8400-e29b-41d4-a716-446655440000"
```

#### Get Messages
```bash
curl "http://localhost:8001/conversations/CONVERSATION_ID/messages?user_id=550e8400-e29b-41d4-a716-446655440000"
```

## Testing

### Run Unit Tests
```bash
cd chatbot
uv run pytest tests/test_agent*.py -v
```

### Run Integration Tests
```bash
# Requires MCP server running
cd chatbot
uv run pytest tests/test_chat_integration.py -v
```

### Run All Tests with Coverage
```bash
cd chatbot
uv run pytest --cov=mcp_server --cov-report=term-missing
```

## Troubleshooting

### "OpenRouter API key not found"
- Check `OPENROUTER_API_KEY` is set in `.env`
- Verify key is valid at https://openrouter.ai/keys

### "MCP server unavailable"
- Ensure Part 1 MCP server is running: `curl http://localhost:8001/health`
- Check `MCP_SERVER_URL` in `.env`

### "Rate limit exceeded"
- OpenRouter has rate limits per model
- Wait a moment and retry, or use a different model

### "Tool call failed"
- Check MCP server logs for errors
- Verify database connection

## Architecture Overview

```
User Request
     │
     ▼
┌─────────────────┐
│  /chat endpoint │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Conversation    │  ← Get/create from DB
│ Manager         │  ← Load last 10 messages
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OpenRouter      │  ← gpt-4o-mini via OpenAI SDK
│ (LLM)           │  ← with tool definitions
└────────┬────────┘
         │
         ▼ (if tool_calls)
┌─────────────────┐
│ MCP Tool        │  ← HTTP call to Part 1
│ Executor        │  ← inject user_id
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Response        │  ← Natural language
│ Formatter       │  ← Store messages
└────────┬────────┘
         │
         ▼
User Response
```
