# Offline Bundle Setup - No HuggingFace at Work

This guide lets you set up diarization at home, bundle the models, and use them at work **without** needing HuggingFace access at work.

## Why This Approach?

- Download models once at home (personal computer)
- Package models into git repo
- At work: clone repo, everything already included
- No HuggingFace account needed at work
- 100% offline at work

## Part 1: Home Setup (Do This Once)

### Step 1: Get HuggingFace Token (Home Only)

1. Create account: https://huggingface.co/join
2. Accept license: https://huggingface.co/pyannote/speaker-diarization-3.1
3. Get token: https://huggingface.co/settings/tokens
   - Name: `whisper-live-home`
   - Type: **Read**
   - Copy token (starts with `hf_`)

### Step 2: Download Models at Home

```bash
cd ~/dev/whisper
source venv/bin/activate

# Save token temporarily
export HF_TOKEN="hf_YOUR_TOKEN_HERE"

python3 << 'EOF'
import os
from pyannote.audio import Pipeline

token = os.environ.get('HF_TOKEN')

print("Downloading models to cache...")
print("This will take a few minutes (~1.5GB)")
print("")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=token
)

print("")
print("✓ Models downloaded to: ~/.cache/huggingface/")
EOF
```

### Step 3: Package Models into Repo

```bash
cd ~/dev/whisper

# Run the bundler script (creates models/ directory)
./scripts/bundle_models.sh

# Check size
du -sh models/
```

This creates:
```
whisper/
├── models/              # ← New! Bundled models (~1.5GB)
│   └── pyannote/
│       └── speaker-diarization-3.1/
├── whisper_live/
├── README.md
└── ...
```

### Step 4: Add to Git (Be Careful!)

**Option A: Git LFS (Recommended for GitHub)**
```bash
# Install git-lfs if not installed
brew install git-lfs
git lfs install

# Track large model files
git lfs track "models/**/*.bin"
git lfs track "models/**/*.pt"
git lfs track "models/**/*.safetensors"

# Add and commit
git add .gitattributes
git add models/
git commit -m "Add bundled diarization models for offline use"
git push
```

**Option B: Private Repo (Simpler)**
```bash
# Just add normally (only if private repo!)
git add models/
git commit -m "Add bundled diarization models"
git push
```

**⚠️ Warning:** Models are ~1.5GB. Use private repo or Git LFS.

## Part 2: Work Setup (At RBC)

### Step 1: Clone Repo

```bash
cd ~/dev
git clone <your-repo-url> whisper
cd whisper
```

### Step 2: Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Step 3: Link Models to Cache

```bash
# Run the installer script
./scripts/install_bundled_models.sh
```

This creates symlinks:
```
~/.cache/huggingface/hub/ → ~/dev/whisper/models/
```

### Step 4: Verify & Test

```bash
# Verify models work
python3 << 'EOF'
from pyannote.audio import Pipeline

print("Testing bundled models (offline)...")
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1"
)
print("✓ Success! Models loaded from bundle.")
EOF

# Test with whisper-live
whisper-live start --diarize --no-file
```

## Alternative: USB Drive Method

If repo size is an issue:

### At Home:
```bash
# Package models to USB
tar -czf ~/Desktop/whisper-models.tar.gz -C ~/.cache/huggingface hub/

# Copy whisper-models.tar.gz to USB drive
```

### At Work:
```bash
# Extract to cache
mkdir -p ~/.cache/huggingface
tar -xzf /Volumes/USB/whisper-models.tar.gz -C ~/.cache/huggingface/

# Clone repo (without models)
git clone <repo> whisper
cd whisper
pip install -r requirements.txt

# Test
whisper-live start --diarize --no-file
```

## For Claude Instances at Work

When user says "set up whisper with diarization":

1. Check if `models/` directory exists in repo
2. If yes: Run `./scripts/install_bundled_models.sh`
3. If no: Ask user which method (bundle, USB, or HF token)
4. Verify with test script
5. Run: `whisper-live start --diarize --no-file`

## Size Considerations

- **Models:** ~1.5GB
- **PyTorch + deps:** ~2GB
- **Total:** ~3.5GB

**Git LFS limits:**
- GitHub: 1GB per file, 2GB total (free)
- GitLab: 10GB (free)
- Bitbucket: 1GB (free)

**Recommendation:** Use private GitHub repo with Git LFS.

## Security Notes

- Models are public (pyannote license)
- No token needed at work
- Everything runs offline
- No data leaves work computer
