# Task T101: ExitCommand for /exit
"""Exit command handler for graceful shutdown."""

from src.commands.base import Command
from src.ui.panels import render_goodbye


class ExitCommand(Command):
    """
    Command to exit the application gracefully.

    Usage: /exit
    """

    @property
    def name(self) -> str:
        return "exit"

    @property
    def description(self) -> str:
        return "Exit the application"

    @property
    def usage(self) -> str:
        return "/exit"

    def execute(self, args: list[str]) -> bool:
        """
        Execute the exit command.

        Returns:
            False to signal application should exit.
        """
        render_goodbye()
        return False  # Signal to exit the main loop
