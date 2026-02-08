# Research: MCP Server for Todo Operations

**Feature**: 005-mcp-todo-server
**Date**: 2026-02-06
**Status**: Complete

## Research Topics

### 1. Official MCP Python SDK

**Decision**: Use `mcp` package (official Anthropic MCP SDK for Python)

**Rationale**:
- Official SDK maintained by Anthropic ensures protocol compliance
- Provides built-in tool registration, parameter validation, and error handling
- Supports multiple transports: stdio, HTTP/SSE
- Well-documented with examples for FastAPI integration

**Alternatives Considered**:
- Custom MCP implementation: Rejected due to protocol complexity and maintenance burden
- Third-party MCP libraries: Rejected due to lack of official support

**Key Findings**:
```python
# MCP SDK usage pattern
from mcp.server.fastapi import MCPServer
from mcp.types import Tool

mcp = MCPServer()

@mcp.tool()
async def add_task(user_id: str, title: str, description: str = None) -> dict:
    """Add a new task for the user."""
    # Implementation
    return {"task_id": task.id, "status": "created", "title": title}
```

**Version**: `mcp>=1.0.0` (latest stable)

---

### 2. FastAPI + MCP Integration Pattern

**Decision**: Standalone FastAPI app with MCP server mounted at `/mcp` endpoint

**Rationale**:
- Clean separation from Phase II API (port 8000 vs 8001)
- MCP SDK provides FastAPI integration via `MCPServer` class
- HTTP/SSE transport is compatible with OpenAI Agents SDK
- Easy to containerize independently

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server (Port 8001)                    │
├─────────────────────────────────────────────────────────────┤
│  FastAPI App                                                 │
│  ├── /health          → Health check endpoint               │
│  ├── /mcp/tools       → List available tools                │
│  └── /mcp/call        → Execute tool (SSE response)         │
├─────────────────────────────────────────────────────────────┤
│  MCP Tool Registry                                          │
│  ├── add_task                                               │
│  ├── list_tasks                                             │
│  ├── complete_task                                          │
│  ├── delete_task                                            │
│  └── update_task                                            │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│           Neon PostgreSQL (Shared with Phase II)            │
│  ├── users (existing)                                       │
│  ├── tasks (existing)                                       │
│  ├── conversations (new)                                    │
│  └── messages (new)                                         │
└─────────────────────────────────────────────────────────────┘
```

**Alternatives Considered**:
- Embedded in Phase II API: Rejected due to coupling concerns and port conflicts
- Stdio transport: Rejected as not compatible with web-based agents

---

### 3. Database Connection Strategy

**Decision**: Direct SQLModel access with connection pooling, reusing Phase II patterns

**Rationale**:
- Lower latency than HTTP API calls (~20ms vs ~200ms)
- Consistent with Phase II codebase (SQLModel + async engine)
- Connection pooling handles concurrent requests efficiently
- Neon supports multiple connection pools

**Implementation Pattern**:
```python
# Reuse Phase II connection pattern
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
)

async_session = async_sessionmaker(engine, expire_on_commit=False)
```

**Connection String**: Shared `DATABASE_URL` environment variable with Phase II

**Alternatives Considered**:
- Separate database: Rejected to maintain single source of truth
- Call Phase II API: Rejected due to latency impact on tool response times

---

### 4. Conversation Session Management

**Decision**: Session-based with 30-minute inactivity timeout, automatic creation

**Rationale**:
- Balances context continuity with practical session boundaries
- 30 minutes is industry standard for session timeout
- Automatic creation reduces complexity for agent integration
- Stored in database for stateless server architecture

**Implementation Logic**:
```python
async def get_or_create_conversation(user_id: str, session: AsyncSession) -> Conversation:
    """Get active conversation or create new one."""
    cutoff = datetime.utcnow() - timedelta(minutes=30)

    # Find active conversation
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.last_activity > cutoff)
        .order_by(Conversation.last_activity.desc())
    )
    conversation = result.scalar_one_or_none()

    if conversation:
        conversation.last_activity = datetime.utcnow()
        return conversation

    # Create new conversation
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.flush()
    return conversation
```

**Alternatives Considered**:
- Per-request conversations: Rejected due to loss of context
- Explicit start/end: Rejected as adds complexity for agent integration
- Never expire: Rejected due to unbounded conversation growth

---

### 5. Structured Logging Best Practices

**Decision**: Structured JSON logs to stdout using Python `structlog`

**Rationale**:
- JSON format compatible with all log aggregators
- Stdout follows 12-factor app principles
- `structlog` provides clean API for structured logging
- Easy filtering by tool_name, user_id, latency

**Log Format**:
```json
{
  "timestamp": "2026-02-06T12:34:56.789Z",
  "level": "info",
  "event": "tool_invoked",
  "tool_name": "add_task",
  "user_id": "user_123",
  "latency_ms": 45,
  "success": true,
  "correlation_id": "req_abc123"
}
```

**Error Log Format**:
```json
{
  "timestamp": "2026-02-06T12:34:56.789Z",
  "level": "error",
  "event": "tool_failed",
  "tool_name": "complete_task",
  "user_id": "user_123",
  "error_code": "TASK_NOT_FOUND",
  "error_message": "Task with ID 999 not found",
  "correlation_id": "req_abc123"
}
```

**Alternatives Considered**:
- Plain text logs: Rejected due to parsing difficulty
- File-based logging: Rejected as not cloud-native
- External logging service: Deferred to Phase V

---

### 6. Pydantic Tool Parameter Models

**Decision**: Pydantic v2 models for all tool parameters, matching Phase II patterns

**Rationale**:
- Automatic validation with clear error messages
- Type safety and IDE autocomplete
- Consistent with Phase II codebase
- Integrates well with FastAPI and MCP SDK

**Model Examples**:
```python
from pydantic import BaseModel, Field

class AddTaskParams(BaseModel):
    """Parameters for add_task tool."""
    user_id: str = Field(..., description="User's unique identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Task description")

class ListTasksParams(BaseModel):
    """Parameters for list_tasks tool."""
    user_id: str = Field(..., description="User's unique identifier")
    status: str = Field("all", pattern="^(all|pending|completed)$", description="Filter by status")

class TaskIdParams(BaseModel):
    """Parameters for complete/delete task tools."""
    user_id: str = Field(..., description="User's unique identifier")
    task_id: int = Field(..., gt=0, description="Task ID")

class UpdateTaskParams(BaseModel):
    """Parameters for update_task tool."""
    user_id: str = Field(..., description="User's unique identifier")
    task_id: int = Field(..., gt=0, description="Task ID")
    title: str | None = Field(None, min_length=1, max_length=200, description="New title")
    description: str | None = Field(None, max_length=1000, description="New description")
```

**Alternatives Considered**:
- Manual validation: Rejected due to boilerplate and error-prone
- JSON Schema only: Rejected as less ergonomic for Python

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.13+ |
| Framework | FastAPI | 0.109+ |
| MCP SDK | mcp | 1.0+ |
| ORM | SQLModel | 0.0.22 |
| Validation | Pydantic | 2.9.2 |
| Database | Neon PostgreSQL | (shared) |
| Logging | structlog | 24.1+ |
| Testing | pytest + pytest-asyncio | 8.0+ |

## Resolved Clarifications

All technical unknowns from the spec have been resolved:

| Unknown | Resolution |
|---------|------------|
| MCP SDK package | `mcp` (official Anthropic SDK) |
| Transport protocol | HTTP/SSE via FastAPI |
| Database pattern | Direct SQLModel access |
| Conversation lifecycle | 30-minute session timeout |
| Logging format | Structured JSON to stdout |
| Validation approach | Pydantic v2 models |
