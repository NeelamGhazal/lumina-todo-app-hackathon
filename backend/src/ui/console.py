# Tasks T024-T025: Rich Console Singleton per ADR-004
"""Rich Console singleton for consistent output across all UI components."""

from typing import Optional

from rich.console import Console


# Task T024: Global console singleton
_console: Optional[Console] = None


def get_console() -> Console:
    """
    Get the global Rich Console singleton instance.

    Per ADR-004: Global singleton ensures consistent formatting.

    Returns:
        The shared Console instance.
    """
    global _console
    if _console is None:
        _console = Console()
    return _console


# Task T025: Testing support
def set_console(console: Console) -> None:
    """
    Set a custom Console instance (for testing).

    Use Console(file=StringIO()) for output capture in tests.

    Args:
        console: Custom Console instance to use.
    """
    global _console
    _console = console


def reset_console() -> None:
    """Reset the console singleton to default (for testing)."""
    global _console
    _console = None
