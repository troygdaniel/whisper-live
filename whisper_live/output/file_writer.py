"""File writer for saving transcriptions."""

from pathlib import Path
from datetime import datetime
from ..utils import format_timestamp, ensure_directory


class FileWriter:
    """Writes transcriptions to file."""

    def __init__(self, output_path, model_name="base", source="microphone"):
        """
        Initialize file writer.

        Args:
            output_path: Path to output file
            model_name: Name of the Whisper model being used
            source: Audio source name
        """
        self.output_path = Path(output_path)
        self.model_name = model_name
        self.source = source
        self.start_time = None
        self.file_handle = None

        # Ensure output directory exists
        ensure_directory(self.output_path.parent)

    def start(self):
        """Start writing to file."""
        self.start_time = datetime.now()

        # Open file and write header
        self.file_handle = open(self.output_path, 'w', encoding='utf-8')

        header = f"""Whisper Live Transcription
Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Model: {self.model_name} | Source: {self.source}

"""
        self.file_handle.write(header)
        self.file_handle.flush()

    def write_transcript(self, text, timestamp):
        """
        Write a transcript line to file.

        Args:
            text: Transcribed text
            timestamp: Timestamp in seconds
        """
        if not text or not text.strip():
            return

        if self.file_handle is None:
            return

        formatted_time = format_timestamp(timestamp)
        line = f"[{formatted_time}] {text.strip()}\n"

        self.file_handle.write(line)
        self.file_handle.flush()

    def stop(self):
        """Stop writing and close file."""
        if self.file_handle is None:
            return

        # Write footer
        end_time = datetime.now()
        duration = end_time - self.start_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        footer = f"""
---
Duration: {hours:02d}:{minutes:02d}:{seconds:02d}
Ended: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.file_handle.write(footer)
        self.file_handle.flush()
        self.file_handle.close()
        self.file_handle = None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
