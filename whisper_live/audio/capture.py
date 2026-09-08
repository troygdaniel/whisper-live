"""Audio capture using sounddevice."""

import sounddevice as sd
import numpy as np
from queue import Queue
import threading


class AudioCapture:
    """Captures audio from microphone or system audio in chunks."""

    def __init__(self, sample_rate=16000, chunk_duration=2.0, device=None):
        """
        Initialize audio capture.

        Args:
            sample_rate: Audio sample rate in Hz (Whisper requires 16000)
            chunk_duration: Duration of each audio chunk in seconds
            device: Device index or name (None = default input device)
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.device = device

        self.audio_queue = Queue()
        self.is_recording = False
        self.stream = None
        self._buffer = np.array([], dtype=np.float32)

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback function for sounddevice stream."""
        if status:
            print(f"Audio callback status: {status}")

        # Add incoming audio to buffer
        audio_data = indata[:, 0].copy()  # Get mono channel
        self._buffer = np.concatenate([self._buffer, audio_data])

        # If we have enough data for a chunk, put it in queue
        while len(self._buffer) >= self.chunk_size:
            chunk = self._buffer[:self.chunk_size]
            self._buffer = self._buffer[self.chunk_size:]
            self.audio_queue.put(chunk)

    def start(self):
        """Start capturing audio from selected device."""
        if self.is_recording:
            return

        self.is_recording = True
        self._buffer = np.array([], dtype=np.float32)

        # Start audio stream
        self.stream = sd.InputStream(
            device=self.device,  # Use specified device or default
            samplerate=self.sample_rate,
            channels=1,  # Mono
            dtype=np.float32,
            callback=self._audio_callback,
            blocksize=int(self.sample_rate * 0.1),  # 100ms blocks
        )
        self.stream.start()

    def stop(self):
        """Stop capturing audio."""
        if not self.is_recording:
            return

        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Process any remaining audio in buffer
        if len(self._buffer) > 0:
            self.audio_queue.put(self._buffer)
            self._buffer = np.array([], dtype=np.float32)

    def get_chunk(self, timeout=None):
        """
        Get the next audio chunk from the queue.

        Args:
            timeout: Maximum time to wait for a chunk (None = wait forever)

        Returns:
            numpy array of audio data, or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except:
            return None

    def has_data(self):
        """Check if there's audio data available."""
        return not self.audio_queue.empty()

    def list_devices(self):
        """List available audio input devices."""
        return sd.query_devices()

    @staticmethod
    def find_device(name_pattern):
        """
        Find device by name pattern (case-insensitive).

        Args:
            name_pattern: String to search for in device names

        Returns:
            Device index or None if not found
        """
        devices = sd.query_devices()
        name_pattern = name_pattern.lower()

        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                if name_pattern in device['name'].lower():
                    return i
        return None

    @staticmethod
    def get_device_name(device_index):
        """Get device name by index."""
        try:
            device = sd.query_devices(device_index)
            return device['name']
        except:
            return "Unknown Device"

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
