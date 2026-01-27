# Task T076: CompleteCommand for /complete <id>
"""Complete command handler for toggling task completion."""

from src.commands.base import Command
from src.storage.memory import get_storage
from src.ui.panels import render_completion_toggle, render_error


class CompleteCommand(Command):
    """
    Command to toggle task completion status.

    Usage: /complete <id>
    """

    @property
    def name(self) -> str:
        return "complete"

    @property
    def description(self) -> str:
        return "Toggle task completion"

    @property
    def usage(self) -> str:
        return "/complete <id>"

    def execute(self, args: list[str]) -> bool:
        """Execute the complete command."""
        if not args:
            render_error(
                "Please provide a task ID.",
                "Usage: /complete <id>"
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

        # Toggle completion status
        new_status = not task.is_completed
        updated_task = storage.update(task_id, is_completed=new_status)

        render_completion_toggle(updated_task)
        return True
