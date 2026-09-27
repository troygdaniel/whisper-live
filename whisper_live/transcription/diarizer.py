"""Speaker diarization using pyannote.audio."""

import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class SpeakerDiarizer:
    """
    Wrapper for pyannote.audio speaker diarization.

    This runs 100% offline after initial model download.
    Models are cached to ~/.cache/huggingface/
    """

    def __init__(self, use_auth_token=None):
        """
        Initialize speaker diarizer.

        Args:
            use_auth_token: HuggingFace token (only needed for first download)
        """
        self.pipeline = None
        self.use_auth_token = use_auth_token
        self._model_loaded = False

    def load_model(self):
        """Load the diarization model (downloads on first run)."""
        if self._model_loaded:
            return

        try:
            from pyannote.audio import Pipeline

            # Try to load from cache first (offline)
            try:
                # Try new API first (token parameter), fall back to old API (use_auth_token)
                try:
                    self.pipeline = Pipeline.from_pretrained(
                        "pyannote/speaker-diarization-3.1",
                        token=self.use_auth_token
                    )
                except TypeError:
                    # Fallback for older pyannote versions
                    self.pipeline = Pipeline.from_pretrained(
                        "pyannote/speaker-diarization-3.1",
                        use_auth_token=self.use_auth_token
                    )
            except Exception as e:
                error_msg = str(e).lower()
                if "offline" in error_msg or "connection" in error_msg or "not found" in error_msg:
                    raise RuntimeError(
                        "Diarization models not found in cache. "
                        "You need to download them once while online. "
                        "See DIARIZATION.md for setup instructions."
                    )
                raise

            self._model_loaded = True

        except ImportError:
            raise RuntimeError(
                "pyannote.audio not installed. Run: pip install pyannote.audio torch torchaudio"
            )

    def diarize_audio(self, audio_data, sample_rate=16000):
        """
        Perform speaker diarization on audio chunk.

        Args:
            audio_data: numpy array of audio samples
            sample_rate: Audio sample rate

        Returns:
            List of dicts with 'start', 'end', 'speaker' keys
        """
        if self.pipeline is None:
            self.load_model()

        # Ensure audio is float32 and 2D
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # pyannote expects (channels, samples) format
        if audio_data.ndim == 1:
            audio_data = audio_data.reshape(1, -1)

        # Create temporary audio dict for pyannote
        audio = {
            'waveform': audio_data,
            'sample_rate': sample_rate
        }

        # Run diarization
        try:
            diarization = self.pipeline(audio)

            # Convert to list of segments
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    'start': turn.start,
                    'end': turn.end,
                    'speaker': speaker
                })

            return segments

        except Exception as e:
            # If diarization fails, return empty segments
            # (transcription will continue without speaker labels)
            return []

    def assign_speaker_to_segment(self, segment_start, segment_end, diarization_segments):
        """
        Assign a speaker to a transcription segment based on overlap.

        Args:
            segment_start: Start time of transcription segment
            segment_end: End time of transcription segment
            diarization_segments: List of diarization segments

        Returns:
            Speaker label or None
        """
        if not diarization_segments:
            return None

        # Find the diarization segment with maximum overlap
        max_overlap = 0
        best_speaker = None

        for d_seg in diarization_segments:
            # Calculate overlap
            overlap_start = max(segment_start, d_seg['start'])
            overlap_end = min(segment_end, d_seg['end'])
            overlap = max(0, overlap_end - overlap_start)

            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = d_seg['speaker']

        return best_speaker
