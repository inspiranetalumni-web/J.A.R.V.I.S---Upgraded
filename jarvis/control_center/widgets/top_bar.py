"""
jarvis/control_center/widgets/top_bar.py — Master Control Center Header & Top Bar
Includes title badge, performance mode selectors (BALANCED / SURVIVAL / TURBO / AUTO),
online/offline network pill, live clock/date, and Model Info trigger in a perfectly balanced 3-column layout.
"""

import time
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QButtonGroup, QWidget
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QMouseEvent
from jarvis.control_center.state import OperatingMode, state_manager
from jarvis.control_center.theme import (
    COLOR_BG_SURFACE, COLOR_BG_CARD, COLOR_CYAN, COLOR_CYAN_DIM, COLOR_CYAN_GLOW,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, COLOR_EMERALD,
    COLOR_AMBER, COLOR_VERONICA_RED, COLOR_BORDER_NORMAL, COLOR_BORDER_CARD,
    FONT_FAMILY_MONO
)

class ModeContainerFrame(QFrame):
    """Container frame for mode buttons that emits a signal on double-click."""
    double_clicked = Signal()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

class TopBarWidget(QFrame):
    """
    Symmetrical 3-column header bar providing:
    - Left: Brand Title & Local Sovereign Subtitle
    - Center: Centered Cognitive Operating Mode Selector Pill with Model Info Trigger
    - Right: Local Sovereign / Online Status Pill, Cyber Divider, and Live Clock & Date
    """
    developer_window_requested = Signal()
    model_info_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("headerFrame")
        self.setFixedHeight(56)
        self.setStyleSheet(
            f"QFrame#headerFrame {{ background-color: rgba(12, 28, 58, 0.92); "
            f"border-bottom: 1px solid rgba(0, 240, 255, 0.28); }}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(0)

        # =========================================================================
        # 1. LEFT COLUMN: Brand / Title with Glowing Arc Beacon
        # =========================================================================
        brand_container = QWidget()
        brand_layout = QHBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(10)

        lbl_beacon = QLabel("✦")
        lbl_beacon.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_beacon.setStyleSheet(f"color: {COLOR_CYAN}; background: transparent;")
        brand_layout.addWidget(lbl_beacon)

        title_vbox = QVBoxLayout()
        title_vbox.setContentsMargins(0, 0, 0, 0)
        title_vbox.setSpacing(1)

        self.lbl_title = QLabel("J.A.R.V.I.S. CONTROL CENTER")
        self.lbl_title.setObjectName("brandTitle")
        self.lbl_title.setStyleSheet(f"color: {COLOR_CYAN}; font-size: 13px; font-weight: bold; letter-spacing: 1.1px; background: transparent;")
        title_vbox.addWidget(self.lbl_title)

        self.lbl_sub = QLabel("STARK HORIZON OS // 100% LOCAL SOVEREIGN AI")
        self.lbl_sub.setObjectName("brandSub")
        self.lbl_sub.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 8.5px; letter-spacing: 0.8px; background: transparent;")
        title_vbox.addWidget(self.lbl_sub)

        brand_layout.addLayout(title_vbox)
        layout.addWidget(brand_container, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # =========================================================================
        # 2. CENTER COLUMN: Perfectly Centered Mode Selector Group
        # =========================================================================
        layout.addStretch(1)

        self.mode_container = ModeContainerFrame()
        self.mode_container.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(16, 38, 76, 0.72);
                border: 1px solid rgba(0, 240, 255, 0.28);
                border-radius: 8px;
                padding: 2px 4px;
            }}
            QFrame:hover {{
                border: 1px solid rgba(0, 240, 255, 0.48);
            }}
        """)
        self.mode_container.setToolTip("Select cognitive operating mode (Double-click to view Model architecture details)")
        self.mode_container.double_clicked.connect(self.model_info_requested.emit)
        
        mode_layout = QHBoxLayout(self.mode_container)
        mode_layout.setContentsMargins(4, 2, 4, 2)
        mode_layout.setSpacing(4)

        mode_lbl = QLabel("MODE:")
        mode_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        mode_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; padding-left: 4px; padding-right: 2px; background: transparent;")
        mode_layout.addWidget(mode_lbl)

        self.mode_buttons = {}
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        mode_defs = [
            (OperatingMode.BALANCED, "BALANCED"),
            (OperatingMode.SURVIVAL, "SURVIVAL"),
            (OperatingMode.TURBO, "TURBO"),
            (OperatingMode.AUTO, "AUTO")
        ]

        for mode_enum, label_text in mode_defs:
            btn = QPushButton(label_text)
            btn.setObjectName("modeBtn")
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_TEXT_SECONDARY};
                    border: 1px solid transparent;
                    border-radius: 5px;
                    padding: 4px 12px;
                    font-size: 10.5px;
                    font-weight: 600;
                    letter-spacing: 0.4px;
                }}
                QPushButton:hover {{
                    color: #ffffff;
                    background-color: rgba(0, 240, 255, 0.12);
                    border: 1px solid rgba(0, 240, 255, 0.30);
                }}
                QPushButton:checked {{
                    background-color: rgba(0, 240, 255, 0.25);
                    color: {COLOR_CYAN};
                    border: 1px solid {COLOR_CYAN};
                    font-weight: bold;
                }}
            """)
            if mode_enum == OperatingMode.BALANCED:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, m=mode_enum: self._on_mode_button_clicked(m))
            mode_layout.addWidget(btn)
            self.button_group.addButton(btn)
            self.mode_buttons[mode_enum.value] = btn

        # Info button next to modes
        self.btn_mode_info = QPushButton("ℹ️")
        self.btn_mode_info.setFixedSize(24, 24)
        self.btn_mode_info.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid transparent;
                font-size: 11px;
                padding: 0px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 240, 255, 0.20);
                border: 1px solid {COLOR_CYAN_DIM};
            }}
        """)
        self.btn_mode_info.setToolTip("View Model Architecture & Operating Profiles (Read-Only)")
        self.btn_mode_info.clicked.connect(self.model_info_requested.emit)
        mode_layout.addWidget(self.btn_mode_info)

        layout.addWidget(self.mode_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # =========================================================================
        # 3. RIGHT COLUMN: Online Pill + Cyber Divider + Live Clock
        # =========================================================================
        layout.addStretch(1)

        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Offline / Online Connectivity Indicator Pill
        self.online_pill = QLabel("● LOCAL SOVEREIGN")
        self.online_pill.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.online_pill.setStyleSheet(
            f"color: {COLOR_EMERALD}; background-color: rgba(0, 255, 170, 0.12); "
            f"border: 1px solid rgba(0, 255, 170, 0.38); border-radius: 12px; padding: 4px 12px;"
        )
        self.online_pill.setToolTip("Local Sovereign Mode: 100% local processing with zero cloud data leakage")
        right_layout.addWidget(self.online_pill)

        # Cyber Vertical Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet("color: rgba(0, 240, 255, 0.25); background-color: rgba(0, 240, 255, 0.25); width: 1px; max-height: 24px;")
        right_layout.addWidget(divider)

        # Live Cybernetic Clock & Date Display
        clock_layout = QVBoxLayout()
        clock_layout.setContentsMargins(0, 0, 0, 0)
        clock_layout.setSpacing(1)

        self.lbl_clock = QLabel("00:00:00")
        self.lbl_clock.setFont(QFont(FONT_FAMILY_MONO, 11, QFont.Weight.Bold))
        self.lbl_clock.setStyleSheet(f"color: {COLOR_CYAN}; background: transparent; letter-spacing: 0.5px;")
        self.lbl_clock.setAlignment(Qt.AlignmentFlag.AlignRight)
        clock_layout.addWidget(self.lbl_clock)

        self.lbl_date = QLabel("2026-09-01")
        self.lbl_date.setFont(QFont("Segoe UI", 8))
        self.lbl_date.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
        self.lbl_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        clock_layout.addWidget(self.lbl_date)

        right_layout.addLayout(clock_layout)
        layout.addWidget(right_container, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # 1-Second Timer for Clock updates
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

        # Connect state manager signals
        state_manager.mode_changed.connect(self.set_active_mode)
        state_manager.online_status_changed.connect(self.set_online_status)

    def _update_clock(self):
        now = time.localtime()
        self.lbl_clock.setText(time.strftime("%H:%M:%S", now))
        self.lbl_date.setText(time.strftime("%Y-%m-%d", now))

    def _on_mode_button_clicked(self, mode: OperatingMode):
        state_manager.set_operating_mode(mode)
        try:
            from jarvis.system.cpu_survival import cpu_survival_manager
            if mode.value in ["BALANCED", "SURVIVAL", "TURBO"]:
                cpu_survival_manager.set_mode(mode.value)
        except Exception:
            pass

    def set_active_mode(self, mode_name: str):
        mode_upper = mode_name.upper()
        for name, btn in self.mode_buttons.items():
            is_active = (name == mode_upper)
            btn.setChecked(is_active)

    def set_online_status(self, is_online: bool):
        if is_online:
            self.online_pill.setText("● ONLINE CONNECTED")
            self.online_pill.setStyleSheet(
                f"color: {COLOR_CYAN}; background-color: rgba(0, 240, 255, 0.12); "
                f"border: 1px solid rgba(0, 240, 255, 0.38); border-radius: 12px; padding: 4px 12px;"
            )
            self.online_pill.setToolTip("External internet connectivity active")
        else:
            self.online_pill.setText("● LOCAL SOVEREIGN")
            self.online_pill.setStyleSheet(
                f"color: {COLOR_EMERALD}; background-color: rgba(0, 255, 170, 0.12); "
                f"border: 1px solid rgba(0, 255, 170, 0.38); border-radius: 12px; padding: 4px 12px;"
            )
            self.online_pill.setToolTip("Local Sovereign Mode: 100% local processing with zero cloud data leakage")
