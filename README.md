# Whisper Live Transcription

Real-time audio transcription using OpenAI Whisper. Runs completely offline with no API calls.

## Features

- **Real-time transcription** - See text appear as you speak
- **Completely offline** - No internet required, no API calls
- **Privacy-focused** - All processing happens locally
- **Multiple models** - Choose speed vs accuracy
- **Auto-save** - Timestamped transcript files
- **Live terminal display** - Rich formatted output

## Installation

```bash
cd ~/dev/whisper
/opt/homebrew/bin/python3.13 -m venv venv
source venv/bin/activate
pip install -e .
```

Or use the existing venv:
```bash
cd ~/dev/whisper
source venv/bin/activate
```

## Quick Start

```bash
# Start transcription (base model, auto filename)
whisper-live start

# Speak into your microphone
# Press Ctrl+C to stop and save
```

## Commands

### Start Transcription
```bash
whisper-live start                    # Default settings
whisper-live start --model tiny       # Faster model
whisper-live start --model small      # More accurate
whisper-live start --output notes.txt # Custom filename
whisper-live start --no-file          # Terminal only
whisper-live start --language en      # Force language
```

### List Audio Devices
```bash
whisper-live devices
```

## Models

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| `tiny` | ~1x realtime | Lower | Quick notes, casual use |
| `base` | ~0.3x realtime | Good | **Recommended** - meetings, general use |
| `small` | ~0.15x realtime | Higher | Important transcription, accuracy critical |

Models download automatically on first use (~140MB for base).

## Output

Transcripts are saved to `./transcripts/` with format:
```
transcript_YYYY-MM-DD_HH-MM-SS.txt
```

Example output:
```
Whisper Live Transcription
Started: 2026-09-07 21:45:12
Model: base | Source: microphone

[00:00:05] So I think we should focus on the user experience first.
[00:00:12] Yeah that makes sense. What are the key flows we need to support?
[00:00:25] Well the primary use case is real time meeting transcription.

---
Duration: 00:01:45
Ended: 2026-09-07 21:46:57
```

## Integration with Claude

Claude can start whisper-live and read the results:

```bash
whisper-live start --output meeting_notes.txt
# ... speak during meeting ...
# Ctrl+C to stop
# Claude reads meeting_notes.txt
```

## Project Structure

```
whisper/
├── whisper_live/          # Main package
│   ├── audio/            # Microphone capture
│   ├── transcription/    # Whisper engine
│   ├── output/           # Display & file writing
│   └── cli/              # Command-line interface
├── transcripts/          # Output directory
├── config.yaml           # Configuration
└── venv/                 # Virtual environment
```

## Technical Details

- **Audio**: sounddevice (16kHz mono, 2-second chunks)
- **Transcription**: faster-whisper (4-5x faster than official)
- **Display**: rich (formatted terminal output)
- **Platform**: macOS (tested), Linux (should work), Windows (untested)

## Requirements

- Python 3.9+ (tested with 3.13)
- Microphone access
- ~500MB disk space (for models + cache)

## Troubleshooting

**No audio detected:**
```bash
whisper-live devices  # Check available microphones
```

**Slow transcription:**
```bash
whisper-live start --model tiny  # Use faster model
```

**Model download issues:**
- Models cache to `~/.cache/huggingface/`
- Delete cache and retry if corrupted

## Future Enhancements (Phase 2)

- System audio capture (via BlackHole)
- Rich terminal UI with panels
- Clipboard auto-copy
- Multiple output formats (JSON, Markdown)
- Configuration commands

## See Also

- `USAGE.md` - Detailed usage guide
- `config.yaml` - Configuration options
- `test_imports.py` - Verify installation
