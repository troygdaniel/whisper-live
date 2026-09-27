"""Whisper transcription engine using faster-whisper."""

from faster_whisper import WhisperModel
import numpy as np


class TranscriptionEngine:
    """Wrapper for faster-whisper transcription."""

    def __init__(self, model_name="base", language=None, device="cpu", enable_diarization=False):
        """
        Initialize transcription engine.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            language: Language code (None = auto-detect)
            device: Device to run on ("cpu" or "cuda")
            enable_diarization: Enable speaker diarization
        """
        self.model_name = model_name
        self.language = language
        self.device = device
        self.enable_diarization = enable_diarization
        self.model = None
        self.diarizer = None
        self._total_duration = 0
        self._audio_buffer = []  # Store audio for diarization

    def load_model(self):
        """Load the Whisper model and optionally diarizer."""
        if self.model is not None:
            return

        # Load model with faster-whisper
        # compute_type="int8" for CPU efficiency
        self.model = WhisperModel(
            self.model_name,
            device=self.device,
            compute_type="int8" if self.device == "cpu" else "float16"
        )

        # Load diarizer if enabled
        if self.enable_diarization and self.diarizer is None:
            from .diarizer import SpeakerDiarizer
            self.diarizer = SpeakerDiarizer()
            self.diarizer.load_model()

    def transcribe_chunk(self, audio_data, sample_rate=16000):
        """
        Transcribe an audio chunk with optional speaker diarization.

        Args:
            audio_data: numpy array of audio samples
            sample_rate: Audio sample rate

        Returns:
            dict with 'text', 'start', 'end', 'speaker' (if diarization enabled) keys
        """
        if self.model is None:
            self.load_model()

        # Ensure audio is float32
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Store audio for diarization
        if self.enable_diarization:
            self._audio_buffer.append(audio_data)

        # Transcribe
        segments, info = self.model.transcribe(
            audio_data,
            language=self.language,
            beam_size=5,
            vad_filter=True,  # Voice activity detection
        )

        # Collect segments with timestamps
        segment_list = []
        for segment in segments:
            if segment.text.strip():
                segment_list.append({
                    'text': segment.text.strip(),
                    'start': segment.start,
                    'end': segment.end
                })

        # Calculate timestamps
        chunk_duration = len(audio_data) / sample_rate
        chunk_start = self._total_duration
        chunk_end = chunk_start + chunk_duration
        self._total_duration = chunk_end

        # Perform diarization if enabled
        speaker = None
        if self.enable_diarization and self.diarizer and segment_list:
            try:
                # Run diarization on this chunk
                diarization_segments = self.diarizer.diarize_audio(audio_data, sample_rate)

                # Assign speaker to each segment
                for seg in segment_list:
                    # Adjust segment times to be relative to chunk start
                    abs_start = chunk_start + seg['start']
                    abs_end = chunk_start + seg['end']

                    # Find speaker for this segment
                    seg_speaker = self.diarizer.assign_speaker_to_segment(
                        seg['start'], seg['end'], diarization_segments
                    )
                    if seg_speaker:
                        speaker = seg_speaker
                        break  # Use first identified speaker for the chunk
            except Exception as e:
                # Diarization failed, continue without speaker labels
                pass

        # Combine all segments into one result
        full_text = " ".join([seg['text'] for seg in segment_list])

        result = {
            'text': full_text,
            'start': chunk_start,
            'end': chunk_end,
            'duration': chunk_duration,
        }

        if speaker:
            result['speaker'] = speaker

        return result

    def reset_duration(self):
        """Reset the total duration counter."""
        self._total_duration = 0

    @property
    def total_duration(self):
        """Get total duration of transcribed audio."""
        return self._total_duration
