# Tasks T054-T057, T059-T060: AddCommand for /add
"""Add command handler with wizard and NLP modes."""

from src.commands.base import Command
from src.storage.memory import get_storage
from src.models.task import Priority, Category
from src.parsers.nlp import parse_date, parse_time, parse_natural_language
from src.ui.console import get_console
from src.ui.panels import render_task_created, render_error
from src.ui.prompts import (
    prompt_text,
    prompt_optional,
    prompt_priority,
    prompt_category,
    prompt_tags,
    prompt_date,
    prompt_time,
)


class AddCommand(Command):
    """
    Command to add a new task.

    Usage:
        /add              - Interactive wizard mode
        /add <text>       - Natural language mode
    """

    @property
    def name(self) -> str:
        return "add"

    @property
    def description(self) -> str:
        return "Add a new task"

    @property
    def usage(self) -> str:
        return "/add [natural language text]"

    # Task T054: Detect wizard vs NLP mode
    def execute(self, args: list[str]) -> bool:
        """
        Execute the add command.

        If no args, runs interactive wizard.
        If args provided, parses natural language.

        Args:
            args: Command arguments (natural language text if provided).

        Returns:
            True if task was created successfully.
        """
        if args:
            # Task T059-T060: NLP mode
            return self._run_nlp(" ".join(args))
        else:
            # Task T055-T056: Wizard mode
            return self._run_wizard()

    # Task T055: Interactive wizard
    def _run_wizard(self) -> bool:
        """
        Run the interactive wizard to create a task.

        Prompts for each field with validation.
        """
        console = get_console()
        console.print("\n[bold blue]📝 Create New Task[/bold blue]\n")

        try:
            # Required: Title (1-200 chars)
            title = prompt_text(
                "Title",
                min_length=1,
                max_length=200,
                required=True,
            )

            # Optional: Description
            description = prompt_optional("Description")

            # Optional: Priority (default: medium)
            priority = prompt_priority(default=Priority.MEDIUM)

            # Optional: Category (default: other)
            category = prompt_category(default=Category.OTHER)

            # Optional: Tags
            tags = prompt_tags()

            # Optional: Due date
            due_date_str = prompt_date()
            due_date = None
            if due_date_str:
                due_date = parse_date(due_date_str)
                if due_date_str and not due_date:
                    console.print(
                        f"  [yellow]Could not parse date '{due_date_str}', skipping[/yellow]"
                    )

            # Optional: Due time
            due_time_str = prompt_time()
            due_time = None
            if due_time_str:
                due_time = parse_time(due_time_str)
                if due_time_str and not due_time:
                    console.print(
                        f"  [yellow]Could not parse time '{due_time_str}', skipping[/yellow]"
                    )

            # Create task
            storage = get_storage()
            task = storage.create_task(
                title=title,
                description=description,
                priority=priority,
                category=category,
                tags=tags,
                due_date=due_date,
                due_time=due_time,
            )

            render_task_created(task)
            return True

        except KeyboardInterrupt:
            console.print("\n[dim]Task creation cancelled.[/dim]")
            return False
        except Exception as e:
            render_error(str(e))
            return False

    # Task T059-T060: NLP mode
    def _run_nlp(self, text: str) -> bool:
        """
        Create a task from natural language text.

        Parses text to extract title, due date, priority, category.
        """
        console = get_console()

        # Parse the natural language input
        parsed = parse_natural_language(text)

        title = parsed["title"]
        if not title:
            render_error(
                "Could not extract task title from input.",
                "Please provide a task description, e.g., /add Buy milk tomorrow"
            )
            return False

        # Validate title length
        if len(title) > 200:
            title = title[:200]
            console.print(
                "[yellow]Title truncated to 200 characters.[/yellow]"
            )

        # Build task fields
        priority = parsed["priority"] or Priority.MEDIUM
        category = parsed["category"] or Category.OTHER
        due_date = parsed["due_date"]
        due_time = parsed["due_time"]

        # Show what was parsed
        console.print("\n[dim]Interpreted:[/dim]")
        console.print(f"  Title: [bold]{title}[/bold]")
        if due_date:
            console.print(f"  Due date: {due_date}")
        if due_time:
            console.print(f"  Due time: {due_time}")
        if parsed["priority"]:
            console.print(f"  Priority: {priority.value}")
        if parsed["category"]:
            console.print(f"  Category: {category.value}")

        # Create task
        storage = get_storage()
        task = storage.create_task(
            title=title,
            priority=priority,
            category=category,
            due_date=due_date,
            due_time=due_time,
        )

        render_task_created(task)
        return True
