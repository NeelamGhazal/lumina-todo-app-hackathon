# MCP Builder Skill

> Build Model Context Protocol (MCP) server tools for todo task management operations.

## Skill Identity

| Property | Value |
|----------|-------|
| **Name** | `mcp_builder` |
| **Type** | Development Skill |
| **Version** | 1.0.0 |
| **Phase** | Phase III - AI Chatbot Integration |

## Description

The MCP Builder skill enables the creation of Model Context Protocol (MCP) server tools that expose todo management operations as callable functions. These tools are designed to be stateless, with all persistence handled by the database layer (Neon PostgreSQL via Phase II API).

**Key Capabilities:**
- Design MCP-compliant tool specifications
- Implement stateless tool handlers
- Integrate with Phase II Task API
- Handle authentication and authorization
- Validate inputs and handle errors gracefully

## When to Use This Skill

Use the `mcp_builder` skill when you need to:

1. **Create new MCP tools** for todo management operations
2. **Extend existing tools** with new parameters or functionality
3. **Integrate external APIs** as MCP tools
4. **Debug or fix** MCP tool implementation issues
5. **Validate tool specifications** against MCP protocol
6. **Generate tool documentation** for the agent

### Trigger Phrases
- "Create an MCP tool for..."
- "Add a new tool to the MCP server..."
- "Implement the X tool for the chatbot..."
- "Expose X functionality as an MCP tool..."

## Process Steps

### Step 1: Define Tool Specification

Create a JSON Schema-compliant tool definition:

```python
from typing import TypedDict, Literal

class ToolParameter(TypedDict):
    type: str
    description: str
    enum: list[str] | None
    default: any | None

class ToolDefinition(TypedDict):
    name: str
    description: str
    parameters: dict

def define_tool(
    name: str,
    description: str,
    parameters: dict[str, ToolParameter],
    required: list[str] = None
) -> ToolDefinition:
    """Define an MCP tool specification."""
    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": parameters,
            "required": required or []
        }
    }
```

### Step 2: Implement Tool Handler

Create the stateless handler function:

```python
from typing import Any
from pydantic import BaseModel, ValidationError

class ToolResult(BaseModel):
    success: bool
    data: Any | None = None
    error: str | None = None

async def execute_tool(
    tool_name: str,
    parameters: dict,
    user_context: dict
) -> ToolResult:
    """Execute an MCP tool with the given parameters."""
    try:
        handler = get_tool_handler(tool_name)
        result = await handler(parameters, user_context)
        return ToolResult(success=True, data=result)
    except ValidationError as e:
        return ToolResult(success=False, error=f"Invalid parameters: {e}")
    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

### Step 3: Register with MCP Server

Register the tool with the MCP server:

```python
from mcp.server import Server
from mcp.types import Tool

server = Server("lumina-todo-mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="add_task",
            description="Create a new task",
            inputSchema=ADD_TASK_SCHEMA
        ),
        Tool(
            name="list_tasks",
            description="List tasks with filters",
            inputSchema=LIST_TASKS_SCHEMA
        ),
        # ... additional tools
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """Handle tool execution requests."""
    result = await execute_tool(name, arguments, get_user_context())
    return [TextContent(type="text", text=json.dumps(result.model_dump()))]
```

### Step 4: Validate and Test

Validate tool implementation:

```python
import pytest
from httpx import AsyncClient

@pytest.fixture
async def mcp_client():
    """Create MCP test client."""
    async with AsyncClient(base_url="http://localhost:8001") as client:
        yield client

async def test_add_task_tool(mcp_client):
    """Test add_task tool execution."""
    result = await mcp_client.post("/tools/add_task", json={
        "title": "Test task",
        "priority": "high"
    })
    assert result.status_code == 200
    data = result.json()
    assert data["success"] is True
    assert "id" in data["data"]
```

## Tool Design & Implementation

### Core MCP Tools

#### 1. `add_task` Tool

```python
# Tool Definition
ADD_TASK_TOOL = {
    "name": "add_task",
    "description": "Create a new task for the user. Returns the created task with its ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The task title (required, max 200 chars)",
                "maxLength": 200
            },
            "description": {
                "type": "string",
                "description": "Detailed description of the task",
                "maxLength": 2000
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "default": "medium",
                "description": "Task priority level"
            },
            "due_date": {
                "type": "string",
                "format": "date-time",
                "description": "Due date in ISO 8601 format"
            },
            "category": {
                "type": "string",
                "description": "Task category (e.g., work, personal, shopping)"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of tags for the task"
            }
        },
        "required": ["title"]
    }
}

# Handler Implementation
async def handle_add_task(params: dict, user_context: dict) -> dict:
    """Handle add_task tool execution."""
    from datetime import datetime

    # Validate and prepare task data
    task_data = {
        "title": params["title"],
        "description": params.get("description"),
        "priority": params.get("priority", "medium"),
        "due_date": params.get("due_date"),
        "category": params.get("category"),
        "tags": params.get("tags", []),
        "status": "pending"
    }

    # Call Phase II API
    api_client = get_phase2_client(user_context["token"])
    created_task = await api_client.create_task(task_data)

    return {
        "id": created_task["id"],
        "title": created_task["title"],
        "priority": created_task["priority"],
        "due_date": created_task.get("due_date"),
        "message": f"Task '{created_task['title']}' created successfully"
    }
```

#### 2. `list_tasks` Tool

```python
# Tool Definition
LIST_TASKS_TOOL = {
    "name": "list_tasks",
    "description": "Retrieve the user's tasks with optional filters. Returns a list of tasks.",
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "completed", "all"],
                "default": "all",
                "description": "Filter by task status"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Filter by priority level"
            },
            "category": {
                "type": "string",
                "description": "Filter by category name"
            },
            "due_before": {
                "type": "string",
                "format": "date-time",
                "description": "Filter tasks due before this date"
            },
            "due_after": {
                "type": "string",
                "format": "date-time",
                "description": "Filter tasks due after this date"
            },
            "search": {
                "type": "string",
                "description": "Search in task titles and descriptions"
            },
            "limit": {
                "type": "integer",
                "default": 20,
                "minimum": 1,
                "maximum": 100,
                "description": "Maximum number of tasks to return"
            },
            "offset": {
                "type": "integer",
                "default": 0,
                "minimum": 0,
                "description": "Number of tasks to skip"
            }
        }
    }
}

# Handler Implementation
async def handle_list_tasks(params: dict, user_context: dict) -> dict:
    """Handle list_tasks tool execution."""

    # Build filter parameters
    filters = {}
    if params.get("status") and params["status"] != "all":
        filters["status"] = params["status"]
    if params.get("priority"):
        filters["priority"] = params["priority"]
    if params.get("category"):
        filters["category"] = params["category"]
    if params.get("due_before"):
        filters["due_before"] = params["due_before"]
    if params.get("due_after"):
        filters["due_after"] = params["due_after"]
    if params.get("search"):
        filters["search"] = params["search"]

    filters["limit"] = params.get("limit", 20)
    filters["offset"] = params.get("offset", 0)

    # Call Phase II API
    api_client = get_phase2_client(user_context["token"])
    tasks = await api_client.list_tasks(filters)

    return {
        "tasks": [
            {
                "id": t["id"],
                "title": t["title"],
                "priority": t["priority"],
                "status": t["status"],
                "due_date": t.get("due_date"),
                "category": t.get("category"),
                "tags": t.get("tags", [])
            }
            for t in tasks
        ],
        "count": len(tasks),
        "has_more": len(tasks) == filters["limit"]
    }
```

#### 3. `complete_task` Tool

```python
# Tool Definition
COMPLETE_TASK_TOOL = {
    "name": "complete_task",
    "description": "Mark a task as completed. Can identify task by ID or title (fuzzy match).",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The unique ID of the task to complete"
            },
            "task_title": {
                "type": "string",
                "description": "The title of the task (uses fuzzy matching)"
            }
        }
    }
}

# Handler Implementation
async def handle_complete_task(params: dict, user_context: dict) -> dict:
    """Handle complete_task tool execution."""
    api_client = get_phase2_client(user_context["token"])

    # Find task by ID or title
    task_id = params.get("task_id")
    if not task_id and params.get("task_title"):
        task = await find_task_by_title(
            api_client,
            params["task_title"]
        )
        if not task:
            return {
                "success": False,
                "error": f"No task found matching '{params['task_title']}'"
            }
        task_id = task["id"]

    if not task_id:
        return {
            "success": False,
            "error": "Please provide either task_id or task_title"
        }

    # Update task status
    updated_task = await api_client.update_task(task_id, {
        "status": "completed"
    })

    return {
        "success": True,
        "task_id": updated_task["id"],
        "title": updated_task["title"],
        "message": f"Task '{updated_task['title']}' marked as completed"
    }

async def find_task_by_title(client, title: str) -> dict | None:
    """Find a task by fuzzy title match."""
    from difflib import SequenceMatcher

    tasks = await client.list_tasks({"status": "pending", "limit": 100})

    best_match = None
    best_ratio = 0

    for task in tasks:
        ratio = SequenceMatcher(None, title.lower(), task["title"].lower()).ratio()
        if ratio > best_ratio and ratio > 0.6:  # 60% threshold
            best_ratio = ratio
            best_match = task

    return best_match
```

#### 4. `delete_task` Tool

```python
# Tool Definition
DELETE_TASK_TOOL = {
    "name": "delete_task",
    "description": "Permanently delete a task. Requires confirmation for safety.",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The unique ID of the task to delete"
            },
            "task_title": {
                "type": "string",
                "description": "The title of the task (uses fuzzy matching)"
            },
            "confirm": {
                "type": "boolean",
                "default": False,
                "description": "Set to true to confirm deletion"
            }
        }
    }
}

# Handler Implementation
async def handle_delete_task(params: dict, user_context: dict) -> dict:
    """Handle delete_task tool execution."""
    api_client = get_phase2_client(user_context["token"])

    # Find task
    task_id = params.get("task_id")
    task_title = None

    if not task_id and params.get("task_title"):
        task = await find_task_by_title(api_client, params["task_title"])
        if not task:
            return {
                "success": False,
                "error": f"No task found matching '{params['task_title']}'"
            }
        task_id = task["id"]
        task_title = task["title"]
    else:
        # Fetch task to get title
        task = await api_client.get_task(task_id)
        task_title = task["title"]

    if not task_id:
        return {
            "success": False,
            "error": "Please provide either task_id or task_title"
        }

    # Check confirmation
    if not params.get("confirm", False):
        return {
            "success": False,
            "requires_confirmation": True,
            "task_id": task_id,
            "title": task_title,
            "message": f"Are you sure you want to delete '{task_title}'? This cannot be undone."
        }

    # Delete task
    await api_client.delete_task(task_id)

    return {
        "success": True,
        "task_id": task_id,
        "title": task_title,
        "message": f"Task '{task_title}' has been deleted"
    }
```

#### 5. `update_task` Tool

```python
# Tool Definition
UPDATE_TASK_TOOL = {
    "name": "update_task",
    "description": "Update an existing task's properties.",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "The unique ID of the task to update"
            },
            "task_title": {
                "type": "string",
                "description": "The title of the task (uses fuzzy matching)"
            },
            "updates": {
                "type": "object",
                "description": "Fields to update",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"]
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "category": {"type": "string"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"]
                    }
                }
            }
        },
        "required": ["updates"]
    }
}

# Handler Implementation
async def handle_update_task(params: dict, user_context: dict) -> dict:
    """Handle update_task tool execution."""
    api_client = get_phase2_client(user_context["token"])

    # Find task
    task_id = params.get("task_id")
    if not task_id and params.get("task_title"):
        task = await find_task_by_title(api_client, params["task_title"])
        if not task:
            return {
                "success": False,
                "error": f"No task found matching '{params['task_title']}'"
            }
        task_id = task["id"]

    if not task_id:
        return {
            "success": False,
            "error": "Please provide either task_id or task_title"
        }

    updates = params.get("updates", {})
    if not updates:
        return {
            "success": False,
            "error": "No updates provided"
        }

    # Apply updates
    updated_task = await api_client.update_task(task_id, updates)

    # Build change summary
    changed_fields = list(updates.keys())

    return {
        "success": True,
        "task_id": updated_task["id"],
        "title": updated_task["title"],
        "updated_fields": changed_fields,
        "message": f"Task '{updated_task['title']}' updated: {', '.join(changed_fields)}"
    }
```

## Validation & Error Handling

### Input Validation

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class AddTaskInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[str] = Field("medium", pattern="^(low|medium|high)$")
    due_date: Optional[datetime] = None
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[list[str]] = Field(default_factory=list)

    @validator("tags")
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return v

class ListTasksInput(BaseModel):
    status: Optional[str] = Field("all", pattern="^(pending|in_progress|completed|all)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    category: Optional[str] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    search: Optional[str] = Field(None, max_length=100)
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
```

### Error Taxonomy

```python
from enum import Enum

class MCPErrorCode(Enum):
    INVALID_PARAMETERS = "invalid_parameters"
    TASK_NOT_FOUND = "task_not_found"
    PERMISSION_DENIED = "permission_denied"
    API_ERROR = "api_error"
    RATE_LIMITED = "rate_limited"
    INTERNAL_ERROR = "internal_error"

class MCPError(Exception):
    def __init__(self, code: MCPErrorCode, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "error": True,
            "code": self.code.value,
            "message": self.message,
            "details": self.details
        }
```

## Output Format

### Successful Response

```json
{
  "success": true,
  "data": {
    "id": 123,
    "title": "Buy groceries",
    "priority": "high",
    "status": "pending",
    "due_date": "2026-02-07T17:00:00Z"
  },
  "message": "Task 'Buy groceries' created successfully"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "task_not_found",
    "message": "No task found matching 'groceres'",
    "details": {
      "search_term": "groceres",
      "suggestions": ["Buy groceries", "Get groceries for party"]
    }
  }
}
```

### Confirmation Required Response

```json
{
  "success": false,
  "requires_confirmation": true,
  "task_id": 123,
  "title": "Important project",
  "message": "Are you sure you want to delete 'Important project'? This cannot be undone."
}
```

## Quality Criteria

### Tool Design Checklist
- [ ] Clear, descriptive tool name (verb_noun format)
- [ ] Comprehensive description for LLM understanding
- [ ] All parameters documented with types and descriptions
- [ ] Required vs optional parameters clearly marked
- [ ] Sensible default values provided
- [ ] Input validation with meaningful error messages
- [ ] Idempotent where possible
- [ ] Handles edge cases gracefully

### Implementation Checklist
- [ ] Stateless handler (no local state)
- [ ] All persistence via Phase II API
- [ ] Proper authentication propagation
- [ ] Comprehensive error handling
- [ ] Logging for debugging and monitoring
- [ ] Unit tests covering happy path and edge cases
- [ ] Integration tests with Phase II API

### Security Checklist
- [ ] User can only access own tasks
- [ ] Input sanitization for all parameters
- [ ] Rate limiting implemented
- [ ] No sensitive data in logs
- [ ] Confirmation required for destructive actions

## MCP Server Implementation

### Complete Server Setup

```python
# chatbot/app/mcp/server.py
import json
import logging
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .tools import (
    ADD_TASK_TOOL, LIST_TASKS_TOOL, COMPLETE_TASK_TOOL,
    DELETE_TASK_TOOL, UPDATE_TASK_TOOL
)
from .handlers import (
    handle_add_task, handle_list_tasks, handle_complete_task,
    handle_delete_task, handle_update_task
)

logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("lumina-todo-mcp")

# Tool registry
TOOLS = {
    "add_task": (ADD_TASK_TOOL, handle_add_task),
    "list_tasks": (LIST_TASKS_TOOL, handle_list_tasks),
    "complete_task": (COMPLETE_TASK_TOOL, handle_complete_task),
    "delete_task": (DELETE_TASK_TOOL, handle_delete_task),
    "update_task": (UPDATE_TASK_TOOL, handle_update_task),
}

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return all available MCP tools."""
    return [
        Tool(
            name=name,
            description=tool_def["description"],
            inputSchema=tool_def["parameters"]
        )
        for name, (tool_def, _) in TOOLS.items()
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute the requested tool."""
    if name not in TOOLS:
        error_result = {
            "success": False,
            "error": f"Unknown tool: {name}"
        }
        return [TextContent(type="text", text=json.dumps(error_result))]

    _, handler = TOOLS[name]

    try:
        # Get user context from request (set by middleware)
        user_context = get_current_user_context()

        # Execute handler
        result = await handler(arguments, user_context)

        logger.info(f"Tool {name} executed successfully", extra={
            "tool": name,
            "arguments": arguments,
            "user_id": user_context.get("user_id")
        })

        return [TextContent(type="text", text=json.dumps(result))]

    except MCPError as e:
        logger.warning(f"Tool {name} returned error", extra={
            "tool": name,
            "error": e.to_dict()
        })
        return [TextContent(type="text", text=json.dumps(e.to_dict()))]

    except Exception as e:
        logger.exception(f"Tool {name} failed with unexpected error")
        error_result = {
            "success": False,
            "error": f"Internal error: {str(e)}"
        }
        return [TextContent(type="text", text=json.dumps(error_result))]

async def run_mcp_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_mcp_server())
```

## Example MCP Tool Function

### Complete Example: Search Tasks Tool

```python
# Additional tool example: search_tasks
SEARCH_TASKS_TOOL = {
    "name": "search_tasks",
    "description": "Search for tasks by keyword in title, description, or tags",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (searches title, description, tags)",
                "minLength": 1,
                "maxLength": 100
            },
            "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "completed", "all"],
                "default": "all"
            },
            "limit": {
                "type": "integer",
                "default": 10,
                "minimum": 1,
                "maximum": 50
            }
        },
        "required": ["query"]
    }
}

async def handle_search_tasks(params: dict, user_context: dict) -> dict:
    """Search tasks by keyword."""
    from difflib import SequenceMatcher

    api_client = get_phase2_client(user_context["token"])
    query = params["query"].lower()
    status_filter = params.get("status", "all")
    limit = params.get("limit", 10)

    # Fetch all tasks (with status filter)
    filters = {"limit": 100}
    if status_filter != "all":
        filters["status"] = status_filter

    all_tasks = await api_client.list_tasks(filters)

    # Score and rank tasks by relevance
    scored_tasks = []
    for task in all_tasks:
        title_score = SequenceMatcher(
            None, query, task["title"].lower()
        ).ratio()

        desc_score = 0
        if task.get("description"):
            desc_score = SequenceMatcher(
                None, query, task["description"].lower()
            ).ratio() * 0.8  # Weight description less

        tag_score = 0
        for tag in task.get("tags", []):
            if query in tag.lower():
                tag_score = max(tag_score, 0.9)

        # Check for exact substring match
        if query in task["title"].lower():
            title_score = max(title_score, 0.95)

        total_score = max(title_score, desc_score, tag_score)

        if total_score > 0.3:  # Minimum relevance threshold
            scored_tasks.append((total_score, task))

    # Sort by score descending
    scored_tasks.sort(key=lambda x: x[0], reverse=True)

    # Return top results
    results = [
        {
            "id": task["id"],
            "title": task["title"],
            "priority": task["priority"],
            "status": task["status"],
            "due_date": task.get("due_date"),
            "relevance": round(score, 2)
        }
        for score, task in scored_tasks[:limit]
    ]

    return {
        "success": True,
        "query": params["query"],
        "results": results,
        "count": len(results),
        "message": f"Found {len(results)} task(s) matching '{params['query']}'"
    }
```

## Related Resources

- **Chatbot Agent**: `.claude/agents/chatbot_agent.md`
- **Phase II API**: `api/app/routers/tasks.py`
- **MCP Protocol**: https://modelcontextprotocol.io
- **OpenAI Agents SDK**: https://platform.openai.com/docs/agents
