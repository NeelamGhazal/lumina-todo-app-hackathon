# Feature Specification: OpenAI Agent with MCP Integration

**Feature Branch**: `006-openai-agent-mcp`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase III - Part 2: OpenAI Agent with MCP Integration"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Adds a Task via Natural Language (Priority: P1)

A user types a natural language request like "Add a task to buy groceries" or "Remind me to call the dentist" in the chat interface. The AI agent understands the intent, extracts the task title, calls the MCP `add_task` tool, and responds with a friendly confirmation.

**Why this priority**: Task creation through natural language is the core value proposition. If users cannot add tasks conversationally, the agent provides no unique value over direct UI interaction.

**Independent Test**: Can be fully tested by sending a task creation message to the agent and verifying: (1) the MCP tool is called with correct parameters, (2) the task is created in the database, (3) the user receives a natural confirmation response.

**Acceptance Scenarios**:

1. **Given** a user sends "Add task: buy milk", **When** the agent processes the message, **Then** the agent calls `add_task` with title "buy milk" and responds "I've added 'buy milk' to your tasks."
2. **Given** a user sends "Remind me to pick up dry cleaning tomorrow", **When** the agent processes the message, **Then** the agent extracts "pick up dry cleaning tomorrow" as the title and creates the task.
3. **Given** a user sends "Add task" without specifying what, **When** the agent processes the message, **Then** the agent asks for clarification: "What would you like to add to your task list?"
4. **Given** the MCP tool returns an error, **When** the agent processes the response, **Then** the agent provides a friendly error message without exposing technical details.

---

### User Story 2 - User Lists Their Tasks (Priority: P1)

A user asks to see their tasks with natural language like "What's on my list?", "Show me my tasks", or "What do I need to do?" The agent retrieves tasks via the MCP `list_tasks` tool and presents them in a readable format.

**Why this priority**: Viewing tasks is essential for the agent to be useful. Users need to see their existing tasks to make decisions about what to complete, delete, or add.

**Independent Test**: Can be fully tested by creating sample tasks, sending a list request to the agent, and verifying the response includes all tasks in a readable format.

**Acceptance Scenarios**:

1. **Given** a user with 3 pending tasks, **When** the user asks "Show my tasks", **Then** the agent lists all 3 tasks with their titles and IDs.
2. **Given** a user asks "What have I completed?", **When** the agent processes the message, **Then** the agent calls `list_tasks` with status "completed" and shows only completed tasks.
3. **Given** a user with no tasks, **When** the user asks "What's on my list?", **Then** the agent responds: "You don't have any tasks yet. Would you like to add one?"
4. **Given** a user asks "How many tasks do I have?", **When** the agent processes the message, **Then** the agent provides a count with summary (e.g., "You have 5 tasks: 3 pending and 2 completed").

---

### User Story 3 - User Completes a Task (Priority: P2)

A user indicates they've finished a task with natural language like "I finished the groceries" or "Mark task 5 as done." The agent identifies the task, calls the MCP `complete_task` tool, and confirms the completion.

**Why this priority**: Completing tasks is the primary interaction after viewing and creating. It provides immediate value by tracking progress.

**Independent Test**: Can be fully tested by creating a pending task, sending a completion request, and verifying the task status changes to completed in the database.

**Acceptance Scenarios**:

1. **Given** a task with ID 5 titled "buy milk", **When** the user says "Complete task 5", **Then** the agent marks it complete and responds: "Done! I've marked 'buy milk' as complete."
2. **Given** a user says "I finished buying groceries", **When** the agent has a task matching that description, **Then** the agent identifies the task and marks it complete.
3. **Given** ambiguous input like "mark it done" with no recent task context, **When** the agent processes the message, **Then** the agent asks: "Which task would you like to complete? Here are your pending tasks: [list]"
4. **Given** the user references a task that doesn't exist, **When** the agent processes the message, **Then** the agent responds: "I couldn't find that task. Here are your current tasks: [list]"

---

### User Story 4 - User Deletes a Task (Priority: P2)

A user wants to remove a task with natural language like "Delete task 3" or "Remove the dentist appointment from my list." The agent identifies the task, calls the MCP `delete_task` tool, and confirms the deletion.

**Why this priority**: Users need to remove tasks they no longer want. This completes the essential CRUD operations for task management.

**Independent Test**: Can be fully tested by creating a task, sending a deletion request, and verifying the task no longer exists in the database.

**Acceptance Scenarios**:

1. **Given** a task with ID 3, **When** the user says "Delete task 3", **Then** the agent deletes it and confirms: "I've removed that task from your list."
2. **Given** a user says "Remove the meeting task", **When** the agent finds a task matching "meeting", **Then** the agent deletes it and confirms.
3. **Given** the user tries to delete a task that doesn't exist, **When** the agent processes the message, **Then** the agent responds: "I couldn't find that task to delete."

---

### User Story 5 - User Updates a Task (Priority: P3)

A user wants to modify an existing task with natural language like "Change task 2 to 'buy organic milk'" or "Update the title of my first task." The agent identifies the task, calls the MCP `update_task` tool, and confirms the change.

**Why this priority**: Updates are less frequent but necessary for correcting mistakes or refining task details.

**Independent Test**: Can be fully tested by creating a task, sending an update request, and verifying the task reflects the new values.

**Acceptance Scenarios**:

1. **Given** a task with ID 2, **When** the user says "Change task 2 to 'buy organic milk'", **Then** the agent updates the title and confirms: "I've updated task 2 to 'buy organic milk'."
2. **Given** a user says "Add a description to task 1: bring the receipt", **When** the agent processes the message, **Then** the agent adds the description and confirms.
3. **Given** the user references a task that doesn't exist, **When** the agent attempts to update, **Then** the agent responds with an appropriate error message.

---

### User Story 6 - Multi-Turn Conversation (Priority: P3)

A user engages in a multi-turn conversation where context from previous messages informs the current action. For example, after listing tasks, saying "complete the first one" should work based on context.

**Why this priority**: Natural conversation flow makes the agent more intuitive but is not essential for basic functionality.

**Independent Test**: Can be fully tested by having a conversation with multiple turns and verifying context is maintained correctly.

**Acceptance Scenarios**:

1. **Given** user just listed 3 tasks, **When** user says "complete the first one", **Then** the agent uses context to identify task 1 and completes it.
2. **Given** user said "add task buy milk" in previous turn, **When** user says "actually make that 'buy oat milk'", **Then** the agent updates the just-created task.
3. **Given** user has been idle for more than 30 minutes, **When** user sends a new message, **Then** a new conversation session begins with fresh context.

---

### Edge Cases

- What happens when the user's message is ambiguous? Agent asks a clarifying question with options.
- How does the agent handle messages unrelated to tasks? Agent politely redirects to task management.
- What happens when MCP server is unavailable? Agent responds with immediate user-friendly error (no automatic retry) and suggests trying again.
- How does the agent handle very long task titles (>200 chars)? Agent truncates or asks user to shorten.
- What happens when multiple tasks match a description? Agent lists matching tasks and asks user to specify.

## Requirements *(mandatory)*

### Functional Requirements

**Agent Configuration**

- **FR-001**: System MUST use the OpenAI Python SDK with base URL configured for OpenRouter (`https://openrouter.ai/api/v1`)
- **FR-002**: System MUST authenticate via `OPENROUTER_API_KEY` environment variable (not OPENAI_API_KEY)
- **FR-003**: System MUST configure the agent with model `gpt-4o` or `gpt-4o-mini`
- **FR-004**: System MUST provide agent instructions that define personality, capabilities, and tool usage guidelines
- **FR-005**: System MUST register all 5 MCP tools as callable functions for the agent

**Natural Language Understanding**

- **FR-010**: Agent MUST recognize task creation intents (add, create, remind, new task, etc.)
- **FR-011**: Agent MUST recognize task listing intents (show, list, what's on, tasks, to-do, etc.)
- **FR-012**: Agent MUST recognize task completion intents (done, complete, finish, mark as done, etc.)
- **FR-013**: Agent MUST recognize task deletion intents (delete, remove, cancel, drop, etc.)
- **FR-014**: Agent MUST recognize task update intents (change, update, modify, rename, etc.)
- **FR-015**: Agent MUST extract task parameters (title, description, task ID) from natural language

**MCP Tool Integration**

- **FR-020**: System MUST convert MCP tool schemas to OpenAI function format
- **FR-021**: System MUST call MCP server at configurable URL for tool execution
- **FR-022**: System MUST include `user_id` in all tool calls for user isolation
- **FR-023**: System MUST handle tool execution results and format them for natural response
- **FR-024**: System MUST handle tool errors gracefully and provide user-friendly messages
- **FR-025**: System MUST use manual tool execution pattern (requires_action) where agent signals tool need and system explicitly calls MCP HTTP endpoint and submits results back to agent
- **FR-026**: System MUST fetch MCP tool schemas once at startup and convert to OpenAI function format (no per-request schema fetching)

**Response Generation**

- **FR-030**: Agent MUST respond in conversational, friendly tone
- **FR-031**: Agent MUST confirm successful operations with relevant details (task title, ID)
- **FR-032**: Agent MUST ask clarifying questions when user intent is ambiguous
- **FR-033**: Agent MUST handle errors without exposing technical details
- **FR-034**: Agent MUST stay focused on task management and politely redirect off-topic requests

**Conversation Management**

- **FR-040**: System MUST maintain conversation history within a session
- **FR-041**: System MUST persist conversation and message records to database
- **FR-042**: System MUST link all messages to the authenticated user
- **FR-043**: System MUST create new conversation after 30 minutes of inactivity
- **FR-044**: System MUST support context-aware responses based on conversation history
- **FR-045**: System MUST retrieve recent message history from database and include with each LLM request (no reliance on external thread/session state)
- **FR-046**: System MUST include last 10 messages (5 user + 5 assistant exchanges) as context for each LLM request

**API Endpoints**

- **FR-050**: System MUST expose `/chat` endpoint for sending messages to the agent
- **FR-051**: System MUST accept user message and user_id as input
- **FR-052**: System MUST return agent response with conversation_id
- **FR-053**: System MUST expose `/conversations` endpoint to list user's conversations
- **FR-054**: System MUST expose `/conversations/{id}/messages` endpoint to get conversation history

### Key Entities

- **Agent**: The AI assistant configured with instructions and tools. Represents the conversational interface to MCP tools. Stateless - configured at startup, processes requests independently.

- **Conversation**: A session of interaction between user and agent (existing from Part 1 database schema). Contains messages and tracks activity for session management.

- **Message**: A single exchange in a conversation (existing from Part 1 database schema). Captures both user input and agent responses.

- **Tool Call**: A request from agent to MCP server. Ephemeral - not persisted, but results influence conversation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Agent correctly identifies user intent in 95% of clearly-stated task requests
- **SC-002**: Agent responds to user messages within 3 seconds under normal load
- **SC-003**: 100% of successful tool calls result in appropriate natural language confirmation
- **SC-004**: Users can complete basic task operations (add, list, complete) in 2 or fewer conversation turns
- **SC-005**: Agent asks clarifying questions in 100% of ambiguous requests (instead of guessing wrong)
- **SC-006**: Error messages are user-friendly in 100% of error scenarios (no stack traces or technical codes)
- **SC-007**: Multi-turn conversations maintain context correctly for at least 5 consecutive exchanges
- **SC-008**: Unit test coverage reaches 80% or higher for agent and tool integration code

## Clarifications

### Session 2026-02-08

- Q: Tool Execution Pattern - automatic or manual? → A: Manual execution (requires_action pattern) - agent signals tool need, system explicitly calls MCP and submits results
- Q: Conversation Context Storage - where to store history? → A: Database only - store all messages in Postgres, send recent history with each LLM call
- Q: Context Window Size - how many messages to include? → A: Last 10 messages per LLM call
- Q: MCP Tool Schema Loading - when to fetch? → A: Startup only - fetch MCP schemas once when agent service starts
- Q: MCP Tool Error Recovery - how to handle failures? → A: Immediate user-friendly error, no automatic retry

## Assumptions

- User authentication happens before chat requests reach the agent (user_id always provided)
- MCP Server from Part 1 is running and accessible at configurable URL (default: localhost:8001)
- OpenRouter API key is valid and has sufficient quota for agent operations
- The conversation/message database schema from Part 1 is deployed and operational
- The agent runs as part of the same chatbot service as the MCP server (shared `chatbot/` directory)

## Dependencies

- MCP Server from Part 1 (running with all 5 tools operational)
- OpenRouter API access (for routing to OpenAI-compatible models)
- OpenAI Python SDK (official package, configured for OpenRouter)
- Neon PostgreSQL database (shared with Parts 1 and 2)
- Conversation/Message tables from Part 1 database schema

## Out of Scope

- User authentication implementation (handled by Phase II backend)
- Chat UI implementation (Phase III Part 3)
- Voice input/output
- Real-time streaming responses (basic request/response for now)
- Advanced conversation features (branching, undo, conversation export)
- Multiple concurrent conversations per user
- Agent personality customization by users
