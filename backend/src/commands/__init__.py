# Task T003, T109: Package initialization for commands
"""Command handlers for Todo CLI."""

from src.commands.base import Command, CommandRegistry, get_registry, reset_registry

# Import all command classes
from src.commands.help import HelpCommand
from src.commands.add import AddCommand
from src.commands.list import ListCommand
from src.commands.show import ShowCommand
from src.commands.update import UpdateCommand
from src.commands.complete import CompleteCommand
from src.commands.delete import DeleteCommand
from src.commands.search import SearchCommand
from src.commands.stats import StatsCommand
from src.commands.exit import ExitCommand


def register_all_commands() -> None:
    """Register all commands with the global registry."""
    registry = get_registry()

    # Task T109: Register all 10 commands
    registry.register(HelpCommand())
    registry.register(AddCommand())
    registry.register(ListCommand())
    registry.register(ShowCommand())
    registry.register(UpdateCommand())
    registry.register(CompleteCommand())
    registry.register(DeleteCommand())
    registry.register(SearchCommand())
    registry.register(StatsCommand())
    registry.register(ExitCommand())


__all__ = [
    "Command",
    "CommandRegistry",
    "get_registry",
    "reset_registry",
    "register_all_commands",
    "HelpCommand",
    "AddCommand",
    "ListCommand",
    "ShowCommand",
    "UpdateCommand",
    "CompleteCommand",
    "DeleteCommand",
    "SearchCommand",
    "StatsCommand",
    "ExitCommand",
]
