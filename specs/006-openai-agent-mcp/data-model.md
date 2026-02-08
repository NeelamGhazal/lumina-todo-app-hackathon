# Data Model: OpenAI Agent with MCP Integration

**Feature Branch**: `006-openai-agent-mcp`
**Date**: 2026-02-08

## Overview

This document defines data entities for Phase III Part 2. Most entities already exist from Part 1 (Conversation, Message). This part adds no new database tables but defines runtime data structures for agent operations.

---

## Existing Entities (from Part 1)

### Conversation
Already defined in `chatbot/mcp_server/models.py:97-121`

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Owner (validated at application layer) |
| created_at | datetime | Session start |
| last_activity | datetime | Updated on each message |

**Session Rules:**
- New conversation after 30 minutes of inactivity (FR-043)
- No deletion (audit trail)

### Message
Already defined in `chatbot/mcp_server/models.py:124-144`

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| conversation_id | UUID | FK to conversations |
| role | MessageRole | "user" or "assistant" |
| content | str | Message text |
| created_at | datetime | Timestamp |

**Storage Rules:**
- Only user and assistant messages stored
- Tool call internals NOT persisted
- Last 10 messages used for context (FR-046)

---

## Runtime Data Structures (New for Part 2)

### ChatRequest
Input to `/chat` endpoint.

```python
class ChatRequest(BaseModel):
    """Request to send message to agent."""
    message: str = Field(..., min_length=1, max_length=4000)
    user_id: UUID  # From auth, not user-provided in production
    conversation_id: UUID | None = None  # Optional: continue specific conversation
```

### ChatResponse
Output from `/chat` endpoint.

```python
class ChatResponse(BaseModel):
    """Response from agent."""
    message: str  # Agent's natural language response
    conversation_id: UUID  # For continuing the conversation
    tool_calls: list[ToolCallSummary] | None = None  # Optional: tools used
```

### ToolCallSummary
Summary of tool execution (for transparency).

```python
class ToolCallSummary(BaseModel):
    """Summary of a tool call made during response generation."""
    tool: str  # Tool name (add_task, list_tasks, etc.)
    success: bool
    result_preview: str | None = None  # Brief description of result
```

### ConversationSummary
For `/conversations` endpoint.

```python
class ConversationSummary(BaseModel):
    """Summary of a conversation for listing."""
    id: UUID
    created_at: datetime
    last_activity: datetime
    message_count: int
    preview: str | None = None  # First user message (truncated)
```

### MessageResponse
For `/conversations/{id}/messages` endpoint.

```python
class MessageResponse(BaseModel):
    """Message for history viewing."""
    id: UUID
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime
```

---

## OpenAI Function Definitions (Runtime)

These are generated at startup from MCP tool schemas (FR-026).

### add_task Function
```json
{
    "type": "function",
    "function": {
        "name": "add_task",
        "description": "Create a new task for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title (1-200 characters)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional task description"
                }
            },
            "required": ["title"]
        }
    }
}
```

### list_tasks Function
```json
{
    "type": "function",
    "function": {
        "name": "list_tasks",
        "description": "List user's tasks with optional status filter",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": "Filter by status (default: all)"
                }
            },
            "required": []
        }
    }
}
```

### complete_task Function
```json
{
    "type": "function",
    "function": {
        "name": "complete_task",
        "description": "Mark a task as complete or toggle back to pending",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "ID of the task to complete"
                }
            },
            "required": ["task_id"]
        }
    }
}
```

### delete_task Function
```json
{
    "type": "function",
    "function": {
        "name": "delete_task",
        "description": "Permanently delete a task",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "ID of the task to delete"
                }
            },
            "required": ["task_id"]
        }
    }
}
```

### update_task Function
```json
{
    "type": "function",
    "function": {
        "name": "update_task",
        "description": "Update a task's title or description",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "ID of the task to update"
                },
                "title": {
                    "type": "string",
                    "description": "New title (optional)"
                },
                "description": {
                    "type": "string",
                    "description": "New description (optional)"
                }
            },
            "required": ["task_id"]
        }
    }
}
```

**Note:** `user_id` is NOT exposed to the LLM. It's injected by the system from the authenticated user context before calling MCP tools.

---

## Entity Relationships

```
User (Phase II)
  │
  ├─── Conversation (1:N)
  │       │
  │       └─── Message (1:N)
  │
  └─── Task (1:N, via MCP tools)

Agent (Runtime)
  │
  ├─── OpenAI Client (singleton)
  │
  ├─── Tool Definitions (loaded at startup)
  │
  └─── MCP Client (for tool execution)
```

---

## Data Flow

```
1. Chat Request
   ├── user_id (from auth)
   ├── message (user input)
   └── conversation_id (optional)

2. Context Building
   ├── Get/create conversation (30-min timeout)
   ├── Fetch last 10 messages
   └── Build OpenAI messages array

3. LLM Processing
   ├── Send to OpenRouter (gpt-4o-mini)
   ├── Receive tool_calls or response
   └── Execute tools if needed

4. Tool Execution (if required)
   ├── Inject user_id into params
   ├── Call MCP server
   └── Submit results to LLM

5. Response Storage
   ├── Store user message
   ├── Store assistant response
   └── Update conversation.last_activity

6. Chat Response
   ├── message (natural language)
   ├── conversation_id
   └── tool_calls (optional summary)
```
