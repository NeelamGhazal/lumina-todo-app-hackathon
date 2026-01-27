# Tasks T026-T029: Theme Constants per research.md
"""Color scheme, status icons, and visual constants for Todo CLI."""

from src.models.task import Priority, Category


# Task T026: COLORS dict per research.md
COLORS = {
    # Priority colors per FR-015
    "high": "red",
    "medium": "yellow",
    "low": "green",
    # Status colors
    "info": "blue",
    "error": "red",
    "success": "green",
    "warning": "yellow",
    # UI colors
    "muted": "dim",
    "accent": "cyan",
    "header": "bold blue",
}

# Priority-specific colors for Rich styling
PRIORITY_COLORS = {
    Priority.HIGH: "red",
    "high": "red",
    Priority.MEDIUM: "yellow",
    "medium": "yellow",
    Priority.LOW: "green",
    "low": "green",
}


# Task T027: STATUS_ICONS dict per FR-016
STATUS_ICONS = {
    True: "✓",   # Completed
    False: "✗",  # Pending
    "completed": "✓",
    "pending": "✗",
    "due": "⏰",  # Has due date
}


# Task T028: CATEGORY_ICONS dict per data-model.md
CATEGORY_ICONS = {
    Category.WORK: "💼",
    "work": "💼",
    Category.PERSONAL: "🏠",
    "personal": "🏠",
    Category.SHOPPING: "🛒",
    "shopping": "🛒",
    Category.HEALTH: "❤️",
    "health": "❤️",
    Category.OTHER: "📌",
    "other": "📌",
}


# Task T029: PRIORITY_ICONS dict per data-model.md
PRIORITY_ICONS = {
    Priority.HIGH: "🔴",
    "high": "🔴",
    Priority.MEDIUM: "🟡",
    "medium": "🟡",
    Priority.LOW: "🟢",
    "low": "🟢",
}


def get_priority_style(priority: Priority | str) -> str:
    """Get Rich style string for a priority level."""
    color = PRIORITY_COLORS.get(priority, "white")
    return color


def get_priority_display(priority: Priority | str) -> str:
    """Get formatted priority display with icon."""
    icon = PRIORITY_ICONS.get(priority, "")
    label = priority if isinstance(priority, str) else priority.value
    return f"{icon} {label}"


def get_category_display(category: Category | str) -> str:
    """Get formatted category display with icon."""
    icon = CATEGORY_ICONS.get(category, "")
    label = category if isinstance(category, str) else category.value
    return f"{icon} {label}"


def get_status_display(is_completed: bool) -> str:
    """Get status display icon."""
    return STATUS_ICONS.get(is_completed, "?")
