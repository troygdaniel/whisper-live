#!/bin/bash
# Bundle pyannote models from HuggingFace cache into repo
# Run this at HOME after downloading models

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MODELS_DIR="$REPO_ROOT/models"
CACHE_DIR="$HOME/.cache/huggingface/hub"

echo "=================================================="
echo "Bundling Diarization Models for Offline Use"
echo "=================================================="
echo ""

# Check if cache exists
if [ ! -d "$CACHE_DIR" ]; then
    echo "✗ Error: HuggingFace cache not found at: $CACHE_DIR"
    echo ""
    echo "You need to download models first:"
    echo "  1. Get HuggingFace token"
    echo "  2. Run: python3 -c 'from pyannote.audio import Pipeline; Pipeline.from_pretrained(\"pyannote/speaker-diarization-3.1\", token=\"hf_...\")'"
    echo ""
    exit 1
fi

# Find ALL pyannote models in cache
PYANNOTE_MODELS=$(find "$CACHE_DIR" -type d -name "*pyannote*" -maxdepth 1 2>/dev/null)

if [ -z "$PYANNOTE_MODELS" ]; then
    echo "✗ Error: Pyannote models not found in cache"
    echo ""
    echo "Cache directory: $CACHE_DIR"
    echo ""
    echo "Download models first with:"
    echo "  export HF_TOKEN='hf_YOUR_TOKEN'"
    echo "  python3 << EOF"
    echo "  from pyannote.audio import Pipeline"
    echo "  import os"
    echo "  Pipeline.from_pretrained('pyannote/speaker-diarization-3.1', token=os.environ['HF_TOKEN'])"
    echo "  EOF"
    echo ""
    exit 1
fi

echo "Found models in cache:"
echo "$PYANNOTE_MODELS" | while read model; do
    echo "  - $(basename $model)"
done
echo ""

# Create models directory (this will be the hub directory)
echo "Creating models directory..."
mkdir -p "$MODELS_DIR/hub"

# Copy ALL pyannote models and blobs
echo "Copying all pyannote models and dependencies..."
echo "  From: $CACHE_DIR"
echo "  To:   $MODELS_DIR/hub/"
echo ""

# Copy all pyannote model directories
find "$CACHE_DIR" -type d -name "*pyannote*" -maxdepth 1 -exec cp -R {} "$MODELS_DIR/hub/" \;

# Also copy shared files if they exist
if [ -f "$CACHE_DIR/CACHEDIR.TAG" ]; then
    cp "$CACHE_DIR/CACHEDIR.TAG" "$MODELS_DIR/hub/"
fi

# Check size
SIZE=$(du -sh "$MODELS_DIR" | cut -f1)

echo ""
echo "=================================================="
echo "✓ Success!"
echo "=================================================="
echo "Models bundled to: $MODELS_DIR"
echo "Size: $SIZE"
echo ""
echo "Next steps:"
echo "  1. Add to git:"
echo "     cd $REPO_ROOT"
echo "     git add models/"
echo "     git commit -m 'Add bundled diarization models'"
echo "     git push"
echo ""
echo "  2. At work:"
echo "     git clone <repo>"
echo "     cd whisper"
echo "     ./scripts/install_bundled_models.sh"
echo ""
echo "Note: Models are ~1.5GB. Consider:"
echo "  - Git LFS (for GitHub)"
echo "  - Private repo"
echo "  - USB transfer instead"
echo "=================================================="
