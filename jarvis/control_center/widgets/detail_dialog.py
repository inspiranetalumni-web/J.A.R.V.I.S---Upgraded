"""
jarvis/control_center/widgets/detail_dialog.py — Compact Subsystem Metrics Detail Pop-up
Displays a crisp, complete summary of a subsystem with 3 to 5 key real metrics,
one-line explanations, zero text clipping, and a direct action to open the Developer Window.
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from jarvis.control_center.theme import (
    MASTER_STYLESHEET, COLOR_BG_DARK, COLOR_BG_SURFACE, COLOR_BG_CARD,
    COLOR_CYAN, COLOR_CYAN_DIM, COLOR_EMERALD, COLOR_AMBER,
    COLOR_VERONICA_RED, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_BORDER_CARD, FONT_FAMILY_MONO
)

class SubsystemDetailDialog(QDialog):
    """
    Compact popup dialog triggered on double-click of any Subsystem Matrix card.
    """
    view_developer_requested = Signal(str)  # Emits subsystem_key

    def __init__(self, subsystem_key: str, data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.subsystem_key = subsystem_key
        self.data = data

        self.setWindowTitle(f"J.A.R.V.I.S. Diagnostic — {data.get('name', 'Subsystem Detail')}")
        self.resize(520, 480)
        self.setMinimumSize(440, 380)
        self.setStyleSheet(MASTER_STYLESHEET)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(12)

        # 1. Header Bar: Icon + Name + Status Pill
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        lbl_icon = QLabel(self.data.get("icon", "⚡"))
        lbl_icon.setFont(QFont("Segoe UI Emoji", 14))
        header_layout.addWidget(lbl_icon)

        lbl_name = QLabel(self.data.get("name", "SUBSYSTEM").upper())
        lbl_name.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_name.setStyleSheet(f"color: {COLOR_CYAN}; letter-spacing: 1px;")
        header_layout.addWidget(lbl_name)

        header_layout.addStretch()

        status_str = self.data.get("status", "NOMINAL")
        lbl_status = QLabel(f"● {status_str}")
        lbl_status.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        status_color = COLOR_EMERALD if status_str == "NOMINAL" else (COLOR_AMBER if status_str == "WARNING" else COLOR_CYAN)
        lbl_status.setStyleSheet(
            f"color: {status_color}; background-color: rgba(10, 20, 35, 0.8); "
            f"border: 1px solid {status_color}; border-radius: 10px; padding: 3px 10px;"
        )
        header_layout.addWidget(lbl_status)

        main_layout.addLayout(header_layout)

        # 2. Executive Purpose Summary Box
        summary_box = QFrame()
        summary_box.setStyleSheet(f"background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER_CARD}; border-radius: 6px; padding: 6px;")
        s_layout = QVBoxLayout(summary_box)
        s_layout.setContentsMargins(10, 8, 10, 8)
        s_layout.setSpacing(2)

        lbl_sum_hdr = QLabel("OPERATIONAL OVERVIEW:")
        lbl_sum_hdr.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_sum_hdr.setStyleSheet(f"color: {COLOR_CYAN_DIM}; letter-spacing: 0.8px;")
        s_layout.addWidget(lbl_sum_hdr)

        lbl_summary = QLabel(self.data.get("summary", "Subsystem telemetry verified and operational."))
        lbl_summary.setFont(QFont("Segoe UI", 9))
        lbl_summary.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        lbl_summary.setWordWrap(True)
        s_layout.addWidget(lbl_summary)

        main_layout.addWidget(summary_box)

        # 3. Key Metrics List (Scrollable to guarantee zero text clipping)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"QScrollArea {{ border: 1px solid {COLOR_BORDER_CARD}; background-color: {COLOR_BG_CARD}; border-radius: 6px; }}")

        metrics_container = QWidget()
        metrics_container.setStyleSheet("background: transparent; background-color: transparent;")
        m_layout = QVBoxLayout(metrics_container)
        m_layout.setContentsMargins(8, 8, 8, 8)
        m_layout.setSpacing(8)

        lbl_m_hdr = QLabel("REAL KEY METRICS & VERIFICATION (3-5 INDICATORS):")
        lbl_m_hdr.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_m_hdr.setStyleSheet(f"color: {COLOR_CYAN}; letter-spacing: 0.8px; background: transparent;")
        m_layout.addWidget(lbl_m_hdr)

        metrics_list = self.data.get("metrics", [])
        for m in metrics_list:
            item_card = QFrame()
            item_card.setStyleSheet(f"QFrame {{ background-color: rgba(20, 31, 54, 0.65); border: 1px solid {COLOR_BORDER_CARD}; border-radius: 5px; padding: 6px; }} QLabel {{ background: transparent; background-color: transparent; }}")
            i_layout = QVBoxLayout(item_card)
            i_layout.setContentsMargins(8, 6, 8, 6)
            i_layout.setSpacing(2)

            top_row = QHBoxLayout()
            lbl_label = QLabel(m.get("label", "Metric").upper())
            lbl_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            lbl_label.setStyleSheet(f"color: {COLOR_CYAN}; background: transparent;")
            lbl_label.setWordWrap(True)
            top_row.addWidget(lbl_label)

            top_row.addStretch()

            lbl_val = QLabel(str(m.get("value", "--")))
            lbl_val.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            lbl_val.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; background: transparent;")
            lbl_val.setWordWrap(True)
            top_row.addWidget(lbl_val)
            i_layout.addLayout(top_row)

            lbl_exp = QLabel(m.get("explanation", ""))
            lbl_exp.setFont(QFont("Segoe UI", 8))
            lbl_exp.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent;")
            lbl_exp.setWordWrap(True)
            i_layout.addWidget(lbl_exp)

            m_layout.addWidget(item_card)

        m_layout.addStretch()
        scroll_area.setWidget(metrics_container)
        main_layout.addWidget(scroll_area, stretch=1)

        # 4. Action Footer
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(10)

        self.btn_open_dev = QPushButton("🔍 View Raw Details in Developer Window")
        self.btn_open_dev.setStyleSheet(
            f"background-color: rgba(0, 240, 255, 0.15); color: {COLOR_CYAN}; "
            f"border: 1px solid {COLOR_CYAN}; border-radius: 6px; padding: 8px 14px; font-weight: bold;"
        )
        self.btn_open_dev.clicked.connect(self._on_view_raw_details)
        footer_layout.addWidget(self.btn_open_dev)

        footer_layout.addStretch()

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        footer_layout.addWidget(self.btn_close)

        main_layout.addLayout(footer_layout)

    def _on_view_raw_details(self):
        self.view_developer_requested.emit(self.subsystem_key)
        self.accept()
