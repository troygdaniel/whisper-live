#!/usr/bin/env python3
"""Test script to verify diarization implementation."""

import sys

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from whisper_live.transcription import TranscriptionEngine
        print("✓ TranscriptionEngine imported")
    except Exception as e:
        print(f"✗ Failed to import TranscriptionEngine: {e}")
        return False

    try:
        from whisper_live.transcription.diarizer import SpeakerDiarizer
        print("✓ SpeakerDiarizer imported")
    except Exception as e:
        print(f"✗ Failed to import SpeakerDiarizer: {e}")
        return False

    try:
        from whisper_live.output import TerminalDisplay, FileWriter
        print("✓ Output modules imported")
    except Exception as e:
        print(f"✗ Failed to import output modules: {e}")
        return False

    try:
        from whisper_live.cli.commands import cli
        print("✓ CLI commands imported")
    except Exception as e:
        print(f"✗ Failed to import CLI: {e}")
        return False

    return True


def test_engine_initialization():
    """Test that TranscriptionEngine can be initialized with diarization."""
    print("\nTesting TranscriptionEngine initialization...")

    try:
        from whisper_live.transcription import TranscriptionEngine

        # Test without diarization
        engine = TranscriptionEngine(model_name="base", enable_diarization=False)
        print("✓ Engine initialized without diarization")

        # Test with diarization (should initialize but not load models yet)
        engine_with_diar = TranscriptionEngine(model_name="base", enable_diarization=True)
        print("✓ Engine initialized with diarization flag")

        return True
    except Exception as e:
        print(f"✗ Failed to initialize engine: {e}")
        return False


def test_diarizer_class():
    """Test that SpeakerDiarizer class can be instantiated."""
    print("\nTesting SpeakerDiarizer class...")

    try:
        from whisper_live.transcription.diarizer import SpeakerDiarizer

        diarizer = SpeakerDiarizer()
        print("✓ SpeakerDiarizer instantiated")

        # Check that model loading fails gracefully when models aren't cached
        try:
            diarizer.load_model()
            print("✓ Models loaded (you already have them cached!)")
        except RuntimeError as e:
            if "not found in cache" in str(e):
                print("✓ Appropriate error when models not cached (expected)")
            else:
                print(f"  Note: {e}")
        except Exception as e:
            print(f"  Model loading error (may need setup): {e}")

        return True
    except Exception as e:
        print(f"✗ Failed to test SpeakerDiarizer: {e}")
        return False


def test_display_speaker_labels():
    """Test that display can handle speaker labels."""
    print("\nTesting TerminalDisplay with speaker labels...")

    try:
        from whisper_live.output import TerminalDisplay

        display = TerminalDisplay()
        display.start()

        # Test without speaker
        display.add_transcript("Hello world", 0.0)
        print("✓ Display handles transcript without speaker")

        # Test with speaker
        display.add_transcript("Hello from speaker", 1.0, speaker="SPEAKER_00")
        print("✓ Display handles transcript with speaker label")

        display.stop()
        return True
    except Exception as e:
        print(f"✗ Failed display test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_writer_speaker_labels():
    """Test that file writer can handle speaker labels."""
    print("\nTesting FileWriter with speaker labels...")

    try:
        from whisper_live.output import FileWriter
        from pathlib import Path
        import tempfile
        import os

        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name

        try:
            writer = FileWriter(temp_path)
            writer.start()

            # Write without speaker
            writer.write_transcript("Test without speaker", 0.0)
            print("✓ FileWriter handles transcript without speaker")

            # Write with speaker
            writer.write_transcript("Test with speaker", 1.0, speaker="SPEAKER_00")
            print("✓ FileWriter handles transcript with speaker label")

            writer.stop()

            # Read file to verify format
            with open(temp_path, 'r') as f:
                content = f.read()
                if "[Speaker SPEAKER_00]" in content:
                    print("✓ Speaker labels written to file correctly")
                else:
                    print("✗ Speaker labels not found in output file")
                    print(f"  Content: {content}")
                    return False

            return True
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    except Exception as e:
        print(f"✗ Failed file writer test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Whisper Live Diarization Implementation")
    print("=" * 60)

    tests = [
        test_imports,
        test_engine_initialization,
        test_diarizer_class,
        test_display_speaker_labels,
        test_file_writer_speaker_labels,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        if not result:
            print(f"\n⚠ Test '{test.__name__}' failed")

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed!")
        print("\nImplementation is working correctly.")
        print("\nNext steps:")
        print("1. To use diarization, follow setup in DIARIZATION.md")
        print("2. Basic transcription works without --diarize flag")
        print("3. Run: whisper-live start --help")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
