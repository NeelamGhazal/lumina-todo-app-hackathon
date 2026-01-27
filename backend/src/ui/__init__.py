# Task T003: Package initialization for ui
"""Rich UI components for Todo CLI."""

from src.ui.console import get_console, set_console, reset_console
from src.ui.theme import (
    COLORS,
    PRIORITY_COLORS,
    STATUS_ICONS,
    CATEGORY_ICONS,
    PRIORITY_ICONS,
    get_priority_style,
    get_priority_display,
    get_category_display,
    get_status_display,
)

__all__ = [
    "get_console",
    "set_console",
    "reset_console",
    "COLORS",
    "PRIORITY_COLORS",
    "STATUS_ICONS",
    "CATEGORY_ICONS",
    "PRIORITY_ICONS",
    "get_priority_style",
    "get_priority_display",
    "get_category_display",
    "get_status_display",
]
