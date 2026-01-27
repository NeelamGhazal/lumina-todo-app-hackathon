# Task T043: Welcome Banner per quickstart.md
"""ASCII art welcome banner for Todo CLI."""

from rich.panel import Panel
from rich.text import Text

from src.ui.console import get_console


# ASCII art logo per quickstart.md specification
BANNER_ART = """
████████╗ ██████╗ ██████╗  ██████╗
╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗
   ██║   ██║   ██║██║  ██║██║   ██║
   ██║   ██║   ██║██║  ██║██║   ██║
   ██║   ╚██████╔╝██████╔╝╚██████╔╝
   ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝
"""


def render_banner() -> None:
    """
    Render the welcome banner with ASCII art logo.

    Per quickstart.md: Professional welcome banner with app name and version.
    Uses rich Panel for styled output.
    """
    console = get_console()

    # Create styled text content
    content = Text()
    content.append(BANNER_ART, style="bold cyan")
    content.append("\n")
    content.append("        Professional Todo CLI v1.0.0", style="bold white")
    content.append("\n\n")
    content.append("   Type ", style="dim")
    content.append("/help", style="bold green")
    content.append(" for available commands", style="dim")

    # Render in a panel
    panel = Panel(
        content,
        border_style="cyan",
        padding=(1, 2),
    )

    console.print(panel)
