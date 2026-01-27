# Tasks T105-T108: Main Application Entry Point
"""Main REPL loop for Todo CLI application."""

from src.commands import register_all_commands, get_registry
from src.parsers.commands import parse_command
from src.ui.banner import render_banner
from src.ui.console import get_console
from src.ui.panels import render_unknown_command, render_invalid_input


def main() -> None:
    """
    Main entry point for Todo CLI.

    Task T105: Render banner and start REPL loop.
    """
    console = get_console()

    # Register all commands on startup
    register_all_commands()

    # Display welcome banner
    render_banner()

    # Task T106: Main REPL loop
    running = True
    while running:
        try:
            # Show prompt
            console.print("\n[bold cyan]todo>[/bold cyan] ", end="")
            user_input = input().strip()

            if not user_input:
                continue

            # Task T108: Check for slash prefix
            if not user_input.startswith("/"):
                render_invalid_input()
                continue

            # Parse command
            parsed = parse_command(user_input)

            if parsed is None:
                render_invalid_input()
                continue

            # Task T107: Get and execute command
            registry = get_registry()
            command = registry.get_command(parsed.name)

            if command is None:
                render_unknown_command(parsed.name)
                continue

            # Execute command
            result = command.execute(parsed.args)

            # Check for exit signal
            if not result and parsed.name == "exit":
                running = False

        except KeyboardInterrupt:
            console.print("\n[dim]Use /exit to quit.[/dim]")
        except EOFError:
            console.print()
            running = False
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
