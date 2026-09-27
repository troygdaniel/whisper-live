# Diarization Setup - Claude Assisted Guide

This guide is for Claude instances to help users set up speaker diarization.

## Prerequisites Check

```bash
# 1. Check if models already cached
ls ~/.cache/huggingface/hub/ | grep -i pyannote

# 2. Check if HF token exists
cat ~/.huggingface/token 2>/dev/null
```

If models exist, skip to "Verify Installation" at bottom.

## Step 1: Get HuggingFace Token (User Action Required)

User must do this in browser:

1. **Create account** (if needed): https://huggingface.co/join
2. **Accept model license**: https://huggingface.co/pyannote/speaker-diarization-3.1
   - Click "Agree and access repository"
3. **Create token**: https://huggingface.co/settings/tokens
   - Click "New token"
   - Name: `whisper-live-diarization`
   - Type: **Read** (not Write)
   - Click "Generate token"
   - Copy token (starts with `hf_`)

**Ask user:** "Please go to those URLs and get your token, then paste it here."

## Step 2: Save Token Securely

```bash
# Create directory
mkdir -p ~/.huggingface

# Save token (user will provide the actual token)
echo "hf_YOUR_TOKEN_HERE" > ~/.huggingface/token

# Secure it
chmod 600 ~/.huggingface/token

# Verify
cat ~/.huggingface/token
```

## Step 3: Download Models

```bash
cd ~/dev/whisper
source venv/bin/activate

python3 << 'EOF'
import os
from pyannote.audio import Pipeline

# Read token from file
with open(os.path.expanduser("~/.huggingface/token"), "r") as f:
    token = f.read().strip()

print("=" * 60)
print("Downloading pyannote speaker-diarization-3.1 models")
print("This is a one-time download (~1.5GB)")
print("=" * 60)
print("")

try:
    # Download and cache models
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=token
    )

    print("")
    print("=" * 60)
    print("✓ SUCCESS!")
    print("=" * 60)
    print("Models cached to: ~/.cache/huggingface/hub/")
    print("")
    print("You can now use: whisper-live start --diarize")
    print("Models will work offline from now on.")
    print("=" * 60)

except Exception as e:
    print("")
    print("=" * 60)
    print("✗ ERROR")
    print("=" * 60)
    print(f"Error: {e}")
    print("")
    print("Common issues:")
    print("1. Invalid token - check it starts with 'hf_'")
    print("2. Haven't accepted license at:")
    print("   https://huggingface.co/pyannote/speaker-diarization-3.1")
    print("3. No internet connection")
    print("=" * 60)
    exit(1)
EOF
```

## Step 4: Verify Installation

```bash
cd ~/dev/whisper
source venv/bin/activate

python3 << 'EOF'
from pyannote.audio import Pipeline
import os

print("Testing offline model loading...")

try:
    # Load without token (should work from cache)
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1"
    )
    print("✓ Models load from cache (offline mode works!)")
    print("")
    print("Setup complete! You can now use:")
    print("  whisper-live start --diarize")

except Exception as e:
    print(f"✗ Error loading models: {e}")
    print("")
    print("Models may not be properly cached.")
    print("Try running Step 3 again.")
    exit(1)
EOF
```

## Step 5: Test with Whisper Live

```bash
# Quick test (no file output)
whisper-live start --model base --diarize --no-file

# Speak into microphone
# Should see: [Speaker SPEAKER_00] before text
# Press Ctrl+C to stop
```

## Troubleshooting

### "Pipeline.from_pretrained() got an unexpected keyword argument 'use_auth_token'"

Old documentation used `use_auth_token`. Current version uses `token`.
The code above is already fixed.

### "Repository not found"

- You haven't accepted the license
- Go to: https://huggingface.co/pyannote/speaker-diarization-3.1
- Click "Agree and access repository"

### "Invalid token"

- Token should start with `hf_`
- Check: `cat ~/.huggingface/token`
- Create new token: https://huggingface.co/settings/tokens

### Models won't load offline

- Check cache exists: `ls ~/.cache/huggingface/hub/ | grep pyannote`
- Re-run Step 3 if empty

## For Claude: Quick Command Summary

When user says "set up diarization":

1. Check prerequisites (see top)
2. If no token: Send user to get token, save it with Step 2
3. Run download script (Step 3)
4. Verify with Step 4
5. Test with Step 5

**Important:** User MUST do browser steps themselves (get token, accept license).
Claude can do everything else (save token, download models, verify, test).

## Files Created

- `~/.huggingface/token` - Your HF token (keep secret!)
- `~/.cache/huggingface/hub/models--pyannote--speaker-diarization-3.1/` - Cached models (~1.5GB)

## Disk Space

- Models: ~1.5GB
- PyTorch: ~2GB (already installed)
- Total: ~3.5GB

## Security Notes

- Token is read-only (can't modify your HF account)
- Token only needed for initial download
- After download, works 100% offline
- Token stored in `~/.huggingface/token` (chmod 600)
- No data sent externally during transcription
