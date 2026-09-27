# Changelog

## [2026-09-27] - Speaker Diarization Update

### Added
- **Speaker diarization** support using pyannote.audio
  - Identifies different speakers in conversations
  - Labels speakers as SPEAKER_00, SPEAKER_01, etc.
  - 100% offline after one-time model download
  - Toggle with `--diarize` flag
- New CLI flag: `--diarize` to enable speaker identification
- Speaker labels in terminal output (colored green)
- Speaker labels in transcript files
- Support for larger Whisper models (`medium`, `large`)
- Comprehensive documentation:
  - [DIARIZATION.md](DIARIZATION.md) - Detailed diarization setup guide
  - [SETUP_WORK.md](SETUP_WORK.md) - Work computer setup instructions

### Changed
- Updated `requirements.txt` with pyannote.audio, torch, torchaudio
- Enhanced `TranscriptionEngine` to support diarization
- Updated `TerminalDisplay` to show speaker labels
- Updated `FileWriter` to include speaker labels in output
- Updated `TranscriptionSession` to pass speaker info through pipeline
- Improved model comparison table with diarization quality ratings
- Updated README.md with diarization examples

### Dependencies
- pyannote.audio >= 3.1.0
- torch >= 2.0.0
- torchaudio >= 2.0.0

### Model Sizes
- Base Whisper model: ~140MB
- Medium Whisper model: ~1.5GB
- Large Whisper model: ~3GB
- Diarization models: ~1.5GB (one-time download)

### Privacy
- All processing remains 100% offline after setup
- Models cache locally to ~/.cache/huggingface/
- No data sent to external servers during use
- HuggingFace token only needed for one-time model download

### Setup Requirements
For diarization:
1. HuggingFace account (free)
2. Accept pyannote model license
3. Create read-only HF token
4. Download models once (~1.5GB)
5. Run offline forever

### Performance Impact
- Diarization adds ~20-30% processing overhead
- Requires ~1GB additional RAM
- Recommended: Use `medium` model or larger for best speaker accuracy

---

## [2026-09-07] - Initial Release

### Features
- Real-time audio transcription using faster-whisper
- Multiple Whisper models (tiny, base, small)
- Microphone input support
- System audio capture (BlackHole)
- Timestamped transcript files
- Rich terminal display
- 100% offline operation
- Privacy-focused (no API calls)
- Auto-save to ./transcripts/
- Live terminal output with Rich formatting

### Models Supported
- tiny (~75MB)
- base (~140MB)
- small (~460MB)

### Commands
- `whisper-live start` - Begin transcription
- `whisper-live devices` - List audio devices
