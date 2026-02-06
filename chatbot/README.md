# MCP Server for Todo Operations

Phase III - Part 1: MCP Server exposing todo CRUD operations for AI agents via the Model Context Protocol.

## Features

- **5 MCP Tools**: add_task, list_tasks, complete_task, delete_task, update_task
- **Direct Database Access**: SQLModel with async PostgreSQL/SQLite support
- **Structured Logging**: JSON logs with correlation IDs via structlog
- **Pydantic Validation**: Automatic parameter validation for all tools
- **User Isolation**: All operations scoped to user_id

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

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mcp_server --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_add_task.py -v
```

## Project Structure

```
chatbot/
├── mcp_server/
│   ├── __init__.py        # Package exports
│   ├── config.py          # Pydantic Settings
│   ├── database.py        # Async SQLModel engine
│   ├── logging.py         # Structlog configuration
│   ├── main.py            # FastAPI application
│   ├── migrations.py      # Database migration script
│   ├── models.py          # SQLModel entities
│   ├── schemas.py         # Pydantic parameter models
│   └── tools/
│       ├── __init__.py    # Tool registry
│       ├── base.py        # Error handling utilities
│       ├── add_task.py    # US1: Create task
│       ├── list_tasks.py  # US2: List tasks
│       ├── complete_task.py # US3: Toggle completion
│       ├── delete_task.py # US4: Delete task
│       └── update_task.py # US5: Update task
├── tests/
│   ├── conftest.py        # Pytest fixtures
│   ├── test_add_task.py   # US1 tests
│   ├── test_list_tasks.py # US2 tests
│   ├── test_complete_task.py # US3 tests
│   ├── test_delete_task.py # US4 tests
│   ├── test_update_task.py # US5 tests
│   └── test_api.py        # Integration tests
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

## License

Part of Evolution Todo - Phase III
