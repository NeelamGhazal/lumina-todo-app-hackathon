# Quickstart Guide: Phase I - Professional Todo Console Application

**Date**: 2026-01-26
**Branch**: `001-phase1-todo-cli`

## Prerequisites

- Python 3.13+
- UV package manager
- Terminal with ANSI color support (most modern terminals)

---

## Installation

### 1. Install UV (if not already installed)

**Linux/macOS**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup

```bash
# Navigate to project root
cd evolution-todo

# Navigate to backend
cd backend

# Install dependencies
uv sync

# Run the application
uv run python -m src.main
```

---

## Quick Usage

### Starting the Application

```bash
cd backend
uv run python -m src.main
```

You'll see a welcome banner:

```
╭─────────────────────────────────────────────────────────────╮
│                                                              │
│   ████████╗ ██████╗ ██████╗  ██████╗                        │
│   ╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗                       │
│      ██║   ██║   ██║██║  ██║██║   ██║                       │
│      ██║   ██║   ██║██║  ██║██║   ██║                       │
│      ██║   ╚██████╔╝██████╔╝╚██████╔╝                       │
│      ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝                        │
│                                                              │
│              Professional Todo CLI v1.0.0                    │
│                                                              │
│   Type /help for available commands                          │
│                                                              │
╰─────────────────────────────────────────────────────────────╯

todo>
```

### Basic Commands

**Add a task (quick mode)**:
```
todo> /add Buy groceries tomorrow #shopping high
```

**Add a task (wizard mode)**:
```
todo> /add
Title: Buy groceries
Description: Milk, bread, eggs
Priority [m]: h
Category [o]: s
...
```

**List all tasks**:
```
todo> /list
```

**View task details**:
```
todo> /show a1b2c3
```

**Mark task complete**:
```
todo> /complete a1b2c3
```

**Search tasks**:
```
todo> /search groceries
```

**View statistics**:
```
todo> /stats
```

**Exit**:
```
todo> /exit
```

---

## Command Reference

| Command | Description |
|---------|-------------|
| `/help` | Show help screen |
| `/add` | Add task (wizard mode) |
| `/add <text>` | Add task (NLP mode) |
| `/list` | List all tasks |
| `/show <id>` | View task details |
| `/update <id>` | Edit a task |
| `/complete <id>` | Toggle completion |
| `/delete <id>` | Delete a task |
| `/search <query>` | Search tasks |
| `/stats` | View statistics |
| `/exit` | Exit application |

---

## Natural Language Examples

The `/add` command supports natural language:

```bash
# Basic task
/add Buy milk

# With due date
/add Buy milk tomorrow
/add Call mom next monday

# With priority
/add Finish report urgent
/add Review docs high

# With category
/add Team meeting #work
/add Buy birthday gift #personal

# Combined
/add Buy groceries tomorrow #shopping high
/add Doctor appointment next friday morning #health
```

---

## Running Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/unit/test_models.py
```

---

## Troubleshooting

### Colors not showing

Ensure your terminal supports ANSI colors. Try:
- Windows: Use Windows Terminal or PowerShell 7+
- macOS: Default Terminal works
- Linux: Most terminals work

### UV not found

Make sure UV is in your PATH:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Python version issues

Verify Python version:
```bash
python --version  # Should be 3.13+
```

---

## Data Persistence

**Note**: Phase I uses in-memory storage. All tasks are lost when you exit the application. This is by design for Phase I scope.

Persistence will be added in Phase II with database integration.
