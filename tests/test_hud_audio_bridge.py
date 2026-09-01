"""
tests/test_hud_audio_bridge.py — Test Suite for Real-Time HUD & Audio-Visual Perception Bridge
Verifies 48-band FFT frequency binning, RMS volume, peak decay physics, dynamic persona HUD themes, and WebSocket streaming.
"""

import pytest
import time
import math
import numpy as np
from fastapi.testclient import TestClient

from jarvis.main import app
from jarvis.audio.spectrum_analyzer import SpectrumAnalyzer, spectrum_analyzer
from jarvis.audio.manager import AudioManager
from jarvis.audio.persona_manager import persona_manager
from jarvis.sensors.biometric_harvester import biometric_harvester
from jarvis.control_center.state import state_manager
from jarvis.control_center.widgets.voice_orb import VoiceOrbWidget, OrbDisplayMode

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Spectrum Analyzer Unit Tests
# ---------------------------------------------------------------------------

def test_spectrum_analyzer_fft_bins():
    analyzer = SpectrumAnalyzer(sample_rate=16000, num_bands=48)
    assert analyzer.num_bands == 48

    # Process random audio chunk (1280 samples = 80ms at 16kHz)
    rng = np.random.default_rng(42)
    chunk = rng.standard_normal(1280).astype(np.float32) * 0.1

    data = analyzer.analyze_pcm_chunk(chunk)
    assert data["num_bands"] == 48
    assert len(data["bands"]) == 48
    assert len(data["peaks"]) == 48
    assert 0.0 <= data["amplitude"] <= 1.0
    assert 0.0 <= data["spectral_centroid"] <= 1.0
    assert all(0.0 <= b <= 1.0 for b in data["bands"])
    assert all(0.0 <= p <= 1.0 for p in data["peaks"])


def test_spectrum_analyzer_sine_tone():
    analyzer = SpectrumAnalyzer(sample_rate=16000, num_bands=48)

    # Generate 440 Hz pure tone (1280 samples)
    t = np.linspace(0, 1280 / 16000, 1280, endpoint=False)
    sine_440 = (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    data = analyzer.analyze_pcm_chunk(sine_440)
    assert data["amplitude"] > 0.1
    assert data["is_active_speech"] is True

    # Peak band should be in the mid-low range (around 440 Hz)
    peak_band_idx = int(np.argmax(data["bands"]))
    assert 10 <= peak_band_idx <= 25


def test_spectrum_analyzer_rms_and_decay():
    analyzer = SpectrumAnalyzer(sample_rate=16000, num_bands=48)

    # High amplitude tone across 3 chunks to reach steady state
    loud_chunk = np.ones(1280, dtype=np.float32) * 0.8
    analyzer.analyze_pcm_chunk(loud_chunk)
    analyzer.analyze_pcm_chunk(loud_chunk)
    data_loud = analyzer.analyze_pcm_chunk(loud_chunk)
    amp_initial = data_loud["amplitude"]
    assert amp_initial > 0.5

    # Silence decay over consecutive empty frames
    time.sleep(0.05)
    data_silence = analyzer.analyze_pcm_chunk(np.zeros(1280, dtype=np.float32))
    assert data_silence["amplitude"] < amp_initial


def test_spectrum_analyzer_execution_latency():
    analyzer = SpectrumAnalyzer(sample_rate=16000, num_bands=48)
    chunk = (np.sin(np.linspace(0, 10, 1280)) * 0.2).astype(np.float32)

    # Warmup
    for _ in range(5):
        analyzer.analyze_pcm_chunk(chunk)

    t0 = time.perf_counter()
    iterations = 50
    for _ in range(iterations):
        analyzer.analyze_pcm_chunk(chunk)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    avg_latency_ms = elapsed_ms / iterations

    # Must execute in < 0.8ms per frame
    assert avg_latency_ms < 0.8


# ---------------------------------------------------------------------------
# 2. Audio Manager Spectrum Ingestion & Callbacks
# ---------------------------------------------------------------------------

def test_audio_manager_spectrum_callback():
    manager = AudioManager(async_mode=False)
    captured_data = []

    def on_spec(data):
        captured_data.append(data)

    manager.register_on_spectrum_callback(on_spec)

    chunk = (np.sin(np.linspace(0, 5, 1280)) * 0.3).astype(np.float32)
    manager.process_audio_chunk(chunk)

    assert len(captured_data) == 1
    assert len(captured_data[0]["bands"]) == 48
    assert captured_data[0]["amplitude"] > 0.0

    # Ingest output TTS audio chunk
    manager.ingest_output_audio_chunk(chunk)
    assert len(captured_data) == 2


# ---------------------------------------------------------------------------
# 3. Control Center State Manager & Voice Orb Reactivity
# ---------------------------------------------------------------------------

def test_state_manager_persona_and_spectrum_signals():
    persona_updates = []
    spectrum_updates = []
    stress_updates = []

    state_manager.persona_changed.connect(lambda p, c: persona_updates.append((p, c)))
    state_manager.spectrum_updated.connect(lambda b, a, c: spectrum_updates.append((b, a, c)))
    state_manager.stress_updated.connect(lambda s, c: stress_updates.append((s, c)))

    # Persona swap
    state_manager.set_active_persona("FRIDAY")
    assert state_manager.active_persona == "F.R.I.D.A.Y."
    assert len(persona_updates) >= 1
    assert persona_updates[-1][0] == "F.R.I.D.A.Y."

    state_manager.set_active_persona("EDITH")
    assert state_manager.active_persona == "E.D.I.T.H."
    assert persona_updates[-1][0] == "E.D.I.T.H."

    # Spectrum feed
    dummy_bands = [0.5] * 48
    state_manager.set_spectrum(dummy_bands, 0.42, 0.6)
    assert len(spectrum_updates) >= 1
    assert spectrum_updates[-1][1] == 0.42

    # Stress update
    state_manager.set_stress(0.85)
    assert state_manager.stress_level == 0.85
    assert len(stress_updates) >= 1


def test_voice_orb_dynamic_persona_and_spectrum():
    from PySide6.QtWidgets import QApplication
    app_qt = QApplication.instance() or QApplication([])

    orb = VoiceOrbWidget()
    assert orb._persona_name == "J.A.R.V.I.S."

    # Switch persona to FRIDAY
    orb.set_active_persona("FRIDAY")
    assert orb._persona_name == "F.R.I.D.A.Y."
    assert orb._persona_accent_color == "#FFB300"

    # Switch persona to EDITH
    orb.set_active_persona("EDITH")
    assert orb._persona_name == "E.D.I.T.H."
    assert orb._persona_accent_color == "#00FF88"

    # Feed spectrum data
    bands = [0.1 * (i % 10) for i in range(48)]
    orb.set_spectrum_data(bands, amplitude=0.75, centroid=0.65)
    assert len(orb._live_bands) == 48
    assert orb._amplitude == 0.75
    assert orb._spectral_centroid == 0.65

    # Stress level
    orb.set_stress_level(0.9, hud_color="#FF2A2A")
    assert orb._stress_level == 0.9
    assert orb._stress_color == "#FF2A2A"


# ---------------------------------------------------------------------------
# 4. FastAPI REST & WebSocket Telemetry Endpoints
# ---------------------------------------------------------------------------

def test_fastapi_spectrum_rest_endpoint():
    # Prime spectrum analyzer with tone
    chunk = (np.sin(np.linspace(0, 10, 1280)) * 0.4).astype(np.float32)
    spectrum_analyzer.analyze_pcm_chunk(chunk)

    r = client.get("/api/v1/audio/spectrum")
    assert r.status_code == 200
    data = r.json()
    assert data["num_bands"] == 48
    assert len(data["bands"]) == 48
    assert "active_persona" in data
    assert "persona_color" in data
    assert "stress_level" in data
    assert "hud_theme" in data


def test_fastapi_telemetry_websocket():
    with client.websocket_connect("/ws/telemetry") as ws:
        # Receive at least 1 telemetry frame
        frame = ws.receive_json()
        assert "spectrum" in frame
        assert "active_persona" in frame
        assert "persona_color" in frame
        assert "stress_level" in frame
        assert "hud_theme" in frame
        assert "cpu_percent" in frame
        assert "ram_percent" in frame
        assert frame["spectrum"]["num_bands"] == 48


# ---------------------------------------------------------------------------
# 5. Dynamic Local Cognitive Reasoner (Zero Generic Outputs)
# ---------------------------------------------------------------------------

def test_dynamic_cognitive_reasoner_no_generic_fallbacks():
    from jarvis.llm.cognitive_reasoner import cognitive_reasoner
    from jarvis.agents.conversational import ConversationalAgent

    agent = ConversationalAgent()

    # 1. Greetings check
    resp_greeting = cognitive_reasoner.analyze_and_respond("Hello J.A.R.V.I.S.")
    assert "J.A.R.V.I.S." in resp_greeting or "Sir" in resp_greeting
    assert "RAM" in resp_greeting or "mode" in resp_greeting.lower()
    assert resp_greeting != "At your service, Sir. All core systems are nominal."

    # 2. Architecture & Code Graph check
    resp_arch = cognitive_reasoner.analyze_and_respond("Explain our codebase architecture and AST graph")
    assert "modules" in resp_arch
    assert "dependency edges" in resp_arch or "spatial spheres" in resp_arch

    # 3. System Vitals & Performance check
    resp_health = cognitive_reasoner.analyze_and_respond("How is my system performance and memory?")
    assert "utilization" in resp_health.lower() or "memory" in resp_health.lower()

    # 4. Custom Directive check
    resp_custom = cognitive_reasoner.analyze_and_respond("Analyze quantum neural synchronization subroutines")
    assert "quantum neural synchronization" in resp_custom.lower() or "subroutines" in resp_custom.lower()
    assert "Understood, Sir. Processing your request:" not in resp_custom


def test_websocket_telemetry_worker_instantiation():
    from jarvis.control_center.telemetry import WebSocketTelemetryWorker
    worker = WebSocketTelemetryWorker()
    assert worker.ws_url == "ws://127.0.0.1:8765/ws/telemetry"
    assert worker._running is True

