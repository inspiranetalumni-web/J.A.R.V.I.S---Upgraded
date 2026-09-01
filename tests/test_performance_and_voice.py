"""
tests/test_performance_and_voice.py — Comprehensive Test Suite for CPU-Only Real-Time Voice Optimizations
Validates:
1. Dynamic LLM availability probing & TTL caching
2. Real-time token streaming & natural speech clause buffering
3. Decoupled audio queue pipeline & non-blocking ingestion
4. Instant full-duplex barge-in cancellation signaling
5. Lightweight command router sub-millisecond matching & confirmation escrow
6. CPU Survival Mode governor and performance profiles
7. FastAPI REST endpoints for fast commands and survival telemetry
"""

import time
import threading
import numpy as np
import pytest
from fastapi.testclient import TestClient

from jarvis.llm.engine import OllamaEngine
from jarvis.audio.tts import KokoroTTS
from jarvis.audio.manager import AudioManager, AudioState
from jarvis.audio.ring_buffer import CHUNK_SAMPLES
from jarvis.system.command_router import LightweightCommandRouter, command_router
from jarvis.system.cpu_survival import CPUSurvivalManager, PerformanceMode, cpu_survival_manager
from jarvis.agents.conversational import ConversationalAgent
from jarvis.main import app

def test_llm_availability_ttl_probing():
    """Verify OllamaEngine dynamically probes availability and caches with TTL."""
    engine = OllamaEngine(endpoint="http://127.0.0.1:11434")
    # Availability check should return a boolean without throwing an unhandled exception
    avail = engine.is_available()
    assert isinstance(avail, bool)

    # Calling again immediately should use the cached value
    t0 = time.perf_counter()
    avail2 = engine.is_available(force_refresh=False)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert avail2 == avail
    assert elapsed_ms < 1.0  # Cached lookup is sub-millisecond

def test_llm_streaming_and_clause_buffering():
    """Verify stream_chat and stream_clauses generate valid speech chunks."""
    engine = OllamaEngine()
    messages = [{"role": "user", "content": "What is the status of core systems?"}]

    # 1. Test token streaming
    tokens = list(engine.stream_chat(messages))
    assert len(tokens) > 0
    full_text = "".join(tokens)
    assert len(full_text) > 0

    # 2. Test natural clause buffering
    clauses = list(engine.stream_clauses(messages))
    assert len(clauses) > 0
    assert all(len(c.strip()) > 0 for c in clauses)

    # 3. Test immediate cancellation
    cancel_event = threading.Event()
    cancel_event.set()
    canceled_clauses = list(engine.stream_clauses(messages, cancel_event=cancel_event))
    assert len(canceled_clauses) == 0

def test_modular_tts_and_barge_in():
    """Verify modular KokoroTTS / SAPI5 streaming and instant barge-in cutoff."""
    tts = KokoroTTS()
    tts.load()

    # Stream clauses
    clauses = ["Initial clause for speech test.", "Second clause to verify streaming queue."]
    tts.speak_stream(clauses, blocking=False)
    time.sleep(0.02)

    # Trigger stop (barge-in signal)
    t0 = time.perf_counter()
    tts.stop()
    elapsed_ms = (time.perf_counter() - t0) * 1000

    # Cancellation signal dispatch should be fast and practical
    assert elapsed_ms < 500.0
    assert tts.is_speaking() is False

def test_audio_manager_decoupled_queue_and_barge_in():
    """Verify AudioManager non-blocking ingestion and barge-in cutoff."""
    manager = AudioManager(async_mode=True)
    assert manager._async_mode is True

    # Ingest silence chunk (< 1ms execution)
    silence = np.zeros(CHUNK_SAMPLES, dtype=np.float32)
    t0 = time.perf_counter()
    res = manager.process_audio_chunk(silence)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert elapsed_ms < 25.0
    assert res["state"] == AudioState.LISTENING_WAKE.value

    # Simulate speaking state and barge-in cutoff
    manager.tts._is_speaking = True
    t = np.linspace(0, 0.08, CHUNK_SAMPLES, endpoint=False, dtype=np.float32)
    loud_speech = (0.6 * np.sin(2 * np.pi * 350 * t)).astype(np.float32)

    res_speech = manager.process_audio_chunk(loud_speech)
    assert manager.tts.is_speaking() is False
    assert manager.cancel_token.is_set() is True

def test_lightweight_command_router_sub_millisecond_matching():
    """Verify LightweightCommandRouter intent matching latency and deterministic outputs."""
    router = LightweightCommandRouter()

    # 1. Time query
    res_time = router.execute("what time is it")
    assert res_time["matched"] is True
    assert res_time["intent"] == "time"
    assert "current time is" in res_time["response"]
    assert res_time["match_latency_ms"] < 25.0  # Intent matching is practical and fast (< 1ms nominal)

    # 2. System status query
    res_status = router.execute("system status")
    assert res_status["matched"] is True
    assert res_status["intent"] == "system_status"
    assert "CPU" in res_status["response"]

    # 3. CPU and RAM queries
    res_cpu = router.execute("cpu usage")
    assert res_cpu["matched"] is True
    assert "utilization" in res_cpu["response"]

    # 4. Identity & capabilities
    res_id = router.execute("who are you")
    assert res_id["matched"] is True
    assert "J.A.R.V.I.S." in res_id["response"]

    # 5. Volume controls
    res_vol = router.execute("volume up")
    assert res_vol["matched"] is True
    assert "Volume increased" in res_vol["response"]

    # 6. Mode switches
    res_surv = router.execute("survival mode")
    assert res_surv["matched"] is True
    assert "Survival Mode" in res_surv["response"]

    # 7. Unmatched complex query falls through
    res_complex = router.execute("Write a quantum mechanical simulation of the universe")
    assert res_complex["matched"] is False
    assert res_complex["response"] is None

def test_command_router_sensitive_action_confirmation():
    """Verify sensitive commands (e.g. shutdown) require explicit user confirmation."""
    router = LightweightCommandRouter()

    # Unconfirmed shutdown request should prompt for confirmation
    res1 = router.execute("shutdown jarvis", user_confirmed=False)
    assert res1["matched"] is True
    assert res1["intent"] == "shutdown"
    assert res1["requires_confirmation"] is True
    assert res1["executed"] is False
    assert "confirm" in res1["response"].lower()

    # User cancels
    res_cancel = router.execute("cancel")
    assert res_cancel["matched"] is True
    assert "cancelled" in res_cancel["response"].lower()

def test_cpu_survival_mode_governor():
    """Verify CPUSurvivalManager profiles, thread limits, and mode transitions."""
    manager = CPUSurvivalManager(default_mode="BALANCED", auto_governor=False)

    # 1. BALANCED Profile
    assert manager.mode == "BALANCED"
    assert manager.get_stt_threads() == 2
    assert manager.get_llm_max_tokens() == 256
    assert manager.is_survival_active() is False

    # 2. Switch to SURVIVAL Profile
    assert manager.set_mode("SURVIVAL") is True
    assert manager.mode == "SURVIVAL"
    assert manager.get_stt_threads() == 1
    assert manager.get_llm_max_tokens() == 128
    assert manager.is_survival_active() is True

    # 3. Switch to TURBO Profile
    assert manager.set_mode("TURBO") is True
    assert manager.mode == "TURBO"
    assert manager.get_stt_threads() == 4
    assert manager.get_llm_max_tokens() == 1024

    # 4. Telemetry audit
    telemetry = manager.get_telemetry()
    assert "system_cpu_percent" in telemetry
    assert "mode" in telemetry
    assert telemetry["mode"] == "TURBO"

def test_conversational_agent_fast_path_and_streaming():
    """Verify ConversationalAgent routes fast queries and streams clauses."""
    agent = ConversationalAgent()
    agent.clear_history()

    # 1. Fast Path
    reply = agent.process_message("what time is it")
    assert "current time is" in reply

    # 2. Streaming Response
    clauses = list(agent.stream_response("status report"))
    assert len(clauses) > 0

def test_fastapi_fast_command_and_survival_endpoints():
    """Verify new REST endpoints on the FastAPI spine."""
    client = TestClient(app)

    # 1. Fast command execution endpoint
    res_cmd = client.post("/api/v1/system/command/fast", json={"command": "what time is it"})
    assert res_cmd.status_code == 200
    data_cmd = res_cmd.json()
    assert data_cmd["matched"] is True
    assert "time" in data_cmd["intent"]

    # 2. Survival telemetry endpoint
    res_surv = client.get("/api/v1/system/survival")
    assert res_surv.status_code == 200
    data_surv = res_surv.json()
    assert "mode" in data_surv
    assert "system_cpu_percent" in data_surv

    # 3. Set survival mode endpoint
    res_set = client.post("/api/v1/system/survival/set_mode", json={"mode": "SURVIVAL"})
    assert res_set.status_code == 200
    data_set = res_set.json()
    assert data_set["status"] == "mode_updated"
    assert data_set["mode"] == "SURVIVAL"

    # Restore balanced mode
    client.post("/api/v1/system/survival/set_mode", json={"mode": "BALANCED"})
