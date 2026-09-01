"""
jarvis/control_center/widgets/model_info_dialog.py — Model Architecture & Operating Profiles Dialog
Provides a read-only, non-configurable explanation of local models used in
Balanced, Survival, Turbo, and Auto modes, along with the hardware engineering rationale.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from jarvis.control_center.theme import (
    MASTER_STYLESHEET, COLOR_BG_DARK, COLOR_BG_SURFACE, COLOR_BG_CARD,
    COLOR_CYAN, COLOR_CYAN_DIM, COLOR_EMERALD, COLOR_AMBER,
    COLOR_BLUE, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED, COLOR_BORDER_CARD, FONT_FAMILY_MONO
)

class ModelInformationDialog(QDialog):
    """
    Read-only informational dialog detailing model allocation, token budgets,
    and engineering rationale across all J.A.R.V.I.S. operating modes.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("J.A.R.V.I.S. Cognitive Architecture & Operating Profiles")
        self.resize(560, 560)
        self.setMinimumSize(460, 420)
        self.setStyleSheet(MASTER_STYLESHEET)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(10)

        # 1. Header Bar: Icon + Title + Read-Only Badge
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        lbl_icon = QLabel("🧠")
        lbl_icon.setFont(QFont("Segoe UI Emoji", 14))
        header_layout.addWidget(lbl_icon)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(1)
        lbl_name = QLabel("LOCAL COGNITIVE TIERS & PROFILES")
        lbl_name.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_name.setStyleSheet(f"color: {COLOR_CYAN}; letter-spacing: 0.8px;")
        title_layout.addWidget(lbl_name)

        lbl_sub = QLabel("100% Local Sovereign Inference Engine // Zero Cloud Keys")
        lbl_sub.setFont(QFont("Segoe UI", 8))
        lbl_sub.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        title_layout.addWidget(lbl_sub)
        header_layout.addLayout(title_layout)

        header_layout.addStretch()

        lbl_readonly = QLabel("READ-ONLY SPEC")
        lbl_readonly.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_readonly.setStyleSheet(
            f"color: {COLOR_EMERALD}; background-color: rgba(0, 255, 170, 0.1); "
            f"border: 1px solid rgba(0, 255, 170, 0.3); border-radius: 8px; padding: 3px 8px;"
        )
        header_layout.addWidget(lbl_readonly)

        main_layout.addLayout(header_layout)

        # 2. Scrollable Mode Breakdown Container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"QScrollArea {{ border: 1px solid {COLOR_BORDER_CARD}; background: {COLOR_BG_DARK}; border-radius: 6px; }}")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        modes_info = [
            {
                "mode": "BALANCED MODE",
                "tag": "DEFAULT // DAILY DRIVER",
                "color": COLOR_CYAN,
                "model": "Qwen 2.5 3B / 7B INT4 (Local OpenVINO / CPU)",
                "budget": "256 Tokens / Turn | 2 P-Cores Pinned (Mask 0x00F)",
                "details": "Optimized for sub-250ms Time-to-First-Token (TTFT) and fluid conversational voice output. Pins execution to Performance Cores while leaving Efficiency Cores free for host OS tasks."
            },
            {
                "mode": "SURVIVAL MODE",
                "tag": "HIGH LOAD // POWER CONSERVATION",
                "color": COLOR_AMBER,
                "model": "Ultra-Quantized Local LLM + Fast Intent Router Fallback",
                "budget": "64–128 Tokens / Turn | Single-Core Throttled",
                "details": "Engaged automatically or manually when sustained host CPU load exceeds 85% or battery is low. Relaxes VAD thresholds, activates 3-ring memory compaction, and throttles compute to prevent thermal throttling on Intel Core i7-1255U."
            },
            {
                "mode": "TURBO MODE",
                "tag": "MAXIMUM COMPUTE // AC POWERED",
                "color": COLOR_BLUE,
                "model": "Qwen 2.5 7B / DeepSeek R1 Local / Full Precision Weights",
                "budget": "512 Tokens / Turn | Multi-Threaded P-Core Max",
                "details": "Reserved for heavy multi-turn code generation, dynamic task workflows (PRDs, architecture diagrams, AST audits), and complex problem decomposition when connected to AC power."
            },
            {
                "mode": "AUTO MODE",
                "tag": "DYNAMIC AUTONOMOUS GOVERNOR",
                "color": COLOR_EMERALD,
                "model": "Autonomous Dynamic Mode Selector",
                "budget": "Context-Driven Adaptive Budgeting",
                "details": "Continuous background governor monitoring live CPU temperatures, queue pressure, and power telemetry. Seamlessly shifts between Balanced, Survival, and Turbo without requiring manual operator intervention."
            }
        ]

        for item in modes_info:
            card = QFrame()
            card.setStyleSheet(f"background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER_CARD}; border-radius: 6px; padding: 6px;")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(10, 8, 10, 8)
            c_layout.setSpacing(4)

            # Card Header
            c_header = QHBoxLayout()
            lbl_title = QLabel(item["mode"])
            lbl_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            lbl_title.setStyleSheet(f"color: {item['color']}; letter-spacing: 0.5px;")
            c_header.addWidget(lbl_title)

            c_header.addStretch()

            lbl_tag = QLabel(item["tag"])
            lbl_tag.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
            lbl_tag.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
            c_header.addWidget(lbl_tag)
            c_layout.addLayout(c_header)

            # Model & Specs
            lbl_model = QLabel(f"• Target Model: {item['model']}")
            lbl_model.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
            lbl_model.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
            lbl_model.setWordWrap(True)
            c_layout.addWidget(lbl_model)

            lbl_budget = QLabel(f"• Allocation: {item['budget']}")
            lbl_budget.setFont(QFont("Consolas", 8))
            lbl_budget.setStyleSheet(f"color: {COLOR_CYAN_DIM};")
            lbl_budget.setWordWrap(True)
            c_layout.addWidget(lbl_budget)

            # Description
            lbl_desc = QLabel(item["details"])
            lbl_desc.setFont(QFont("Segoe UI", 8))
            lbl_desc.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
            lbl_desc.setWordWrap(True)
            c_layout.addWidget(lbl_desc)

            content_layout.addWidget(card)

        # Hardware Architecture Rationale Box
        rationale_box = QFrame()
        rationale_box.setStyleSheet(f"background-color: {COLOR_BG_SURFACE}; border: 1px solid {COLOR_BORDER_CARD}; border-radius: 6px; padding: 6px;")
        r_layout = QVBoxLayout(rationale_box)
        r_layout.setContentsMargins(10, 8, 10, 8)
        r_layout.setSpacing(3)

        lbl_r_title = QLabel("HARDWARE CONSTRAINTS & STARK OS DIRECTIVES:")
        lbl_r_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lbl_r_title.setStyleSheet(f"color: {COLOR_CYAN}; letter-spacing: 0.8px;")
        r_layout.addWidget(lbl_r_title)

        lbl_r_text = QLabel(
            "1. Hardware Target: Intel Core i7-1255U (2 P-Cores, 8 E-Cores / 12 Threads) with Iris Xe Graphics.\n"
            "2. P-Core Affinity: Process pinned via Affinity Mask 0x00F to eliminate Windows thread-hopping latency.\n"
            "3. Memory Guardrail: Strict 512MB RAM allocation ceiling prevents inference spikes from starving host OS.\n"
            "4. Sovereign Philosophy: 100% local weights; no external APIs, cloud subscriptions, or telemetry egress."
        )
        lbl_r_text.setFont(QFont("Segoe UI", 8))
        lbl_r_text.setStyleSheet(f"color: {COLOR_TEXT_MUTED};")
        lbl_r_text.setWordWrap(True)
        r_layout.addWidget(lbl_r_text)

        content_layout.addWidget(rationale_box)
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area, stretch=1)

        # 3. Action Footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        footer_layout.addWidget(self.btn_close)

        main_layout.addLayout(footer_layout)
