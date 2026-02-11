---
name: "openai_agents_sdk"
description: "Build conversational AI agents using OpenAI Agents SDK with tool integration"
version: "1.0.0"
---

# OpenAI Agents SDK Skill

## When to Use
- Creating OpenAI agent configurations
- Integrating external tools (MCP, functions)
- Designing agent instructions
- Building conversation flows

## Process Steps

### 1. Agent Design
- Define agent personality and tone
- List required capabilities
- Map to available tools (MCP from Part 1)

### 2. Implementation
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

agent = client.beta.assistants.create(
    name="Todo Assistant",
    instructions="""You help users manage tasks.
    Use tools to add/list/update tasks.
    Be friendly and conversational.""",
    model="gpt-4o",
    tools=[...]
)
```

### 3. Tool Integration
```python
mcp_tools = await fetch_mcp_tools("http://localhost:8001/mcp/tools")
openai_functions = convert_mcp_to_openai_functions(mcp_tools)
```

### 4. Conversation Handling
```python
thread = client.beta.threads.create()

client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Add task to buy groceries"
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=agent.id
)

if run.status == "requires_action":
    # Call MCP tools and submit outputs
```

## Quality Criteria
- Agent responds naturally
- Tools called correctly
- Errors handled gracefully
- Context maintained across turns
- Fast responses (<2s)

## Example Flow
User: "show my tasks"

1. Agent receives message
2. Identifies intent: list_tasks
3. Calls MCP tool
4. Formats response
5. Returns result to user

## MCP Tool Mapping

| User Intent | MCP Tool | Parameters |
|-------------|----------|------------|
| "Add task X" | `add_task` | `title`, `description` |
| "Show tasks" | `list_tasks` | `status` filter |
| "Complete task N" | `complete_task` | `task_id` |
| "Delete task N" | `delete_task` | `task_id` |
| "Update task N" | `update_task` | `task_id`, fields |

## Error Handling

### Tool Not Found
```python
if tool_name not in available_tools:
    return "I can't do that right now. Try: add, list, complete, delete, or update tasks."
```

### Task Not Found
```python
if error_code == "TASK_NOT_FOUND":
    return f"I couldn't find task {task_id}. Use 'show my tasks' to see available tasks."
```

### Validation Error
```python
if error_code == "VALIDATION_ERROR":
    return "I need more information. What would you like to call this task?"
```

## Testing

### Unit Tests
- Intent extraction accuracy
- Tool parameter mapping
- Response formatting

### Integration Tests
- Full conversation flows
- Multi-turn dialogues
- Error recovery scenarios
