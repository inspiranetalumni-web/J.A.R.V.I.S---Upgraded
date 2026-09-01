"""
jarvis/control_center/widgets/bottom_panel.py — Next-Gen HUD Transcript & Interactive Action Panel
Displays real-time timestamped voice transcripts, interactive quick action chips,
active operation status, user permission escrow modals, and proactive security alerts.
"""

import time
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QWidget, QStackedWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from jarvis.control_center.state import state_manager
from jarvis.control_center.theme import (
    COLOR_BG_SURFACE, COLOR_BG_CARD, COLOR_BG_INPUT, COLOR_BORDER_CARD, COLOR_CYAN,
    COLOR_CYAN_DIM, COLOR_EMERALD, COLOR_AMBER, COLOR_VERONICA_RED,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    FONT_FAMILY_MONO, FONT_FAMILY_UI
)

class BottomPanelWidget(QFrame):
    """
    Bottom dock handling live conversational transcript, interactive prompt chips,
    action verification, and safety notifications.
    """
    recon_requested = Signal()
    model_info_requested = Signal()
    veronica_requested = Signal()
    dev_window_requested = Signal()
    mic_toggle_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bottomFrame")
        self.setFixedHeight(175)
        self.setStyleSheet(
            f"QFrame#bottomFrame {{ background-color: rgba(15, 35, 71, 0.88); "
            f"border-top: 1px solid rgba(0, 240, 255, 0.25); }}"
        )

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 8, 16, 8)
        main_layout.setSpacing(14)

        # 1. Left Sub-Panel: Live Transcript Feed + Interactive Quick Chips
        transcript_container = QVBoxLayout()
        transcript_container.setSpacing(4)

        lbl_transcript_title = QLabel("LIVE PERCEPTION TRANSCRIPT // HUD TERMINAL")
        lbl_transcript_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_transcript_title.setStyleSheet(f"color: {COLOR_CYAN}; letter-spacing: 0.8px; background: transparent;")
        transcript_container.addWidget(lbl_transcript_title)

        self.txt_transcript = QTextEdit()
        self.txt_transcript.setReadOnly(True)
        self.txt_transcript.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.txt_transcript.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.txt_transcript.setStyleSheet(
            f"background-color: rgba(20, 48, 92, 0.48); color: {COLOR_TEXT_PRIMARY}; "
            f"border: 1px solid rgba(0, 240, 255, 0.22); border-radius: 6px; font-size: 11px; padding: 6px;"
        )
        init_time = time.strftime("%H:%M:%S")
        self.txt_transcript.setHtml(
            f"<span style='color:{COLOR_TEXT_MUTED}; font-size:10px;'>[{init_time}]</span> "
            f"<span style='color:#00ffaa; font-weight:bold;'>[JARVIS]:</span> J.A.R.V.I.S Control Center initialized. Standing by."
        )
        transcript_container.addWidget(self.txt_transcript)

        # Interactive Quick Action Chips Row
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)

        self.btn_chip_recon = QPushButton("🔍 Recon Audit")
        self.btn_chip_recon.setObjectName("quickChip")
        self.btn_chip_recon.setToolTip("Run Tony Stark 5-Stage Recon Scan")
        self.btn_chip_recon.clicked.connect(self.recon_requested.emit)
        chips_layout.addWidget(self.btn_chip_recon)

        self.btn_chip_model = QPushButton("🧠 Model Specs")
        self.btn_chip_model.setObjectName("quickChip")
        self.btn_chip_model.setToolTip("View Model Architecture & Operating Profiles")
        self.btn_chip_model.clicked.connect(self.model_info_requested.emit)
        chips_layout.addWidget(self.btn_chip_model)

        self.btn_chip_guardrails = QPushButton("🛠️ Dev Inspector")
        self.btn_chip_guardrails.setObjectName("quickChip")
        self.btn_chip_guardrails.setToolTip("Open Developer Window & Diagnostic Inspector")
        self.btn_chip_guardrails.clicked.connect(self.dev_window_requested.emit)
        chips_layout.addWidget(self.btn_chip_guardrails)

        self.btn_chip_veronica = QPushButton("⚡ VERONICA")
        self.btn_chip_veronica.setObjectName("quickChip")
        self.btn_chip_veronica.setToolTip("Engage Protocol VERONICA Emergency Halt")
        self.btn_chip_veronica.clicked.connect(self.veronica_requested.emit)
        chips_layout.addWidget(self.btn_chip_veronica)

        self.btn_chip_mic = QPushButton("🎤 Mic Toggle")
        self.btn_chip_mic.setObjectName("quickChip")
        self.btn_chip_mic.setToolTip("Mute or Unmute Voice Microphone")
        self.btn_chip_mic.clicked.connect(self.mic_toggle_requested.emit)
        chips_layout.addWidget(self.btn_chip_mic)

        chips_layout.addStretch()
        transcript_container.addLayout(chips_layout)

        main_layout.addLayout(transcript_container, stretch=3)

        # 2. Right Sub-Panel: Action Escrow & Safety Alerts Area
        action_container = QVBoxLayout()
        action_container.setSpacing(6)

        lbl_action_title = QLabel("ACTION STATUS & ESCROW GATE")
        lbl_action_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_action_title.setStyleSheet(f"color: {COLOR_CYAN}; letter-spacing: 0.8px; background: transparent;")
        action_container.addWidget(lbl_action_title)

        # Stacked Widget: Normal Status vs. Escrow Prompt
        self.action_stack = QStackedWidget()
        
        # Page 0: Normal Status View
        self.page_normal = QWidget()
        p0_layout = QVBoxLayout(self.page_normal)
        p0_layout.setContentsMargins(0, 0, 0, 0)
        p0_layout.setSpacing(4)

        self.lbl_current_action = QLabel("Current Action: Idle (Listening for wake word 'JARVIS')")
        self.lbl_current_action.setFont(QFont("Segoe UI", 9))
        self.lbl_current_action.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; background: transparent;")
        self.lbl_current_action.setWordWrap(True)
        p0_layout.addWidget(self.lbl_current_action)

        self.lbl_safety_alert = QLabel("● Safety: 4-Layer Guardrails Armed | System Nominal")
        self.lbl_safety_alert.setFont(QFont("Segoe UI", 8))
        self.lbl_safety_alert.setStyleSheet(f"color: {COLOR_EMERALD}; background: transparent;")
        self.lbl_safety_alert.setWordWrap(True)
        p0_layout.addWidget(self.lbl_safety_alert)

        p0_layout.addStretch()
        self.action_stack.addWidget(self.page_normal)

        # Page 1: Escrow Prompt View (User approval needed)
        self.page_escrow = QWidget()
        p1_layout = QVBoxLayout(self.page_escrow)
        p1_layout.setContentsMargins(0, 0, 0, 0)
        p1_layout.setSpacing(4)

        self.lbl_escrow_desc = QLabel("Awaiting confirmation for: [Operation]")
        self.lbl_escrow_desc.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.lbl_escrow_desc.setStyleSheet(f"color: {COLOR_AMBER}; background: transparent;")
        self.lbl_escrow_desc.setWordWrap(True)
        p1_layout.addWidget(self.lbl_escrow_desc)

        escrow_btn_layout = QHBoxLayout()
        escrow_btn_layout.setSpacing(8)

        self.btn_authorize = QPushButton("AUTHORIZE (YES)")
        self.btn_authorize.setObjectName("successBtn")
        self.btn_authorize.clicked.connect(self._on_authorize_clicked)
        escrow_btn_layout.addWidget(self.btn_authorize)

        self.btn_deny = QPushButton("DENY / HALT")
        self.btn_deny.setObjectName("dangerBtn")
        self.btn_deny.clicked.connect(self._on_deny_clicked)
        escrow_btn_layout.addWidget(self.btn_deny)

        p1_layout.addLayout(escrow_btn_layout)
        self.action_stack.addWidget(self.page_escrow)

        action_container.addWidget(self.action_stack)

        main_layout.addLayout(action_container, stretch=2)

        # Hook signals
        state_manager.transcript_added.connect(self.add_transcript_line)
        state_manager.action_escrow_requested.connect(self.show_escrow_prompt)
        state_manager.safety_alert_emitted.connect(self.display_safety_alert)
        state_manager.active_task_changed.connect(self.set_current_action)

        self._current_action_id = ""

    def add_transcript_line(self, speaker: str, text: str):
        time_str = time.strftime("%H:%M:%S")
        if speaker.lower() in ["jarvis", "system"]:
            speaker_tag = f"<span style='color:{COLOR_TEXT_MUTED}; font-size:10px;'>[{time_str}]</span> <span style='color:#00f0ff; font-weight:bold;'>[JARVIS]:</span>"
        elif speaker.lower() in ["security", "alert"]:
            speaker_tag = f"<span style='color:{COLOR_TEXT_MUTED}; font-size:10px;'>[{time_str}]</span> <span style='color:#ffaa00; font-weight:bold;'>[ALERT]:</span>"
        else:
            speaker_tag = f"<span style='color:{COLOR_TEXT_MUTED}; font-size:10px;'>[{time_str}]</span> <span style='color:#00ffaa; font-weight:bold;'>[USER]:</span>"
        
        self.txt_transcript.append(f"{speaker_tag} {text}")
        sb = self.txt_transcript.verticalScrollBar()
        sb.setValue(sb.maximum())

    def set_current_action(self, action_text: str):
        self.lbl_current_action.setText(f"Current Action: {action_text}")

    def show_escrow_prompt(self, action_id: str, description: str):
        self._current_action_id = action_id
        self.lbl_escrow_desc.setText(f"⚠️ USER APPROVAL REQUIRED:\n{description}")
        self.action_stack.setCurrentIndex(1)

    def display_safety_alert(self, level: str, message: str):
        if not message:
            self.lbl_safety_alert.setText("● Safety: 4-Layer Guardrails Armed | System Nominal")
            self.lbl_safety_alert.setStyleSheet(f"color: {COLOR_EMERALD}; background: transparent;")
            return

        color = {
            "INFO": COLOR_CYAN,
            "WARN": COLOR_AMBER,
            "ALERT": COLOR_VERONICA_RED,
            "VERONICA": COLOR_VERONICA_RED
        }.get(level.upper(), COLOR_EMERALD)

        self.lbl_safety_alert.setText(f"● [{level.upper()}]: {message}")
        self.lbl_safety_alert.setStyleSheet(f"color: {color}; background: transparent;")

    def _on_authorize_clicked(self):
        state_manager.resolve_action_escrow(self._current_action_id, True)
        self.add_transcript_line("system", f"Action '{self._current_action_id}' AUTHORIZED by operator.")
        self.action_stack.setCurrentIndex(0)

    def _on_deny_clicked(self):
        state_manager.resolve_action_escrow(self._current_action_id, False)
        self.add_transcript_line("system", f"Action '{self._current_action_id}' DENIED by operator.")
        self.action_stack.setCurrentIndex(0)
