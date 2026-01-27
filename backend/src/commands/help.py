# Task T099: HelpCommand for /help
"""Help command handler for displaying available commands."""

from src.commands.base import Command, get_registry
from src.ui.panels import render_help


class HelpCommand(Command):
    """
    Command to display help screen with all commands.

    Usage: /help
    """

    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Show this help screen"

    @property
    def usage(self) -> str:
        return "/help"

    def execute(self, args: list[str]) -> bool:
        """Execute the help command."""
        registry = get_registry()
        commands = registry.list_commands()
        render_help(commands)
        return True
