# Research: Phase I - Professional Todo Console Application

**Date**: 2026-01-26
**Branch**: `001-phase1-todo-cli`

## Overview

This document consolidates research findings and technology decisions for Phase I implementation.

---

## Technology Decisions

### 1. Python Version

**Decision**: Python 3.13+

**Rationale**:
- Constitution mandates Python 3.13+
- Latest stable version with improved performance
- Full type hint support including `type` statement
- UV supports Python 3.13

**Alternatives Considered**:
- Python 3.12: Stable but missing some 3.13 features
- Python 3.11: Older, no compelling reason to use

---

### 2. Package Manager: UV

**Decision**: UV (astral-sh/uv)

**Rationale**:
- Constitution mandates UV
- 10-100x faster than pip
- Built-in virtual environment management
- `pyproject.toml` based configuration
- Excellent dependency resolution

**Installation**:
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Project Setup**:
```bash
cd backend
uv init
uv add rich pydantic python-dateutil pytest pytest-cov
```

---

### 3. CLI Rendering: Rich

**Decision**: rich library (Textualize)

**Rationale**:
- Constitution mandates rich for Phase I CLI
- Professional terminal output with minimal code
- Built-in components: Table, Panel, Progress, Console
- Excellent documentation and examples

**Version**: Latest stable (13.x+)

**Key Components Used**:
| Component | Use Case |
|-----------|----------|
| `Console` | All output, singleton pattern |
| `Table` | Task list display |
| `Panel` | Task details, empty states, errors |
| `Progress` | Statistics progress bar |
| `Prompt` | Interactive input |
| `Text` | Styled text with colors |

**Color Scheme**:
```python
COLORS = {
    "high": "red",
    "medium": "yellow",
    "low": "green",
    "info": "blue",
    "error": "red",
    "success": "green",
    "warning": "yellow",
}
```

---

### 4. Data Validation: Pydantic

**Decision**: Pydantic v2

**Rationale**:
- Constitution mandates Pydantic for data models
- Automatic validation with clear error messages
- Type coercion for dates/times
- JSON serialization built-in

**Version**: 2.x (latest)

**Key Features Used**:
- `BaseModel` for Task entity
- `Field()` for constraints (min_length, max_length)
- `validator` decorators for custom validation
- Enum support for Priority and Category

---

### 5. Date Parsing: python-dateutil

**Decision**: python-dateutil for natural language dates

**Rationale**:
- Handles relative dates ("tomorrow", "next monday")
- Parses weekday names
- Robust ISO format support
- Lightweight (~100KB)

**Version**: 2.x (latest)

**Usage Pattern**:
```python
from dateutil import parser
from dateutil.relativedelta import relativedelta, MO
from datetime import datetime, date

def parse_date(text: str) -> date | None:
    text = text.lower().strip()
    today = date.today()

    if text == "tomorrow":
        return today + relativedelta(days=1)
    if text == "today":
        return today
    if text.startswith("next "):
        # Handle "next monday", "next friday", etc.
        weekday = text.replace("next ", "")
        # Use dateutil to find next occurrence
        ...

    # Fall back to dateutil parser
    try:
        return parser.parse(text, fuzzy=True).date()
    except:
        return None
```

---

### 6. Testing: Pytest

**Decision**: pytest with pytest-cov

**Rationale**:
- Constitution mandates pytest
- Industry standard for Python testing
- Excellent fixture system
- Coverage reporting via pytest-cov

**Configuration** (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["src"]
omit = ["src/ui/*"]  # Exclude UI from coverage
```

---

## Best Practices Research

### Rich Console Patterns

**Singleton Pattern**:
```python
# ui/console.py
from rich.console import Console

_console: Console | None = None

def get_console() -> Console:
    global _console
    if _console is None:
        _console = Console()
    return _console

# For testing
def set_console(console: Console) -> None:
    global _console
    _console = console
```

**Error Display**:
```python
from rich.panel import Panel

def show_error(message: str, suggestion: str | None = None):
    content = f"[red]{message}[/red]"
    if suggestion:
        content += f"\n[dim]{suggestion}[/dim]"
    get_console().print(Panel(content, title="Error", border_style="red"))
```

---

### Command Pattern

**Base Command Interface**:
```python
from abc import ABC, abstractmethod

class Command(ABC):
    name: str
    description: str
    usage: str

    @abstractmethod
    def execute(self, args: list[str]) -> None:
        """Execute the command with given arguments."""
        pass
```

**Command Registry**:
```python
COMMANDS: dict[str, Command] = {}

def register(command: Command) -> None:
    COMMANDS[command.name.lower()] = command

def get_command(name: str) -> Command | None:
    return COMMANDS.get(name.lower())
```

---

### In-Memory Storage Pattern

**Thread-Safe Storage** (even though single-threaded, good practice):
```python
from threading import Lock

class TaskStorage:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._lock = Lock()

    def add(self, task: Task) -> None:
        with self._lock:
            self._tasks[task.id] = task

    def get(self, id: str) -> Task | None:
        return self._tasks.get(id)

    # ... other methods
```

---

## Dependency Summary

| Package | Version | Purpose |
|---------|---------|---------|
| rich | ^13.0 | CLI rendering |
| pydantic | ^2.0 | Data validation |
| python-dateutil | ^2.8 | Date parsing |
| pytest | ^8.0 | Testing |
| pytest-cov | ^4.0 | Coverage |

---

## References

- [Rich Documentation](https://rich.readthedocs.io/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/)
- [python-dateutil Documentation](https://dateutil.readthedocs.io/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [Pytest Documentation](https://docs.pytest.org/)
