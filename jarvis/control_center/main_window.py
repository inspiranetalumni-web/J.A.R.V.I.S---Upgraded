"""
jarvis/control_center/main_window.py — Master J.A.R.V.I.S Control Center Window
Assembles the futuristic Stark Horizon Top Bar, Left Circular Gauges Panel, Center Voice Orb,
Right Subsystem Matrix Status Cards with double-click detail popups, Model Architecture popup, and Developer Inspector.
Native Windows controls are used for window management.
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy, QProgressBar
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont

from jarvis.control_center.theme import (
    MASTER_STYLESHEET, COLOR_BG_DARK, COLOR_BG_SURFACE, COLOR_BG_CARD,
    COLOR_CYAN, COLOR_CYAN_DIM, COLOR_EMERALD, COLOR_AMBER,
    COLOR_VERONICA_RED, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_BORDER_CARD, FONT_FAMILY_MONO, FONT_FAMILY_UI
)
from jarvis.control_center.state import AssistantState, OperatingMode, state_manager
from jarvis.control_center.telemetry import TelemetryWorker, WebSocketTelemetryWorker
from jarvis.control_center.developer_window import DeveloperInspectorWindow
from jarvis.control_center.widgets.circular_gauge import CircularGauge
from jarvis.control_center.widgets.voice_orb import VoiceOrbWidget
from jarvis.control_center.widgets.status_card import StatusCardWidget
from jarvis.control_center.widgets.top_bar import TopBarWidget
from jarvis.control_center.widgets.bottom_panel import BottomPanelWidget
from jarvis.control_center.widgets.detail_dialog import SubsystemDetailDialog
from jarvis.control_center.widgets.model_info_dialog import ModelInformationDialog

class JarvisControlCenterWindow(QMainWindow):
    """
    Main Desktop Control Center Application Shell for J.A.R.V.I.S.
    """
    def __init__(self, endpoint: str = "http://127.0.0.1:8765"):
        super().__init__()
        self.endpoint = endpoint
        self.setWindowTitle("J.A.R.V.I.S Control Center")
        self.resize(1260, 840)
        self.setMinimumSize(1024, 680)
        self.setStyleSheet(MASTER_STYLESHEET)

        self._latest_telemetry: Dict[str, Any] = {}

        # Singleton Developer Inspector Window
        self.dev_window = DeveloperInspectorWindow()

        # Build Main UI Layout
        self._init_ui()

        # Initialize Background Telemetry Thread
        self.telemetry_worker = TelemetryWorker(poll_interval_s=1.2)
        self.telemetry_worker.telemetry_updated.connect(self._on_telemetry_updated)
        self.telemetry_worker.spine_health_updated.connect(self._on_spine_health_updated)
        self.telemetry_worker.start()

        # Initialize High-Speed 30 Hz WebSocket Telemetry & Spectrum Visualizer Stream
        self.ws_worker = WebSocketTelemetryWorker()
        self.ws_worker.spectrum_received.connect(self.voice_orb.set_spectrum_data)
        self.ws_worker.persona_received.connect(self._on_persona_changed)
        self.ws_worker.stress_received.connect(self.voice_orb.set_stress_level)
        self.ws_worker.start()

        # Connect State Manager Signals
        state_manager.state_changed.connect(self._on_assistant_state_changed)
        state_manager.welcome_message_changed.connect(self.lbl_welcome.setText)
        state_manager.active_task_changed.connect(self.lbl_active_task.setText)
        state_manager.persona_changed.connect(self._on_persona_changed)
        state_manager.spectrum_updated.connect(self.voice_orb.set_spectrum_data)
        state_manager.stress_updated.connect(self.voice_orb.set_stress_level)

    def _on_persona_changed(self, persona_name: str, color: str):
        """Updates voice orb, greeting label, and theme when persona is swapped."""
        self.voice_orb.set_active_persona(persona_name, color)
        self.lbl_welcome.setText(f"Active AI Persona: {persona_name}")
        self.lbl_welcome.setStyleSheet(f"color: {color};")

    def _init_ui(self):
        root_widget = QWidget()
        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Header Bar (uses native Windows controls for window management)
        self.top_bar = TopBarWidget(self)
        self.top_bar.developer_window_requested.connect(self._open_developer_window)
        self.top_bar.model_info_requested.connect(self._open_model_info_dialog)
        root_layout.addWidget(self.top_bar)

        # 2. Main Middle Workspace
        workspace = QWidget()
        workspace_layout = QHBoxLayout(workspace)
        workspace_layout.setContentsMargins(12, 10, 12, 8)
        workspace_layout.setSpacing(12)

        # --- LEFT PANEL: System Telemetry & Circular Gauges ---
        left_panel = self._build_left_panel()
        workspace_layout.addWidget(left_panel, stretch=3)

        # --- CENTER PANEL: Voice Orb & State Centerpiece ---
        center_panel = self._build_center_panel()
        workspace_layout.addWidget(center_panel, stretch=4)

        # --- RIGHT PANEL: Expanded Subsystem Matrix (Scrollable) ---
        right_panel = self._build_right_panel()
        workspace_layout.addWidget(right_panel, stretch=4)

        root_layout.addWidget(workspace, stretch=1)

        # 3. Bottom Dock: HUD Transcript, Quick Chips & Escrow
        self.bottom_panel = BottomPanelWidget(self)
        self.bottom_panel.recon_requested.connect(self._trigger_recon)
        self.bottom_panel.model_info_requested.connect(self._open_model_info_dialog)
        self.bottom_panel.veronica_requested.connect(self._trigger_veronica_halt)
        self.bottom_panel.dev_window_requested.connect(self._open_developer_window)
        self.bottom_panel.mic_toggle_requested.connect(self._toggle_mute)
        root_layout.addWidget(self.bottom_panel)

        self.setCentralWidget(root_widget)

    def _build_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("cardFrame")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Section Header
        lbl_header = QLabel("SYSTEM TELEMETRY")
        lbl_header.setObjectName("sectionTitle")
        layout.addWidget(lbl_header)

        # Circular Gauges Grid (2 Columns) with Metric-Specific Color Modes
        gauges_widget = QWidget()
        gauges_grid = QGridLayout(gauges_widget)
        gauges_grid.setContentsMargins(0, 0, 0, 0)
        gauges_grid.setSpacing(6)

        self.gauge_cpu = CircularGauge("CPU LOAD", "%", "P-Cores Pinned", metric_type="cpu")
        gauges_grid.addWidget(self.gauge_cpu, 0, 0)

        self.gauge_ram = CircularGauge("RAM USAGE", "%", "512MB Cap", metric_type="ram")
        gauges_grid.addWidget(self.gauge_ram, 0, 1)

        self.gauge_disk = CircularGauge("DISK NVMe", "%", "Storage", metric_type="disk")
        gauges_grid.addWidget(self.gauge_disk, 1, 0)

        self.gauge_battery = CircularGauge("BATTERY", "%", "AC Connected", metric_type="battery")
        gauges_grid.addWidget(self.gauge_battery, 1, 1)

        self.gauge_gpu = CircularGauge("GPU / iGPU", "%", "Intel Iris Xe", metric_type="gpu")
        gauges_grid.addWidget(self.gauge_gpu, 2, 0, 1, 2)

        layout.addWidget(gauges_widget)

        # Hardware Topology Specs Box with Visual Micro-Progress Bars (Frosted Cosmic Glass)
        specs_box = QFrame()
        specs_box.setStyleSheet("background-color: rgba(20, 48, 92, 0.48); border: 1px solid rgba(0, 240, 255, 0.22); border-radius: 6px; padding: 6px;")
        specs_layout = QVBoxLayout(specs_box)
        specs_layout.setContentsMargins(8, 6, 8, 6)
        specs_layout.setSpacing(3)

        lbl_spec_title = QLabel("HARDWARE TOPOLOGY")
        lbl_spec_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_spec_title.setStyleSheet(f"color: {COLOR_CYAN_DIM};")
        specs_layout.addWidget(lbl_spec_title)

        self.lbl_cpu_topo = QLabel("CPU: Intel Core i7 (2P / 12T) @ 0 MHz")
        self.lbl_cpu_topo.setFont(QFont("Consolas", 8))
        self.lbl_cpu_topo.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        self.lbl_cpu_topo.setWordWrap(True)
        specs_layout.addWidget(self.lbl_cpu_topo)

        self.bar_cpu = QProgressBar()
        self.bar_cpu.setRange(0, 100)
        self.bar_cpu.setValue(0)
        specs_layout.addWidget(self.bar_cpu)

        self.lbl_ram_topo = QLabel("RAM: 0.0 GB Total | Ceiling 14.5 GB")
        self.lbl_ram_topo.setFont(QFont("Consolas", 8))
        self.lbl_ram_topo.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        self.lbl_ram_topo.setWordWrap(True)
        specs_layout.addWidget(self.lbl_ram_topo)

        self.bar_ram = QProgressBar()
        self.bar_ram.setRange(0, 100)
        self.bar_ram.setValue(0)
        specs_layout.addWidget(self.bar_ram)

        self.lbl_affinity = QLabel("AFFINITY: P-Core Mask 0x00F [ACTIVE]")
        self.lbl_affinity.setFont(QFont("Consolas", 8))
        self.lbl_affinity.setStyleSheet(f"color: {COLOR_EMERALD};")
        self.lbl_affinity.setWordWrap(True)
        specs_layout.addWidget(self.lbl_affinity)

        layout.addWidget(specs_box)
        layout.addStretch()

        return panel

    def _build_center_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("cardFrame")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        # Welcome Greeting Banner
        self.lbl_welcome = QLabel(state_manager.welcome_message)
        self.lbl_welcome.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_welcome.setStyleSheet(f"color: {COLOR_CYAN};")
        self.lbl_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_welcome.setWordWrap(True)
        layout.addWidget(self.lbl_welcome)

        # Holographic 3D Neural Sphere Voice Orb & Code Graph Centerpiece (Full Canvas Expansion)
        self.voice_orb = VoiceOrbWidget(self)
        self.voice_orb.node_selected.connect(self._on_code_graph_node_selected)
        self.voice_orb.node_double_clicked.connect(self._on_code_graph_node_double_clicked)
        layout.addWidget(self.voice_orb, stretch=1)

        # 3D Holograph Display Mode Selector Strip
        mode_strip = QHBoxLayout()
        mode_strip.setSpacing(6)
        mode_strip.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_mode_voice = QPushButton("🎙️ VOICE ORB")
        self.btn_mode_graph = QPushButton("🕸️ CODE GRAPH")
        self.btn_mode_hybrid = QPushButton("⚡ HYBRID")

        for btn in [self.btn_mode_voice, self.btn_mode_graph, self.btn_mode_hybrid]:
            btn.setCheckable(True)
            btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            btn.setStyleSheet(
                f"QPushButton {{ background-color: rgba(0, 240, 255, 0.08); color: {COLOR_CYAN}; "
                f"border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 4px; padding: 3px 8px; font-size: 10px; }} "
                f"QPushButton:hover {{ background-color: rgba(0, 240, 255, 0.18); color: #ffffff; }} "
                f"QPushButton:checked {{ background-color: rgba(0, 240, 255, 0.30); color: #ffffff; border: 1px solid {COLOR_CYAN}; }}"
            )

        self.btn_mode_voice.setChecked(True)
        self.btn_mode_voice.clicked.connect(lambda: self._set_orb_mode("VOICE_ORB"))
        self.btn_mode_graph.clicked.connect(lambda: self._set_orb_mode("CODE_GRAPH"))
        self.btn_mode_hybrid.clicked.connect(lambda: self._set_orb_mode("HYBRID"))

        mode_strip.addWidget(self.btn_mode_voice)
        mode_strip.addWidget(self.btn_mode_graph)
        mode_strip.addWidget(self.btn_mode_hybrid)
        layout.addLayout(mode_strip)

        # State Indicator Badge
        self.lbl_state_badge = QLabel("STATE: IDLE")
        self.lbl_state_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_state_badge.setStyleSheet(
            f"color: {COLOR_EMERALD}; background-color: rgba(0, 255, 170, 0.15); "
            f"border: 1px solid rgba(0, 255, 170, 0.45); border-radius: 12px; padding: 4px 16px;"
        )
        self.lbl_state_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_state_badge, alignment=Qt.AlignmentFlag.AlignCenter)

        # Current Active Task Card (Frosted Cosmic Glass)
        task_card = QFrame()
        task_card.setStyleSheet("background-color: rgba(20, 48, 92, 0.48); border: 1px solid rgba(0, 240, 255, 0.22); border-radius: 6px; padding: 6px;")
        task_layout = QVBoxLayout(task_card)
        task_layout.setContentsMargins(10, 8, 10, 8)
        task_layout.setSpacing(2)

        lbl_task_hdr = QLabel("ACTIVE OPERATION / GOAL:")
        lbl_task_hdr.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_task_hdr.setStyleSheet(f"color: {COLOR_CYAN_DIM}; letter-spacing: 0.8px;")
        task_layout.addWidget(lbl_task_hdr)

        self.lbl_active_task = QLabel(state_manager.active_task)
        self.lbl_active_task.setFont(QFont("Segoe UI", 9))
        self.lbl_active_task.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        self.lbl_active_task.setWordWrap(True)
        task_layout.addWidget(self.lbl_active_task)

        layout.addWidget(task_card)

        # Quick Action Controls Toolbar
        btn_toolbar = QHBoxLayout()
        btn_toolbar.setSpacing(8)

        self.btn_mute = QPushButton("🎤 MUTE MIC")
        self.btn_mute.clicked.connect(self._toggle_mute)
        btn_toolbar.addWidget(self.btn_mute)

        self.btn_recon = QPushButton("🔍 RECON SCAN")
        self.btn_recon.clicked.connect(self._trigger_recon)
        btn_toolbar.addWidget(self.btn_recon)

        self.btn_veronica = QPushButton("⚡ VERONICA")
        self.btn_veronica.setObjectName("dangerBtn")
        self.btn_veronica.setToolTip("Protocol VERONICA — Safe Halt & Sandbox Reset")
        self.btn_veronica.clicked.connect(self._trigger_veronica_halt)
        btn_toolbar.addWidget(self.btn_veronica)

        layout.addLayout(btn_toolbar)
        layout.addStretch()

        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("cardFrame")
        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        # Section Header with Hint
        hdr_layout = QHBoxLayout()
        lbl_header = QLabel("SUBSYSTEM MATRIX")
        lbl_header.setObjectName("sectionTitle")
        hdr_layout.addWidget(lbl_header)

        hdr_layout.addStretch()

        lbl_hint = QLabel("(Double-click card for details)")
        lbl_hint.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        lbl_hint.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        hdr_layout.addWidget(lbl_hint)

        main_layout.addLayout(hdr_layout)

        # Scroll Area for Subsystem Cards to prevent any text clipping
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: transparent; }}")

        container = QWidget()
        container.setStyleSheet("background: transparent; background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(6)

        # 7 Real Subsystem Diagnostic Cards
        self.subsystem_cards: Dict[str, StatusCardWidget] = {}

        cards_config = [
            ("voice_pipeline", "Voice Pipeline Health", "🎙️", "DualGate VAD + Kokoro TTS", "16kHz Stream | Barge-in Armed"),
            ("cognitive_engine", "Local Cognitive Engine", "🧠", "P-Core Affinity (Mask 0x00F)", "Token Ceiling: 256 | Cap: 512MB"),
            ("queue_latency", "Queue Pressure & Latency", "⚡", "Depth: 0/8 | Intent: <1ms", "Real-Time Streaming (<200ms)"),
            ("skill_registry", "Skill Registry & Knowledge", "📚", "15 Dynamic Workflows", "100+ CS Terms | Stdio MCP Tools"),
            ("memory_vault", "Memory Vault & Storage", "💾", "ChromaDB + SQLite Triples", "AES-256 Vault | 3-Ring Token Budget"),
            ("privacy_gate", "Privacy Gate & Guardrails", "🛡️", "100% OFFLINE Sovereign", "4-Layer Sandbox | VERONICA Armed"),
            ("power_thermal", "Power & Thermal Governor", "🔋", "Battery: 100% (AC Supply)", "Clock Dynamic | CPU Survival Ready"),
        ]

        for key, title, icon, init_val, subtext in cards_config:
            card = StatusCardWidget(
                title=title,
                icon=icon,
                initial_val=init_val,
                subtext=subtext,
                status_color=COLOR_EMERALD,
                subsystem_key=key,
                parent=self
            )
            card.double_clicked.connect(self._on_subsystem_card_double_clicked)
            layout.addWidget(card)
            self.subsystem_cards[key] = card

        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll, stretch=1)

        return panel

    def _open_developer_window(self):
        """Opens the full Developer Inspector Window."""
        if self._latest_telemetry:
            self.dev_window.update_telemetry(self._latest_telemetry)
        self.dev_window.show()
        self.dev_window.raise_()
        self.dev_window.activateWindow()

    def _open_model_info_dialog(self):
        """Opens the read-only Model Architecture & Operating Profiles dialog."""
        dialog = ModelInformationDialog(parent=self)
        dialog.exec()

    def _on_subsystem_card_double_clicked(self, subsystem_key: str):
        """Opens the compact SubsystemDetailDialog popup."""
        subsystems_data = self._latest_telemetry.get("subsystems", {})
        sub_info = subsystems_data.get(subsystem_key)
        if not sub_info:
            card = self.subsystem_cards.get(subsystem_key)
            sub_info = {
                "name": card.lbl_title.text() if card else subsystem_key.upper(),
                "icon": card.lbl_icon.text() if card else "⚡",
                "status": "UNAVAILABLE",
                "summary": "Subsystem telemetry currently unavailable or disconnected.",
                "metrics": [
                    {"label": "Current Status", "value": "Unavailable", "explanation": "No telemetry response received from host module."},
                    {"label": "Host Integration", "value": "Not Connected", "explanation": "Host service unreachable."}
                ]
            }

        dialog = SubsystemDetailDialog(subsystem_key=subsystem_key, data=sub_info, parent=self)
        dialog.view_developer_requested.connect(self._on_view_raw_in_dev_window)
        dialog.exec()

    def _on_view_raw_in_dev_window(self, subsystem_key: str):
        """Opens and focuses the Developer Window to the specific subsystem."""
        if self._latest_telemetry:
            self.dev_window.update_telemetry(self._latest_telemetry)
        self.dev_window.focus_subsystem(subsystem_key)

    def _toggle_mute(self):
        if state_manager.assistant_state == AssistantState.MUTED:
            state_manager.set_assistant_state(AssistantState.IDLE)
            self.btn_mute.setText("🎤 MUTE MIC")
            state_manager.add_transcript_entry("system", "Microphone unmuted. Listening resumed.")
        else:
            state_manager.set_assistant_state(AssistantState.MUTED)
            self.btn_mute.setText("🎙️ UNMUTE MIC")
            state_manager.add_transcript_entry("system", "Microphone muted by operator.")

    def _trigger_recon(self):
        state_manager.set_assistant_state(AssistantState.THINKING)
        state_manager.set_active_task("Running Tony Stark 5-Stage RECON scan...")
        state_manager.add_transcript_entry("system", "Stage 1: RECON surface audit initialized.")
        try:
            from jarvis.system.stark_mindset_engine import stark_engine
            res = stark_engine.recon()
            state_manager.set_last_command({"command": "stark_recon", "result": f"OK ({res.get('status', 'success')})", "status": "success"})
        except Exception as e:
            state_manager.set_last_command({"command": "stark_recon", "result": f"Error ({e})", "status": "error"})

    def _trigger_veronica_halt(self):
        state_manager.request_action_escrow(
            action_id="VERONICA_EMERGENCY_HALT",
            description="Engage Protocol VERONICA: Terminate non-critical background jobs, purge working memory, and reset guardrails."
        )

    def _on_assistant_state_changed(self, state_str: str):
        self.voice_orb.set_state(state_str)
        self.lbl_state_badge.setText(f"STATE: {state_str.upper()}")
        
        color_map = {
            "IDLE": COLOR_EMERALD,
            "LISTENING": COLOR_CYAN,
            "THINKING": COLOR_CYAN_DIM,
            "SPEAKING": COLOR_EMERALD,
            "EXECUTING": COLOR_CYAN,
            "MUTED": COLOR_AMBER,
            "ERROR": COLOR_VERONICA_RED
        }
        color = color_map.get(state_str.upper(), COLOR_EMERALD)
        self.lbl_state_badge.setStyleSheet(
            f"color: {color}; background-color: rgba(15, 35, 71, 0.85); "
            f"border: 1px solid {color}; border-radius: 12px; padding: 4px 16px;"
        )

    def _on_telemetry_updated(self, data: dict):
        self._latest_telemetry = data

        # 1. Update circular gauges with real values & metric types
        self.gauge_cpu.set_value(data.get("cpu_percent"))
        self.gauge_ram.set_value(data.get("ram_percent"))
        self.gauge_disk.set_value(data.get("disk_percent"))
        
        is_plugged = bool(data.get("power_plugged", True))
        self.gauge_battery.set_charging(is_plugged)
        self.gauge_battery.set_value(data.get("battery_percent", 100.0))
        
        self.gauge_gpu.set_value(data.get("gpu_load_percent"))

        # Subtexts
        if data.get("cpu_percent") is not None:
            self.gauge_cpu.set_subtext(f"{data.get('cpu_cores', '2P/12T')} @ {data.get('cpu_freq_mhz', 0)}MHz")
        else:
            self.gauge_cpu.set_subtext("Unavailable")

        if data.get("ram_percent") is not None:
            self.gauge_ram.set_subtext(f"{data.get('ram_used_gb', 0)}GB / {data.get('ram_total_gb', 16)}GB")
        else:
            self.gauge_ram.set_subtext("Unavailable")

        if data.get("disk_percent") is not None:
            self.gauge_disk.set_subtext(f"{data.get('disk_used_gb', 0)}GB / {data.get('disk_total_gb', 512)}GB")
        else:
            self.gauge_disk.set_subtext("Unavailable")
        
        power_str = "⚡ AC Connected" if is_plugged else "On Battery"
        self.gauge_battery.set_subtext(power_str)

        # Update Hardware Readouts & Micro-Bars
        cpu_val = data.get("cpu_percent")
        if cpu_val is not None:
            self.lbl_cpu_topo.setText(f"CPU: {data.get('cpu_cores', '2P/12T')} @ {data.get('cpu_freq_mhz', 0)} MHz")
            self.bar_cpu.setValue(int(cpu_val))
        else:
            self.lbl_cpu_topo.setText("CPU: Unavailable")
            self.bar_cpu.setValue(0)

        ram_val = data.get("ram_percent")
        if ram_val is not None:
            self.lbl_ram_topo.setText(f"RAM: {data.get('ram_used_gb', 0)}GB / {data.get('ram_total_gb', 16)}GB")
            self.bar_ram.setValue(int(ram_val))
        else:
            self.lbl_ram_topo.setText("RAM: Unavailable")
            self.bar_ram.setValue(0)

        # Update Status Cards with Subsystems Telemetry
        subsystems = data.get("subsystems", {})
        for key, card in self.subsystem_cards.items():
            if key in subsystems:
                info = subsystems[key]
                metrics = info.get("metrics", [])
                if metrics:
                    card.set_value(f"{metrics[0].get('value', '--')}")
                    if len(metrics) > 1:
                        card.set_subtext(f"{metrics[1].get('label', '')}: {metrics[1].get('value', '')}")
                status = info.get("status", "NOMINAL")
                card.set_status_color(COLOR_EMERALD if status == "NOMINAL" else (COLOR_AMBER if status == "WARNING" else COLOR_CYAN))
            else:
                card.set_value("Unavailable")
                card.set_subtext("Not Connected")
                card.set_status_color(COLOR_TEXT_MUTED)

        # 2. Check and Display Proactive Warnings (strictly real conditions)
        warnings = data.get("warnings", [])
        if warnings:
            top_warn = warnings[0]
            self.bottom_panel.display_safety_alert(top_warn.get("level", "WARN"), top_warn.get("message", ""))
        else:
            self.bottom_panel.display_safety_alert("INFO", "")

        # 3. Update Developer Window if visible
        if self.dev_window.isVisible():
            self.dev_window.update_telemetry(data)

    def _on_spine_health_updated(self, health: dict):
        status = health.get("status", "offline")
        uptime = health.get("uptime_seconds", 0)
        self.lbl_affinity.setText(f"SPINE: {status.upper()} (Uptime: {int(uptime)}s | P-Cores)")

    def _set_orb_mode(self, mode: str):
        """Sets the active display mode on the 3D Holograph centerpiece."""
        self.voice_orb.set_display_mode(mode)
        self.btn_mode_voice.setChecked(mode == "VOICE_ORB")
        self.btn_mode_graph.setChecked(mode == "CODE_GRAPH")
        self.btn_mode_hybrid.setChecked(mode == "HYBRID")

    def _on_code_graph_node_selected(self, node_id: str):
        """Handles selection of a code node in the 3D holographic graph."""
        from jarvis.analysis.code_graph import code_graph_engine
        blast = code_graph_engine.get_blast_radius(node_id)
        msg = f"Inspecting AST Node: {node_id} ({len(blast['downstream_dependencies'])} dependencies, {len(blast['callers_and_importers'])} callers)"
        self.bottom_panel.display_safety_alert("INFO", msg)

    def _on_code_graph_node_double_clicked(self, node_id: str):
        """Opens the full Stark HUD AST Inspector Dialog for the double-clicked node."""
        from jarvis.control_center.widgets.code_graph_detail_dialog import CodeGraphDetailDialog
        dlg = CodeGraphDetailDialog(node_id, self)
        dlg.exec()

    def closeEvent(self, event):
        """Cleanly terminate telemetry thread, websocket stream, and child windows upon window closure."""
        if hasattr(self, "telemetry_worker") and self.telemetry_worker.isRunning():
            self.telemetry_worker.stop()
        if hasattr(self, "ws_worker") and self.ws_worker.isRunning():
            self.ws_worker.stop()
        if hasattr(self, "dev_window") and self.dev_window.isVisible():
            self.dev_window.close()
        event.accept()

