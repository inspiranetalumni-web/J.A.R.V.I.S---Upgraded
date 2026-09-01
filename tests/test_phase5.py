"""
tests/test_phase5.py — Pytest Verification Suite for Phase 5 OS Actuation & Security Guardrails
"""

import os
import pytest
from pathlib import Path
from jarvis.actuation.win32 import Win32Actuator
from jarvis.security.guardrails import SecurityGuardrails
from jarvis.security.veronica_containment import ProtocolVERONICA
from jarvis.vision.gesture_engine import SpatialGestureEngine
from jarvis.vision.gaze_tracker import GazeTracker
from jarvis.config import config

def test_win32_actuator():
    """Verify Win32Actuator window title and key simulation interface."""
    actuator = Win32Actuator()

    title = actuator.get_active_window_title()
    assert isinstance(title, str)
    assert len(title) > 0

    # Key resolution and simulation test (dry_run=True prevents injecting Ctrl+C into running test terminal)
    res_hotkey = actuator.send_hotkey("ctrl", "c", dry_run=True)
    assert res_hotkey is True

    res_press = actuator.press_key("enter", dry_run=True)
    assert res_press is True

def test_security_guardrails():
    """Verify 4-Layer Security Defense System."""
    guard = SecurityGuardrails()

    # Layer 1: Regex Blacklist
    safe1, _ = guard.validate_command("python scripts/verify_system.py")
    assert safe1 is True

    unsafe1, reason1 = guard.validate_command("rm -rf /")
    assert unsafe1 is False
    assert "Blacklisted" in reason1

    unsafe2, reason2 = guard.validate_command("format C:")
    assert unsafe2 is False

    unsafe3, reason3 = guard.validate_command("powershell -Enc AQBmA...")
    assert unsafe3 is False
    assert "Base64" in reason3

    # Layer 2: Path Bounds Validator
    path_safe, _ = guard.validate_path(str(config.root_dir / "jarvis/main.py"))
    assert path_safe is True

    path_unsafe, path_reason = guard.validate_path("C:/Windows/System32/cmd.exe")
    assert path_unsafe is False
    assert "outside authorized roots" in path_reason

    # Layer 3: HMAC Cryptographic HITL Escrow
    assert guard.is_mutating_action("delete_file") is True
    assert guard.is_mutating_action("read_file") is False

    token = guard.create_escrow_token("act_123", "Write to config.py")
    assert isinstance(token, str)
    assert len(token) == 64  # SHA256 hex string

    approved = guard.verify_escrow_approval(token)
    assert approved is True

    # Layer 4: Sandboxing limit
    assert guard.get_job_object_limit_mb() == 512

def test_veronica_containment():
    """Verify Protocol VERONICA emergency lockdown and isolation."""
    veronica = ProtocolVERONICA()

    assert veronica.is_locked_down() is False

    lock_res = veronica.trigger_lockdown("Simulated Intrusion Test")
    assert lock_res["status"] == "CONTAINMENT_ACTIVE"
    assert veronica.is_locked_down() is True

    veronica.release_lockdown()
    assert veronica.is_locked_down() is False

def test_spatial_gesture_and_gaze():
    """Verify 3D Spatial Gesture Engine and Pupil Gaze Tracker."""
    gesture_engine = SpatialGestureEngine()
    gesture_data = gesture_engine.process_frame()
    assert "gesture" in gesture_data
    assert "latency_ms" in gesture_data

    gaze_engine = GazeTracker()
    gaze_data = gaze_engine.get_gaze_point()
    assert "gaze_x" in gaze_data
    assert "gaze_y" in gaze_data
