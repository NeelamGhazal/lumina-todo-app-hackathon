# Data Model: ChatKit UI

**Feature**: 007-chatkit-ui
**Date**: 2026-02-08

## Overview

ChatKit UI uses existing data models from Part 1 (MCP Server) and Part 2 (OpenRouter Agent). No new database tables are required.

## Existing Entities (Part 1/2)

### Conversation

Represents a chat session between user and AI assistant.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Owner of conversation |
| created_at | datetime | When conversation started |
| last_activity | datetime | Last message timestamp |

**Behavior**:
- One active conversation per user (30-min timeout)
- After timeout, new conversation created automatically
- Managed by Part 2 agent's `get_or_create_conversation()`

### Message

Represents a single message in a conversation.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| conversation_id | UUID | FK to Conversation |
| role | enum | "user" or "assistant" |
| content | text | Message text (supports markdown) |
| created_at | datetime | When message was sent |

**Constraints**:
- Content max length: 4000 characters (user), unlimited (assistant)
- Role values: "user", "assistant"

---

## Frontend Runtime Types

### Message (Frontend)

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string; // ISO 8601
  status?: 'sending' | 'sent' | 'error'; // UI-only, not persisted
}
```

### ChatResponse (API Response)

```typescript
interface ChatResponse {
  message: string;
  conversation_id: string;
  tool_calls?: ToolCallSummary[];
}

interface ToolCallSummary {
  tool: string;
  success: boolean;
  result_preview?: string;
}
```

### ConversationSummary (List View)

```typescript
interface ConversationSummary {
  id: string;
  created_at: string;
  last_activity: string;
  message_count: number;
  preview?: string; // First user message, truncated
}
```

### ChatState (Frontend State)

```typescript
interface ChatState {
  messages: Message[];
  conversationId: string | null;
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
}
```

---

## API Request/Response Types

### Send Message

**Request** (POST /chat):
```typescript
interface ChatRequest {
  message: string;        // 1-4000 chars
  user_id: string;        // UUID
  conversation_id?: string; // Optional, continue existing
}
```

**Response**:
```typescript
interface ChatResponse {
  message: string;
  conversation_id: string;
  tool_calls?: ToolCallSummary[];
}
```

### Get History

**Request** (GET /conversations/{id}/messages):
- Path: `conversation_id` (UUID)
- Query: `user_id` (UUID), `limit` (1-200, default 50)

**Response**:
```typescript
interface HistoryResponse {
  messages: Message[];
}
```

### List Conversations

**Request** (GET /conversations):
- Query: `user_id` (UUID), `limit` (1-100, default 20)

**Response**:
```typescript
interface ConversationsResponse {
  conversations: ConversationSummary[];
}
```

---

## State Transitions

### Message Status Flow

```
[User types] → 'sending' → [API success] → 'sent'
                        ↘ [API error] → 'error' → [Retry] → 'sending'
```

### Conversation Lifecycle

```
[No conversation] → [First message] → [New conversation created]
                                           ↓
                              [Messages within 30 min] → [Same conversation]
                                           ↓
                              [30+ min inactive] → [New conversation on next message]
```

---

## Validation Rules

| Field | Rule |
|-------|------|
| message | Required, 1-4000 chars, non-empty after trim |
| user_id | Required, valid UUID format |
| conversation_id | Optional, valid UUID format if provided |

---

## Data Flow Diagram

```
┌─────────────────┐
│   Frontend      │
│  (ChatKit UI)   │
└────────┬────────┘
         │ HTTP (fetch)
         ▼
┌─────────────────┐
│  Part 2 Agent   │
│  (Port 8001)    │
│  /chat          │
│  /conversations │
└────────┬────────┘
         │ SQLModel
         ▼
┌─────────────────┐
│   Database      │
│  (Neon/SQLite)  │
│  conversations  │
│  messages       │
└─────────────────┘
```

---

## No New Tables Required

ChatKit UI is a frontend feature. All data persistence is handled by:

1. **Part 1 (MCP Server)**: Database schema, models
2. **Part 2 (OpenRouter Agent)**: Conversation/message management

Frontend only needs to:
- Call existing API endpoints
- Store UI state in React hooks
- Display data from API responses
