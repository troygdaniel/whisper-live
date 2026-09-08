#!/usr/bin/env python3
"""Quick test to verify all modules import correctly."""

import sys

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from whisper_live import __version__
        print(f"✓ whisper_live v{__version__}")

        from whisper_live.config import Config
        print("✓ config")

        from whisper_live.audio import AudioCapture
        print("✓ audio.capture")

        from whisper_live.transcription import TranscriptionEngine
        print("✓ transcription.engine")

        from whisper_live.output import TerminalDisplay, FileWriter
        print("✓ output.display")
        print("✓ output.file_writer")

        from whisper_live.cli import cli
        print("✓ cli.commands")

        print("\n✓ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from whisper_live.config import Config
        config = Config()

        print(f"  Sample rate: {config.sample_rate}")
        print(f"  Chunk duration: {config.chunk_duration}")
        print(f"  Model: {config.model}")
        print(f"  Output directory: {config.output_directory}")

        print("✓ Configuration loaded successfully!")
        return True

    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False


if __name__ == "__main__":
    success = test_imports() and test_config()
    sys.exit(0 if success else 1)
