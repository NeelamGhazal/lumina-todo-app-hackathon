# Task T046: ListCommand for /list
"""List command handler for displaying all tasks."""

from src.commands.base import Command
from src.storage.memory import get_storage
from src.ui.tables import render_task_table
from src.ui.panels import render_empty_state


class ListCommand(Command):
    """
    Command to display all tasks in a formatted table.

    Usage: /list
    """

    @property
    def name(self) -> str:
        return "list"

    @property
    def description(self) -> str:
        return "Show all tasks in a table"

    @property
    def usage(self) -> str:
        return "/list"

    def execute(self, args: list[str]) -> bool:
        """
        Execute the list command.

        Displays all tasks in a formatted table, or an empty state
        message if no tasks exist.

        Args:
            args: Command arguments (ignored for /list).

        Returns:
            True (always succeeds).
        """
        storage = get_storage()
        tasks = storage.list_all()

        if not tasks:
            render_empty_state()
        else:
            render_task_table(tasks)

        return True
