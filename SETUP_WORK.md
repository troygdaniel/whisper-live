# Setting Up Whisper Live on Your Work Computer

This guide explains how to set up the enhanced Whisper Live transcription tool with speaker diarization on your RBC work computer.

## What's New

The tool now supports:
1. **Speaker Diarization** - Identifies different speakers in conversations
2. **Better Transcription** - Support for larger, more accurate models
3. **100% Offline** - All processing happens locally (after one-time setup)

## Prerequisites

- Python 3.9+ installed
- Git access to this repository
- Internet connection (one-time, for model downloads)
- ~4GB disk space (for models and dependencies)

## Step 1: Clone or Pull Latest Code

If you already have the repo:
```bash
cd ~/dev/whisper
git pull origin main
```

If starting fresh:
```bash
cd ~/dev
git clone <repo-url> whisper
cd whisper
```

## Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment (if not exists)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

## Step 3: Install Dependencies

**Option A: With Diarization (Recommended)**
```bash
pip install -r requirements.txt
```

This installs:
- faster-whisper (transcription)
- pyannote.audio (speaker diarization)
- torch + torchaudio (ML framework, ~2GB)
- UI libraries (rich, click)

**Option B: Without Diarization (Lighter)**
```bash
pip install faster-whisper sounddevice numpy click rich pyperclip pyyaml
```

Skip diarization if:
- Limited disk space
- Only transcribing single speaker
- Don't need speaker labels

## Step 4: Install the Tool

```bash
pip install -e .
```

Verify installation:
```bash
whisper-live --help
```

You should see command options including `--diarize`.

## Step 5: Test Basic Transcription

Test without diarization first:
```bash
whisper-live start --model base --no-file
```

Speak into your microphone. You should see text appear in real-time.
Press Ctrl+C to stop.

**If this works, basic setup is complete!**

## Step 6: Set Up Speaker Diarization (Optional)

If you want to identify different speakers, follow these steps:

### 6.1: Create HuggingFace Account

1. Go to https://huggingface.co/join
2. Create free account
3. Verify email

### 6.2: Accept Model License

1. Visit: https://huggingface.co/pyannote/speaker-diarization-3.1
2. Click "Agree and access repository"
3. Accept license

### 6.3: Create Access Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `whisper-live-diarization`
4. Type: **Read** (not Write)
5. Copy token (starts with `hf_...`)

### 6.4: Download Diarization Models

Run this **one-time** setup script:

```bash
cd ~/dev/whisper
source venv/bin/activate

python3 << 'EOF'
from pyannote.audio import Pipeline

# Replace YOUR_TOKEN with your actual HuggingFace token
token = "hf_YOUR_TOKEN_HERE"

print("Downloading diarization models (~1.5GB)...")
print("This only needs to be done once.\n")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=token
)

print("\n✓ Success! Models cached to ~/.cache/huggingface/")
print("You can now run whisper-live --diarize offline.\n")
EOF
```

**What this downloads:**
- Speaker identification models (~1.5GB)
- Cached to: `~/.cache/huggingface/`
- Only downloads once

### 6.5: Test Diarization

```bash
whisper-live start --model medium --diarize --no-file
```

Speak with a colleague or play a video with multiple speakers.
You should see speaker labels like `[Speaker SPEAKER_00]`.

Press Ctrl+C to stop.

**If you see speaker labels, diarization is working!**

## Step 7: Verify Offline Operation

To confirm everything works offline:

1. **Disconnect from internet**
2. Run: `whisper-live start --diarize --no-file`
3. Should work without network

If it fails, models aren't cached properly (repeat Step 6.4).

## Usage Examples

### Basic Transcription
```bash
# Microphone input
whisper-live start

# Save to specific file
whisper-live start --output meeting-notes.txt

# Use more accurate model
whisper-live start --model medium
```

### System Audio Capture

To transcribe Zoom calls, videos, or any system audio:

1. **Install BlackHole:**
   ```bash
   brew install blackhole-2ch
   ```

2. **Set up Multi-Output Device:**
   - Open "Audio MIDI Setup" (in /Applications/Utilities/)
   - Click + → Create Multi-Output Device
   - Check: "Built-in Output" + "BlackHole 2ch"
   - Right-click → Use This Device For Sound Output

3. **Transcribe system audio:**
   ```bash
   whisper-live start --source system
   ```

### With Speaker Diarization
```bash
# Microphone with speaker ID
whisper-live start --diarize

# System audio with speaker ID
whisper-live start --source system --diarize

# Best quality + speaker ID
whisper-live start --model medium --diarize
```

## Output Files

Transcripts are saved to `./transcripts/` by default:
```
./transcripts/transcript_2026-09-27_14-30-00.txt
```

**Example output with diarization:**
```
Whisper Live Transcription
Started: 2026-09-27 14:30:00
Model: medium | Source: microphone

[00:00:05] [Speaker SPEAKER_00] So I think we should focus on UX first.
[00:00:12] [Speaker SPEAKER_01] Yeah that makes sense. What are the key flows?
[00:00:25] [Speaker SPEAKER_00] The primary use case is meeting transcription.

---
Duration: 00:02:30
Ended: 2026-09-27 14:32:30
```

## Recommended Settings

**For best accuracy:**
- Model: `medium` or `large`
- With diarization: `--model medium --diarize`
- Good microphone
- Quiet environment

**For speed:**
- Model: `base` or `tiny`
- Without diarization
- Trade-off: lower accuracy

**For meetings with multiple speakers:**
- Model: `medium` (minimum)
- Always use: `--diarize`
- Consider: `--source system` for Zoom calls

## Troubleshooting

### "whisper-live: command not found"

Virtual environment not activated:
```bash
cd ~/dev/whisper
source venv/bin/activate
pip install -e .
```

### "No module named 'faster_whisper'"

Dependencies not installed:
```bash
pip install -r requirements.txt
```

### "Diarization models not found"

Models not downloaded:
- Follow Step 6.4
- Ensure valid HuggingFace token
- Check internet connection during download

### Slow transcription

- Use smaller model: `--model base` or `--model tiny`
- Diarization adds ~20-30% overhead
- Consider disabling for single speaker: remove `--diarize`

### No audio detected

List available devices:
```bash
whisper-live devices
```

Select specific device:
```bash
whisper-live start --device 0
```

## Disk Space Requirements

**Minimum (no diarization):**
- Dependencies: ~500MB
- Base model: ~140MB
- **Total: ~650MB**

**With diarization:**
- Dependencies: ~2.5GB (includes PyTorch)
- Models: ~1.5GB (Whisper + pyannote)
- **Total: ~4GB**

## Privacy & Security

**100% Offline After Setup:**
- Models cache locally
- No API calls during use
- All processing on your machine
- No data sent externally

**One-time downloads:**
- Whisper models: From HuggingFace (OpenAI)
- Diarization models: From HuggingFace (pyannote)
- After download: fully offline

**HuggingFace Token:**
- Only for initial model download
- Read-only access
- Can be revoked after download
- No tracking or telemetry

## Support & Documentation

**Quick reference:**
```bash
whisper-live --help          # Show all commands
whisper-live start --help    # Show start command options
whisper-live devices         # List audio devices
```

**Documentation:**
- [README.md](README.md) - Main documentation
- [DIARIZATION.md](DIARIZATION.md) - Detailed diarization guide
- [USAGE.md](USAGE.md) - Usage examples

**GitHub issues:**
- Report bugs or request features
- Check existing issues for solutions

## Quick Start Checklist

- [ ] Clone/pull latest code
- [ ] Create virtual environment
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Install tool (`pip install -e .`)
- [ ] Test basic transcription (`whisper-live start --no-file`)
- [ ] (Optional) Set up HuggingFace account
- [ ] (Optional) Download diarization models
- [ ] (Optional) Test diarization (`whisper-live start --diarize --no-file`)
- [ ] Verify offline operation

## Summary

**Without diarization:**
```bash
whisper-live start
```

**With diarization:**
```bash
whisper-live start --diarize
```

**System audio:**
```bash
whisper-live start --source system
```

**Everything:**
```bash
whisper-live start --model medium --source system --diarize
```

You're all set! The tool will:
- Transcribe in real-time
- Identify speakers (if `--diarize`)
- Save timestamped transcripts
- Work 100% offline

Enjoy your enhanced transcription tool!
