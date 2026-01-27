# Tasks T068-T070: UpdateCommand for /update <id>
"""Update command handler for editing tasks."""

from src.commands.base import Command
from src.storage.memory import get_storage
from src.models.task import Priority, Category
from src.parsers.nlp import parse_date, parse_time
from src.ui.console import get_console
from src.ui.panels import render_update_comparison, render_error
from src.ui.prompts import prompt_with_default, prompt_priority, prompt_category


class UpdateCommand(Command):
    """
    Command to update an existing task.

    Usage: /update <id>
    """

    @property
    def name(self) -> str:
        return "update"

    @property
    def description(self) -> str:
        return "Edit a task"

    @property
    def usage(self) -> str:
        return "/update <id>"

    def execute(self, args: list[str]) -> bool:
        """Execute the update command."""
        if not args:
            render_error(
                "Please provide a task ID.",
                "Usage: /update <id>"
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

        console = get_console()
        console.print(f"\n[bold blue]📝 Updating task {task_id}[/bold blue]")
        console.print("[dim]Press Enter to keep current value[/dim]\n")

        # Store original for comparison
        old_task = task.model_copy()

        try:
            # Title
            new_title = prompt_with_default("Title", task.title)

            # Description
            new_description = prompt_with_default(
                "Description", task.description or "(empty)"
            )
            if new_description == "(empty)":
                new_description = ""

            # Priority
            console.print(f"\nCurrent priority: [bold]{task.priority}[/bold]")
            console.print("[dim]Press Enter to keep, or select new:[/dim]")
            new_priority = prompt_priority(default=Priority(task.priority))

            # Category
            console.print(f"\nCurrent category: [bold]{task.category}[/bold]")
            console.print("[dim]Press Enter to keep, or select new:[/dim]")
            new_category = prompt_category(default=Category(task.category))

            # Tags
            current_tags = ", ".join(task.tags) if task.tags else "(none)"
            new_tags_str = prompt_with_default("Tags (comma-separated)", current_tags)
            if new_tags_str == "(none)":
                new_tags = []
            else:
                new_tags = [t.strip() for t in new_tags_str.split(",") if t.strip()]

            # Due date
            current_date = str(task.due_date) if task.due_date else "(none)"
            new_date_str = prompt_with_default("Due date", current_date)
            if new_date_str == "(none)" or not new_date_str:
                new_due_date = None
            elif new_date_str == current_date and task.due_date:
                new_due_date = task.due_date
            else:
                new_due_date = parse_date(new_date_str)

            # Due time
            current_time = str(task.due_time) if task.due_time else "(none)"
            new_time_str = prompt_with_default("Due time", current_time)
            if new_time_str == "(none)" or not new_time_str:
                new_due_time = None
            elif new_time_str == current_time and task.due_time:
                new_due_time = task.due_time
            else:
                new_due_time = parse_time(new_time_str)

            # Apply updates
            updated_task = storage.update(
                task_id,
                title=new_title,
                description=new_description,
                priority=new_priority,
                category=new_category,
                tags=new_tags,
                due_date=new_due_date,
                due_time=new_due_time,
            )

            render_update_comparison(old_task, updated_task)
            return True

        except KeyboardInterrupt:
            console.print("\n[dim]Update cancelled.[/dim]")
            return False
