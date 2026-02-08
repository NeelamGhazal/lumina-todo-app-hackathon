# Implementation Plan: MCP Server for Todo Operations

**Branch**: `005-mcp-todo-server` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-mcp-todo-server/spec.md`

## Summary

Build a stateless MCP (Model Context Protocol) server that exposes 5 todo CRUD operations as tools for AI agents. The server runs as a standalone FastAPI application on port 8001, using HTTP/SSE transport. All state is persisted to the shared Neon PostgreSQL database (Phase II), with new tables for conversation and message tracking.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI, MCP SDK (`mcp`), SQLModel, Pydantic, structlog
**Storage**: Neon PostgreSQL (shared with Phase II, direct SQLModel access)
**Testing**: pytest + pytest-asyncio, 80%+ coverage target
**Target Platform**: Linux server (Docker-ready, HF Spaces compatible)
**Project Type**: Single backend service (MCP server)
**Performance Goals**: <500ms tool response time, 50 concurrent invocations
**Constraints**: Stateless architecture, no in-memory state, 30-min conversation timeout
**Scale/Scope**: Single user operations, audit trail via conversation/message tables

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | PASS | Spec complete with clarifications |
| II. Professional Quality | PASS | Type hints, Pydantic, async, tests planned |
| III. Visual Excellence | N/A | Server-side, no UI |
| IV. Task-Driven Implementation | PASS | Tasks to be generated via /sp.tasks |
| V. Checkpoint Control | PASS | 4 checkpoints defined |
| VI. AI-First Engineering | PASS | MCP SDK for tool exposure |
| VII. Cloud-Native Mindset | PASS | Stateless, containerizable, 12-factor logging |

**Technology Stack Compliance**:
- Python 3.13+ ✓
- FastAPI ✓
- SQLModel ✓
- Pydantic ✓
- MCP SDK ✓

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI Agent (OpenAI Agents SDK)                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP/SSE
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MCP Server (Port 8001)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         FastAPI Application                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │    │
│  │  │   /health   │  │ /mcp/tools  │  │  /mcp/call  │  │  Logging  │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          MCP Tool Registry                           │    │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────────┐ ┌────────────┐       │    │
│  │  │ add_task │ │ list_tasks │ │ complete_task│ │ delete_task│ ...   │    │
│  │  └──────────┘ └────────────┘ └──────────────┘ └────────────┘       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     Pydantic Validation Layer                        │    │
│  │  AddTaskParams | ListTasksParams | CompleteTaskParams | ...          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ SQLModel (async)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Neon PostgreSQL (Shared with Phase II)                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   users (P2)    │  │   tasks (P2)    │  │  conversations (P3 - NEW)  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
│                                            ┌─────────────────────────────┐  │
│                                            │    messages (P3 - NEW)      │  │
│                                            └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

### Documentation (this feature)

```text
specs/005-mcp-todo-server/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology research & decisions
├── data-model.md        # Entity definitions & migrations
├── quickstart.md        # Setup guide
├── contracts/
│   └── mcp-tools.yaml   # OpenAPI contract for MCP tools
└── tasks.md             # Implementation tasks (via /sp.tasks)
```

### Source Code (repository root)

```text
chatbot/
├── mcp_server/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + MCP server setup
│   ├── config.py            # Pydantic settings
│   ├── database.py          # Async engine + session factory
│   ├── models.py            # Conversation, Message SQLModels
│   ├── schemas.py           # Pydantic tool parameter models
│   ├── logging.py           # Structured JSON logging
│   └── tools/
│       ├── __init__.py      # Tool registry
│       ├── base.py          # Base tool class/decorator
│       ├── add_task.py
│       ├── list_tasks.py
│       ├── complete_task.py
│       ├── delete_task.py
│       └── update_task.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures (test DB, mock user)
│   ├── test_add_task.py
│   ├── test_list_tasks.py
│   ├── test_complete_task.py
│   ├── test_delete_task.py
│   ├── test_update_task.py
│   └── test_api.py          # Integration tests
├── pyproject.toml
├── .env.example
└── Dockerfile
```

**Structure Decision**: Single backend service in `chatbot/mcp_server/` to keep Phase III code separate from Phase II `api/` directory.

## Architecture Decision Records

### ADR-001: MCP Server Deployment Model

**Status**: Accepted
**Context**: Need to expose MCP tools for AI agents. Options: embed in Phase II API or run standalone.

**Decision**: Standalone FastAPI app on port 8001

**Rationale**:
- Clear separation of concerns (Phase II handles auth/web, Phase III handles AI tools)
- Independent scaling and deployment
- No port conflicts with Phase II (8000)
- Easier to containerize separately

**Consequences**:
- (+) Clean architecture, independent deployments
- (+) Can scale MCP server separately from main API
- (-) Additional process to manage
- (-) Separate monitoring/logging configuration needed

---

### ADR-002: Database Access Strategy

**Status**: Accepted
**Context**: MCP tools need to read/write tasks. Options: call Phase II API or direct DB access.

**Decision**: Direct SQLModel access to shared Neon PostgreSQL

**Rationale**:
- Lower latency (~20ms vs ~200ms for HTTP)
- Consistent with Phase II codebase patterns
- Single source of truth for data
- Connection pooling handles concurrency

**Consequences**:
- (+) Fast tool responses (<500ms target)
- (+) Code consistency with Phase II
- (-) Schema coupling (must match Phase II models)
- (-) Direct DB dependency (no API abstraction)

---

### ADR-003: Tool Parameter Validation

**Status**: Accepted
**Context**: Need to validate tool inputs. Options: Pydantic, manual, JSON Schema.

**Decision**: Pydantic v2 models for all tool parameters

**Rationale**:
- Automatic validation with clear error messages
- Type safety and IDE support
- Consistent with Phase II patterns
- Integrates with FastAPI

**Consequences**:
- (+) Clean validation code
- (+) Automatic error responses
- (-) Extra model classes per tool
- (-) Schema duplication (Pydantic + MCP JSON Schema)

---

### ADR-004: Conversation Storage Strategy

**Status**: Accepted
**Context**: Need to track conversation history. Options: store all, store chat only, store nothing.

**Decision**: Store user and assistant messages only (skip tool call internals)

**Rationale**:
- Provides conversation context for multi-turn interactions
- Reduces storage bloat (tool calls are verbose)
- Sufficient for conversation reconstruction
- Audit trail for compliance

**Consequences**:
- (+) Smaller message table
- (+) Cleaner conversation history
- (-) Cannot replay exact tool calls
- (-) Tool debugging requires logs instead

---

## Implementation Phases

### Phase 1A: Database Schema (30-45 mins)

**Objective**: Create database tables for conversation tracking

**Tasks**:
1. Create `Conversation` SQLModel in `chatbot/mcp_server/models.py`
2. Create `Message` SQLModel with role enum
3. Create Alembic migration script
4. Run migration against Neon PostgreSQL
5. Verify tables exist via Neon dashboard

**Dependencies**: None
**Outputs**:
- `chatbot/mcp_server/models.py`
- Database migration applied

**Checkpoint 1**: Tables `conversations` and `messages` visible in Neon

---

### Phase 1B: MCP Server Scaffold (45-60 mins)

**Objective**: Set up FastAPI application with MCP server integration

**Tasks**:
1. Initialize `chatbot/` project with UV
2. Install dependencies: fastapi, mcp, sqlmodel, pydantic, structlog
3. Create `config.py` with Pydantic settings
4. Create `database.py` with async engine (reuse Phase II pattern)
5. Create `logging.py` with structured JSON output
6. Create `main.py` with FastAPI app + health endpoint
7. Integrate MCP server mount at `/mcp`
8. Configure CORS middleware

**Dependencies**: Phase 1A (models exist)
**Outputs**:
- `chatbot/mcp_server/main.py`
- `chatbot/mcp_server/config.py`
- `chatbot/mcp_server/database.py`
- `chatbot/mcp_server/logging.py`

**Checkpoint 2**: Server starts, `/health` returns 200, `/mcp/tools` returns empty array

---

### Phase 1C: Core Tools Implementation (2-3 hours)

**Objective**: Implement all 5 MCP tools with tests

**Tasks** (per tool):
1. Create Pydantic parameter model in `schemas.py`
2. Implement tool function in `tools/<name>.py`
3. Register tool with MCP server
4. Write unit tests with mocked database
5. Write integration tests with real database

**Tool Order** (by priority):
1. `add_task` (P1) - Foundation for all other tests
2. `list_tasks` (P1) - Needed to verify add_task
3. `complete_task` (P2) - Toggle completion
4. `delete_task` (P2) - Remove tasks
5. `update_task` (P3) - Modify existing

**Dependencies**: Phase 1B (server running)
**Outputs**:
- `chatbot/mcp_server/schemas.py`
- `chatbot/mcp_server/tools/*.py`
- `chatbot/tests/test_*.py`

**Checkpoint 3**: All 5 tools callable via curl, unit tests passing

---

### Phase 1D: Integration & Testing (1-1.5 hours)

**Objective**: End-to-end validation and documentation

**Tasks**:
1. End-to-end tool invocation tests
2. Error handling verification (all error codes)
3. Performance benchmarking (<500ms per tool)
4. User isolation tests (cross-user blocked)
5. Create README.md for chatbot module
6. Create Dockerfile for containerization
7. Update test coverage to 80%+

**Dependencies**: Phase 1C (tools working)
**Outputs**:
- `chatbot/tests/test_integration.py`
- `chatbot/README.md`
- `chatbot/Dockerfile`
- Coverage report

**Checkpoint 4**: Integration tests pass, coverage ≥80%, README complete

---

## Component Responsibilities

| Component | Responsibility | Key Files |
|-----------|---------------|-----------|
| **Config** | Load env vars, validate settings | `config.py` |
| **Database** | Async connection, session factory | `database.py` |
| **Models** | SQLModel entities | `models.py` |
| **Schemas** | Pydantic validation models | `schemas.py` |
| **Logging** | Structured JSON logging | `logging.py` |
| **Tools** | MCP tool implementations | `tools/*.py` |
| **Main** | FastAPI app, MCP mount | `main.py` |

## Testing Strategy

### Unit Tests
- Each tool function tested in isolation
- Mocked database sessions
- Cover happy path + error cases
- Target: 85% coverage on tool logic

### Integration Tests
- Real database with test fixtures
- Full request/response cycle
- User isolation verification
- Error code verification

### Performance Tests
- Benchmark each tool response time
- Verify <500ms under normal load
- Test with 50 concurrent requests

### Error Tests
- Invalid parameters (validation errors)
- Missing tasks (TASK_NOT_FOUND)
- Cross-user access (UNAUTHORIZED)
- Database failures (DATABASE_ERROR)

## Success Criteria per Checkpoint

| Checkpoint | Criteria | Verification |
|------------|----------|--------------|
| **1** | DB schema deployed | Tables visible in Neon |
| **2** | Server starts | `/health` returns 200 |
| **3** | Tools implemented | curl invocations succeed |
| **4** | Integration complete | Tests pass, 80%+ coverage |

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| MCP SDK API changes | High | Pin version, review changelog |
| Neon connection limits | Medium | Connection pooling, pool_size=5 |
| Schema drift from Phase II | Medium | Import Phase II Task model directly |
| Performance bottlenecks | Medium | Async everywhere, index tuning |

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Approach | Rationale |
|--------|----------|-----------|
| Single service | Standalone FastAPI | Clean separation from Phase II |
| Direct DB access | SQLModel async | Performance (<500ms requirement) |
| No caching | Database-first | Simplicity, stateless architecture |
