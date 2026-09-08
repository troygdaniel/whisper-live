"""CLI commands for Whisper Live."""

import click
import signal
import sys
from pathlib import Path

from ..config import Config
from ..audio import AudioCapture
from ..transcription import TranscriptionEngine
from ..output import TerminalDisplay, FileWriter
from ..utils import get_output_filename, ensure_directory


class TranscriptionSession:
    """Manages a transcription session."""

    def __init__(self, model_name, output_path, language=None, device=None, source_name="microphone"):
        self.model_name = model_name
        self.output_path = output_path
        self.language = language
        self.device = device
        self.source_name = source_name

        self.config = Config()
        self.audio = None
        self.engine = None
        self.display = None
        self.writer = None
        self.is_running = False

    def start(self):
        """Start the transcription session."""
        # Initialize components
        self.display = TerminalDisplay(
            model_name=self.model_name,
            source=self.source_name
        )
        self.display.start()

        # Load transcription model
        self.display.show_status("Loading Whisper model (this may take a moment on first run)...")
        self.engine = TranscriptionEngine(
            model_name=self.model_name,
            language=self.language
        )
        self.engine.load_model()
        self.display.show_status("Model loaded successfully")

        # Start audio capture
        self.audio = AudioCapture(
            sample_rate=self.config.sample_rate,
            chunk_duration=self.config.chunk_duration,
            device=self.device
        )
        self.audio.start()

        # Start file writer
        if self.output_path:
            self.writer = FileWriter(
                self.output_path,
                model_name=self.model_name,
                source=self.source_name
            )
            self.writer.start()
            self.display.print_info(f"Saving to: {self.output_path}")

        self.display.print_info("Recording... (Press Ctrl+C to stop)\n")
        self.is_running = True

        # Main transcription loop
        try:
            self._transcription_loop()
        except KeyboardInterrupt:
            self.stop()

    def _transcription_loop(self):
        """Main loop for processing audio chunks."""
        while self.is_running:
            # Get next audio chunk (wait up to 0.5 seconds)
            chunk = self.audio.get_chunk(timeout=0.5)

            if chunk is None:
                continue

            # Transcribe the chunk
            try:
                result = self.engine.transcribe_chunk(chunk, self.config.sample_rate)

                if result['text']:
                    # Display in terminal
                    self.display.add_transcript(result['text'], result['start'])

                    # Write to file
                    if self.writer:
                        self.writer.write_transcript(result['text'], result['start'])

            except Exception as e:
                self.display.print_error(f"Transcription error: {e}")

    def stop(self):
        """Stop the transcription session."""
        if not self.is_running:
            return

        self.is_running = False

        self.display.print_info("\nStopping...")

        # Stop audio capture
        if self.audio:
            self.audio.stop()

        # Process any remaining audio chunks
        while self.audio and self.audio.has_data():
            chunk = self.audio.get_chunk(timeout=0.1)
            if chunk is not None:
                try:
                    result = self.engine.transcribe_chunk(chunk, self.config.sample_rate)
                    if result['text']:
                        self.display.add_transcript(result['text'], result['start'])
                        if self.writer:
                            self.writer.write_transcript(result['text'], result['start'])
                except:
                    pass

        # Close file writer
        if self.writer:
            self.writer.stop()
            self.display.print_info(f"Transcript saved to: {self.output_path}")

        # Stop display
        if self.display:
            self.display.stop()


@click.group()
def cli():
    """Whisper Live - Real-time audio transcription."""
    pass


@cli.command()
@click.option('--model', default='base',
              type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Whisper model to use (default: base)')
@click.option('--output', default=None,
              help='Output file path (default: auto-generated timestamp)')
@click.option('--language', default=None,
              help='Language code (default: auto-detect)')
@click.option('--no-file', is_flag=True,
              help='Disable file output (terminal only)')
@click.option('--device', default=None,
              help='Audio device index or name pattern (e.g., "BlackHole", "Microphone")')
@click.option('--source', default=None,
              type=click.Choice(['mic', 'system', 'blackhole']),
              help='Audio source shortcut (mic=default, system/blackhole=system audio)')
def start(model, output, language, no_file, device, source):
    """Start live transcription from microphone or system audio."""

    # Determine device and source name
    device_index = None
    source_name = "microphone"

    if source:
        # Handle source shortcuts
        if source in ['system', 'blackhole']:
            device_index = AudioCapture.find_device('blackhole')
            if device_index is None:
                click.echo("Error: BlackHole device not found.")
                click.echo("\nTo capture system audio, install BlackHole:")
                click.echo("  brew install blackhole-2ch")
                click.echo("\nThen set up Multi-Output Device in Audio MIDI Setup.")
                click.echo("See README for detailed instructions.")
                sys.exit(1)
            source_name = "system audio (BlackHole)"
    elif device:
        # Try to parse device as integer index first
        try:
            device_index = int(device)
            device_name = AudioCapture.get_device_name(device_index)
            source_name = device_name
        except ValueError:
            # Not an integer, treat as name pattern
            device_index = AudioCapture.find_device(device)
            if device_index is None:
                click.echo(f"Error: No device found matching '{device}'")
                click.echo("\nRun 'whisper-live devices' to see available devices.")
                sys.exit(1)
            source_name = AudioCapture.get_device_name(device_index)

    # Show selected device
    if device_index is not None:
        click.echo(f"Using device: {source_name}\n")

    # Determine output path
    config = Config()
    if no_file:
        output_path = None
    else:
        if output is None:
            # Auto-generate filename
            ensure_directory(config.output_directory)
            filename = get_output_filename()
            output_path = Path(config.output_directory) / filename
        else:
            output_path = Path(output)
            ensure_directory(output_path.parent)

    # Create and start session
    session = TranscriptionSession(
        model_name=model,
        output_path=output_path,
        language=language,
        device=device_index,
        source_name=source_name
    )

    # Set up signal handler for graceful shutdown
    def signal_handler(sig, frame):
        session.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start transcription
    session.start()


@cli.command()
def devices():
    """List available audio input devices."""
    import sounddevice as sd

    click.echo("Available audio input devices:\n")
    devices = sd.query_devices()

    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            click.echo(f"[{i}] {device['name']}")
            click.echo(f"    Channels: {device['max_input_channels']}")
            click.echo(f"    Sample rate: {device['default_samplerate']} Hz\n")


if __name__ == '__main__':
    cli()
