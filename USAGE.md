# Whisper Live - Usage Guide

## Quick Start

1. Activate virtual environment:
```bash
source venv/bin/activate
```

2. Start transcription:
```bash
whisper-live start
```

3. Speak into your microphone. You'll see transcriptions appear in the terminal.

4. Stop with `Ctrl+C`. The transcript will be saved automatically.

## Commands

### Start Transcription
```bash
whisper-live start                    # Default (base model, auto filename)
whisper-live start --model tiny       # Faster, less accurate
whisper-live start --model small      # Slower, more accurate
whisper-live start --output meeting.txt  # Custom filename
whisper-live start --no-file          # Terminal only (don't save)
whisper-live start --language en      # Force English
```

### List Audio Devices
```bash
whisper-live devices
```

## Models

- **tiny**: Fastest, lowest accuracy (~1x realtime)
- **base**: Balanced (default, ~0.3x realtime) ← Recommended
- **small**: Slower, higher accuracy (~0.15x realtime)
- **medium**: Very slow, very accurate (not recommended for real-time)

On first run, the model will download automatically (~140MB for base).

## Output

Transcripts are saved to `./transcripts/` with format:
```
transcript_YYYY-MM-DD_HH-MM-SS.txt
```

Example content:
```
Whisper Live Transcription
Started: 2026-09-07 21:45:12
Model: base | Source: microphone

[00:00:05] So I think we should focus on the user experience first.
[00:00:12] Yeah that makes sense. What are the key flows we need to support?

---
Duration: 00:01:45
Ended: 2026-09-07 21:46:57
```

## Tips

- Speak clearly and avoid background noise
- Use `tiny` model for casual notes
- Use `base` model for meetings (good balance)
- Use `small` model for important transcription accuracy
- Check `transcripts/` folder for saved files

## Integration with Claude

Claude can invoke whisper-live and then read the transcript:

```bash
# Start transcription
whisper-live start --output ./meeting_notes.txt

# Speak during meeting...
# Press Ctrl+C when done

# Claude can then read the file
# (Claude will use Read tool on meeting_notes.txt)
```

## Troubleshooting

### No audio / microphone not working
```bash
whisper-live devices  # Check which device is being used
```

### Model download slow
- Models are cached after first download
- Located in `~/.cache/huggingface/`

### Transcription quality issues
- Try a larger model (--model small)
- Ensure microphone is close and clear
- Check for background noise

### Python version issues
- Requires Python 3.9+
- Tested with Python 3.13
