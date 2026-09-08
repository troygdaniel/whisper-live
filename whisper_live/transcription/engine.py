"""Whisper transcription engine using faster-whisper."""

from faster_whisper import WhisperModel
import numpy as np


class TranscriptionEngine:
    """Wrapper for faster-whisper transcription."""

    def __init__(self, model_name="base", language=None, device="cpu"):
        """
        Initialize transcription engine.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            language: Language code (None = auto-detect)
            device: Device to run on ("cpu" or "cuda")
        """
        self.model_name = model_name
        self.language = language
        self.device = device
        self.model = None
        self._total_duration = 0

    def load_model(self):
        """Load the Whisper model."""
        if self.model is not None:
            return

        # Load model with faster-whisper
        # compute_type="int8" for CPU efficiency
        self.model = WhisperModel(
            self.model_name,
            device=self.device,
            compute_type="int8" if self.device == "cpu" else "float16"
        )

    def transcribe_chunk(self, audio_data, sample_rate=16000):
        """
        Transcribe an audio chunk.

        Args:
            audio_data: numpy array of audio samples
            sample_rate: Audio sample rate

        Returns:
            dict with 'text', 'start', 'end' keys
        """
        if self.model is None:
            self.load_model()

        # Ensure audio is float32
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Transcribe
        segments, info = self.model.transcribe(
            audio_data,
            language=self.language,
            beam_size=5,
            vad_filter=True,  # Voice activity detection
        )

        # Combine all segments into one result
        text_parts = []
        for segment in segments:
            if segment.text.strip():
                text_parts.append(segment.text.strip())

        full_text = " ".join(text_parts)

        # Calculate timestamps
        chunk_duration = len(audio_data) / sample_rate
        start_time = self._total_duration
        end_time = start_time + chunk_duration
        self._total_duration = end_time

        return {
            'text': full_text,
            'start': start_time,
            'end': end_time,
            'duration': chunk_duration,
        }

    def reset_duration(self):
        """Reset the total duration counter."""
        self._total_duration = 0

    @property
    def total_duration(self):
        """Get total duration of transcribed audio."""
        return self._total_duration
