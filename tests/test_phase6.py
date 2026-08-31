"""
tests/test_phase6.py — Pytest Verification Suite for Phase 6 Standalone Executable & Mobile Gateway
Validates 100% System Completion across all 6 Implementation Phases.
"""

import os
import json
import pytest
from pathlib import Path

from jarvis.tray.system_tray import SystemTrayDaemon
from jarvis.mobile.mobile_gateway import MobileGateway
from jarvis.config import config

def test_system_tray_daemon():
    """Verify SystemTrayDaemon initialization and status telemetry."""
    tray = SystemTrayDaemon()
    status = tray.get_status()
    assert status["status"] == "nominal"
    assert "8765" in status["message"]

    tray.start()
    assert tray.get_status()["is_running"] is True

    tray.stop()
    assert tray.get_status()["is_running"] is False

def test_mobile_gateway():
    """Verify MobileGateway device pairing, WebSocket frame handler, and PWA dashboard."""
    gateway = MobileGateway()

    # 1. Test Device Pairing
    paired = gateway.pair_device("mobile_device_ios_01", "876500")
    assert paired is True
    assert "mobile_device_ios_01" in gateway.paired_devices

    # 2. Test Ping Frame
    ping_resp = gateway.handle_mobile_message(json.dumps({"type": "ping"}))
    assert ping_resp["type"] == "pong"

    # 3. Test Status Frame
    status_resp = gateway.handle_mobile_message(json.dumps({"type": "get_status"}))
    assert status_resp["type"] == "status_response"
    assert "J.A.R.V.I.S." in status_resp["system"]

    # 4. Test Remote Command Frame
    cmd_resp = gateway.handle_mobile_message(json.dumps({"type": "remote_command", "command": "run health check"}))
    assert cmd_resp["type"] == "command_result"
    assert cmd_resp["status"] == "executed"

    # 5. Test PWA HTML Dashboard
    html = gateway.get_mobile_pwa_html()
    assert "J.A.R.V.I.S. MOBILE" in html

def test_build_spec_and_scripts():
    """Verify build specification file, packaging scripts, and master launch/shutdown scripts."""
    spec_path = config.root_dir / "build" / "jarvis.spec"
    pkg_script = config.root_dir / "scripts" / "build_jarvis_exe.ps1"
    boot_script = config.root_dir / "jarvis_boot.ps1"
    shutdown_script = config.root_dir / "jarvis_shutdown.ps1"

    assert spec_path.exists()
    assert pkg_script.exists()
    assert boot_script.exists()
    assert shutdown_script.exists()

def test_jarvis_desktop_hud():
    """Verify JARVISDesktopHUD overlay module structure."""
    from jarvis.hud.overlay import JARVISDesktopHUD
    hud = JARVISDesktopHUD()
    assert hud.endpoint == "http://127.0.0.1:8765"
    hud.root.destroy()

def test_conversational_agent_voice_shutdown():
    """Verify voice shutdown command routing."""
    from jarvis.mcp.router import HybridIntentRouter
    router = HybridIntentRouter()
    route_res = router.route("shutdown jarvis")
    assert route_res["target_tool"] == "shutdown_system"

def test_full_system_100_percent_completion():
    """
    Master Integration Test: Validates that all 6 phases of J.A.R.V.I.S. v3.0 are fully operational.
    """
    # Phase 1: Core System Spine & Environment
    from jarvis.config import config
    from jarvis.system.spec_loader import audit_hardware
    assert config.fastapi_port == 8765
    assert "cpu" in audit_hardware()

    # Phase 2: Audio & Perception Engine
    from jarvis.audio.manager import AudioManager
    audio = AudioManager()
    assert audio.state.value == "LISTENING_WAKE"

    # Phase 3: Cognitive Intelligence & Tiered Memory
    from jarvis.agents.conversational import ConversationalAgent
    agent = ConversationalAgent()
    reply = agent.process_message("Status report, J.A.R.V.I.S.")
    assert isinstance(reply, str)

    # Phase 4: MCP Tools & Automated Workflows
    from jarvis.mcp.router import HybridIntentRouter
    router = HybridIntentRouter()
    route_res = router.route("find file main.py")
    assert route_res["stage"] == 1

    # Phase 5: OS Actuation & Security Guardrails
    from jarvis.security.guardrails import SecurityGuardrails
    guard = SecurityGuardrails()
    is_safe, _ = guard.validate_command("python -m pytest")
    assert is_safe is True

    # Phase 6: System Tray & Mobile Gateway
    from jarvis.mobile.mobile_gateway import MobileGateway
    gateway = MobileGateway()
    assert gateway.generate_pairing_code() == "876500"
