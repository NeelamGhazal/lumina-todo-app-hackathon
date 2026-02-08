# Tasks: OpenAI Agent with MCP Integration

**Feature Branch**: `006-openai-agent-mcp`
**Input**: Design documents from `/specs/006-openai-agent-mcp/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/agent-api.yaml (complete)

**Tests**: Integration tests included in Phase 2D. Unit tests for all agent components.

**Organization**: Tasks organized by implementation phase from plan.md (2A-2D), mapping to user stories for traceability.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

## Path Conventions

- **Agent Module**: `chatbot/agent/` for new agent implementation
- **MCP Server**: `chatbot/mcp_server/` for endpoint additions (existing from Part 1)
- **Tests**: `chatbot/tests/` for test files
- Paths based on project structure from plan.md

---

## Phase 2A: OpenRouter Client Setup (45-60 mins)

**Purpose**: Initialize OpenAI SDK with OpenRouter and verify connectivity

**Objective**: Agent can send messages to OpenRouter and receive responses

- [X] T001 Add `openai>=1.12.0` dependency to `chatbot/pyproject.toml` and run `uv sync`
- [X] T002 [P] Update `chatbot/.env.example` with `OPENROUTER_API_KEY` and `AGENT_MODEL` variables
- [X] T003 Create `chatbot/agent/__init__.py` with module exports
- [X] T004 Create `chatbot/agent/config.py` with Pydantic Settings for OPENROUTER_API_KEY, AGENT_MODEL, MCP_SERVER_URL, and agent instructions template
- [X] T005 Create `chatbot/agent/schemas.py` with ChatRequest, ChatResponse, ToolCallSummary Pydantic models per contracts/agent-api.yaml
- [X] T006 Create `chatbot/agent/client.py` with OpenRouter client wrapper (OpenAI SDK with custom base_url), singleton pattern, and structured logging
- [X] T007 Add agent health status to existing `/health` endpoint in `chatbot/mcp_server/main.py`

**Checkpoint 1**: OpenRouter client initialized, `/health` returns agent status, basic message send/receive works

---

## Phase 2B: MCP Tool Integration (1-1.5 hours)

**Purpose**: Fetch MCP tools and integrate with OpenAI function calling

**Objective**: Agent can call MCP tools and receive results

- [X] T008 Create `chatbot/agent/tools.py` with `fetch_mcp_tools()` function to GET tool schemas from MCP server
- [X] T009 Implement `mcp_to_openai_function(mcp_tool)` converter in `chatbot/agent/tools.py` to transform MCP schemas to OpenAI function format
- [X] T010 Implement `get_openai_tools()` in `chatbot/agent/tools.py` to return all 5 tools in OpenAI format (user_id excluded from LLM-visible params)
- [X] T011 Implement `execute_mcp_tool(tool_name, arguments, user_id)` in `chatbot/agent/tools.py` to call MCP server's `/mcp/call` endpoint
- [X] T012 Add error handling in `chatbot/agent/tools.py` for MCP server unavailable, validation errors, and tool execution failures
- [X] T013 Update `chatbot/agent/client.py` to load tools at module initialization (startup loading per ADR-007)

**Checkpoint 2**: All 5 MCP tools registered as OpenAI functions, tool execution works, errors handled gracefully

---

## Phase 2C: Conversation Management (1-1.5 hours)

**Purpose**: Implement session management and context retrieval

**Objective**: Multi-turn conversations maintain context correctly

- [ ] T014 Create `chatbot/agent/conversation.py` with `get_or_create_conversation(db, user_id)` function (30-min timeout per FR-043)
- [ ] T015 Implement `get_context_messages(db, conversation_id, limit=10)` in `chatbot/agent/conversation.py` to retrieve last 10 messages
- [ ] T016 Implement `store_message(db, conversation_id, role, content)` in `chatbot/agent/conversation.py` to persist user and assistant messages
- [ ] T017 Implement `update_conversation_activity(db, conversation_id)` in `chatbot/agent/conversation.py` to update last_activity timestamp
- [ ] T018 Create `chatbot/agent/chat.py` with main `process_chat(message, user_id, db)` orchestration function
- [ ] T019 Implement tool execution loop in `chatbot/agent/chat.py` with max 5 rounds limit per request
- [ ] T020 Add `/chat` POST endpoint to `chatbot/mcp_server/main.py` per contracts/agent-api.yaml
- [ ] T021 Add `/conversations` GET endpoint to `chatbot/mcp_server/main.py` for listing user conversations
- [ ] T022 Add `/conversations/{conversation_id}/messages` GET endpoint to `chatbot/mcp_server/main.py` for conversation history

**Checkpoint 3**: Conversations persist, context maintained across turns, 30-min timeout works, all endpoints respond correctly

---

## Phase 2D: Testing & Documentation (1.5-2 hours)

**Purpose**: Complete integration with natural responses and full test coverage

**Objective**: All tests pass with 80%+ coverage

### Unit Tests

- [ ] T023 [P] Create `chatbot/tests/test_agent_config.py` with tests for config loading and agent instructions
- [ ] T024 [P] Create `chatbot/tests/test_agent_client.py` with tests for OpenRouter client initialization and message sending (mock API)
- [ ] T025 [P] Create `chatbot/tests/test_agent_tools.py` with tests for schema conversion and tool execution (mock MCP server)
- [ ] T026 [P] Create `chatbot/tests/test_agent_conversation.py` with tests for session management, timeout logic, and message storage
- [ ] T027 [P] Create `chatbot/tests/test_agent_chat.py` with tests for chat orchestration, tool loop, and response formatting

### Integration Tests

- [ ] T028 [US1] Create `chatbot/tests/test_chat_add_task.py` with integration tests for adding tasks via natural language
- [ ] T029 [US2] Create `chatbot/tests/test_chat_list_tasks.py` with integration tests for listing tasks via natural language
- [ ] T030 [US3] [US4] Create `chatbot/tests/test_chat_complete_delete.py` with integration tests for completing and deleting tasks
- [ ] T031 [US5] Create `chatbot/tests/test_chat_update_task.py` with integration tests for updating tasks via natural language
- [ ] T032 [US6] Create `chatbot/tests/test_chat_multi_turn.py` with integration tests for multi-turn conversations with context

### Documentation

- [ ] T033 Update `chatbot/README.md` with agent setup instructions, environment variables, and example conversations
- [ ] T034 Run full test suite with coverage: `uv run pytest --cov=mcp_server --cov=agent --cov-report=term-missing` and verify 80%+ coverage

**Checkpoint 4**: All tests passing, 80%+ coverage, README complete, ready for Part 3 (ChatKit UI)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 2A (OpenRouter Client Setup)
    │
    ▼
Phase 2B (MCP Tool Integration) ← Requires Part 1 MCP server running
    │
    ▼
Phase 2C (Conversation Management)
    │
    ▼
Phase 2D (Testing & Documentation)
```

### Task Dependencies Within Phases

**Phase 2A**: T001 first, then T002-T003 in parallel, then T004-T006 sequential, finally T007
- Dependencies must be installed before config
- Config needed before client
- Client needed before health check integration

**Phase 2B**: T008 → T009 → T010 → T011 → T012 → T013
- Must fetch schemas before converting
- Must convert before exposing to client
- Must have execution before error handling
- Client updated last after all tools ready

**Phase 2C**: T014-T017 (conversation functions), then T018-T019 (chat orchestration), then T020-T022 (endpoints)
- Conversation functions before chat orchestration
- Chat orchestration before endpoints
- Endpoints can be parallel once chat.py complete

**Phase 2D**: T023-T027 in parallel (unit tests), then T028-T032 in parallel (integration), then T033-T034 (docs)
- All unit tests are independent
- All integration tests are independent
- Documentation after tests confirm functionality

### Parallel Opportunities

**Phase 2A Parallel Tasks**:
```bash
# After T001 (dependencies), run in parallel:
Task T002: "Update .env.example with agent variables"
Task T003: "Create agent/__init__.py"
```

**Phase 2D Unit Tests (all parallel)**:
```bash
Task T023: "test_agent_config.py"
Task T024: "test_agent_client.py"
Task T025: "test_agent_tools.py"
Task T026: "test_agent_conversation.py"
Task T027: "test_agent_chat.py"
```

**Phase 2D Integration Tests (all parallel)**:
```bash
Task T028: "test_chat_add_task.py" [US1]
Task T029: "test_chat_list_tasks.py" [US2]
Task T030: "test_chat_complete_delete.py" [US3/US4]
Task T031: "test_chat_update_task.py" [US5]
Task T032: "test_chat_multi_turn.py" [US6]
```

---

## User Story Mapping

| User Story | Priority | Related Tasks | Integration Test |
|------------|----------|---------------|------------------|
| US1: Add Task | P1 | T018-T020 | T028 |
| US2: List Tasks | P1 | T018-T020 | T029 |
| US3: Complete Task | P2 | T018-T020 | T030 |
| US4: Delete Task | P2 | T018-T020 | T030 |
| US5: Update Task | P3 | T018-T020 | T031 |
| US6: Multi-Turn | P3 | T014-T019 | T032 |

**Note**: All user stories share the same core components (chat orchestration, conversation management). The differentiation is in how the LLM uses tools based on user intent, tested via integration tests.

---

## Implementation Strategy

### MVP First (Phases 2A + 2B only)

1. Complete Phase 2A (OpenRouter Client)
2. Complete Phase 2B (MCP Tool Integration)
3. **STOP and VALIDATE**: Test basic chat with tools via curl
4. This provides US1 + US2 (add/list tasks) functionality

### Full Implementation

1. Complete Phase 2A → Checkpoint 1
2. Complete Phase 2B → Checkpoint 2
3. Complete Phase 2C → Checkpoint 3
4. Complete Phase 2D → Checkpoint 4 (FINAL)

### Checkpoint Verification

**Checkpoint 1 Verification**:
```bash
curl http://localhost:8001/health
# Should include: "agent_status": "ready"
```

**Checkpoint 2 Verification**:
```bash
# Start MCP server, then test tool listing
curl http://localhost:8001/mcp/tools
# Should return 5 tools in OpenAI function format
```

**Checkpoint 3 Verification**:
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task: test checkpoint", "user_id": "550e8400-e29b-41d4-a716-446655440000"}'
# Should create task and return natural response with conversation_id
```

**Checkpoint 4 Verification**:
```bash
cd chatbot && uv run pytest --cov=mcp_server --cov=agent --cov-report=term-missing
# Should show 80%+ coverage, all tests passing
```

---

## Notes

- Each task targets 15-30 minutes of focused work
- [P] tasks can run in parallel when marked
- [Story] labels map to user stories from spec.md
- Verify quickstart.md examples work at each checkpoint
- Commit after completing each phase
- Run tests incrementally (don't wait until Phase 2D)
- MCP server from Part 1 must be running for Phases 2B-2D
