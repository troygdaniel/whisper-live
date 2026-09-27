# Whisper Live Transcription

Real-time audio transcription using OpenAI Whisper. Runs completely offline with no API calls.

## Features

- **Real-time transcription** - See text appear as you speak
- **Completely offline** - No internet required, no API calls
- **Privacy-focused** - All processing happens locally
- **Speaker diarization** - Identify different speakers (optional, offline)
- **Multiple models** - Choose speed vs accuracy
- **Auto-save** - Timestamped transcript files
- **Live terminal display** - Rich formatted output
- **System audio capture** - Transcribe Zoom calls, videos, podcasts

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

**Microphone (default):**
```bash
whisper-live start                    # Default microphone
whisper-live start --model tiny       # Faster model
whisper-live start --model small      # More accurate
whisper-live start --output notes.txt # Custom filename
whisper-live start --no-file          # Terminal only
whisper-live start --language en      # Force language
whisper-live start --diarize          # Identify different speakers
```

**System Audio (requires BlackHole):**
```bash
whisper-live start --source system       # Capture system audio
whisper-live start --device "BlackHole"  # Select device by name
whisper-live start --device 5            # Select device by index
whisper-live start --source system --diarize  # System audio + speaker ID
```

**Speaker Diarization:**
```bash
whisper-live start --diarize                    # Enable speaker identification
whisper-live start --model medium --diarize     # Better accuracy for speakers
whisper-live start --source system --diarize    # Identify speakers in system audio
```

See [DIARIZATION.md](DIARIZATION.md) for setup instructions (one-time, ~10 minutes).

### List Audio Devices
```bash
whisper-live devices
```

## Models

| Model | Speed | Accuracy | Diarization Quality | Use Case |
|-------|-------|----------|---------------------|----------|
| `tiny` | ~1x realtime | Lower | Lower | Quick notes, casual use |
| `base` | ~0.3x realtime | Good | Good | **Recommended** - meetings, general use |
| `small` | ~0.15x realtime | Higher | Better | Important transcription |
| `medium` | ~0.1x realtime | Very High | Better | **Best for diarization** |
| `large` | ~0.05x realtime | Highest | Best | Maximum accuracy (slow) |

Models download automatically on first use:
- `base`: ~140MB
- `medium`: ~1.5GB
- `large`: ~3GB

For diarization, use `medium` or larger for best speaker identification.

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

**With speaker diarization** (`--diarize`):
```
Whisper Live Transcription
Started: 2026-09-27 14:30:00
Model: medium | Source: microphone

[00:00:05] [Speaker SPEAKER_00] So I think we should focus on the user experience first.
[00:00:12] [Speaker SPEAKER_01] Yeah that makes sense. What are the key flows?
[00:00:25] [Speaker SPEAKER_00] Well the primary use case is meeting transcription.

---
Duration: 00:01:45
Ended: 2026-09-27 14:31:45
```

## System Audio Capture

To transcribe audio playing on your computer (Zoom calls, YouTube videos, podcasts):

### 1. Install BlackHole

```bash
brew install blackhole-2ch
```

### 2. Create Multi-Output Device

1. Open **Audio MIDI Setup** app (in /Applications/Utilities/)
2. Click the **+** button (bottom left) → **Create Multi-Output Device**
3. Check both:
   - **Built-in Output** (so you can hear audio)
   - **BlackHole 2ch** (captures audio for whisper-live)
4. Right-click the Multi-Output Device → **Use This Device For Sound Output**

### 3. Start Transcription

```bash
whisper-live start --source system
```

This captures all system audio playing through your speakers/headphones.

### Use Cases
- Transcribe Zoom/Teams meetings
- Capture YouTube video audio
- Transcribe podcasts
- Convert any audio playback to text

**Note:** You'll still hear the audio normally while transcribing.

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

## Future Enhancements

- ✓ **System audio capture** - Implemented! Use `--source system`
- ✓ **Speaker diarization** - Implemented! Use `--diarize`
- Rich terminal UI with panels
- Clipboard auto-copy
- Multiple output formats (JSON, Markdown)
- Configuration commands
- Speaker name customization (map SPEAKER_00 → "Alice")

## See Also

- [DIARIZATION.md](DIARIZATION.md) - **Speaker diarization setup guide** (one-time setup)
- [USAGE.md](USAGE.md) - Detailed usage guide
- `config.yaml` - Configuration options
- `test_imports.py` - Verify installation
