# Tasks T063-T064: ShowCommand for /show <id>
"""Show command handler for viewing task details."""

from src.commands.base import Command
from src.storage.memory import get_storage
from src.ui.panels import render_task_detail, render_error


class ShowCommand(Command):
    """
    Command to display detailed view of a single task.

    Usage: /show <id>
    """

    @property
    def name(self) -> str:
        return "show"

    @property
    def description(self) -> str:
        return "View task details"

    @property
    def usage(self) -> str:
        return "/show <id>"

    def execute(self, args: list[str]) -> bool:
        """
        Execute the show command.

        Args:
            args: Command arguments (should contain task ID).

        Returns:
            True if task was displayed, False on error.
        """
        # Task T064: ID validation
        if not args:
            render_error(
                "Please provide a task ID.",
                "Usage: /show <id>"
            )
            return False

        task_id = args[0].lower()

        storage = get_storage()
        task = storage.get(task_id)

        if task is None:
            render_error(
                f"Task '{task_id}' not found.",
                "Use /list to see all tasks."
            )
            return False

        render_task_detail(task)
        return True
