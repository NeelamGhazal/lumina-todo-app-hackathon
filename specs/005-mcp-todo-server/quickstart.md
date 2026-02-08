# Quickstart: MCP Server for Todo Operations

**Feature**: 005-mcp-todo-server
**Date**: 2026-02-06

## Prerequisites

- Python 3.13+
- UV package manager
- Access to Neon PostgreSQL (shared with Phase II)
- Phase II API running (for shared database)

## Environment Setup

```bash
# Navigate to chatbot directory
cd chatbot

# Create .env file
cat > .env << 'EOF'
# Database (same as Phase II)
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/lumina_todo

# Server
MCP_SERVER_PORT=8001
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF
```

## Installation

```bash
# Initialize project with UV
uv init chatbot
cd chatbot

# Add dependencies
uv add fastapi uvicorn sqlmodel pydantic structlog mcp

# Add dev dependencies
uv add --dev pytest pytest-asyncio pytest-cov httpx
```

## Project Structure

```
chatbot/
├── mcp_server/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Settings management
│   ├── database.py       # DB connection & session
│   ├── models.py         # Conversation, Message SQLModels
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py       # Base tool class
│   │   ├── add_task.py
│   │   ├── list_tasks.py
│   │   ├── complete_task.py
│   │   ├── delete_task.py
│   │   └── update_task.py
│   ├── schemas.py        # Pydantic parameter models
│   └── logging.py        # Structured logging setup
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Test fixtures
│   ├── test_tools.py     # Tool unit tests
│   └── test_api.py       # API integration tests
├── pyproject.toml
└── .env
```

## Running the Server

```bash
# Development mode
uv run uvicorn mcp_server.main:app --reload --port 8001

# Production mode
uv run uvicorn mcp_server.main:app --host 0.0.0.0 --port 8001
```

## Verify Installation

```bash
# Health check
curl http://localhost:8001/health

# Expected response:
# {"status": "healthy", "timestamp": "2026-02-06T12:00:00Z"}

# List tools
curl http://localhost:8001/mcp/tools

# Expected response:
# [
#   {"name": "add_task", "description": "Create a new task", ...},
#   {"name": "list_tasks", "description": "List user tasks", ...},
#   ...
# ]
```

## Quick Tool Test

```bash
# Add a task
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "add_task",
    "parameters": {
      "user_id": "00000000-0000-0000-0000-000000000001",
      "title": "Test task from MCP",
      "description": "Created via MCP server"
    }
  }'

# Expected response:
# {"status": "success", "data": {"task_id": "...", "status": "created", "title": "Test task from MCP"}}

# List tasks
curl -X POST http://localhost:8001/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "list_tasks",
    "parameters": {
      "user_id": "00000000-0000-0000-0000-000000000001",
      "status": "all"
    }
  }'
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mcp_server --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_tools.py -v
```

## Database Migration

```bash
# Generate migration (from Phase II api directory)
cd ../api
uv run alembic revision --autogenerate -m "Add Phase III conversation tables"

# Apply migration
uv run alembic upgrade head

# Verify tables exist
# Check Neon dashboard for 'conversations' and 'messages' tables
```

## Troubleshooting

### Connection Refused on Port 8001
- Verify server is running: `ps aux | grep uvicorn`
- Check port availability: `lsof -i :8001`
- Restart server: `uv run uvicorn mcp_server.main:app --reload --port 8001`

### Database Connection Error
- Verify `DATABASE_URL` in `.env`
- Check Neon dashboard for connection limits
- Ensure IP is whitelisted in Neon project settings

### Tool Returns UNAUTHORIZED
- Verify `user_id` is valid UUID format
- Confirm user exists in database
- Check task ownership for complete/delete/update operations

### Import Errors
- Run `uv sync` to ensure dependencies installed
- Verify Python version: `python --version` (should be 3.13+)

## Next Steps

After MCP server is running:

1. **Phase III Part 2**: Configure OpenAI agent to use these tools
2. **Phase III Part 3**: Build ChatKit frontend
3. **Integration test**: Full conversation flow with tool calls
