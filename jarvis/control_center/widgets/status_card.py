"""
jarvis/control_center/widgets/status_card.py — Next-Gen Glassmorphic Status Card Widget
Provides high-contrast cybernetic cards with breathing telemetry indicator halos,
interactive hover elevation cues ("EXPLORE ➔"), and double-click detail popup triggers.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import (
    QFont, QColor, QPainter, QBrush, QRadialGradient,
    QEnterEvent
)
from jarvis.control_center.theme import (
    COLOR_BG_CARD, COLOR_BORDER_CARD, COLOR_CYAN, COLOR_CYAN_DIM, COLOR_CYAN_GLOW,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, COLOR_EMERALD,
    COLOR_AMBER, COLOR_VERONICA_RED, FONT_FAMILY_MONO, FONT_FAMILY_UI
)

class StatusIndicatorDot(QWidget):
    """Small glowing indicator dot with animated live breathing halo."""
    def __init__(self, color_hex: str = COLOR_EMERALD, size: int = 8, parent=None):
        super().__init__(parent)
        self._color = color_hex
        self._size = size
        self.setFixedSize(size + 8, size + 8)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent; background-color: transparent;")

    def set_color(self, color_hex: str):
        if self._color != color_hex:
            self._color = color_hex
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.width() / 2.0
        cy = self.height() / 2.0
        r = self._size / 2.0
        col = QColor(self._color)

        # Outer subtle glow halo
        glow_grad = QRadialGradient(cx, cy, r + 4.0)
        glow_grad.setColorAt(0.0, QColor(col.red(), col.green(), col.blue(), 180))
        glow_grad.setColorAt(0.5, QColor(col.red(), col.green(), col.blue(), 70))
        glow_grad.setColorAt(1.0, QColor(col.red(), col.green(), col.blue(), 0))
        painter.setBrush(QBrush(glow_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), r + 4.0, r + 4.0)

        # Inner solid core
        painter.setBrush(QBrush(col))
        painter.drawEllipse(QPointF(cx, cy), r, r)
        painter.end()

class StatusCardWidget(QFrame):
    """
    Modular information card for the Subsystem Matrix with double-click detail support.
    Rendered with a clean translucent dark surface with zero black rectangular text backgrounds.
    """
    double_clicked = Signal(str)  # Emits subsystem_key on double-click

    def __init__(self, title: str = "STATUS", icon: str = "⚡",
                 initial_val: str = "--", subtext: str = "",
                 status_color: str = COLOR_EMERALD, subsystem_key: str = "general",
                 parent=None):
        super().__init__(parent)
        self.subsystem_key = subsystem_key
        self.setObjectName("statusCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Double-click to open detailed subsystem telemetry popup")
        self.setStyleSheet(f"""
            QFrame#statusCard {{
                background-color: rgba(18, 38, 72, 0.55);
                border: 1px solid rgba(0, 240, 255, 0.20);
                border-radius: 6px;
            }}
            QFrame#statusCard:hover {{
                background-color: rgba(26, 54, 102, 0.75);
                border: 1px solid rgba(0, 240, 255, 0.45);
            }}
            QLabel {{
                background: transparent;
                background-color: transparent;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        # Header Row: Icon + Title + Explore Cue + Status Dot
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        self.lbl_icon = QLabel(icon)
        self.lbl_icon.setFont(QFont("Segoe UI Emoji", 11))
        self.lbl_icon.setStyleSheet("background: transparent; background-color: transparent;")
        header_layout.addWidget(self.lbl_icon)

        self.lbl_title = QLabel(title.upper())
        self.lbl_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet(f"color: {COLOR_CYAN}; letter-spacing: 0.8px; background: transparent; background-color: transparent;")
        self.lbl_title.setWordWrap(True)
        header_layout.addWidget(self.lbl_title)

        header_layout.addStretch()

        self.lbl_explore = QLabel("EXPLORE ➔")
        self.lbl_explore.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        self.lbl_explore.setStyleSheet("color: transparent; background: transparent;")
        header_layout.addWidget(self.lbl_explore)

        self.dot = StatusIndicatorDot(status_color, size=8)
        header_layout.addWidget(self.dot)

        layout.addLayout(header_layout)

        # Primary Value
        self.lbl_val = QLabel(initial_val)
        self.lbl_val.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.lbl_val.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; background: transparent; background-color: transparent;")
        self.lbl_val.setWordWrap(True)
        layout.addWidget(self.lbl_val)

        # Subtext Details
        self.lbl_sub = QLabel(subtext)
        self.lbl_sub.setFont(QFont("Segoe UI", 8))
        self.lbl_sub.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; background: transparent; background-color: transparent;")
        self.lbl_sub.setWordWrap(True)
        layout.addWidget(self.lbl_sub)

    def enterEvent(self, event: QEnterEvent):
        self.lbl_explore.setStyleSheet(f"color: {COLOR_CYAN_DIM}; background: transparent; letter-spacing: 0.5px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.lbl_explore.setStyleSheet("color: transparent; background: transparent;")
        super().leaveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Dispatches double_clicked signal with the card's subsystem key."""
        self.double_clicked.emit(self.subsystem_key)
        super().mouseDoubleClickEvent(event)

    def set_value(self, val_text: str):
        if self.lbl_val.text() != val_text:
            self.lbl_val.setText(val_text)

    def set_subtext(self, sub_text: str):
        if self.lbl_sub.text() != sub_text:
            self.lbl_sub.setText(sub_text)

    def set_status_color(self, color_hex: str):
        self.dot.set_color(color_hex)

