"""
jarvis/audio/manager.py — Full-Duplex Audio Pipeline Orchestrator v3.0
Coordinates microphone ingestion, dual-gate VAD, wake word triggering, STT transcription,
TTS response playback, and full-duplex barge-in voice interruption.
"""

import time
import threading
import numpy as np
from enum import Enum
from typing import Callable, Optional, Dict, Any

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
    Master Audio Pipeline Manager with continuous laptop microphone intake and SAPI5 speech synthesis.
    """
    def __init__(self):
        self.ring_buffer = AudioRingBuffer()
        self.vad = DualGateVAD()
        self.wakeword = WakeWordDetector()
        self.stt = SpeechTranscriber()
        self.tts = KokoroTTS()

        self.state = AudioState.LISTENING_WAKE
        self.utterance_buffer = []
        self.silence_chunks = 0
        self.max_silence_chunks = 10  # ~800ms silence threshold

        self.on_utterance_callback: Optional[Callable[[str], None]] = None
        self._lock = threading.Lock()
        self._is_active = False
        self._mic_thread = None

    def register_on_utterance_callback(self, callback: Callable[[str], None]) -> None:
        """Registers listener callback for finalized voice transcriptions."""
        self.on_utterance_callback = callback

    def process_audio_chunk(self, chunk: np.ndarray) -> Dict[str, Any]:
        """
        Process single 80ms PCM audio chunk (1280 samples float32 at 16kHz).
        Returns status dictionary of perception engine state.
        """
        with self._lock:
            # 1. Ingest into circular ring buffer
            self.ring_buffer.write(chunk)

            # 2. Check for Barge-in during active TTS playback
            if self.tts.is_speaking():
                is_speech, speech_prob = self.vad.is_speech(chunk)
                if is_speech and speech_prob > 0.60:
                    print("[AUDIO MANAGER] Speech detected during playback — triggering Barge-in cutoff")
                    self.tts.stop()
                    self.state = AudioState.LISTENING_WAKE

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
                        full_audio = np.concatenate(self.utterance_buffer)
                        self.utterance_buffer.clear()

                        # Execute Speech-to-Text transcription
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
        """Stops background mic thread."""
        self._is_active = False

    def speak(self, text: str, blocking: bool = False) -> None:
        """Synthesizes text and streams output audio through speakers."""
        with self._lock:
            self.state = AudioState.SPEAKING
        self.tts.speak(text, blocking=blocking)

    def stop_playback(self) -> None:
        """Interrupts voice playback immediately."""
        self.tts.stop()
        with self._lock:
            self.state = AudioState.LISTENING_WAKE
