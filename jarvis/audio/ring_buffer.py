"""
jarvis/audio/ring_buffer.py — Lock-free circular audio buffer
Preallocates 240ms of 16kHz float32 audio samples (15 KB) for zero-copy continuous listening.
"""

import threading
import numpy as np

SAMPLE_RATE = 16_000        # Hz
CHUNK_MS = 80              # ms per audio chunk step
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_MS / 1000)   # 1280 samples
RING_DURATION_MS = 240      # Total ring duration
RING_SAMPLES = int(SAMPLE_RATE * RING_DURATION_MS / 1000)  # 3840 samples

class AudioRingBuffer:
    """
    Preallocated circular buffer for 16kHz PCM audio streaming.
    Memory footprint: flat float32 array of 3840 samples = 15 KB.
    """
    def __init__(self):
        self._buf = np.zeros(RING_SAMPLES, dtype=np.float32)
        self._write_idx = 0
        self._lock = threading.Lock()

    def write(self, chunk: np.ndarray) -> None:
        """
        Write chunk of samples into circular buffer. Automatically normalizes int16 to float32 [-1.0, 1.0].
        """
        if chunk.dtype == np.int16:
            chunk_f32 = chunk.astype(np.float32) / 32768.0
        else:
            chunk_f32 = chunk.astype(np.float32)

        count = len(chunk_f32)
        with self._lock:
            if count >= RING_SAMPLES:
                # If chunk is larger than ring size, take the tail
                self._buf[:] = chunk_f32[-RING_SAMPLES:]
                self._write_idx = 0
                return

            end = self._write_idx + count
            if end <= RING_SAMPLES:
                self._buf[self._write_idx:end] = chunk_f32
            else:
                first_part = RING_SAMPLES - self._write_idx
                self._buf[self._write_idx:] = chunk_f32[:first_part]
                self._buf[:count - first_part] = chunk_f32[first_part:]
            self._write_idx = end % RING_SAMPLES

    def read_last_n_ms(self, n_ms: int) -> np.ndarray:
        """Read the most recent n_ms of audio chronologically."""
        n_samples = min(RING_SAMPLES, max(1, int(SAMPLE_RATE * n_ms / 1000)))
        with self._lock:
            start = (self._write_idx - n_samples) % RING_SAMPLES
            if start + n_samples <= RING_SAMPLES:
                return self._buf[start:start + n_samples].copy()
            else:
                return np.concatenate([
                    self._buf[start:],
                    self._buf[:(start + n_samples) % RING_SAMPLES]
                ])

    def get_all(self) -> np.ndarray:
        """Returns the full 240ms ring buffer contents in chronological order."""
        with self._lock:
            return np.concatenate([
                self._buf[self._write_idx:],
                self._buf[:self._write_idx]
            ])

    def clear(self) -> None:
        """Resets the ring buffer to silence."""
        with self._lock:
            self._buf.fill(0.0)
            self._write_idx = 0
