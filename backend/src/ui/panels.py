# Task T045, T052, T053, and future panel tasks
"""Panel-based UI components for Todo CLI."""

from datetime import date
from typing import Optional

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn

from src.models.task import Task, Priority, Category
from src.ui.console import get_console
from src.ui.theme import (
    COLORS,
    PRIORITY_ICONS,
    PRIORITY_COLORS,
    CATEGORY_ICONS,
    STATUS_ICONS,
)


# Task T045: Empty state panel per contracts/commands.md /list empty state
def render_empty_state() -> None:
    """
    Render a friendly empty state message when no tasks exist.

    Per FR-018: Styled panel when no data exists.
    """
    console = get_console()

    content = Text()
    content.append("📋 No Tasks Yet\n\n", style="bold blue")
    content.append("Get started by adding your first task:\n", style="dim")
    content.append("/add Buy groceries tomorrow", style="green")
    content.append("\n\nOr use the interactive wizard:\n", style="dim")
    content.append("/add", style="green")

    panel = Panel(
        content,
        border_style="blue",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


# Task T052: Task created success panel
def render_task_created(task: Task) -> None:
    """
    Render a success panel showing created task details.

    Per contracts/commands.md /add output specification.
    """
    console = get_console()

    content = Text()
    content.append(f"ID: ", style="dim")
    content.append(f"{task.id}\n", style="bold")
    content.append(f"Title: ", style="dim")
    content.append(f"{task.title}\n", style="bold white")

    if task.description:
        content.append(f"Description: ", style="dim")
        content.append(f"{task.description}\n")

    # Priority with color
    priority_icon = PRIORITY_ICONS.get(task.priority, "")
    priority_color = PRIORITY_COLORS.get(task.priority, "white")
    content.append(f"Priority: ", style="dim")
    content.append(f"{priority_icon} {task.priority}\n", style=priority_color)

    # Category with icon
    category_icon = CATEGORY_ICONS.get(task.category, "")
    content.append(f"Category: ", style="dim")
    content.append(f"{category_icon} {task.category}\n")

    if task.tags:
        content.append(f"Tags: ", style="dim")
        content.append(f"{', '.join(task.tags)}\n")

    if task.due_date:
        content.append(f"Due: ", style="dim")
        due_str = task.due_date.strftime("%Y-%m-%d")
        if task.due_time:
            due_str += f" {task.due_time.strftime('%H:%M')}"
        content.append(f"{due_str}\n")

    panel = Panel(
        content,
        title="✅ Task Created",
        title_align="left",
        border_style="green",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


# Task T053: Error panel
def render_error(message: str, suggestion: Optional[str] = None) -> None:
    """
    Render an error message panel.

    Per FR-022: User-friendly error messages (no stack traces).
    """
    console = get_console()

    content = Text()
    content.append(message, style="red")
    if suggestion:
        content.append(f"\n\n{suggestion}", style="dim")

    panel = Panel(
        content,
        title="❌ Error",
        title_align="left",
        border_style="red",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


# Task T062: Task detail panel for /show command
def render_task_detail(task: Task) -> None:
    """
    Render a detailed view of a single task.

    Per contracts/commands.md /show output specification.
    """
    console = get_console()

    content = Text()

    # ID
    content.append("ID:          ", style="dim")
    content.append(f"{task.id}\n", style="bold")

    # Title
    content.append("Title:       ", style="dim")
    content.append(f"{task.title}\n", style="bold white")

    # Description
    content.append("Description: ", style="dim")
    content.append(f"{task.description or '(none)'}\n")

    content.append("\n")

    # Priority with color
    priority_icon = PRIORITY_ICONS.get(task.priority, "")
    priority_color = PRIORITY_COLORS.get(task.priority, "white")
    content.append("Priority:    ", style="dim")
    content.append(f"{priority_icon} {task.priority}\n", style=priority_color)

    # Category with icon
    category_icon = CATEGORY_ICONS.get(task.category, "")
    content.append("Category:    ", style="dim")
    content.append(f"{category_icon} {task.category}\n")

    # Tags
    content.append("Tags:        ", style="dim")
    content.append(f"{', '.join(task.tags) if task.tags else '(none)'}\n")

    content.append("\n")

    # Due date
    content.append("Due Date:    ", style="dim")
    if task.due_date:
        due_str = task.due_date.strftime("%Y-%m-%d")
        # Warn if past due
        if task.due_date < date.today() and not task.is_completed:
            content.append(f"{due_str} ", style="red")
            content.append("(overdue!)", style="bold red")
        else:
            content.append(due_str)
    else:
        content.append("-")
    content.append("\n")

    # Due time
    content.append("Due Time:    ", style="dim")
    content.append(f"{task.due_time.strftime('%H:%M') if task.due_time else '-'}\n")

    # Status
    status_icon = STATUS_ICONS.get(task.is_completed, "?")
    status_text = "Completed" if task.is_completed else "Pending"
    status_style = "green" if task.is_completed else "yellow"
    content.append("Status:      ", style="dim")
    content.append(f"{status_icon} {status_text}\n", style=status_style)

    content.append("\n")

    # Created at
    content.append("Created:     ", style="dim")
    content.append(f"{task.created_at.strftime('%Y-%m-%d %H:%M')}\n")

    panel = Panel(
        content,
        title="📋 Task Details",
        title_align="left",
        border_style="blue",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


# Task T067: Update comparison panel
def render_update_comparison(old_task: Task, new_task: Task) -> None:
    """
    Render a before/after comparison of task updates.

    Per contracts/commands.md /update output specification.
    """
    console = get_console()

    content = Text()
    content.append("Changed fields:\n", style="bold")

    changes_found = False

    # Check each field for changes
    if old_task.title != new_task.title:
        content.append(f"• Title: ", style="dim")
        content.append(f"{old_task.title}", style="red strikethrough")
        content.append(" → ")
        content.append(f"{new_task.title}\n", style="green")
        changes_found = True

    if old_task.description != new_task.description:
        old_desc = old_task.description or "(empty)"
        new_desc = new_task.description or "(empty)"
        content.append(f"• Description: ", style="dim")
        content.append(f"{old_desc[:30]}", style="red")
        content.append(" → ")
        content.append(f"{new_desc[:30]}\n", style="green")
        changes_found = True

    if old_task.priority != new_task.priority:
        content.append(f"• Priority: ", style="dim")
        content.append(f"{old_task.priority}", style="red")
        content.append(" → ")
        content.append(f"{new_task.priority}\n", style="green")
        changes_found = True

    if old_task.category != new_task.category:
        content.append(f"• Category: ", style="dim")
        content.append(f"{old_task.category}", style="red")
        content.append(" → ")
        content.append(f"{new_task.category}\n", style="green")
        changes_found = True

    if old_task.tags != new_task.tags:
        content.append(f"• Tags: ", style="dim")
        content.append(f"{', '.join(old_task.tags) or '(none)'}", style="red")
        content.append(" → ")
        content.append(f"{', '.join(new_task.tags) or '(none)'}\n", style="green")
        changes_found = True

    if old_task.due_date != new_task.due_date:
        content.append(f"• Due date: ", style="dim")
        content.append(f"{old_task.due_date or '(none)'}", style="red")
        content.append(" → ")
        content.append(f"{new_task.due_date or '(none)'}\n", style="green")
        changes_found = True

    if old_task.due_time != new_task.due_time:
        content.append(f"• Due time: ", style="dim")
        content.append(f"{old_task.due_time or '(none)'}", style="red")
        content.append(" → ")
        content.append(f"{new_task.due_time or '(none)'}\n", style="green")
        changes_found = True

    if not changes_found:
        content.append("No changes made.", style="dim")

    panel = Panel(
        content,
        title="✅ Task Updated",
        title_align="left",
        border_style="green",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


# Task T073: Completion toggle message
def render_completion_toggle(task: Task) -> None:
    """Render completion status change message."""
    console = get_console()

    if task.is_completed:
        console.print(f"\n✓ Task '{task.title}' marked as [green]completed[/green]!")
    else:
        console.print(f"\n✗ Task '{task.title}' marked as [yellow]pending[/yellow].")


# Task T075: Delete result message
def render_delete_result(task: Task, deleted: bool) -> None:
    """Render delete confirmation result."""
    console = get_console()

    if deleted:
        console.print(f"\n🗑️  Task '[bold]{task.title}[/bold]' deleted.")
    else:
        console.print("\nDeletion cancelled.", style="dim")


# Task T083: No search results panel
def render_no_results(query: str) -> None:
    """Render no search results message."""
    console = get_console()

    content = Text()
    content.append(f'No tasks matching "{query}" found.\n\n', style="dim")
    content.append("Try:\n", style="dim")
    content.append("• Using different keywords\n")
    content.append("• Checking spelling\n")
    content.append("• Using /list to see all tasks")

    panel = Panel(
        content,
        title="🔍 No Results Found",
        title_align="left",
        border_style="yellow",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


# Task T088-T090: Statistics dashboard
def render_stats_dashboard(
    total: int,
    completed: int,
    pending: int,
    by_priority: dict[Priority, int],
    by_category: dict[Category, int],
) -> None:
    """
    Render statistics dashboard with progress bar and breakdowns.

    Per contracts/commands.md /stats output specification.
    Per FR-019: Progress bars and visual charts.
    """
    console = get_console()

    content = Text()

    # Overview section
    content.append("Overview\n", style="bold")
    content.append("────────\n", style="dim")
    content.append(f"Total Tasks:     {total}\n")

    pct = (completed / total * 100) if total > 0 else 0
    content.append(f"Completed:       {completed}  ({pct:.0f}%)\n", style="green")
    content.append(f"Pending:         {pending}  ({100 - pct:.0f}%)\n", style="yellow")

    content.append("\n")

    # Progress bar representation
    content.append("Completion Progress\n", style="bold")
    bar_width = 25
    filled = int(bar_width * pct / 100) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_width - filled)
    content.append(f"{bar}  {pct:.0f}%\n", style="green")

    content.append("\n")

    # By Priority
    content.append("By Priority\n", style="bold")
    content.append("───────────\n", style="dim")
    for priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
        count = by_priority.get(priority, 0)
        icon = PRIORITY_ICONS.get(priority, "")
        color = PRIORITY_COLORS.get(priority, "white")
        bar = "█" * min(count, 20)
        content.append(f"{icon} {priority.value.capitalize():8} {count:3}  ", style=color)
        content.append(f"{bar}\n", style=color)

    content.append("\n")

    # By Category
    content.append("By Category\n", style="bold")
    content.append("───────────\n", style="dim")
    for category in Category:
        count = by_category.get(category, 0)
        icon = CATEGORY_ICONS.get(category, "")
        content.append(f"{icon} {category.value.capitalize():10} {count}\n")

    panel = Panel(
        content,
        title="📊 Task Statistics",
        title_align="left",
        border_style="blue",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


def render_no_stats() -> None:
    """Render empty statistics state."""
    console = get_console()

    content = Text()
    content.append("📊 No Statistics Yet\n\n", style="bold blue")
    content.append("Add some tasks to see your productivity stats!\n", style="dim")
    content.append("/add", style="green")

    panel = Panel(
        content,
        border_style="blue",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


# Task T095: Help screen
def render_help(commands: list) -> None:
    """
    Render formatted help screen with all commands.

    Per contracts/commands.md /help output specification.
    """
    console = get_console()

    content = Text()

    content.append("  Task Management\n", style="bold")
    content.append("  ───────────────\n", style="dim")
    content.append("  /add              ", style="green")
    content.append("Interactive wizard to create a task\n")
    content.append("  /add <text>       ", style="green")
    content.append("Quick add with natural language\n")
    content.append("  /list             ", style="green")
    content.append("Show all tasks in a table\n")
    content.append("  /show <id>        ", style="green")
    content.append("View task details\n")
    content.append("  /update <id>      ", style="green")
    content.append("Edit a task\n")
    content.append("  /complete <id>    ", style="green")
    content.append("Toggle task completion\n")
    content.append("  /delete <id>      ", style="green")
    content.append("Remove a task\n")

    content.append("\n")
    content.append("  Search & Stats\n", style="bold")
    content.append("  ──────────────\n", style="dim")
    content.append("  /search <query>   ", style="green")
    content.append("Search tasks by keyword\n")
    content.append("  /stats            ", style="green")
    content.append("View task statistics\n")

    content.append("\n")
    content.append("  Application\n", style="bold")
    content.append("  ───────────\n", style="dim")
    content.append("  /help             ", style="green")
    content.append("Show this help screen\n")
    content.append("  /exit             ", style="green")
    content.append("Exit the application\n")

    content.append("\n")
    content.append("  Examples\n", style="bold")
    content.append("  ────────\n", style="dim")
    content.append("  /add Buy milk tomorrow #shopping high\n", style="cyan")
    content.append("  /show a1b2c3\n", style="cyan")
    content.append("  /search groceries\n", style="cyan")

    panel = Panel(
        content,
        title="📋 Todo CLI Help",
        title_align="center",
        border_style="blue",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


# Task T096: Goodbye message
def render_goodbye() -> None:
    """Render exit/goodbye message."""
    console = get_console()
    console.print(
        "\n👋 Goodbye! Your tasks will not be saved (in-memory mode).",
        style="dim",
    )


# Task T097: Unknown command error
def render_unknown_command(command: str) -> None:
    """Render unknown command error with help suggestion."""
    console = get_console()

    content = Text()
    content.append(f"Unknown command: /{command}\n\n")
    content.append("Type ", style="dim")
    content.append("/help", style="green")
    content.append(" to see available commands.", style="dim")

    panel = Panel(
        content,
        border_style="yellow",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


# Task T098: Invalid input (no slash prefix)
def render_invalid_input() -> None:
    """Render error for input without / prefix."""
    console = get_console()

    content = Text()
    content.append("Commands must start with /\n\n")
    content.append("Examples:\n", style="dim")
    content.append("/add Buy groceries\n", style="green")
    content.append("/list\n", style="green")
    content.append("/help\n", style="green")

    panel = Panel(
        content,
        border_style="yellow",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)
