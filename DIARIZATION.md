# Speaker Diarization Setup Guide

This guide explains how to set up and use speaker diarization (identifying different speakers) in Whisper Live.

## What is Speaker Diarization?

Speaker diarization identifies and labels different speakers in audio, producing transcripts like:

```
[00:00:05] [Speaker SPEAKER_00] So I think we should focus on the user experience first.
[00:00:12] [Speaker SPEAKER_01] Yeah that makes sense. What are the key flows?
[00:00:25] [Speaker SPEAKER_00] Well the primary use case is real time transcription.
```

## Privacy & Offline Operation

**100% Offline After Setup:**
- Models download once from HuggingFace (requires internet + HF account)
- Models cache locally to `~/.cache/huggingface/`
- After download, runs completely offline
- No data ever sent to external servers
- All processing happens on your Mac

## Installation

### 1. Install Dependencies

```bash
cd ~/dev/whisper
source venv/bin/activate
pip install -r requirements.txt
```

This installs:
- `pyannote.audio` - Speaker diarization library
- `torch` - PyTorch (ML framework)
- `torchaudio` - Audio processing for PyTorch

**Note:** This adds ~2GB of dependencies (PyTorch + models).

### 2. Create HuggingFace Account

You need a HuggingFace account to download the diarization models (one-time):

1. Go to https://huggingface.co/join
2. Create a free account
3. Verify your email

### 3. Accept Model License

The diarization model requires accepting a license:

1. Visit: https://huggingface.co/pyannote/speaker-diarization-3.1
2. Click "Agree and access repository"
3. Accept the license terms

### 4. Create Access Token

Create a token to download the model:

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `whisper-live-diarization`
4. Type: **Read** (not Write)
5. Click "Generate token"
6. Copy the token (starts with `hf_...`)

### 5. Download Models (One-Time)

Run this Python script to download and cache the models:

```bash
cd ~/dev/whisper
source venv/bin/activate
python3 << 'EOF'
from pyannote.audio import Pipeline

# Replace with your HuggingFace token
token = "hf_YOUR_TOKEN_HERE"

print("Downloading speaker diarization models...")
print("This is a one-time download (~1.5GB)")
print("")

# Use 'token' parameter (newer pyannote versions)
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=token
)

print("")
print("✓ Models downloaded and cached successfully!")
print("Location: ~/.cache/huggingface/")
print("")
print("You can now use --diarize flag offline.")
EOF
```

**What gets downloaded:**
- Speaker embedding model (~250MB)
- Segmentation model (~45MB)
- Voice activity detection model (~45MB)
- PyTorch models cache (~1GB)

**Total:** ~1.5GB

### 6. Verify Installation

Test that diarization works:

```bash
whisper-live start --model base --diarize --no-file
```

Speak into your microphone. You should see speaker labels like `[Speaker SPEAKER_00]` appear.

Press Ctrl+C to stop.

## Usage

### Basic Usage

Add `--diarize` flag to any transcription command:

```bash
# Microphone with diarization
whisper-live start --diarize

# System audio with diarization
whisper-live start --source system --diarize

# Better accuracy + diarization
whisper-live start --model medium --diarize
```

### Output Format

**Terminal output:**
```
[00:00:05] [Speaker SPEAKER_00] So I think we should focus on UX first.
[00:00:12] [Speaker SPEAKER_01] Yeah that makes sense.
[00:00:25] [Speaker SPEAKER_00] Well the primary use case is meetings.
```

**File output** (same format):
```
Whisper Live Transcription
Started: 2026-09-27 14:30:00
Model: base | Source: microphone

[00:00:05] [Speaker SPEAKER_00] So I think we should focus on UX first.
[00:00:12] [Speaker SPEAKER_01] Yeah that makes sense.
[00:00:25] [Speaker SPEAKER_00] Well the primary use case is meetings.

---
Duration: 00:02:30
Ended: 2026-09-27 14:32:30
```

### Recommended Settings

**For best diarization accuracy:**
- Use `--model medium` or larger
- Ensure speakers speak clearly
- Minimize background noise
- Use good quality microphone

**Performance vs Accuracy:**

| Model | Transcription Quality | Diarization Quality | Speed |
|-------|----------------------|---------------------|-------|
| `tiny` | Lower | Lower | ~1x realtime |
| `base` | Good | Good | ~0.3x realtime |
| `medium` | Higher | Better | ~0.15x realtime |
| `large` | Highest | Best | ~0.1x realtime |

## Offline Verification

To confirm you're running offline:

1. Disconnect from internet
2. Run: `whisper-live start --diarize --no-file`
3. If models are cached, it should work without network

If you get an error about missing models:
- You need to download them first (step 5 above)
- Models must be in `~/.cache/huggingface/`

## Use Cases

**Perfect for:**
- Meeting transcription (identify participants)
- Interview recordings (distinguish interviewer/interviewee)
- Podcast transcription (separate hosts and guests)
- Phone calls (identify caller/receiver)
- Multi-person conversations

**Not ideal for:**
- Single speaker (unnecessary overhead)
- Very noisy environments
- Overlapping speech (diarization may struggle)

## Troubleshooting

### "Diarization models not found in cache"

You need to download models first:
- Follow step 5 above
- Ensure you have a valid HuggingFace token
- Check internet connection during download

### "pyannote.audio not installed"

Run:
```bash
pip install pyannote.audio torch torchaudio
```

### Speaker labels are wrong/inconsistent

- Speaker labels (SPEAKER_00, SPEAKER_01) are arbitrary
- They're consistent within a session but not across sessions
- SPEAKER_00 in one recording ≠ SPEAKER_00 in another
- Labels just mean "speaker #1", "speaker #2", etc.

### Diarization is slow

- Use a smaller Whisper model (`--model base`)
- Diarization adds ~20-30% overhead
- Running on CPU (no GPU) is slower
- Consider disabling for single-speaker scenarios

### No speaker labels appear

- Ensure `--diarize` flag is used
- Check that audio contains multiple speakers
- Models may need clear speaker transitions
- Try speaking more distinctly

## Technical Details

### How It Works

1. **Whisper** transcribes audio to text
2. **pyannote.audio** analyzes same audio for speakers
3. Segments are matched: transcription ↔ speaker
4. Output combines text + speaker labels

### Models Used

- **Whisper**: faster-whisper (transcription)
- **pyannote**: speaker-diarization-3.1 (speaker identification)

Both run locally, no cloud API calls.

### Performance Impact

- **CPU**: +20-30% overhead vs transcription-only
- **RAM**: +500MB-1GB (PyTorch + models)
- **Disk**: +1.5GB (cached models)

### Cache Location

Models are stored in:
```
~/.cache/huggingface/hub/
```

To free up space:
```bash
rm -rf ~/.cache/huggingface/
```

(You'll need to re-download if you delete this)

## Security Notes

**Why HuggingFace Account Required:**
- Models are gated (require license acceptance)
- HuggingFace enforces this via auth token
- Only needed for initial download
- No tracking or telemetry after download

**Token Security:**
- Use **Read-only** tokens (not Write)
- Token only accesses public models
- Can't modify your HF account
- Can be revoked anytime at https://huggingface.co/settings/tokens

**Privacy Guarantee:**
- After model download, 100% offline
- No network calls during transcription
- No data sent to HuggingFace or anyone
- All processing local to your Mac

## Advanced: Manual Model Download

If you prefer not to use a token, you can manually download models:

1. Download from: https://huggingface.co/pyannote/speaker-diarization-3.1
2. Place in `~/.cache/huggingface/hub/`
3. Follow HuggingFace cache directory structure

(Not recommended - token method is easier)

## Uninstalling Diarization

To remove diarization support:

1. **Remove packages:**
   ```bash
   pip uninstall pyannote.audio torch torchaudio
   ```

2. **Remove cached models:**
   ```bash
   rm -rf ~/.cache/huggingface/
   ```

3. **Use whisper-live without `--diarize` flag**

Total space reclaimed: ~3.5GB

## See Also

- Main documentation: [README.md](README.md)
- Usage guide: [USAGE.md](USAGE.md)
- pyannote.audio: https://github.com/pyannote/pyannote-audio
- HuggingFace Models: https://huggingface.co/pyannote
