# Todo CLI - Professional Task Management

A beautiful, Rich-powered command-line todo application built with Python 3.13+.

## Features

- Interactive task creation wizard with validation
- Natural language task input (e.g., `/add Buy groceries tomorrow #shopping urgent`)
- Color-coded priority and status indicators
- Search across all task fields
- Statistics dashboard with progress visualization
- All output styled with Rich panels, tables, and colors

## Installation

### Prerequisites

- Python 3.13 or higher
- [UV](https://docs.astral.sh/uv/) package manager

### Setup

```bash
cd backend
uv sync
```

## Usage

### Start the Application

```bash
uv run python -m src.main
```

Or directly:

```bash
cd backend
uv run python -m src
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Display all commands | `/help` |
| `/add` | Create a new task | `/add` (wizard) or `/add Buy milk tomorrow #shopping` |
| `/list` | Show all tasks | `/list` |
| `/show <id>` | View task details | `/show abc123` |
| `/update <id>` | Modify a task | `/update abc123` |
| `/complete <id>` | Toggle completion | `/complete abc123` |
| `/delete <id>` | Remove a task | `/delete abc123` |
| `/search <query>` | Find tasks | `/search groceries` |
| `/stats` | View statistics | `/stats` |
| `/exit` | Quit application | `/exit` |

### Natural Language Input

When using `/add` with arguments, the app parses:

- **Dates**: `today`, `tomorrow`, `next monday`, `2025-01-30`
- **Times**: `morning` (09:00), `afternoon` (14:00), `evening` (18:00), `14:30`
- **Priority**: `urgent`, `high`, `medium`, `low`
- **Category**: `#work`, `#personal`, `#shopping`, `#health`, `#other`

Example:
```
/add Finish report tomorrow morning #work urgent
```

## Development

### Run Tests

```bash
uv run pytest -v
```

### Test Coverage

```bash
uv run pytest --cov=src --cov-report=term-missing
```

### Project Structure

```
backend/
├── src/
│   ├── commands/       # Command handlers (add, list, show, etc.)
│   ├── models/         # Pydantic models (Task, Priority, Category)
│   ├── parsers/        # NLP and command parsing
│   ├── storage/        # In-memory task storage
│   ├── ui/             # Rich console, panels, tables, prompts
│   └── main.py         # REPL entry point
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
└── pyproject.toml      # Project configuration
```

## Architecture Decisions

- **ADR-001**: 6-character alphanumeric task IDs for uniqueness
- **ADR-002**: Hybrid input (wizard + NLP) for flexibility
- **ADR-003**: In-memory dict storage for Phase I simplicity
- **ADR-004**: Rich Console singleton for consistent styling
- **ADR-005**: python-dateutil for robust date parsing

## License

MIT
