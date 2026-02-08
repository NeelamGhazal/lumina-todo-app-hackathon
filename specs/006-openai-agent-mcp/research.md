# Research: OpenAI Agent with MCP Integration

**Feature Branch**: `006-openai-agent-mcp`
**Date**: 2026-02-08

## Research Summary

This document captures research findings for Phase III Part 2 - OpenAI Agent Setup using OpenRouter API.

---

## R1: OpenRouter API Compatibility with OpenAI SDK

### Decision
Use official OpenAI Python SDK with custom `base_url` pointing to OpenRouter.

### Rationale
- OpenRouter provides OpenAI-compatible API surface
- Single code path works with both OpenRouter and direct OpenAI
- No additional dependencies required
- Same function calling interface supported

### Implementation Pattern
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
```

### Alternatives Considered
1. **Custom HTTP client** - Rejected: More code to maintain
2. **OpenRouter-specific SDK** - Rejected: Doesn't exist, unnecessary

---

## R2: Chat Completions vs Assistants API

### Decision
Use Chat Completions API with function calling, NOT Assistants API.

### Rationale
- Assistants API relies on OpenAI-hosted threads/state
- OpenRouter doesn't support Assistants API (only Chat Completions)
- Chat Completions with functions provides same tool-calling capability
- Aligns with FR-045: database-only context storage

### Implementation Pattern
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],  # From database
    tools=[...],     # MCP tools as functions
    tool_choice="auto"
)
```

### Alternatives Considered
1. **Assistants API** - Rejected: Not supported by OpenRouter
2. **LangChain agents** - Rejected: Unnecessary abstraction layer

---

## R3: MCP Tool to OpenAI Function Conversion

### Decision
Convert MCP tool schemas to OpenAI function format at startup.

### Rationale
- MCP uses JSON Schema for parameters
- OpenAI functions use same JSON Schema format
- Simple mapping: MCP tool → OpenAI function definition
- One-time conversion at startup (FR-026)

### Conversion Mapping
```python
# MCP Tool Schema (from /mcp/tools)
{
    "name": "add_task",
    "description": "Create a new task",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "format": "uuid"},
            "title": {"type": "string", "minLength": 1}
        },
        "required": ["user_id", "title"]
    }
}

# OpenAI Function Format
{
    "type": "function",
    "function": {
        "name": "add_task",
        "description": "Create a new task",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title"}
                # Note: user_id injected by system, not exposed to LLM
            },
            "required": ["title"]
        }
    }
}
```

### Key Insight
- `user_id` is injected by system (from authenticated user)
- LLM only sees user-facing parameters (title, description, task_id, status)
- Prevents user_id manipulation via prompt injection

---

## R4: Manual Tool Execution Pattern (requires_action)

### Decision
Implement manual tool execution where system handles MCP calls.

### Rationale
- Per clarification: Manual execution pattern selected
- System receives tool call request from LLM
- System executes against MCP server
- System submits results back to LLM
- Provides full control over error handling and logging

### Execution Flow
```
1. User sends message
2. System builds context (last 10 messages from DB)
3. System calls LLM with message + context + tools
4. LLM returns tool_calls (if needed)
5. System executes each tool against MCP server
6. System submits tool results back to LLM
7. LLM generates natural language response
8. System stores user message + assistant response in DB
9. System returns response to user
```

### Loop Handling
- Max 5 tool call rounds per request (prevent infinite loops)
- If LLM keeps calling tools, force completion after limit

---

## R5: Agent Instructions Design

### Decision
Use structured system prompt with clear personality and tool guidelines.

### Rationale
- Clear instructions improve intent recognition
- Tool descriptions help LLM understand when to use each
- Personality guidelines ensure consistent tone

### Agent Instructions Template
```
You are a helpful todo assistant. You help users manage their tasks through natural conversation.

## Personality
- Friendly and conversational
- Concise but helpful
- Confirm successful operations
- Ask for clarification when needed

## Available Tools
You have access to these tools for managing tasks:

1. add_task - Create a new task
   Use when user wants to add, create, or remind about something

2. list_tasks - View tasks
   Use when user asks to show, list, or see their tasks
   Supports filtering: all, pending, completed

3. complete_task - Mark task done
   Use when user says they finished or completed something

4. delete_task - Remove a task
   Use when user wants to delete or remove a task

5. update_task - Modify a task
   Use when user wants to change or update a task's title or description

## Guidelines
- Always use tools for task operations (don't pretend to do them)
- If task_id is ambiguous, list tasks first to help user identify
- Confirm operations with task details in response
- Stay focused on task management; politely redirect off-topic requests
```

---

## R6: Message History Context Window

### Decision
Include last 10 messages (5 exchanges) with each LLM request.

### Rationale
- Per clarification: 10 messages selected
- Covers SC-007 requirement (5 consecutive exchanges)
- Balances context quality with token usage
- Retrieved from database per FR-045

### Implementation
```python
async def get_context_messages(db: AsyncSession, conversation_id: UUID) -> list[dict]:
    """Get last 10 messages for LLM context."""
    messages = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(10)
    )
    # Return in chronological order for LLM
    return [{"role": m.role, "content": m.content} for m in reversed(messages.scalars())]
```

---

## R7: Conversation Session Management

### Decision
Create new conversation after 30 minutes of inactivity (FR-043).

### Rationale
- Single active conversation per user simplifies UX
- 30-minute timeout aligns with typical session expectations
- Database lookup on each request to check last_activity

### Session Logic
```python
async def get_or_create_conversation(db: AsyncSession, user_id: UUID) -> Conversation:
    """Get active conversation or create new one."""
    cutoff = datetime.now(UTC) - timedelta(minutes=30)

    conversation = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.last_activity > cutoff)
        .order_by(Conversation.last_activity.desc())
        .limit(1)
    )

    if existing := conversation.scalar_one_or_none():
        return existing

    # Create new conversation
    new_conv = Conversation(user_id=user_id)
    db.add(new_conv)
    await db.commit()
    return new_conv
```

---

## R8: Error Handling Strategy

### Decision
Immediate user-friendly error with no automatic retry.

### Rationale
- Per clarification: No automatic retry
- Simple, predictable behavior
- Users can manually retry if needed
- Prevents cascading failures

### Error Categories
1. **MCP Server Unavailable**: "I'm having trouble accessing your tasks right now. Please try again in a moment."
2. **Tool Execution Error**: "Something went wrong while [action]. Please try again."
3. **Validation Error**: Pass through as clarification request (e.g., "Which task do you mean?")
4. **Rate Limit**: "I'm a bit overwhelmed right now. Please wait a moment and try again."

---

## R9: OpenRouter Model Selection

### Decision
Use `gpt-4o-mini` as default, `gpt-4o` for complex reasoning.

### Rationale
- `gpt-4o-mini` is cost-effective for simple task operations
- Sufficient for intent recognition and tool calling
- Can upgrade to `gpt-4o` if accuracy issues arise
- Configurable via environment variable

### Configuration
```python
# Default model (cost-optimized)
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini")

# OpenRouter-specific headers (optional)
OPENROUTER_HEADERS = {
    "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),
    "X-Title": "Evolution Todo"
}
```

---

## Dependencies Verified

| Dependency | Version | Status |
|------------|---------|--------|
| openai (Python SDK) | 1.x | Compatible with OpenRouter |
| httpx | 0.28+ | For async MCP calls |
| sqlmodel | 0.0.22+ | Already in chatbot/ |
| pydantic | 2.10+ | Already in chatbot/ |

---

## Next Steps

1. **Phase 1: Design** - Create data-model.md, contracts/, quickstart.md
2. **Phase 2: Implementation** - Tasks for 2A-2D phases
