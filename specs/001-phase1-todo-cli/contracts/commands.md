# Command Contracts: Phase I - Professional Todo Console Application

**Date**: 2026-01-26
**Branch**: `001-phase1-todo-cli`

## Overview

This document defines the CLI command interface contracts for Phase I.

---

## Command Format

**Syntax**: `/<command> [arguments]`

**Rules**:
- All commands start with `/` prefix (mandatory)
- Commands are case-insensitive (`/LIST` = `/list` = `/List`)
- Arguments are space-separated
- Quoted strings preserve spaces: `/add "Buy groceries tomorrow"`

---

## Commands

### /help

**Description**: Display formatted help screen with all commands

**Syntax**: `/help`

**Arguments**: None

**Output**:
```
╭─────────────────────────────────────────────────────────────╮
│                      📋 Todo CLI Help                        │
╰─────────────────────────────────────────────────────────────╯

  Task Management
  ───────────────
  /add              Interactive wizard to create a task
  /add <text>       Quick add with natural language
  /list             Show all tasks in a table
  /show <id>        View task details
  /update <id>      Edit a task
  /complete <id>    Toggle task completion
  /delete <id>      Remove a task

  Search & Stats
  ──────────────
  /search <query>   Search tasks by keyword
  /stats            View task statistics

  Application
  ───────────
  /help             Show this help screen
  /exit             Exit the application

  Examples
  ────────
  /add Buy milk tomorrow #shopping high
  /show a1b2c3
  /search groceries
```

**Error Handling**: N/A (always succeeds)

---

### /add

**Description**: Create a new task (wizard or NLP mode)

**Syntax**:
- `/add` - Launch interactive wizard
- `/add <natural language text>` - Quick add with NLP parsing

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| text | string | No | Natural language task description |

**Wizard Mode** (no arguments):

Interactive prompts for each field:
1. Title (required): "Enter task title:"
2. Description (optional): "Enter description (press Enter to skip):"
3. Priority (optional): "Select priority: [h]igh, [m]edium, [l]ow"
4. Category (optional): "Select category: [w]ork, [p]ersonal, [s]hopping, [h]ealth, [o]ther"
5. Tags (optional): "Enter tags (comma-separated, press Enter to skip):"
6. Due date (optional): "Enter due date (YYYY-MM-DD or 'tomorrow', press Enter to skip):"
7. Due time (optional): "Enter due time (HH:MM or 'morning', press Enter to skip):"

**NLP Mode** (with arguments):

Parse natural language to extract:
- Title: Remaining text after extraction
- Priority: `urgent`, `high`, `medium`, `low`
- Category: `#work`, `#personal`, `#shopping`, `#health`, `#other`
- Due date: `today`, `tomorrow`, `next monday`, `friday`, `YYYY-MM-DD`
- Due time: `morning`, `afternoon`, `evening`, `HH:MM`

**Examples**:
```
/add                          # Wizard mode
/add Buy milk                 # Simple task
/add Buy milk tomorrow        # Task with due date
/add Buy milk tomorrow #shopping high   # Full NLP parsing
/add "Meeting with team" next monday morning #work
```

**Output** (success):
```
╭─────────────────────── Task Created ────────────────────────╮
│  ID: a1b2c3                                                 │
│  Title: Buy milk                                            │
│  Priority: high                                             │
│  Category: shopping                                         │
│  Due: 2026-01-27                                           │
╰─────────────────────────────────────────────────────────────╯
```

**Error Handling**:
| Error | Message |
|-------|---------|
| Empty title | "Title is required. Please enter a task title." |
| Title too long | "Title must be 200 characters or less." |

---

### /list

**Description**: Display all tasks in a formatted table

**Syntax**: `/list`

**Arguments**: None

**Output** (with tasks):
```
╭──────────────────────────────────────────────────────────────────────────────╮
│                                📋 All Tasks                                   │
╰──────────────────────────────────────────────────────────────────────────────╯

┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID     ┃ Title                ┃ Status ┃ Priority ┃ Category ┃ Due Date   ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ a1b2c3 │ Buy groceries        │ ✗      │ 🔴 high  │ shopping │ 2026-01-27 │
│ x9y8z7 │ Finish report        │ ✓      │ 🟡 medium│ work     │ -          │
│ p4q5r6 │ Call doctor          │ ✗      │ 🟢 low   │ health   │ 2026-01-28 │
└────────┴──────────────────────┴────────┴──────────┴──────────┴────────────┘

Total: 3 tasks (1 completed, 2 pending)
```

**Output** (empty state):
```
╭─────────────────────────────────────────────────────────────╮
│                      📋 No Tasks Yet                         │
│                                                              │
│  Get started by adding your first task:                     │
│  /add Buy groceries tomorrow                                │
│                                                              │
│  Or use the interactive wizard:                             │
│  /add                                                       │
╰─────────────────────────────────────────────────────────────╯
```

**Error Handling**: N/A (always succeeds, may show empty state)

---

### /show <id>

**Description**: Display detailed view of a single task

**Syntax**: `/show <id>`

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | Yes | 6-character task ID |

**Output** (success):
```
╭─────────────────────── Task Details ────────────────────────╮
│                                                              │
│  ID:          a1b2c3                                        │
│  Title:       Buy groceries for dinner party                │
│  Description: Need vegetables, chicken, and dessert         │
│                                                              │
│  Priority:    🔴 high                                       │
│  Category:    🛒 shopping                                   │
│  Tags:        food, party, weekend                          │
│                                                              │
│  Due Date:    2026-01-28                                    │
│  Due Time:    14:00                                         │
│  Status:      ✗ Pending                                     │
│                                                              │
│  Created:     2026-01-26 10:30                              │
╰─────────────────────────────────────────────────────────────╯
```

**Error Handling**:
| Error | Message |
|-------|---------|
| Missing ID | "Please provide a task ID. Usage: /show <id>" |
| Invalid ID | "Task 'xyz123' not found. Use /list to see all tasks." |

---

### /update <id>

**Description**: Update task fields with current values shown

**Syntax**: `/update <id>`

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | Yes | 6-character task ID |

**Behavior**:

1. Display current task values
2. Prompt for each field with current value shown
3. Press Enter to keep current value
4. Show before/after comparison on completion

**Prompts**:
```
Updating task a1b2c3...

Title [Buy groceries]: Buy groceries and snacks
Description []: Need chips and drinks too
Priority [high]: (press Enter to keep)
Category [shopping]: (press Enter to keep)
Tags [food, party]: food, party, snacks
Due date [2026-01-28]: 2026-01-29
Due time [14:00]: 15:00
```

**Output** (success):
```
╭───────────────────── Task Updated ──────────────────────╮
│                                                          │
│  Changed fields:                                         │
│  • Title: Buy groceries → Buy groceries and snacks      │
│  • Description: (empty) → Need chips and drinks too     │
│  • Tags: food, party → food, party, snacks              │
│  • Due date: 2026-01-28 → 2026-01-29                    │
│  • Due time: 14:00 → 15:00                              │
│                                                          │
╰─────────────────────────────────────────────────────────╯
```

**Error Handling**:
| Error | Message |
|-------|---------|
| Missing ID | "Please provide a task ID. Usage: /update <id>" |
| Invalid ID | "Task 'xyz123' not found. Use /list to see all tasks." |

---

### /complete <id>

**Description**: Toggle task completion status

**Syntax**: `/complete <id>`

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | Yes | 6-character task ID |

**Output** (marking complete):
```
✓ Task 'Buy groceries' marked as completed!
```

**Output** (marking pending):
```
✗ Task 'Buy groceries' marked as pending.
```

**Error Handling**:
| Error | Message |
|-------|---------|
| Missing ID | "Please provide a task ID. Usage: /complete <id>" |
| Invalid ID | "Task 'xyz123' not found. Use /list to see all tasks." |

---

### /delete <id>

**Description**: Delete a task with confirmation

**Syntax**: `/delete <id>`

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | Yes | 6-character task ID |

**Confirmation Prompt**:
```
Are you sure you want to delete 'Buy groceries'? [y/N]:
```

**Output** (confirmed):
```
🗑️  Task 'Buy groceries' deleted.
```

**Output** (cancelled):
```
Deletion cancelled.
```

**Error Handling**:
| Error | Message |
|-------|---------|
| Missing ID | "Please provide a task ID. Usage: /delete <id>" |
| Invalid ID | "Task 'xyz123' not found. Use /list to see all tasks." |

---

### /search <query>

**Description**: Search tasks by keyword across all text fields

**Syntax**: `/search <query>`

**Arguments**:
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| query | string | Yes | Search keyword(s) |

**Search Fields**: title, description, tags, category

**Output** (matches found):
```
╭─────────────────── Search Results: "groceries" ───────────────────╮

┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ ID     ┃ Title                ┃ Status ┃ Priority ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ a1b2c3 │ Buy [groceries]      │ ✗      │ 🔴 high  │
│ m7n8o9 │ Get [groceries] list │ ✓      │ 🟢 low   │
└────────┴──────────────────────┴────────┴──────────┘

Found 2 tasks matching "groceries"
```

**Output** (no matches):
```
╭─────────────────────────────────────────────────────────────╮
│                   🔍 No Results Found                        │
│                                                              │
│  No tasks matching "xyz" found.                             │
│                                                              │
│  Try:                                                        │
│  • Using different keywords                                  │
│  • Checking spelling                                         │
│  • Using /list to see all tasks                             │
╰─────────────────────────────────────────────────────────────╯
```

**Error Handling**:
| Error | Message |
|-------|---------|
| Missing query | "Please provide a search term. Usage: /search <query>" |

---

### /stats

**Description**: Display task statistics dashboard

**Syntax**: `/stats`

**Arguments**: None

**Output** (with tasks):
```
╭───────────────────────── 📊 Task Statistics ─────────────────────────╮
│                                                                       │
│  Overview                                                             │
│  ────────                                                             │
│  Total Tasks:     15                                                  │
│  Completed:       6  (40%)                                           │
│  Pending:         9  (60%)                                           │
│                                                                       │
│  Completion Progress                                                  │
│  ██████████░░░░░░░░░░░░░░░  40%                                      │
│                                                                       │
│  By Priority                                                          │
│  ───────────                                                          │
│  🔴 High:     5  ████████████                                        │
│  🟡 Medium:   7  ████████████████                                    │
│  🟢 Low:      3  ██████                                              │
│                                                                       │
│  By Category                                                          │
│  ───────────                                                          │
│  💼 Work:       6                                                    │
│  🏠 Personal:   4                                                    │
│  🛒 Shopping:   3                                                    │
│  ❤️  Health:     1                                                    │
│  📌 Other:      1                                                    │
│                                                                       │
╰──────────────────────────────────────────────────────────────────────╯
```

**Output** (no tasks):
```
╭─────────────────────────────────────────────────────────────╮
│                   📊 No Statistics Yet                       │
│                                                              │
│  Add some tasks to see your productivity stats!             │
│  /add                                                       │
╰─────────────────────────────────────────────────────────────╯
```

**Error Handling**: N/A (always succeeds)

---

### /exit

**Description**: Exit the application gracefully

**Syntax**: `/exit`

**Arguments**: None

**Output**:
```
👋 Goodbye! Your tasks will not be saved (in-memory mode).
```

**Behavior**: Clean shutdown, no confirmation (data is in-memory anyway)

**Error Handling**: N/A

---

## Unknown Command Handling

When user enters an unrecognized command:

```
╭─────────────────────────────────────────────────────────────╮
│  Unknown command: /xyz                                       │
│                                                              │
│  Type /help to see available commands.                      │
╰─────────────────────────────────────────────────────────────╯
```

---

## Input Without Slash Prefix

When user enters input without `/` prefix:

```
╭─────────────────────────────────────────────────────────────╮
│  Commands must start with /                                  │
│                                                              │
│  Examples:                                                   │
│  /add Buy groceries                                         │
│  /list                                                       │
│  /help                                                       │
╰─────────────────────────────────────────────────────────────╯
```
