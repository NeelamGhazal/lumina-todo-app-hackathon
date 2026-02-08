# Feature Specification: MCP Server for Todo Operations

**Feature Branch**: `005-mcp-todo-server`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Phase III - Part 1: MCP Server for Todo Operations"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Agent Creates a Task (Priority: P1)

An AI agent (powered by OpenAI Agents SDK) needs to create a new todo task on behalf of a user. The agent invokes the MCP server's `add_task` tool with the user's ID and task details, and receives confirmation that the task was created and persisted to the database.

**Why this priority**: Task creation is the foundational operation. Without the ability to create tasks, no other operations are meaningful. This establishes the core data flow and validates the entire MCP-to-database pipeline.

**Independent Test**: Can be fully tested by invoking the `add_task` tool with valid parameters and verifying the task appears in the database with correct user ownership.

**Acceptance Scenarios**:

1. **Given** an authenticated user ID and valid task title, **When** the agent calls `add_task` with title "Buy groceries", **Then** the system returns a success response with task_id, status "created", and the title.
2. **Given** an authenticated user ID and task title with optional description, **When** the agent calls `add_task` with title "Meeting prep" and description "Review Q1 slides", **Then** the system creates the task with both fields persisted.
3. **Given** an empty task title, **When** the agent calls `add_task`, **Then** the system returns a validation error with code "VALIDATION_ERROR" and a human-readable message.

---

### User Story 2 - AI Agent Lists User's Tasks (Priority: P1)

An AI agent needs to retrieve a user's tasks to answer questions like "What's on my todo list?" or "Show me my completed tasks." The agent invokes the `list_tasks` tool and receives an array of tasks matching the filter criteria.

**Why this priority**: Listing tasks is essential for the agent to provide context-aware responses. Users frequently ask about their existing tasks before creating new ones.

**Independent Test**: Can be fully tested by creating sample tasks for a user, then invoking `list_tasks` and verifying the correct tasks are returned with proper filtering.

**Acceptance Scenarios**:

1. **Given** a user with 5 pending and 3 completed tasks, **When** the agent calls `list_tasks` with status "all", **Then** the system returns all 8 tasks.
2. **Given** a user with 5 pending and 3 completed tasks, **When** the agent calls `list_tasks` with status "pending", **Then** the system returns only the 5 pending tasks.
3. **Given** a user with no tasks, **When** the agent calls `list_tasks`, **Then** the system returns an empty array (not an error).
4. **Given** two different users each with tasks, **When** agent calls `list_tasks` for user A, **Then** only user A's tasks are returned (user isolation).

---

### User Story 3 - AI Agent Completes a Task (Priority: P2)

An AI agent marks a task as complete when the user says something like "Mark 'Buy groceries' as done." The agent invokes the `complete_task` tool, and the task's completion status is toggled in the database.

**Why this priority**: Completing tasks is the primary way users interact with their todo list after creation. It provides immediate value by tracking progress.

**Independent Test**: Can be fully tested by creating a pending task, invoking `complete_task`, and verifying the task status changed to completed in the database.

**Acceptance Scenarios**:

1. **Given** a pending task owned by the user, **When** the agent calls `complete_task` with the task_id, **Then** the task status changes to "completed" and the response confirms the change.
2. **Given** a completed task owned by the user, **When** the agent calls `complete_task` with the task_id, **Then** the task status toggles back to "pending" (un-complete functionality).
3. **Given** a task_id that doesn't exist, **When** the agent calls `complete_task`, **Then** the system returns error code "TASK_NOT_FOUND".
4. **Given** a task owned by user B, **When** agent calls `complete_task` as user A, **Then** the system returns error code "UNAUTHORIZED".

---

### User Story 4 - AI Agent Deletes a Task (Priority: P2)

An AI agent permanently removes a task when the user requests deletion. The agent invokes the `delete_task` tool, and the task is removed from the database.

**Why this priority**: Users need the ability to remove tasks they no longer want. This is secondary to creation and completion but essential for list maintenance.

**Independent Test**: Can be fully tested by creating a task, invoking `delete_task`, and verifying the task no longer exists in the database.

**Acceptance Scenarios**:

1. **Given** a task owned by the user, **When** the agent calls `delete_task` with the task_id, **Then** the task is permanently removed and response confirms deletion.
2. **Given** a task_id that doesn't exist, **When** the agent calls `delete_task`, **Then** the system returns error code "TASK_NOT_FOUND".
3. **Given** a task owned by user B, **When** agent calls `delete_task` as user A, **Then** the system returns error code "UNAUTHORIZED".

---

### User Story 5 - AI Agent Updates a Task (Priority: P3)

An AI agent modifies an existing task when the user wants to change details. The agent invokes the `update_task` tool with the fields to update, and the changes are persisted.

**Why this priority**: Task updates are less frequent than creation, listing, or completion, but necessary for correcting mistakes or refining task details.

**Independent Test**: Can be fully tested by creating a task with initial values, invoking `update_task` with new values, and verifying the database reflects the changes.

**Acceptance Scenarios**:

1. **Given** a task with title "Meeting", **When** the agent calls `update_task` with new title "Team Meeting", **Then** the task title is updated and response confirms the change.
2. **Given** a task with no description, **When** the agent calls `update_task` adding description "Review agenda", **Then** the description is added.
3. **Given** update_task called with no changes (empty update), **When** the agent calls the tool, **Then** the system returns error code "VALIDATION_ERROR" with message about no changes provided.
4. **Given** a task owned by user B, **When** agent calls `update_task` as user A, **Then** the system returns error code "UNAUTHORIZED".

---

### Edge Cases

- What happens when the database connection fails mid-operation? System returns "DATABASE_ERROR" with retry guidance.
- How does the system handle extremely long task titles (>200 chars)? Validation error returned before database operation.
- What happens when two agents try to modify the same task simultaneously? Last-write-wins with no corruption (database handles atomicity).
- How does the system handle special characters in task titles? UTF-8 supported; no injection possible.
- What happens when user_id is null or empty? Validation error with "VALIDATION_ERROR" code.

## Requirements *(mandatory)*

### Functional Requirements

**MCP Server Core**

- **FR-001**: System MUST expose 5 MCP tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`
- **FR-002**: System MUST follow official MCP protocol specification for tool registration and invocation
- **FR-003**: System MUST be completely stateless - no in-memory state between requests
- **FR-004**: System MUST persist all data to the shared database
- **FR-005**: System MUST return standardized error responses with code, message, and optional details

**Tool: add_task**

- **FR-010**: Tool MUST accept `user_id` (required), `title` (required), and `description` (optional)
- **FR-011**: Tool MUST validate title length between 1-200 characters
- **FR-012**: Tool MUST validate description length maximum 1000 characters (if provided)
- **FR-013**: Tool MUST return response containing task_id, status "created", and title
- **FR-014**: Tool MUST associate created task with the provided user_id

**Tool: list_tasks**

- **FR-020**: Tool MUST accept `user_id` (required) and `status` filter (optional: "all", "pending", "completed")
- **FR-021**: Tool MUST default to "all" when status filter not provided
- **FR-022**: Tool MUST return only tasks belonging to the specified user_id
- **FR-023**: Tool MUST return tasks as array of objects with id, title, description, and completed status
- **FR-024**: Tool MUST return empty array (not error) when user has no tasks

**Tool: complete_task**

- **FR-030**: Tool MUST accept `user_id` (required) and `task_id` (required)
- **FR-031**: Tool MUST toggle the task's completion status (pending ↔ completed)
- **FR-032**: Tool MUST verify task belongs to user before modifying
- **FR-033**: Tool MUST return updated task status in response

**Tool: delete_task**

- **FR-040**: Tool MUST accept `user_id` (required) and `task_id` (required)
- **FR-041**: Tool MUST permanently remove the task from database
- **FR-042**: Tool MUST verify task belongs to user before deleting
- **FR-043**: Tool MUST return confirmation with deleted task's id and title

**Tool: update_task**

- **FR-050**: Tool MUST accept `user_id` (required), `task_id` (required), `title` (optional), `description` (optional)
- **FR-051**: Tool MUST require at least one field to update (title or description)
- **FR-052**: Tool MUST apply same validation rules as add_task for updated fields
- **FR-053**: Tool MUST verify task belongs to user before updating
- **FR-054**: Tool MUST return updated task data in response

**Security & Isolation**

- **FR-060**: System MUST validate user_id on every tool invocation
- **FR-061**: System MUST prevent any cross-user data access
- **FR-062**: System MUST sanitize all inputs to prevent injection attacks

**Observability**

- **FR-065**: System MUST emit structured JSON logs to stdout for all tool invocations
- **FR-066**: System MUST log tool name, user_id, latency (ms), and success/error status for each call
- **FR-067**: System MUST include correlation IDs in error logs for debugging

**Database**

- **FR-070**: System MUST store conversation records for audit trail
- **FR-071**: System MUST store message records linked to conversations
- **FR-072**: System MUST use the existing task storage from Phase II

### Key Entities

- **Task**: Represents a todo item. Key attributes: unique identifier, title, description, completion status, owner (user_id), creation timestamp. Owned by exactly one user. (Existing from Phase II - read/write via this server)

- **Conversation**: Represents an interaction session between AI agent and user. Key attributes: unique identifier, user reference, start timestamp, last activity timestamp. Contains multiple messages. Lifecycle: new conversation created when user has no active conversation or last activity exceeds 30 minutes; conversation reused within the 30-minute activity window. (New for Phase III)

- **Message**: Represents a single exchange within a conversation. Key attributes: unique identifier, conversation reference, sender role (user or assistant), content text, timestamp. Belongs to exactly one conversation. (New for Phase III)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 MCP tools respond within 500 milliseconds under normal load
- **SC-002**: System handles 50 concurrent tool invocations without errors or data corruption
- **SC-003**: 100% of tool invocations with valid parameters succeed and persist correctly
- **SC-004**: 100% of unauthorized access attempts (cross-user) are blocked with appropriate error
- **SC-005**: System restarts result in zero data loss (all state in database)
- **SC-006**: Unit test coverage reaches 80% or higher for tool implementations
- **SC-007**: All 5 tools can be successfully invoked by an OpenAI Agents SDK-based agent in integration testing

## Clarifications

### Session 2026-02-06

- Q: MCP Server Deployment Architecture - standalone or embedded? → A: Standalone FastAPI app on port 8001 with HTTP/SSE transport
- Q: Database Access Pattern - direct DB or via Phase II API? → A: Direct database access using SQLModel (reuse Phase II connection pattern)
- Q: Conversation Lifecycle - when to create new vs. reuse? → A: Session-based with 30-minute inactivity timeout
- Q: Observability & Logging Strategy? → A: Structured JSON logs to stdout (tool calls, errors, latency)
- Q: Tool Parameter Validation Approach? → A: Pydantic models with automatic validation (matches Phase II pattern)

## Assumptions

- User authentication and user_id validation happens at the agent layer before MCP tools are invoked
- The existing Phase II database schema for tasks will not be modified
- The MCP server will run as a standalone FastAPI application on port 8001, separate from the Phase II API, using HTTP/SSE transport for MCP protocol communication
- Database connection credentials will be provided via environment variables
- The official Python `mcp` package provides stable APIs for tool registration

## Dependencies

- Phase II Neon PostgreSQL database (existing, operational) - accessed directly via SQLModel, not through Phase II API
- Phase II Task model schema (existing, reuse model definitions for direct database access)
- Official MCP Python SDK (`mcp` package)
- SQLModel for database operations (consistency with Phase II)
- Pydantic for tool parameter validation (consistency with Phase II)

## Out of Scope

- Agent configuration and prompt engineering (Phase III Part 2)
- Chat UI implementation (Phase III Part 3)
- User authentication logic (handled by Phase II)
- Real-time WebSocket notifications
- Advanced task features (priorities, tags, due dates) - reserved for Phase V
- Voice input support
- File attachments
