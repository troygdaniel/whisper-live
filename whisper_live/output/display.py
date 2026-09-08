"""Terminal display for live transcription using rich."""

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from datetime import datetime
from ..utils import format_timestamp


class TerminalDisplay:
    """Live terminal display for transcriptions."""

    def __init__(self, model_name="base", source="microphone", max_lines=20):
        """
        Initialize terminal display.

        Args:
            model_name: Name of the Whisper model being used
            source: Audio source name
            max_lines: Maximum number of transcript lines to show
        """
        self.console = Console()
        self.model_name = model_name
        self.source = source
        self.max_lines = max_lines

        self.transcripts = []
        self.start_time = datetime.now()
        self.is_active = False
        self.live = None

    def start(self):
        """Start the live display."""
        self.is_active = True
        self.start_time = datetime.now()
        self.transcripts = []

        # Print header
        self.console.print("\n[bold cyan]Whisper Live Transcription[/bold cyan]")
        self.console.print(f"Model: [yellow]{self.model_name}[/yellow] | "
                          f"Source: [yellow]{self.source}[/yellow]\n")

    def add_transcript(self, text, timestamp):
        """
        Add a new transcript line.

        Args:
            text: Transcribed text
            timestamp: Timestamp in seconds
        """
        if not text or not text.strip():
            return

        formatted_time = format_timestamp(timestamp)
        self.transcripts.append((formatted_time, text.strip()))

        # Keep only the last max_lines
        if len(self.transcripts) > self.max_lines:
            self.transcripts = self.transcripts[-self.max_lines:]

        # Display the new line
        self.console.print(f"[dim]{formatted_time}[/dim] {text.strip()}")

    def show_status(self, message):
        """Show a status message."""
        self.console.print(f"[dim italic]{message}[/dim italic]")

    def stop(self):
        """Stop the display and show summary."""
        self.is_active = False

        # Calculate session duration
        duration = datetime.now() - self.start_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        self.console.print(f"\n[dim]Session duration: {hours:02d}:{minutes:02d}:{seconds:02d}[/dim]")

    def clear(self):
        """Clear the display."""
        self.console.clear()

    def print_error(self, message):
        """Print an error message."""
        self.console.print(f"[bold red]Error:[/bold red] {message}")

    def print_info(self, message):
        """Print an info message."""
        self.console.print(f"[cyan]{message}[/cyan]")
