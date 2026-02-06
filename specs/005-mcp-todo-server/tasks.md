# Tasks: MCP Server for Todo Operations

**Feature Branch**: `005-mcp-todo-server`
**Input**: Design documents from `/specs/005-mcp-todo-server/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/mcp-tools.yaml (complete)

**Tests**: Integration tests included in Phase 1D. Unit tests for tool validation.

**Organization**: Tasks organized by implementation phase from plan.md, mapping to user stories for traceability.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **MCP Server**: `chatbot/mcp_server/` for source code
- **Tests**: `chatbot/tests/` for test files
- Paths based on project structure from plan.md

---

## Phase 1A: Database Schema (30-45 mins)

**Purpose**: Create database tables for conversation tracking (new Phase III entities)

**Objective**: Deploy `conversations` and `messages` tables to Neon PostgreSQL

- [x] T001 Create SQLModel entities (Conversation, Message, MessageRole enum) in `chatbot/mcp_server/models.py` per data-model.md definitions
- [x] T002 Create Alembic migration script for Phase III tables in `api/alembic/versions/` with proper indexes (user_id, conversation_id, composite indexes)
- [x] T003 Run migration against Neon PostgreSQL and verify tables exist via Neon dashboard or psql

**Checkpoint 1**: Tables `conversations` and `messages` visible in Neon with correct columns and indexes

---

## Phase 1B: MCP Server Scaffold (45-60 mins)

**Purpose**: Set up FastAPI application with MCP server integration

**Objective**: Server starts, `/health` returns 200, MCP endpoints accessible

- [x] T004 Initialize `chatbot/` project with UV, create `pyproject.toml` with dependencies: fastapi, uvicorn, mcp, sqlmodel, pydantic, structlog, asyncpg
- [x] T005 [P] Create `chatbot/mcp_server/config.py` with Pydantic Settings for DATABASE_URL, MCP_SERVER_PORT, ENVIRONMENT, LOG_LEVEL
- [x] T006 [P] Create `chatbot/mcp_server/database.py` with async SQLModel engine and session factory (reuse Phase II pattern from `api/database.py`)
- [x] T007 [P] Create `chatbot/mcp_server/logging.py` with structlog JSON configuration for tool call logging (tool_name, user_id, latency_ms, status)
- [x] T008 Create `chatbot/mcp_server/main.py` with FastAPI app, `/health` endpoint, CORS middleware, and MCP server mount at `/mcp`
- [x] T009 Create `chatbot/mcp_server/__init__.py` with module exports
- [x] T010 Create `chatbot/.env.example` with all required environment variables

**Checkpoint 2**: Server starts with `uv run uvicorn mcp_server.main:app --port 8001`, `/health` returns `{"status": "healthy"}`, `/mcp/tools` returns empty array

---

## Phase 1C: Core Tools Implementation (2-3 hours)

**Purpose**: Implement all 5 MCP tools with Pydantic validation

**Objective**: All tools callable via curl, return correct responses per contracts/mcp-tools.yaml

### Tool Infrastructure

- [x] T011 Create `chatbot/mcp_server/schemas.py` with all Pydantic parameter models: AddTaskParams, ListTasksParams, CompleteTaskParams, DeleteTaskParams, UpdateTaskParams per contracts/mcp-tools.yaml
- [x] T012 Create `chatbot/mcp_server/tools/__init__.py` with tool registry and registration decorator
- [ ] T013 Create `chatbot/mcp_server/tools/base.py` with BaseTool class, error handling utilities, and response builders

### User Story 1 - add_task (P1)

- [ ] T014 [US1] Implement `add_task` tool in `chatbot/mcp_server/tools/add_task.py` with title/description validation, task creation, structured logging
- [ ] T015 [US1] Register `add_task` with MCP server in `chatbot/mcp_server/main.py` and verify via `/mcp/tools` listing

### User Story 2 - list_tasks (P1)

- [ ] T016 [US2] Implement `list_tasks` tool in `chatbot/mcp_server/tools/list_tasks.py` with status filtering (all/pending/completed), user isolation
- [ ] T017 [US2] Register `list_tasks` with MCP server and verify filtering works correctly

### User Story 3 - complete_task (P2)

- [ ] T018 [US3] Implement `complete_task` tool in `chatbot/mcp_server/tools/complete_task.py` with ownership verification, toggle logic, completed_at timestamp
- [ ] T019 [US3] Register `complete_task` with MCP server and verify toggle behavior

### User Story 4 - delete_task (P2)

- [ ] T020 [US4] Implement `delete_task` tool in `chatbot/mcp_server/tools/delete_task.py` with ownership verification, hard delete
- [ ] T021 [US4] Register `delete_task` with MCP server and verify deletion

### User Story 5 - update_task (P3)

- [ ] T022 [US5] Implement `update_task` tool in `chatbot/mcp_server/tools/update_task.py` with partial update support, validation, ownership check
- [ ] T023 [US5] Register `update_task` with MCP server and verify updates persist

**Checkpoint 3**: All 5 tools appear in `/mcp/tools`, each tool callable via curl per quickstart.md examples with correct success/error responses

---

## Phase 1D: Integration & Testing (1-1.5 hours)

**Purpose**: End-to-end validation, testing, and documentation

**Objective**: All tests pass, 80%+ coverage, documentation complete

### Test Setup

- [ ] T024 Create `chatbot/tests/__init__.py` and `chatbot/tests/conftest.py` with pytest fixtures: test database session, mock user_id, cleanup utilities
- [ ] T025 Add dev dependencies to `chatbot/pyproject.toml`: pytest, pytest-asyncio, pytest-cov, httpx

### Tool Unit Tests

- [ ] T026 [P] [US1] Create `chatbot/tests/test_add_task.py` with unit tests for add_task: valid creation, validation errors, database persistence
- [ ] T027 [P] [US2] Create `chatbot/tests/test_list_tasks.py` with unit tests for list_tasks: filtering, empty results, user isolation
- [ ] T028 [P] [US3] Create `chatbot/tests/test_complete_task.py` with unit tests for complete_task: toggle logic, not found, unauthorized
- [ ] T029 [P] [US4] Create `chatbot/tests/test_delete_task.py` with unit tests for delete_task: successful delete, not found, unauthorized
- [ ] T030 [P] [US5] Create `chatbot/tests/test_update_task.py` with unit tests for update_task: partial updates, validation, unauthorized

### Integration Tests

- [ ] T031 Create `chatbot/tests/test_api.py` with integration tests: full request/response cycle, health check, tool listing, end-to-end tool flows

### Documentation & Containerization

- [ ] T032 Create `chatbot/README.md` with setup instructions, running locally, testing, API reference
- [ ] T033 Create `chatbot/Dockerfile` for containerization (Python 3.13, UV-based install)
- [ ] T034 Run full test suite with coverage: `uv run pytest --cov=mcp_server --cov-report=term-missing` and verify 80%+ coverage

**Checkpoint 4**: `uv run pytest` passes all tests, coverage report shows ≥80%, README complete, Dockerfile builds successfully

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1A (Database Schema)
    │
    ▼
Phase 1B (Server Scaffold)
    │
    ▼
Phase 1C (Tools Implementation)
    │
    ▼
Phase 1D (Integration & Testing)
```

### Task Dependencies Within Phases

**Phase 1A**: Sequential (T001 → T002 → T003)
- Models must exist before migration script
- Migration must be created before running

**Phase 1B**: T004 first, then T005-T007 in parallel, then T008-T010
- Project init required before any files
- Config, database, logging are independent
- Main app depends on config/database/logging

**Phase 1C**: T011-T013 first (infrastructure), then tools can be parallel by story
- Schemas and base tool required before individual tools
- Each tool (T014-T023) can be implemented independently per user story
- Tools within same story are sequential (implement → register)

**Phase 1D**: T024-T025 first (setup), then T026-T030 in parallel (unit tests), then T031-T034 sequential
- Test fixtures required before tests
- Tool unit tests are independent of each other
- Integration tests after unit tests
- Documentation and Dockerfile can be parallel
- Coverage check is final

### User Story Dependencies

All user stories depend on Phase 1B completion (server scaffold). After Phase 1B:

- **US1 (add_task)**: Independent - foundational operation
- **US2 (list_tasks)**: Independent - requires tasks exist (US1 helps but can use fixtures)
- **US3 (complete_task)**: Independent - requires task exists (can use fixtures)
- **US4 (delete_task)**: Independent - requires task exists (can use fixtures)
- **US5 (update_task)**: Independent - requires task exists (can use fixtures)

### Parallel Opportunities

**Phase 1B Parallel Tasks**:
```bash
# After T004 (project init), run in parallel:
Task T005: "Create config.py with Pydantic Settings"
Task T006: "Create database.py with async engine"
Task T007: "Create logging.py with structlog"
```

**Phase 1C Tool Implementation (after T011-T013)**:
```bash
# Tools can be implemented in parallel by different developers:
Developer A: US1 tools (T014-T015)
Developer B: US2 tools (T016-T017)
Developer C: US3 tools (T018-T019)
Developer D: US4 tools (T020-T021)
Developer E: US5 tools (T022-T023)
```

**Phase 1D Unit Tests**:
```bash
# All unit tests can run in parallel:
Task T026: "test_add_task.py"
Task T027: "test_list_tasks.py"
Task T028: "test_complete_task.py"
Task T029: "test_delete_task.py"
Task T030: "test_update_task.py"
```

---

## Implementation Strategy

### Recommended Approach: Sequential by Priority

1. **Phase 1A**: Complete database schema (30-45 min)
   - Checkpoint 1: Tables visible in Neon

2. **Phase 1B**: Complete server scaffold (45-60 min)
   - Checkpoint 2: Server starts, health returns 200

3. **Phase 1C - MVP First**:
   - T011-T013: Tool infrastructure (30 min)
   - T014-T015: US1 add_task (30 min) - **STOP and verify**
   - T016-T017: US2 list_tasks (30 min) - **STOP and verify**
   - Checkpoint 3 (partial): Two P1 tools working
   - T018-T023: Remaining tools (P2, P3) (1.5 hours)

4. **Phase 1D**: Complete testing and docs (1-1.5 hours)
   - Checkpoint 4: Full test suite passes, 80%+ coverage

### MVP Milestone

After completing T001-T017 (Phases 1A, 1B, and US1+US2 from 1C):
- Database tables deployed
- Server running on port 8001
- `add_task` and `list_tasks` tools functional
- Agent can create and list tasks

This represents minimal viable MCP server functionality.

---

## Task Time Estimates

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| 1A    | T001-T003 | 30-45 min |
| 1B    | T004-T010 | 45-60 min |
| 1C    | T011-T023 | 2-3 hours |
| 1D    | T024-T034 | 1-1.5 hours |
| **Total** | **34 tasks** | **5-6.5 hours** |

---

## Notes

- Each task targets 15-30 minutes of focused work
- [P] tasks can run in parallel when marked
- [Story] labels map to user stories from spec.md
- Verify quickstart.md examples work at each checkpoint
- Commit after completing each phase
- Run tests incrementally (don't wait until Phase 1D)
- Use existing Phase II patterns for database/config/logging consistency
