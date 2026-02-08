# Evolution Todo - AI Chatbot

Phase III: MCP Server + OpenAI Agent for natural language todo management.

## Features

### Part 1: MCP Server
- **5 MCP Tools**: add_task, list_tasks, complete_task, delete_task, update_task
- **Direct Database Access**: SQLModel with async PostgreSQL/SQLite support
- **Structured Logging**: JSON logs with correlation IDs via structlog
- **Pydantic Validation**: Automatic parameter validation for all tools
- **User Isolation**: All operations scoped to user_id

### Part 2: OpenAI Agent
- **Natural Language Interface**: Chat with your todo list using natural language
- **OpenRouter Integration**: Uses OpenRouter API for LLM access (GPT-4o-mini default)
- **Conversation Memory**: 30-minute session timeout, 10-message context window
- **Automatic Tool Selection**: Agent intelligently selects which MCP tools to call
- **Multi-turn Conversations**: Maintains context across multiple messages

## Quick Start

### Prerequisites

- Python 3.11+
- UV package manager
- PostgreSQL or SQLite

### Installation

```bash
# Clone and navigate
cd chatbot

# Install dependencies
uv sync

# Install dev dependencies (for testing)
uv sync --all-extras
```

### Configuration

Copy the environment template and configure:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./evolution_todo.db` |
| `MCP_SERVER_PORT` | Server port | `8001` |
| `ENVIRONMENT` | development/production | `development` |
| `LOG_LEVEL` | DEBUG/INFO/WARNING/ERROR | `INFO` |
| `CORS_ORIGINS` | Comma-separated origins | `http://localhost:3000` |

Agent-specific variables (Part 2):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key (required for agent) | - |
| `AGENT_MODEL` | LLM model to use | `gpt-4o-mini` |
| `MCP_SERVER_URL` | URL of this MCP server | `http://localhost:8001` |

### Running the Server

```bash
# Development mode with auto-reload
uv run uvicorn mcp_server.main:app --port 8001 --reload

# Production mode
uv run uvicorn mcp_server.main:app --port 8001 --host 0.0.0.0
```

### Database Migration

```bash
# Run migrations to create Phase III tables
uv run python -m mcp_server.migrations

# Verify tables
uv run python -m mcp_server.migrations --verify
```

## API Reference

### Health Check

```bash
curl http://localhost:8001/health
# {"status": "healthy", "version": "0.1.0", "environment": "development"}
```

### List Available Tools

```bash
curl http://localhost:8001/mcp/tools
# {"tools": [{"name": "add_task", ...}, ...]}
```

### Call a Tool

```bash
# Add a task
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "add_task",
    "parameters": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread"
    }
  }'

# List tasks
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_tasks",
    "parameters": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "pending"
    }
  }'

# Complete a task
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "complete_task",
    "parameters": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "task_id": "task-uuid-here"
    }
  }'

# Update a task
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "update_task",
    "parameters": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "task_id": "task-uuid-here",
      "title": "Updated title"
    }
  }'

# Delete a task
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "delete_task",
    "parameters": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "task_id": "task-uuid-here"
    }
  }'
```

### Chat Endpoint (Part 2)

Natural language interface for todo management:

```bash
# Start a conversation
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries tomorrow",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
# Response: {"message": "I've added 'buy groceries tomorrow' to your task list!", "conversation_id": "..."}

# Continue the conversation
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What tasks do I have?",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "conversation_id": "conversation-uuid-here"
  }'

# List user conversations
curl "http://localhost:8001/conversations?user_id=550e8400-e29b-41d4-a716-446655440000"

# Get conversation history
curl "http://localhost:8001/conversations/{conversation_id}/messages?user_id=550e8400-e29b-41d4-a716-446655440000"
```

### Example Conversations

**Adding Tasks:**
- "Add a task to call mom"
- "Create a new task: finish the report by Friday"
- "I need to remember to buy milk"

**Listing Tasks:**
- "What are my tasks?"
- "Show me my todo list"
- "What do I have pending?"

**Completing Tasks:**
- "Mark 'buy groceries' as done"
- "I finished the report"
- "Complete my first task"

**Updating Tasks:**
- "Change 'buy milk' to 'buy almond milk'"
- "Update the deadline for my report"

**Deleting Tasks:**
- "Delete the groceries task"
- "Remove 'call mom' from my list"

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage (MCP server only)
uv run pytest --cov=mcp_server --cov-report=term-missing

# Run with full coverage (MCP server + agent)
uv run pytest --cov=mcp_server --cov=agent --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_add_task.py -v

# Run agent tests only
uv run pytest tests/test_agent_*.py -v
```

## Project Structure

```
chatbot/
├── mcp_server/
│   ├── __init__.py        # Package exports
│   ├── config.py          # Pydantic Settings
│   ├── database.py        # Async SQLModel engine
│   ├── logging.py         # Structlog configuration
│   ├── main.py            # FastAPI application + chat endpoints
│   ├── migrations.py      # Database migration script
│   ├── models.py          # SQLModel entities (Task, Conversation, Message)
│   ├── schemas.py         # Pydantic parameter models
│   └── tools/
│       ├── __init__.py    # Tool registry
│       ├── base.py        # Error handling utilities
│       ├── add_task.py    # US1: Create task
│       ├── list_tasks.py  # US2: List tasks
│       ├── complete_task.py # US3: Toggle completion
│       ├── delete_task.py # US4: Delete task
│       └── update_task.py # US5: Update task
├── agent/                  # Part 2: OpenAI Agent
│   ├── __init__.py        # Package exports
│   ├── config.py          # Agent settings (OpenRouter, model, etc.)
│   ├── client.py          # OpenRouter client wrapper
│   ├── tools.py           # MCP tool integration
│   ├── conversation.py    # Session management
│   ├── chat.py            # Chat orchestration
│   └── schemas.py         # Chat request/response models
├── tests/
│   ├── conftest.py        # Pytest fixtures
│   ├── test_add_task.py   # US1 tests
│   ├── test_list_tasks.py # US2 tests
│   ├── test_complete_task.py # US3 tests
│   ├── test_delete_task.py # US4 tests
│   ├── test_update_task.py # US5 tests
│   ├── test_api.py        # MCP integration tests
│   ├── test_agent_config.py    # Agent config tests
│   ├── test_agent_client.py    # OpenRouter client tests
│   ├── test_agent_tools.py     # Tool integration tests
│   ├── test_agent_conversation.py # Session management tests
│   ├── test_agent_chat.py      # Chat orchestration tests
│   └── test_chat_integration.py # Chat endpoint tests
├── pyproject.toml         # UV project config
├── .env.example           # Environment template
├── Dockerfile             # Container build
└── README.md              # This file
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid parameters |
| `TASK_NOT_FOUND` | Task does not exist |
| `UNAUTHORIZED` | User doesn't own task |
| `DATABASE_ERROR` | Database operation failed |
| `INTERNAL_ERROR` | Unexpected error |

## Architecture Notes

### OpenRouter Integration
The agent uses OpenRouter API (OpenAI-compatible) instead of direct OpenAI API:
- Allows access to multiple LLM providers through a single API
- Uses Chat Completions API (not Assistants API)
- Manual tool execution pattern for maximum compatibility

### Conversation Management
- **Session Timeout**: 30 minutes of inactivity creates a new conversation
- **Context Window**: Last 10 messages sent to LLM for context
- **Tool Loop**: Maximum 5 tool calls per request to prevent infinite loops
- **Database Storage**: All conversation history persisted in database

### Security
- User isolation enforced at database level (user_id on all queries)
- No cross-user data access possible
- API key stored in environment variables

## License

Part of Evolution Todo - Phase III (Part 1: MCP Server, Part 2: OpenAI Agent)
