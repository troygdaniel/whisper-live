# Quick Setup Guide for Work Computer (RBC)

This guide assumes you've already bundled the models at home.

## Option A: Git Clone (If Models in Repo)

```bash
# 1. Clone repo
cd ~/dev
git clone <your-repo-url> whisper
cd whisper

# 2. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# 3. Install bundled models
./scripts/install_bundled_models.sh

# 4. Test
whisper-live start --diarize --no-file
```

## Option B: USB Drive Transfer

### At Home (Prepare USB):
```bash
# Package models
cd ~/.cache/huggingface
tar -czf ~/Desktop/whisper-models.tar.gz hub/

# Copy to USB drive
cp ~/Desktop/whisper-models.tar.gz /Volumes/YOUR_USB/
```

### At Work:
```bash
# 1. Clone repo
cd ~/dev
git clone <your-repo-url> whisper
cd whisper

# 2. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# 3. Extract models from USB
mkdir -p ~/.cache/huggingface
tar -xzf /Volumes/YOUR_USB/whisper-models.tar.gz -C ~/.cache/huggingface/

# 4. Test
whisper-live start --diarize --no-file
```

## For Claude at Work

When user says "set up whisper":

1. **Check for bundled models:**
   ```bash
   ls models/ 2>/dev/null
   ```

2. **If bundled models exist:**
   ```bash
   ./scripts/install_bundled_models.sh
   ```

3. **If no bundled models:**
   Ask user: "Do you have models on USB or want to download with HF token?"

4. **Verify:**
   ```bash
   whisper-live start --diarize --no-file
   ```

## Troubleshooting

### "Bundled models not found"
- Models weren't bundled at home
- Re-run at home: `./scripts/bundle_models.sh`

### "Models don't load"
- Dependencies not installed: `pip install -r requirements.txt`
- Try reinstalling: `./scripts/install_bundled_models.sh`

### "No such file or directory: scripts/"
- You're not in the whisper directory
- Run: `cd ~/dev/whisper`

## What Gets Installed

```
~/.cache/huggingface/hub/
└── models--pyannote--speaker-diarization-3.1/
    ├── snapshots/
    │   └── [model files]
    └── refs/
```

Size: ~1.5GB

## Privacy & Security

- All models cached locally
- No internet needed after setup
- No HuggingFace account needed at work
- All processing happens on your work computer
- No data sent externally

## Usage

```bash
# Microphone with speaker labels
whisper-live start --diarize

# System audio with speaker labels
whisper-live start --source system --diarize

# Best quality
whisper-live start --model medium --diarize
```

Output will show:
```
[00:00:05] [Speaker SPEAKER_00] First person speaking
[00:00:12] [Speaker SPEAKER_01] Second person speaking
```
