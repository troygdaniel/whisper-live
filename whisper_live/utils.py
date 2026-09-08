"""Shared utilities for Whisper Live."""

from datetime import datetime, timedelta


def format_timestamp(seconds):
    """Format seconds into HH:MM:SS timestamp."""
    td = timedelta(seconds=int(seconds))
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_output_filename(custom_name=None):
    """Generate output filename with timestamp."""
    if custom_name:
        return custom_name

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"transcript_{timestamp}.txt"


def ensure_directory(path):
    """Ensure directory exists, create if it doesn't."""
    from pathlib import Path
    Path(path).mkdir(parents=True, exist_ok=True)
