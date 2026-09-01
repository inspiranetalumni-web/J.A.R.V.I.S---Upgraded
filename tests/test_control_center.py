"""
tests/test_control_center.py — Comprehensive Pytest Test Suite for J.A.R.V.I.S Control Center
Validates UI state management, background telemetry collection, custom widgets,
double-click subsystem detail popups, and the Developer Inspector Window.
"""

import sys
import pytest
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt

def test_state_manager(qapp):
    """Test reactive state management, signal emissions, and escrow handling."""
    from jarvis.control_center.state import ControlCenterStateManager, AssistantState, OperatingMode

    sm = ControlCenterStateManager()
    received_states = []
    received_modes = []
    received_escrows = []

    sm.state_changed.connect(lambda s: received_states.append(s))
    sm.mode_changed.connect(lambda m: received_modes.append(m))
    sm.action_escrow_requested.connect(lambda aid, desc: received_escrows.append((aid, desc)))

    # Test State changes
    sm.set_assistant_state(AssistantState.LISTENING)
    assert sm.assistant_state == AssistantState.LISTENING
    assert "Listening" in received_states

    sm.set_assistant_state("thinking")
    assert sm.assistant_state == AssistantState.THINKING

    # Test Mode changes
    sm.set_operating_mode(OperatingMode.TURBO)
    assert sm.operating_mode == OperatingMode.TURBO
    assert "TURBO" in received_modes

    # Test Escrow
    sm.request_action_escrow("TEST_ACT", "Test action description")
    assert len(received_escrows) == 1
    assert received_escrows[0][0] == "TEST_ACT"
    assert sm.current_escrow["id"] == "TEST_ACT"

    sm.resolve_action_escrow("TEST_ACT", True)
    assert sm.current_escrow is None

    # Test Transcript
    sm.add_transcript_entry("user", "Hello Jarvis")
    sm.add_transcript_entry("jarvis", "Greetings, Sir.")
    assert len(sm.transcript_history) >= 2

def test_telemetry_collection_and_subsystems(qapp):
    """Test deep telemetry metric gathering, subsystem extraction, and fallback data resilience."""
    from jarvis.control_center.telemetry import TelemetryWorker

    worker = TelemetryWorker(poll_interval_s=0.5)
    metrics = worker._collect_metrics()

    expected_keys = [
        "cpu_percent", "ram_percent", "disk_percent", "battery_percent",
        "gpu_load_percent", "lan_ip", "is_online", "spine_online", "subsystems", "warnings"
    ]
    for k in expected_keys:
        assert k in metrics, f"Missing telemetry key: {k}"

    assert 0.0 <= metrics["cpu_percent"] <= 100.0
    assert 0.0 <= metrics["ram_percent"] <= 100.0
    assert 0.0 <= metrics["disk_percent"] <= 100.0

    # Verify all 7 real subsystem categories are present
    subsystems = metrics["subsystems"]
    expected_subsystems = [
        "voice_pipeline", "cognitive_engine", "queue_latency",
        "skill_registry", "memory_vault", "privacy_gate", "power_thermal"
    ]
    for s_key in expected_subsystems:
        assert s_key in subsystems, f"Missing subsystem: {s_key}"
        sub_info = subsystems[s_key]
        assert "name" in sub_info
        assert "summary" in sub_info
        assert "metrics" in sub_info
        assert len(sub_info["metrics"]) >= 3, f"Subsystem {s_key} has fewer than 3 metrics"

def test_subsystem_detail_dialog_all_categories(qapp):
    """Test SubsystemDetailDialog pop-up creation and data population for all 7 subsystems."""
    from jarvis.control_center.widgets.detail_dialog import SubsystemDetailDialog
    from jarvis.control_center.telemetry import TelemetryWorker

    worker = TelemetryWorker()
    metrics = worker._collect_metrics()
    subsystems = metrics["subsystems"]

    for s_key, sub_info in subsystems.items():
        dialog = SubsystemDetailDialog(subsystem_key=s_key, data=sub_info)
        dialog.resize(500, 440)
        assert dialog.subsystem_key == s_key
        assert sub_info["name"].upper() in dialog.windowTitle().upper()
        # Verify developer window signal hook
        clicked_keys = []
        dialog.view_developer_requested.connect(lambda k: clicked_keys.append(k))
        dialog._on_view_raw_details()
        assert clicked_keys == [s_key]
        dialog.close()

def test_developer_inspector_window(qapp):
    """Test DeveloperInspectorWindow tabs, JSON snapshot, and subsystem focus."""
    from jarvis.control_center.developer_window import DeveloperInspectorWindow
    from jarvis.control_center.telemetry import TelemetryWorker

    worker = TelemetryWorker()
    metrics = worker._collect_metrics()

    dev_win = DeveloperInspectorWindow()
    dev_win.update_telemetry(metrics)

    assert dev_win.tabs.count() == 5
    assert dev_win.tree_subsystems.topLevelItemCount() == 7
    assert dev_win.tree_code_nodes.topLevelItemCount() > 0

    # Test filtering
    dev_win._filter_tree("voice")
    # Test focus_subsystem
    dev_win.focus_subsystem("voice_pipeline")
    assert dev_win.tabs.currentIndex() == 0

    # Test JSON Tab
    assert "cpu_percent" in dev_win.txt_json.toPlainText()

    dev_win.close()

def test_status_card_double_click(qapp):
    """Test StatusCardWidget double_clicked signal emission and word wrap."""
    from jarvis.control_center.widgets.status_card import StatusCardWidget
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QPointF, Qt

    card = StatusCardWidget(
        title="Voice Health", icon="🎙️",
        initial_val="16kHz", subtext="Nominal",
        subsystem_key="voice_pipeline"
    )

    received_keys = []
    card.double_clicked.connect(lambda k: received_keys.append(k))

    # Simulate mouse double-click event
    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonDblClick,
        QPointF(10, 10),
        QPointF(10, 10),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    card.mouseDoubleClickEvent(event)

    assert received_keys == ["voice_pipeline"]

def test_circular_gauge(qapp):
    """Test CircularGauge creation, delta clamping, and paint event handling."""
    from jarvis.control_center.widgets.circular_gauge import CircularGauge
    from jarvis.control_center.theme import COLOR_CYAN, COLOR_EMERALD, COLOR_AMBER, COLOR_VERONICA_RED, COLOR_BLUE

    # 1. CPU Gauge Color Logic
    gauge_cpu = CircularGauge(title="CPU LOAD", unit="%", metric_type="cpu")
    gauge_cpu.resize(100, 115)
    gauge_cpu.set_value(30.0)
    assert gauge_cpu._compute_color().name().lower() == COLOR_CYAN.lower()

    gauge_cpu.set_value(65.0)
    assert gauge_cpu._compute_color().name().lower() == COLOR_AMBER.lower()

    gauge_cpu.set_value(88.0)
    assert gauge_cpu._compute_color().name().lower() == COLOR_VERONICA_RED.lower()

    # 2. RAM Gauge Color Logic
    gauge_ram = CircularGauge(title="RAM USAGE", unit="%", metric_type="ram")
    gauge_ram.set_value(30.0)
    assert gauge_ram._compute_color().name().lower() == COLOR_EMERALD.lower()

    gauge_ram.set_value(55.0)
    assert gauge_ram._compute_color().name().lower() == COLOR_BLUE.lower()

    gauge_ram.set_value(78.0)
    assert gauge_ram._compute_color().name().lower() == COLOR_AMBER.lower()

    gauge_ram.set_value(92.0)
    assert gauge_ram._compute_color().name().lower() == COLOR_VERONICA_RED.lower()

    # 3. Battery Gauge & Charging State
    gauge_bat = CircularGauge(title="BATTERY", unit="%", metric_type="battery")
    gauge_bat.set_charging(True)
    gauge_bat.set_value(100.0)
    assert gauge_bat._compute_color().name().lower() == COLOR_EMERALD.lower()

    gauge_bat.set_charging(False)
    gauge_bat.set_value(15.0)
    assert gauge_bat._compute_color().name().lower() == COLOR_VERONICA_RED.lower()

    # 4. Clamping and paint event
    gauge_cpu.set_value(150.0)
    assert gauge_cpu.get_value() == 100.0
    gauge_cpu.set_value(-20.0)
    assert gauge_cpu.get_value() == 0.0
    gauge_cpu.repaint()

def test_model_information_dialog(qapp):
    """Test ModelInformationDialog popup instantiation, read-only content, and mode specs."""
    from jarvis.control_center.widgets.model_info_dialog import ModelInformationDialog

    dialog = ModelInformationDialog()
    assert "COGNITIVE ARCHITECTURE" in dialog.windowTitle().upper()
    assert dialog.isModal() is True

    # Check that all 4 modes are present in the dialog text/widgets
    rendered_text = " ".join([lbl.text() for lbl in dialog.findChildren(QLabel)])
    assert "BALANCED MODE" in rendered_text
    assert "SURVIVAL MODE" in rendered_text
    assert "TURBO MODE" in rendered_text
    assert "AUTO MODE" in rendered_text
    assert "P-Core Affinity" in rendered_text or "P-Cores" in rendered_text

    dialog.close()

def test_voice_orb_widget_throttling(qapp):
    """Test VoiceOrbWidget dynamic FPS throttling across Idle vs Active states."""
    from jarvis.control_center.widgets.voice_orb import VoiceOrbWidget
    from jarvis.control_center.state import AssistantState

    orb = VoiceOrbWidget()
    orb.resize(200, 200)

    # Idle state should throttle to 15 FPS (66ms interval)
    orb.set_state(AssistantState.IDLE)
    assert orb._timer.interval() == 66

    # Listening state should switch to 30 FPS (33ms interval)
    orb.set_state(AssistantState.LISTENING)
    assert orb._timer.interval() == 33

    # Speaking state should switch to high rate (22ms interval)
    orb.set_state(AssistantState.SPEAKING)
    assert orb._timer.interval() == 22

    for state in AssistantState:
        orb.set_state(state)
        assert orb._state == state
        orb._on_tick()
        orb.repaint()

def test_top_bar_widget(qapp):
    """Test TopBarWidget header, mode switches, online indicator, and Model Info."""
    from jarvis.control_center.widgets.top_bar import TopBarWidget

    top_bar = TopBarWidget()
    assert "J.A.R.V.I.S. CONTROL CENTER" in top_bar.lbl_title.text()

    # Test Model Info signal
    info_triggered = []
    top_bar.model_info_requested.connect(lambda: info_triggered.append(True))
    top_bar.btn_mode_info.click()
    assert len(info_triggered) == 1

    # Test Mode switcher button interaction
    top_bar.set_active_mode("SURVIVAL")
    assert top_bar.mode_buttons["SURVIVAL"].isChecked()

    # Test Online status toggling
    top_bar.set_online_status(True)
    assert "ONLINE" in top_bar.online_pill.text()

    top_bar.set_online_status(False)
    assert "SOVEREIGN" in top_bar.online_pill.text()

def test_bottom_panel_widget(qapp):
    """Test BottomPanelWidget transcript, quick action chips, action escrow, and safety alerts."""
    from jarvis.control_center.widgets.bottom_panel import BottomPanelWidget

    panel = BottomPanelWidget()
    panel.add_transcript_line("user", "Run diagnostics")
    assert "Run diagnostics" in panel.txt_transcript.toPlainText()

    # Test Quick Action Chips signals
    chips_triggered = []
    panel.recon_requested.connect(lambda: chips_triggered.append("recon"))
    panel.model_info_requested.connect(lambda: chips_triggered.append("model"))
    panel.dev_window_requested.connect(lambda: chips_triggered.append("dev"))
    panel.veronica_requested.connect(lambda: chips_triggered.append("veronica"))
    panel.mic_toggle_requested.connect(lambda: chips_triggered.append("mic"))

    panel.btn_chip_recon.click()
    panel.btn_chip_model.click()
    panel.btn_chip_guardrails.click()
    panel.btn_chip_veronica.click()
    panel.btn_chip_mic.click()

    assert chips_triggered == ["recon", "model", "dev", "veronica", "mic"]

    # Test Escrow prompt display
    panel.show_escrow_prompt("ACTION_01", "Authorize test task")
    assert panel.action_stack.currentIndex() == 1
    assert "ACTION_01" in panel._current_action_id

    # Test Authorize click
    panel.btn_authorize.click()
    assert panel.action_stack.currentIndex() == 0

    # Test Safety Alert display
    panel.display_safety_alert("WARN", "High memory usage")
    assert "WARN" in panel.lbl_safety_alert.text()

def test_main_window_instantiation(qapp):
    """Test JarvisControlCenterWindow full assembly, card double-clicks, and graceful shutdown."""
    from jarvis.control_center.main_window import JarvisControlCenterWindow
    from jarvis.control_center.state import state_manager, AssistantState

    win = JarvisControlCenterWindow(endpoint="http://127.0.0.1:8765")
    win.resize(1100, 750)
    win.show()

    # Verify key widgets are instantiated
    assert win.gauge_cpu is not None
    assert win.gauge_ram is not None
    assert win.gauge_disk is not None
    assert win.gauge_battery is not None
    assert win.gauge_gpu is not None
    assert win.voice_orb is not None
    assert win.top_bar is not None
    assert win.bottom_panel is not None
    assert len(win.subsystem_cards) == 7
    assert win.dev_window is not None

    # Test Dev Window opener
    win._open_developer_window()
    assert win.dev_window.isVisible()

    # Clean close
    win.close()
    if hasattr(win, "telemetry_worker") and win.telemetry_worker.isRunning():
        win.telemetry_worker.stop()
