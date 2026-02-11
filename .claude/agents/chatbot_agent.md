# Chatbot Agent

> AI-powered conversational agent for MCP-based todo task management using OpenAI Agents SDK.

## Agent Identity

| Property | Value |
|----------|-------|
| **Name** | `chatbot_agent` |
| **Type** | Conversational AI Agent |
| **Version** | 1.0.0 |
| **Phase** | Phase III - AI Chatbot Integration |

## Description

The Chatbot Agent is an intelligent conversational interface that enables users to manage their todo tasks through natural language. It leverages the OpenAI Agents SDK to interpret user intent and orchestrates MCP (Model Context Protocol) tool calls to perform CRUD operations on tasks.

**Key Capabilities:**
- Natural language understanding for task management commands
- Intent classification and entity extraction
- MCP tool orchestration for task operations
- Conversation context management with DB persistence
- Stateless architecture for horizontal scalability

## Role & Expertise

### Primary Role
Act as an intelligent intermediary between users and the todo management system, translating natural language requests into structured MCP tool calls.

### Domain Expertise
- **Natural Language Processing**: Parse and understand varied user expressions for task management
- **Intent Recognition**: Classify user requests into actionable intents (add, list, complete, delete, update)
- **Entity Extraction**: Identify task details (title, description, priority, due date, tags, category)
- **Conversational AI**: Maintain context across multi-turn conversations
- **MCP Protocol**: Execute tool calls according to MCP specification

### Technical Expertise
- OpenAI Agents SDK integration
- FastAPI backend communication
- PostgreSQL (Neon) database operations via API
- JWT authentication flow awareness
- RESTful API consumption

## Responsibilities

### 1. Intent Classification
Analyze user input to determine the intended action:

| Intent | Example Phrases |
|--------|-----------------|
| `add_task` | "Add a task to...", "Create a new todo...", "I need to..." |
| `list_tasks` | "Show my tasks", "What's on my list?", "List all todos" |
| `complete_task` | "Mark X as done", "Complete task...", "I finished..." |
| `delete_task` | "Delete task...", "Remove...", "Get rid of..." |
| `update_task` | "Change X to...", "Update the...", "Rename task..." |
| `search_tasks` | "Find tasks about...", "Search for..." |
| `filter_tasks` | "Show high priority", "Tasks due today" |

### 2. Entity Extraction
Extract structured data from natural language:

```python
# Example entity extraction schema
class TaskEntities:
    title: str | None           # "Buy groceries"
    description: str | None     # "Get milk, eggs, and bread"
    priority: str | None        # "high", "medium", "low"
    due_date: str | None        # ISO format or relative ("tomorrow")
    category: str | None        # "work", "personal", "shopping"
    tags: list[str] | None      # ["urgent", "home"]
    status: str | None          # "pending", "in_progress", "completed"
```

### 3. MCP Tool Orchestration
Execute appropriate MCP tools based on classified intent:

```python
async def handle_user_message(message: str, user_id: str) -> str:
    """Process user message and return response."""

    # 1. Classify intent
    intent = await classify_intent(message)

    # 2. Extract entities
    entities = await extract_entities(message, intent)

    # 3. Execute MCP tool
    result = await execute_mcp_tool(intent, entities, user_id)

    # 4. Generate natural language response
    response = await generate_response(result, intent)

    return response
```

### 4. Conversation State Management
Maintain conversation context in database for multi-turn interactions:

```python
class ConversationState:
    conversation_id: str
    user_id: str
    messages: list[dict]        # [{role: "user"|"assistant", content: str}]
    context: dict               # Extracted context from conversation
    last_intent: str | None
    last_entities: dict | None
    created_at: datetime
    updated_at: datetime
```

## Architecture Patterns

### Stateless Agent Design
```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (ChatKit)                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Server (Stateless)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Intent    │  │   Entity    │  │      MCP Tool           │  │
│  │ Classifier  │──▶│  Extractor  │──▶│    Orchestrator        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│      MCP Server (Tools)       │  │   Neon PostgreSQL (State)    │
│  - add_task                   │  │  - conversations             │
│  - list_tasks                 │  │  - messages                  │
│  - complete_task              │  │  - context                   │
│  - delete_task                │  │  - tasks (via Phase II API)  │
│  - update_task                │  └──────────────────────────────┘
└──────────────────────────────┘
```

### Request Flow
1. User sends message via ChatKit frontend
2. Agent server receives message (stateless)
3. Load conversation context from DB
4. Classify intent using OpenAI
5. Extract entities from message
6. Execute appropriate MCP tool
7. Generate natural language response
8. Save updated conversation state to DB
9. Return response to frontend

## MCP Tool Specifications

### Tool: `add_task`
```json
{
  "name": "add_task",
  "description": "Create a new task for the user",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "Task title (required)"
      },
      "description": {
        "type": "string",
        "description": "Detailed task description"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "default": "medium"
      },
      "due_date": {
        "type": "string",
        "format": "date-time",
        "description": "ISO 8601 date-time"
      },
      "category": {
        "type": "string",
        "description": "Task category"
      },
      "tags": {
        "type": "array",
        "items": {"type": "string"}
      }
    },
    "required": ["title"]
  }
}
```

### Tool: `list_tasks`
```json
{
  "name": "list_tasks",
  "description": "Retrieve user's tasks with optional filters",
  "parameters": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["pending", "in_progress", "completed", "all"],
        "default": "all"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"]
      },
      "category": {
        "type": "string"
      },
      "due_before": {
        "type": "string",
        "format": "date-time"
      },
      "due_after": {
        "type": "string",
        "format": "date-time"
      },
      "limit": {
        "type": "integer",
        "default": 20,
        "maximum": 100
      }
    }
  }
}
```

### Tool: `complete_task`
```json
{
  "name": "complete_task",
  "description": "Mark a task as completed",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "ID of task to complete"
      },
      "task_title": {
        "type": "string",
        "description": "Title of task to complete (fuzzy match)"
      }
    }
  }
}
```

### Tool: `delete_task`
```json
{
  "name": "delete_task",
  "description": "Delete a task permanently",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "ID of task to delete"
      },
      "task_title": {
        "type": "string",
        "description": "Title of task to delete (fuzzy match)"
      },
      "confirm": {
        "type": "boolean",
        "description": "Confirmation flag",
        "default": false
      }
    }
  }
}
```

### Tool: `update_task`
```json
{
  "name": "update_task",
  "description": "Update an existing task",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "ID of task to update"
      },
      "task_title": {
        "type": "string",
        "description": "Title of task to update (fuzzy match)"
      },
      "updates": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "description": {"type": "string"},
          "priority": {"type": "string", "enum": ["low", "medium", "high"]},
          "due_date": {"type": "string", "format": "date-time"},
          "category": {"type": "string"},
          "tags": {"type": "array", "items": {"type": "string"}},
          "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]}
        }
      }
    },
    "required": ["updates"]
  }
}
```

## Agent Configuration

### OpenAI Agents SDK Setup
```python
from openai import OpenAI
from openai.types.beta import Assistant

# Agent configuration
AGENT_CONFIG = {
    "name": "Lumina Todo Assistant",
    "model": "gpt-4o-mini",
    "instructions": """You are Lumina, a helpful AI assistant for managing todo tasks.

Your capabilities:
- Add new tasks with titles, descriptions, priorities, due dates, categories, and tags
- List tasks with various filters (status, priority, category, date range)
- Mark tasks as completed
- Delete tasks (with confirmation)
- Update existing tasks

Guidelines:
1. Be concise but friendly
2. Confirm destructive actions before executing
3. Provide helpful summaries after operations
4. Ask for clarification when intent is ambiguous
5. Use the user's timezone for date/time references
6. Format task lists in a readable manner

When users mention relative dates like "tomorrow" or "next week", convert them to specific dates.
When priority is not specified, default to "medium".
""",
    "tools": [
        {"type": "function", "function": ADD_TASK_TOOL},
        {"type": "function", "function": LIST_TASKS_TOOL},
        {"type": "function", "function": COMPLETE_TASK_TOOL},
        {"type": "function", "function": DELETE_TASK_TOOL},
        {"type": "function", "function": UPDATE_TASK_TOOL},
    ]
}
```

### Environment Variables
```bash
# chatbot/.env.example
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Phase II API connection
API_BASE_URL=https://neelumghazal-lumina-todo-api.hf.space/api
JWT_SECRET=<shared-secret-with-phase2>

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/chatbot?sslmode=require

# MCP Server
MCP_SERVER_PORT=8001
```

### FastAPI Integration
```python
# chatbot/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Lumina Chatbot API",
    description="AI-powered chatbot for todo management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lumina-todo.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tool_calls: list[dict] | None = None

@app.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    user_id: str = Depends(get_current_user)
):
    """Process a chat message and return AI response."""
    response = await process_chat_message(
        message=message.message,
        user_id=user_id,
        conversation_id=message.conversation_id
    )
    return response
```

## Quality Standards

### Response Quality
- **Accuracy**: Tool calls must accurately reflect user intent
- **Completeness**: Extract all available entities from user input
- **Clarity**: Responses should be clear and actionable
- **Confirmation**: Always confirm destructive actions

### Error Handling
```python
class ChatbotError(Exception):
    """Base exception for chatbot errors."""
    pass

class IntentClassificationError(ChatbotError):
    """Failed to classify user intent."""
    pass

class EntityExtractionError(ChatbotError):
    """Failed to extract entities from message."""
    pass

class MCPToolError(ChatbotError):
    """MCP tool execution failed."""
    pass

async def handle_error(error: ChatbotError) -> str:
    """Generate user-friendly error response."""
    if isinstance(error, IntentClassificationError):
        return "I'm not sure what you'd like to do. Could you rephrase that?"
    elif isinstance(error, EntityExtractionError):
        return "I understood your request but need more details. What task are you referring to?"
    elif isinstance(error, MCPToolError):
        return "I encountered an issue while processing your request. Please try again."
    return "Something went wrong. Please try again."
```

### Performance Requirements
- **Latency**: < 2s for simple queries, < 5s for complex operations
- **Throughput**: Support 100 concurrent conversations
- **Availability**: 99.9% uptime target

## Integration Points

### Phase II API Integration
```python
import httpx

class PhaseIIClient:
    """Client for Phase II Task API."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    async def create_task(self, task_data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/tasks",
                json=task_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def list_tasks(self, filters: dict = None) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tasks",
                params=filters,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    # ... additional methods
```

### Frontend ChatKit Integration
```typescript
// Frontend integration example
import { useChat } from '@ai-sdk/react';

export function ChatInterface() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    headers: {
      Authorization: `Bearer ${getToken()}`
    }
  });

  return (
    <div className="chat-container">
      <MessageList messages={messages} />
      <ChatInput
        value={input}
        onChange={handleInputChange}
        onSubmit={handleSubmit}
        disabled={isLoading}
      />
    </div>
  );
}
```

## Reporting & Metrics

### Conversation Analytics
- Total conversations per day
- Average messages per conversation
- Intent distribution
- Tool call success rate
- Average response time

### Logging Format
```python
import structlog

logger = structlog.get_logger()

# Log conversation events
logger.info(
    "chat_message_processed",
    user_id=user_id,
    conversation_id=conversation_id,
    intent=classified_intent,
    entities=extracted_entities,
    tool_calls=tool_calls,
    response_time_ms=response_time,
    success=True
)
```

## Example Usage

### Conversation Flow
```
User: Add a task to buy groceries tomorrow
Assistant: I've created a new task "Buy groceries" due tomorrow (Feb 7, 2026).
           Is there anything else you'd like to add to it?

User: Yes, make it high priority and add tags for shopping and home
Assistant: Done! I've updated "Buy groceries" to high priority with tags: shopping, home.

User: Show me all my high priority tasks
Assistant: Here are your high priority tasks:
           1. Buy groceries - Due: Feb 7, 2026 [shopping, home]
           2. Submit report - Due: Feb 10, 2026 [work]
           3. Call dentist - Due: Feb 8, 2026 [health]

User: Mark buy groceries as done
Assistant: Great job! I've marked "Buy groceries" as completed.
```

### Multi-turn Context
```
User: Create a task for the meeting
Assistant: Sure! What should I call this meeting task, and when is it scheduled?

User: Project kickoff, next Monday at 2pm
Assistant: I've created "Project kickoff" scheduled for Monday, Feb 10, 2026 at 2:00 PM.
           Would you like to add a description or set a priority?

User: High priority, add description "Discuss Q1 goals with team"
Assistant: Updated! "Project kickoff" is now high priority with the description added.
```

## File Structure

```
chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core.py          # Agent orchestration
│   │   ├── intents.py       # Intent classification
│   │   ├── entities.py      # Entity extraction
│   │   └── responses.py     # Response generation
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py        # MCP server implementation
│   │   ├── tools.py         # Tool definitions
│   │   └── handlers.py      # Tool handlers
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py        # SQLModel definitions
│   │   ├── database.py      # Database connection
│   │   └── repositories.py  # Data access layer
│   └── api/
│       ├── __init__.py
│       ├── routes.py        # API routes
│       └── deps.py          # Dependencies
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_mcp.py
│   └── test_api.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Related Resources

- **Phase II API**: `api/` - Task CRUD operations
- **Frontend**: `frontend/` - Vercel-deployed Next.js app
- **MCP Builder Skill**: `.claude/skills/mcp_builder/SKILL.md`
- **Spec**: `specs/005-phase3-chatbot/spec.md` (to be created)
