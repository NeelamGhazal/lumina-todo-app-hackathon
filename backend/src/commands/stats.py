# Tasks T091-T092: StatsCommand for /stats
"""Stats command handler for viewing task statistics."""

from collections import Counter

from src.commands.base import Command
from src.storage.memory import get_storage
from src.models.task import Priority, Category
from src.ui.panels import render_stats_dashboard, render_no_stats


class StatsCommand(Command):
    """
    Command to display task statistics dashboard.

    Usage: /stats
    """

    @property
    def name(self) -> str:
        return "stats"

    @property
    def description(self) -> str:
        return "View task statistics"

    @property
    def usage(self) -> str:
        return "/stats"

    def execute(self, args: list[str]) -> bool:
        """Execute the stats command."""
        storage = get_storage()
        tasks = storage.list_all()

        if not tasks:
            render_no_stats()
            return True

        # Task T092: Calculate statistics
        total = len(tasks)
        completed = sum(1 for t in tasks if t.is_completed)
        pending = total - completed

        # Count by priority
        by_priority: dict[Priority, int] = Counter()
        for task in tasks:
            priority = Priority(task.priority) if isinstance(task.priority, str) else task.priority
            by_priority[priority] += 1

        # Count by category
        by_category: dict[Category, int] = Counter()
        for task in tasks:
            category = Category(task.category) if isinstance(task.category, str) else task.category
            by_category[category] += 1

        render_stats_dashboard(
            total=total,
            completed=completed,
            pending=pending,
            by_priority=dict(by_priority),
            by_category=dict(by_category),
        )

        return True
