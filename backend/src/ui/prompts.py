# Tasks T049-T051, T074: Interactive Prompts for Todo CLI
"""Interactive input prompts with validation using rich."""

from typing import Optional, Callable

from rich.prompt import Prompt, Confirm
from rich.text import Text

from src.models.task import Priority, Category
from src.ui.console import get_console
from src.ui.theme import PRIORITY_COLORS, PRIORITY_ICONS, CATEGORY_ICONS


# Task T049: Text input with validation
def prompt_text(
    prompt: str,
    min_length: int = 0,
    max_length: int = 0,
    default: str = "",
    required: bool = True,
) -> str:
    """
    Prompt for text input with length validation.

    Args:
        prompt: The prompt message to display.
        min_length: Minimum length (0 = no minimum).
        max_length: Maximum length (0 = no maximum).
        default: Default value if empty input.
        required: Whether input is required (cannot be empty).

    Returns:
        The validated text input.
    """
    console = get_console()

    while True:
        # Build prompt with hints
        prompt_text = Text()
        prompt_text.append(prompt, style="bold")

        if default:
            prompt_text.append(f" [{default}]", style="dim")

        prompt_text.append(": ")

        console.print(prompt_text, end="")
        value = input().strip()

        # Use default if empty
        if not value and default:
            value = default

        # Validate required
        if required and not value:
            console.print("This field is required. Please enter a value.", style="red")
            continue

        # Validate length
        if min_length and len(value) < min_length:
            console.print(
                f"Input must be at least {min_length} characters.", style="red"
            )
            continue

        if max_length and len(value) > max_length:
            console.print(
                f"Input must be at most {max_length} characters.", style="red"
            )
            continue

        return value


# Task T050: Choice selection with colors
def prompt_choice(
    prompt: str,
    choices: list[tuple[str, str, str]],  # (key, label, style)
    default: str = "",
) -> str:
    """
    Prompt for a choice from options with color-coded display.

    Args:
        prompt: The prompt message.
        choices: List of (key, label, style) tuples.
        default: Default choice key.

    Returns:
        The selected choice key.
    """
    console = get_console()

    # Display options
    console.print(f"\n{prompt}:", style="bold")
    for key, label, style in choices:
        marker = " *" if key == default else ""
        console.print(f"  [{key}] {label}{marker}", style=style)

    valid_keys = [c[0].lower() for c in choices]

    while True:
        prompt_text = Text()
        prompt_text.append("Select option")
        if default:
            prompt_text.append(f" [{default}]", style="dim")
        prompt_text.append(": ")

        console.print(prompt_text, end="")
        value = input().strip().lower()

        # Use default if empty
        if not value and default:
            return default

        if value in valid_keys:
            return value

        console.print(
            f"Invalid choice. Please select from: {', '.join(valid_keys)}", style="red"
        )


def prompt_priority(default: Priority = Priority.MEDIUM) -> Priority:
    """
    Prompt for priority selection with color-coded options.

    Args:
        default: Default priority.

    Returns:
        Selected Priority enum value.
    """
    choices = [
        ("h", f"{PRIORITY_ICONS['high']} High", "red"),
        ("m", f"{PRIORITY_ICONS['medium']} Medium", "yellow"),
        ("l", f"{PRIORITY_ICONS['low']} Low", "green"),
    ]

    # Map default to key
    default_key = {"high": "h", "medium": "m", "low": "l"}.get(default.value, "m")

    result = prompt_choice("Select priority", choices, default=default_key)

    return {"h": Priority.HIGH, "m": Priority.MEDIUM, "l": Priority.LOW}[result]


def prompt_category(default: Category = Category.OTHER) -> Category:
    """
    Prompt for category selection.

    Args:
        default: Default category.

    Returns:
        Selected Category enum value.
    """
    choices = [
        ("w", f"{CATEGORY_ICONS['work']} Work", "blue"),
        ("p", f"{CATEGORY_ICONS['personal']} Personal", "cyan"),
        ("s", f"{CATEGORY_ICONS['shopping']} Shopping", "green"),
        ("h", f"{CATEGORY_ICONS['health']} Health", "red"),
        ("o", f"{CATEGORY_ICONS['other']} Other", "dim"),
    ]

    # Map default to key
    default_key = {
        "work": "w",
        "personal": "p",
        "shopping": "s",
        "health": "h",
        "other": "o",
    }.get(default.value, "o")

    result = prompt_choice("Select category", choices, default=default_key)

    return {
        "w": Category.WORK,
        "p": Category.PERSONAL,
        "s": Category.SHOPPING,
        "h": Category.HEALTH,
        "o": Category.OTHER,
    }[result]


# Task T051: Optional field prompt
def prompt_optional(prompt: str, hint: str = "press Enter to skip") -> str:
    """
    Prompt for an optional field.

    Args:
        prompt: The prompt message.
        hint: Hint text for skipping.

    Returns:
        The input value or empty string if skipped.
    """
    console = get_console()

    prompt_text = Text()
    prompt_text.append(prompt, style="bold")
    prompt_text.append(f" ({hint})", style="dim")
    prompt_text.append(": ")

    console.print(prompt_text, end="")
    return input().strip()


def prompt_tags() -> list[str]:
    """
    Prompt for tags (comma-separated).

    Returns:
        List of tag strings.
    """
    value = prompt_optional("Tags", "comma-separated, press Enter to skip")
    if not value:
        return []
    return [tag.strip() for tag in value.split(",") if tag.strip()]


def prompt_date() -> Optional[str]:
    """
    Prompt for a due date.

    Returns:
        Date string or None if skipped.
    """
    console = get_console()
    console.print(
        "  [dim]Examples: tomorrow, next monday, 2026-02-15[/dim]"
    )
    value = prompt_optional("Due date")
    return value if value else None


def prompt_time() -> Optional[str]:
    """
    Prompt for a due time.

    Returns:
        Time string or None if skipped.
    """
    console = get_console()
    console.print("  [dim]Examples: morning, afternoon, 14:00[/dim]")
    value = prompt_optional("Due time")
    return value if value else None


# Task T074: Delete confirmation
def confirm_delete(task_title: str) -> bool:
    """
    Prompt for delete confirmation.

    Args:
        task_title: Title of task to delete.

    Returns:
        True if confirmed, False if cancelled.
    """
    console = get_console()

    prompt_text = Text()
    prompt_text.append(f"Are you sure you want to delete '{task_title}'? ", style="yellow")
    prompt_text.append("[y/N]", style="dim")
    prompt_text.append(": ")

    console.print(prompt_text, end="")
    response = input().strip().lower()

    return response in ("y", "yes")


# Task T069: Prompt with default value display
def prompt_with_default(prompt: str, current_value: str) -> str:
    """
    Prompt for input showing current value, keep on Enter.

    Args:
        prompt: The field name.
        current_value: Current value to display and use as default.

    Returns:
        New value or current value if Enter pressed.
    """
    console = get_console()

    prompt_text = Text()
    prompt_text.append(prompt, style="bold")
    prompt_text.append(f" [{current_value}]", style="cyan")
    prompt_text.append(": ")

    console.print(prompt_text, end="")
    value = input().strip()

    return value if value else current_value
