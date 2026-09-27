#!/bin/bash
# Install bundled models to HuggingFace cache
# Run this at WORK after cloning repo

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MODELS_DIR="$REPO_ROOT/models"
CACHE_DIR="$HOME/.cache/huggingface/hub"

echo "=================================================="
echo "Installing Bundled Diarization Models"
echo "=================================================="
echo ""

# Check if bundled models exist
if [ ! -d "$MODELS_DIR" ]; then
    echo "✗ Error: Bundled models not found at: $MODELS_DIR"
    echo ""
    echo "This repo doesn't have bundled models."
    echo ""
    echo "Options:"
    echo "  1. At home: Run ./scripts/bundle_models.sh"
    echo "  2. Use HuggingFace token setup instead"
    echo "  3. Transfer models via USB drive"
    echo ""
    exit 1
fi

# Count model directories
MODEL_COUNT=$(find "$MODELS_DIR" -type d -name "*pyannote*" 2>/dev/null | wc -l)

if [ "$MODEL_COUNT" -eq 0 ]; then
    echo "✗ Error: No pyannote models found in: $MODELS_DIR"
    echo ""
    echo "The models/ directory exists but appears empty."
    echo "Re-run ./scripts/bundle_models.sh at home."
    echo ""
    exit 1
fi

echo "Found bundled models:"
find "$MODELS_DIR" -type d -name "*pyannote*" -exec basename {} \;
echo ""

# Create cache directory
echo "Creating HuggingFace cache directory..."
mkdir -p "$CACHE_DIR"

# Copy bundled models to cache
echo "Installing models to cache..."
echo "  From: $MODELS_DIR/hub"
echo "  To:   $CACHE_DIR"
echo ""

# Copy all model directories from the hub subdirectory
if [ -d "$MODELS_DIR/hub" ]; then
    cp -R "$MODELS_DIR/hub"/* "$CACHE_DIR/"
else
    # Fallback for old bundle format
    cp -R "$MODELS_DIR"/* "$CACHE_DIR/"
fi

# Verify installation
echo "Verifying installation..."
python3 << 'EOF'
import sys
try:
    from pyannote.audio import Pipeline
    print("  Testing model load...")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    print("  ✓ Models load successfully!")
except Exception as e:
    print(f"  ✗ Error loading models: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✓ Success!"
    echo "=================================================="
    echo "Models installed to: $CACHE_DIR"
    echo ""
    echo "You can now use:"
    echo "  whisper-live start --diarize"
    echo ""
    echo "This works 100% offline (no HuggingFace needed)."
    echo "=================================================="
else
    echo ""
    echo "✗ Installation failed. See error above."
    exit 1
fi
