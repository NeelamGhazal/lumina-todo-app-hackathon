# Task T078: DeleteCommand for /delete <id>
"""Delete command handler for removing tasks."""

from src.commands.base import Command
from src.storage.memory import get_storage
from src.ui.panels import render_delete_result, render_error
from src.ui.prompts import confirm_delete


class DeleteCommand(Command):
    """
    Command to delete a task with confirmation.

    Usage: /delete <id>
    """

    @property
    def name(self) -> str:
        return "delete"

    @property
    def description(self) -> str:
        return "Remove a task"

    @property
    def usage(self) -> str:
        return "/delete <id>"

    def execute(self, args: list[str]) -> bool:
        """Execute the delete command."""
        if not args:
            render_error(
                "Please provide a task ID.",
                "Usage: /delete <id>"
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

        # Confirm deletion
        if confirm_delete(task.title):
            storage.delete(task_id)
            render_delete_result(task, deleted=True)
        else:
            render_delete_result(task, deleted=False)

        return True
