# Task T044: Task Table Renderer per FR-015, FR-016, FR-017
"""Task list table formatting using rich Table."""

from rich.table import Table
from rich.text import Text

from src.models.task import Task
from src.ui.console import get_console
from src.ui.theme import (
    PRIORITY_COLORS,
    PRIORITY_ICONS,
    STATUS_ICONS,
    CATEGORY_ICONS,
    get_priority_style,
)


def render_task_table(tasks: list[Task], title: str = "All Tasks") -> None:
    """
    Render tasks in a formatted table with colors and icons.

    Per FR-015: Color-coded priorities (high=red, medium=yellow, low=green)
    Per FR-016: Status icons (completed=✓, pending=✗)
    Per FR-017: Formatted table with proper borders and alignment

    Args:
        tasks: List of tasks to display.
        title: Table title (default: "All Tasks").
    """
    console = get_console()

    # Create table with styling
    table = Table(
        title=f"📋 {title}",
        title_style="bold blue",
        border_style="blue",
        header_style="bold",
        show_lines=False,
    )

    # Add columns per contracts/commands.md /list output
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", min_width=20, max_width=40)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Priority", justify="center", width=12)
    table.add_column("Category", width=12)
    table.add_column("Due Date", justify="center", width=12)

    # Add rows for each task
    for task in tasks:
        # Status icon
        status_icon = STATUS_ICONS.get(task.is_completed, "?")
        status_style = "green" if task.is_completed else "red"

        # Priority with color and icon
        priority_icon = PRIORITY_ICONS.get(task.priority, "")
        priority_color = PRIORITY_COLORS.get(task.priority, "white")
        priority_text = Text(f"{priority_icon} {task.priority}", style=priority_color)

        # Category with icon
        category_icon = CATEGORY_ICONS.get(task.category, "")
        category_text = f"{category_icon} {task.category}"

        # Due date formatting
        if task.due_date:
            due_str = task.due_date.strftime("%Y-%m-%d")
        else:
            due_str = "-"

        # Truncate title if too long
        title_display = task.title
        if len(title_display) > 38:
            title_display = title_display[:35] + "..."

        table.add_row(
            task.id,
            title_display,
            Text(status_icon, style=status_style),
            priority_text,
            category_text,
            due_str,
        )

    console.print()
    console.print(table)

    # Summary line
    completed = sum(1 for t in tasks if t.is_completed)
    pending = len(tasks) - completed
    console.print(
        f"\nTotal: {len(tasks)} tasks ({completed} completed, {pending} pending)",
        style="dim",
    )


# Task T082 (partial): Search results table with highlighting
def render_search_results(tasks: list[Task], query: str) -> None:
    """
    Render search results with query highlighting.

    Args:
        tasks: Matching tasks to display.
        query: Search query for highlighting.
    """
    console = get_console()

    # Create table
    table = Table(
        title=f'🔍 Search Results: "{query}"',
        title_style="bold blue",
        border_style="blue",
        header_style="bold",
    )

    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", min_width=20, max_width=40)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Priority", justify="center", width=12)

    for task in tasks:
        # Highlight matching text in title
        title_text = _highlight_match(task.title, query)

        # Status icon
        status_icon = STATUS_ICONS.get(task.is_completed, "?")
        status_style = "green" if task.is_completed else "red"

        # Priority with color
        priority_icon = PRIORITY_ICONS.get(task.priority, "")
        priority_color = PRIORITY_COLORS.get(task.priority, "white")
        priority_text = Text(f"{priority_icon} {task.priority}", style=priority_color)

        table.add_row(
            task.id,
            title_text,
            Text(status_icon, style=status_style),
            priority_text,
        )

    console.print()
    console.print(table)
    console.print(f'\nFound {len(tasks)} tasks matching "{query}"', style="dim")


def _highlight_match(text: str, query: str) -> Text:
    """Highlight query matches in text."""
    result = Text()
    text_lower = text.lower()
    query_lower = query.lower()

    start = 0
    while True:
        pos = text_lower.find(query_lower, start)
        if pos == -1:
            result.append(text[start:])
            break
        result.append(text[start:pos])
        result.append(text[pos : pos + len(query)], style="bold yellow on black")
        start = pos + len(query)

    return result
