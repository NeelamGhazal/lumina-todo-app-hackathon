# Task T023: Command Parser per FR-021a
"""Command parser for slash-based input (case-insensitive)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedCommand:
    """Parsed command result."""
    name: str  # Command name (lowercase, without slash)
    args: list[str]  # Command arguments
    raw_args: str  # Original argument string


def parse_command(input_text: str) -> Optional[ParsedCommand]:
    """
    Parse a slash command from user input.

    Per FR-021a: Commands are case-insensitive.
    Per FR-021b: Commands must start with / prefix.

    Args:
        input_text: Raw user input.

    Returns:
        ParsedCommand if valid command, None if not a command.

    Examples:
        >>> parse_command("/list")
        ParsedCommand(name="list", args=[], raw_args="")

        >>> parse_command("/ADD Buy milk tomorrow")
        ParsedCommand(name="add", args=["Buy", "milk", "tomorrow"], raw_args="Buy milk tomorrow")

        >>> parse_command("hello")
        None  # Not a command (no / prefix)
    """
    input_text = input_text.strip()

    # Must start with /
    if not input_text.startswith("/"):
        return None

    # Remove the leading /
    content = input_text[1:]

    if not content:
        return None

    # Split into command and args
    parts = content.split(maxsplit=1)
    command_name = parts[0].lower()  # Case-insensitive per FR-021a

    if len(parts) > 1:
        raw_args = parts[1]
        # Split args but preserve quoted strings
        args = _split_args(raw_args)
    else:
        raw_args = ""
        args = []

    return ParsedCommand(name=command_name, args=args, raw_args=raw_args)


def _split_args(args_str: str) -> list[str]:
    """
    Split argument string respecting quoted strings.

    Args:
        args_str: Argument string to split.

    Returns:
        List of argument strings.
    """
    args: list[str] = []
    current = ""
    in_quotes = False
    quote_char = None

    for char in args_str:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
        elif char == " " and not in_quotes:
            if current:
                args.append(current)
                current = ""
        else:
            current += char

    if current:
        args.append(current)

    return args
