"""
jarvis/audio/manager.py — Full-Duplex Audio Pipeline Orchestrator v3.0
Coordinates microphone ingestion, dual-gate VAD, wake word triggering, STT transcription,
TTS response playback, bounded queue decoupling, and instant full-duplex barge-in voice interruption.
"""

import time
import queue
import threading
import numpy as np
from enum import Enum
from typing import Callable, Optional, Dict, Any, Iterator, Union, List

from jarvis.audio.ring_buffer import AudioRingBuffer, SAMPLE_RATE, CHUNK_SAMPLES
from jarvis.audio.vad import DualGateVAD
from jarvis.audio.wakeword import WakeWordDetector
from jarvis.audio.stt import SpeechTranscriber
from jarvis.audio.tts import KokoroTTS

class AudioState(Enum):
    LISTENING_WAKE = "LISTENING_WAKE"
    ACCUMULATING_SPEECH = "ACCUMULATING_SPEECH"
    PROCESSING_UTTERANCE = "PROCESSING_UTTERANCE"
    SPEAKING = "SPEAKING"

class AudioManager:
    """
    Master Audio Pipeline Manager with decoupled queue architecture, non-blocking ingestion,
    streaming TTS clause synthesis, and instant full-duplex barge-in interruption.
    """
    def __init__(self, async_mode: bool = False):
        self.ring_buffer = AudioRingBuffer()
        self.vad = DualGateVAD()
        self.wakeword = WakeWordDetector()
        self.stt = SpeechTranscriber()
        self.tts = KokoroTTS()

        self.state = AudioState.LISTENING_WAKE
        self.utterance_buffer: List[np.ndarray] = []
        self.silence_chunks = 0
        self.max_silence_chunks = 10  # ~800ms silence threshold

        self.on_utterance_callback: Optional[Callable[[str], None]] = None
        self._lock = threading.Lock()
        self._is_active = False
        self._mic_thread = None

        # Bounded thread-safe queue for decoupled utterance processing
        self._async_mode = async_mode
        self._utterance_queue: queue.Queue[Optional[np.ndarray]] = queue.Queue(maxsize=8)
        self._worker_thread: Optional[threading.Thread] = None
        self._cancel_token = threading.Event()

        if self._async_mode:
            self._start_utterance_worker()

    @property
    def cancel_token(self) -> threading.Event:
        """Returns the active barge-in cancellation event token."""
        return self._cancel_token

    def register_on_utterance_callback(self, callback: Callable[[str], None]) -> None:
        """Registers listener callback for finalized voice transcriptions."""
        self.on_utterance_callback = callback

    def _start_utterance_worker(self):
        """Starts background worker thread for asynchronous speech transcription."""
        if self._worker_thread and self._worker_thread.is_alive():
            return

        def _worker_loop():
            while self._is_active or self._async_mode:
                try:
                    audio_data = self._utterance_queue.get(timeout=0.1)
                    if audio_data is None:
                        break
                    if len(audio_data) > 0:
                        transcript = self.stt.transcribe(audio_data)
                        if transcript.strip() and self.on_utterance_callback:
                            self.on_utterance_callback(transcript)
                    self._utterance_queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[AUDIO MANAGER] Utterance worker note: {e}")

        self._worker_thread = threading.Thread(target=_worker_loop, daemon=True)
        self._worker_thread.start()

    def _flush_utterance_queue(self):
        """Safely flushes any pending audio in the utterance queue on barge-in."""
        while not self._utterance_queue.empty():
            try:
                self._utterance_queue.get_nowait()
                self._utterance_queue.task_done()
            except Exception:
                break

    def trigger_barge_in(self):
        """Signals instant barge-in cutoff: silences TTS, cancels generation, and flushes queues."""
        self._cancel_token.set()
        self.tts.stop()
        self._flush_utterance_queue()
        with self._lock:
            self.utterance_buffer.clear()
            self.silence_chunks = 0
            self.state = AudioState.LISTENING_WAKE
        print("[AUDIO MANAGER] Barge-in cutoff executed (<50ms cancellation signal dispatched).")

    def process_audio_chunk(self, chunk: np.ndarray) -> Dict[str, Any]:
        """
        Process single 80ms PCM audio chunk (1280 samples float32 at 16kHz).
        Non-blocking ingestion with fast RMS & VAD perception (<1ms cost).
        """
        with self._lock:
            # 1. Ingest into circular ring buffer
            self.ring_buffer.write(chunk)

            # 2. Check for Barge-in during active TTS playback
            if self.tts.is_speaking():
                is_speech, speech_prob = self.vad.is_speech(chunk)
                if is_speech and speech_prob > 0.60:
                    self.trigger_barge_in()

            # 3. Perception State Machine Execution
            is_speech, speech_prob = self.vad.is_speech(chunk)
            wake_score = 0.0
            wake_detected = False
            transcript = ""

            if self.state == AudioState.LISTENING_WAKE:
                if is_speech and speech_prob > 0.45:
                    wake_score = self.wakeword.predict(chunk)
                    if wake_score >= self.wakeword.threshold or speech_prob > 0.55:
                        wake_detected = True
                        self._cancel_token.clear()
                        self.state = AudioState.ACCUMULATING_SPEECH
                        self.utterance_buffer = [self.ring_buffer.get_all(), chunk.copy()]
                        self.silence_chunks = 0
                        print(f"[AUDIO MANAGER] Speech Detected! Prob: {speech_prob:.2f} — Accumulating utterance...")

            elif self.state == AudioState.ACCUMULATING_SPEECH:
                self.utterance_buffer.append(chunk.copy())
                if is_speech:
                    self.silence_chunks = 0
                else:
                    self.silence_chunks += 1
                    if self.silence_chunks >= self.max_silence_chunks:
                        # Silence threshold reached — finalize utterance
                        self.state = AudioState.PROCESSING_UTTERANCE
                        full_audio = np.concatenate(self.utterance_buffer) if self.utterance_buffer else np.zeros(0, dtype=np.float32)
                        self.utterance_buffer.clear()

                        # Dispatch utterance: async via queue if async_mode, else direct
                        if self._async_mode and self._worker_thread and self._worker_thread.is_alive():
                            try:
                                self._utterance_queue.put_nowait(full_audio)
                            except queue.Full:
                                self._flush_utterance_queue()
                                self._utterance_queue.put_nowait(full_audio)
                        else:
                            # Synchronous direct processing for CLI / direct tests
                            transcript = self.stt.transcribe(full_audio)
                            print(f"[AUDIO MANAGER] Utterance Finalized: '{transcript}'")
                            if self.on_utterance_callback and transcript.strip():
                                self.on_utterance_callback(transcript)

                        self.state = AudioState.LISTENING_WAKE

            return {
                "state": self.state.value,
                "is_speech": is_speech,
                "speech_prob": speech_prob,
                "wake_score": wake_score,
                "wake_detected": wake_detected,
                "transcript": transcript,
                "is_speaking": self.tts.is_speaking()
            }

    def start_mic_listener(self) -> bool:
        """Starts background thread to continuously capture physical laptop mic audio."""
        if self._is_active:
            return True

        self._is_active = True
        self._async_mode = True
        self._start_utterance_worker()

        def _mic_loop():
            try:
                import sounddevice as sd
                print("[AUDIO MANAGER] Opening native sounddevice InputStream at 16000Hz...")
                with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', blocksize=CHUNK_SAMPLES) as stream:
                    while self._is_active:
                        data, overflowed = stream.read(CHUNK_SAMPLES)
                        if not overflowed and len(data) > 0:
                            chunk = data.flatten()
                            self.process_audio_chunk(chunk)
            except Exception as e:
                print(f"[AUDIO MANAGER] Native sounddevice mic note: {e} — Voice engine listening via endpoints.")

        self._mic_thread = threading.Thread(target=_mic_loop, daemon=True)
        self._mic_thread.start()
        return True

    def stop_mic_listener(self) -> None:
        """Stops background mic thread and worker."""
        self._is_active = False
        if self._utterance_queue:
            try:
                self._utterance_queue.put_nowait(None)
            except Exception:
                pass

    def speak(self, text: str, blocking: bool = False) -> None:
        """Synthesizes text and streams output audio through speakers."""
        with self._lock:
            self.state = AudioState.SPEAKING
        self.tts.speak(text, blocking=blocking)

    def speak_stream(
        self,
        clause_iterator: Union[Iterator[str], List[str]],
        blocking: bool = False
    ) -> None:
        """Streams and synthesizes incoming natural speech clauses in real time."""
        with self._lock:
            self.state = AudioState.SPEAKING
        self.tts.speak_stream(clause_iterator, cancel_event=self._cancel_token, blocking=blocking)

    def stop_playback(self) -> None:
        """Interrupts voice playback immediately via Barge-in signal."""
        self.trigger_barge_in()
