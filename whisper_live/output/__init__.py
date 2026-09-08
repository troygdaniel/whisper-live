"""Output module for displaying and saving transcriptions."""

from .display import TerminalDisplay
from .file_writer import FileWriter

__all__ = ['TerminalDisplay', 'FileWriter']
