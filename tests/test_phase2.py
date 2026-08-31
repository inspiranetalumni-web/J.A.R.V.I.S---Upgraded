"""
tests/test_phase2.py — Pytest Verification Suite for Phase 2 Streaming Audio & Perception Engine
"""

import time
import numpy as np
import pytest

from jarvis.audio.ring_buffer import AudioRingBuffer, SAMPLE_RATE, CHUNK_SAMPLES
from jarvis.audio.vad import DualGateVAD
from jarvis.audio.wakeword import WakeWordDetector
from jarvis.audio.stt import SpeechTranscriber
from jarvis.audio.tts import KokoroTTS
from jarvis.audio.manager import AudioManager, AudioState

def test_ring_buffer():
    """Verify AudioRingBuffer circular indexing and sample retrieval."""
    ring = AudioRingBuffer()
    chunk1 = np.ones(CHUNK_SAMPLES, dtype=np.float32) * 0.5
    ring.write(chunk1)

    read_80ms = ring.read_last_n_ms(80)
    assert len(read_80ms) == CHUNK_SAMPLES
    assert np.allclose(read_80ms, 0.5)

    # Test wrap-around write
    for i in range(5):
        ring.write(np.ones(CHUNK_SAMPLES, dtype=np.float32) * (i + 1))

    all_samples = ring.get_all()
    assert len(all_samples) == 3840

def test_dual_gate_vad():
    """Verify DualGateVAD RMS energy pre-filter and speech detection."""
    vad = DualGateVAD()

    # Silence chunk
    silence = np.zeros(CHUNK_SAMPLES, dtype=np.float32)
    is_speech, prob = vad.is_speech(silence)
    assert is_speech is False
    assert prob == 0.0

    # Loud speech simulation chunk
    t = np.linspace(0, 0.08, CHUNK_SAMPLES, endpoint=False, dtype=np.float32)
    speech_signal = (0.2 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)
    is_speech_loud, prob_loud = vad.is_speech(speech_signal)
    assert is_speech_loud is True
    assert prob_loud > 0.0

def test_wake_word_detector():
    """Verify WakeWordDetector score calculation and threshold checking."""
    detector = WakeWordDetector(threshold=0.5)

    silence = np.zeros(CHUNK_SAMPLES, dtype=np.float32)
    assert detector.predict(silence) == 0.0
    assert detector.is_wake_detected(silence) is False

    t = np.linspace(0, 0.08, CHUNK_SAMPLES, endpoint=False, dtype=np.float32)
    wake_sim = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    score = detector.predict(wake_sim)
    assert score > 0.0

def test_speech_transcriber():
    """Verify SpeechTranscriber interface returns valid string output."""
    stt = SpeechTranscriber()
    audio = np.zeros(16000, dtype=np.float32)  # 1 second of audio
    result = stt.transcribe(audio)
    assert isinstance(result, str)

def test_kokoro_tts_and_barge_in():
    """Verify KokoroTTS text synthesis and instant barge-in cancellation."""
    tts = KokoroTTS()
    tts.load()

    # Synthesize clause
    clause_audio = tts._synthesize_clause("Good morning Sir.")
    assert isinstance(clause_audio, np.ndarray)

    # Test non-blocking speech & barge-in stop
    tts.speak("Synthesizing multi-clause test sentence for barge-in validation. First clause, second clause.")
    time.sleep(0.05)
    tts.stop()
    assert tts.is_speaking() is False

def test_audio_manager_pipeline():
    """Verify AudioManager pipeline lifecycle from wake detection to utterance callback."""
    manager = AudioManager()
    received_transcripts = []

    def callback(text: str):
        received_transcripts.append(text)

    manager.register_on_utterance_callback(callback)

    # 1. Feed silence — should remain in LISTENING_WAKE
    silence = np.zeros(CHUNK_SAMPLES, dtype=np.float32)
    res1 = manager.process_audio_chunk(silence)
    assert res1["state"] == AudioState.LISTENING_WAKE.value

    # 2. Feed simulated wake chunk — should transition to ACCUMULATING_SPEECH
    t = np.linspace(0, 0.08, CHUNK_SAMPLES, endpoint=False, dtype=np.float32)
    wake_chunk = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    res2 = manager.process_audio_chunk(wake_chunk)
    assert res2["wake_detected"] is True
    assert res2["state"] == AudioState.ACCUMULATING_SPEECH.value

    # 3. Feed 12 silence chunks to trigger silence threshold finalization
    for _ in range(12):
        manager.process_audio_chunk(silence)

    # State should return to LISTENING_WAKE and trigger transcription callback
    assert manager.state == AudioState.LISTENING_WAKE
    assert len(received_transcripts) == 1
