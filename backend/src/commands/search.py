# Tasks T084-T085: SearchCommand for /search <query>
"""Search command handler for finding tasks."""

from src.commands.base import Command
from src.storage.memory import get_storage
from src.ui.tables import render_search_results
from src.ui.panels import render_no_results, render_error


class SearchCommand(Command):
    """
    Command to search tasks by keyword.

    Usage: /search <query>
    """

    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return "Search tasks by keyword"

    @property
    def usage(self) -> str:
        return "/search <query>"

    def execute(self, args: list[str]) -> bool:
        """Execute the search command."""
        # Task T085: Query validation
        if not args:
            render_error(
                "Please provide a search term.",
                "Usage: /search <query>"
            )
            return False

        query = " ".join(args)

        storage = get_storage()
        results = storage.search(query)

        if not results:
            render_no_results(query)
        else:
            render_search_results(results, query)

        return True
