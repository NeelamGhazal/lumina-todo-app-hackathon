# Tasks T030-T032: Base Command Interface per plan.md
"""Base command interface and registry for Todo CLI commands."""

from abc import ABC, abstractmethod
from typing import Optional


# Task T030: Implement Command ABC
class Command(ABC):
    """
    Abstract base class for all CLI commands.

    All commands must implement the execute() method.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name (without / prefix)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what the command does."""
        pass

    @property
    @abstractmethod
    def usage(self) -> str:
        """Usage syntax for help display."""
        pass

    @abstractmethod
    def execute(self, args: list[str]) -> bool:
        """
        Execute the command with given arguments.

        Args:
            args: Command arguments (already parsed).

        Returns:
            True if command executed successfully, False otherwise.
            For /exit command, returns False to signal exit.
        """
        pass


# Task T031: Implement CommandRegistry class
class CommandRegistry:
    """
    Registry for managing available commands.

    Provides command lookup and listing functionality.
    """

    def __init__(self) -> None:
        """Initialize empty command registry."""
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """
        Register a command.

        Args:
            command: Command instance to register.
        """
        self._commands[command.name.lower()] = command

    def get_command(self, name: str) -> Optional[Command]:
        """
        Get a command by name (case-insensitive).

        Args:
            name: Command name (without / prefix).

        Returns:
            Command if found, None otherwise.
        """
        return self._commands.get(name.lower())

    def list_commands(self) -> list[Command]:
        """
        Get all registered commands.

        Returns:
            List of all registered commands.
        """
        return list(self._commands.values())

    def has_command(self, name: str) -> bool:
        """Check if a command is registered."""
        return name.lower() in self._commands


# Task T032: get_registry() singleton
_registry: Optional[CommandRegistry] = None


def get_registry() -> CommandRegistry:
    """
    Get the global CommandRegistry singleton instance.

    Returns:
        The shared CommandRegistry instance.
    """
    global _registry
    if _registry is None:
        _registry = CommandRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the registry singleton (for testing)."""
    global _registry
    _registry = None
