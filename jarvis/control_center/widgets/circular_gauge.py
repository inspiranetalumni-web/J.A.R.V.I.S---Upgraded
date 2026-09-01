"""
jarvis/control_center/widgets/circular_gauge.py — Next-Gen Cyber Radial Gauge Meter
High-precision QPainter radial progress meter with cybernetic segmented dials,
inner dark glass depth, glowing lead nodes, animated AC indicators, and hover feedback.
"""

import math
from typing import Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF, QPointF, Property
from PySide6.QtGui import (
    QPainter, QColor, QPen, QFont, QRadialGradient, QBrush,
    QEnterEvent
)
from jarvis.control_center.theme import (
    COLOR_CYAN, COLOR_CYAN_DIM, COLOR_CYAN_GLOW, COLOR_BLUE, COLOR_EMERALD,
    COLOR_AMBER, COLOR_VERONICA_RED, COLOR_BORDER_NORMAL, COLOR_BORDER_CARD,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_BG_DARK
)

class CircularGauge(QWidget):
    """
    Performance-optimized Next-Gen radial progress meter with cyber dial markings,
    metric-specific color logic, glowing lead nodes, and interactive hover feedback.
    """
    def __init__(self, title: str = "GAUGE", unit: str = "%", subtext: str = "",
                 min_val: float = 0.0, max_val: float = 100.0,
                 metric_type: str = "custom", parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.subtext = subtext
        self.min_val = min_val
        self.max_val = max_val
        self.metric_type = metric_type.lower()
        self._value: float = 0.0
        self._is_available: bool = True
        self._is_charging: bool = False
        self._custom_color: Optional[str] = None
        self._is_hovered: bool = False
        self.setMinimumSize(100, 115)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Pre-allocated fonts
        self._font_val = QFont("Consolas", 11, QFont.Weight.Bold)
        self._font_title = QFont("Segoe UI", 8, QFont.Weight.Bold)
        self._font_sub = QFont("Segoe UI", 7)
        self._font_tick = QFont("Consolas", 6)

        # Pre-allocated pens
        self._track_pen = QPen(QColor(COLOR_BORDER_NORMAL), 5.0)
        self._track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        self._active_pen = QPen(QColor(COLOR_CYAN), 5.5)
        self._active_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        
        self._tick_pen = QPen(QColor(COLOR_BORDER_CARD), 1.0)

    def get_value(self) -> float:
        return self._value

    def set_value(self, val: Optional[float]):
        if val is None:
            if self._is_available:
                self._is_available = False
                self.update()
            return

        self._is_available = True
        clamped = max(self.min_val, min(self.max_val, float(val)))
        if abs(self._value - clamped) >= 0.2:
            self._value = clamped
            self.update()

    value = Property(float, get_value, set_value)

    def set_charging(self, is_charging: bool):
        if self._is_charging != is_charging:
            self._is_charging = is_charging
            self.update()

    def set_color_override(self, color_hex: Optional[str]):
        if self._custom_color != color_hex:
            self._custom_color = color_hex
            self.update()

    def set_subtext(self, text: str):
        if self.subtext != text:
            self.subtext = text
            self.update()

    def enterEvent(self, event: QEnterEvent):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def _compute_color(self) -> QColor:
        if self._custom_color:
            return QColor(self._custom_color)

        if not self._is_available:
            return QColor(COLOR_TEXT_MUTED)

        val = self._value

        if self.metric_type == "cpu":
            if val < 50.0:
                return QColor(COLOR_CYAN)
            elif val <= 80.0:
                return QColor(COLOR_AMBER)
            else:
                return QColor(COLOR_VERONICA_RED)

        elif self.metric_type == "ram":
            if val < 40.0:
                return QColor(COLOR_EMERALD)
            elif val < 70.0:
                return QColor(COLOR_BLUE)
            elif val <= 85.0:
                return QColor(COLOR_AMBER)
            else:
                return QColor(COLOR_VERONICA_RED)

        elif self.metric_type == "disk":
            if val < 75.0:
                return QColor(COLOR_CYAN)
            elif val <= 90.0:
                return QColor(COLOR_AMBER)
            else:
                return QColor(COLOR_VERONICA_RED)

        elif self.metric_type == "battery":
            if self._is_charging:
                return QColor(COLOR_EMERALD if val >= 95.0 else COLOR_CYAN)
            else:
                if val >= 99.5:
                    return QColor(COLOR_EMERALD)
                elif val >= 25.0:
                    return QColor(COLOR_AMBER)
                else:
                    return QColor(COLOR_VERONICA_RED)

        ratio = (self._value - self.min_val) / max(1e-5, (self.max_val - self.min_val))
        if ratio < 0.70:
            return QColor(COLOR_CYAN)
        elif ratio < 0.85:
            return QColor(COLOR_AMBER)
        else:
            return QColor(COLOR_VERONICA_RED)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        size = min(width, height - 25)
        center_x = width / 2.0
        center_y = (height - 18) / 2.0
        radius = max(5.0, (size / 2.0) - 9.0)

        rect = QRectF(center_x - radius, center_y - radius, radius * 2.0, radius * 2.0)

        # 1. Inner Sapphire Glass Lens (Zero pitch black, rich cosmic glass depth)
        lens_grad = QRadialGradient(center_x, center_y, radius * 0.9)
        lens_alpha = 50 if not self._is_hovered else 85
        lens_grad.setColorAt(0.0, QColor(0, 240, 255, int(lens_alpha * 0.25)))
        lens_grad.setColorAt(0.65, QColor(16, 36, 70, lens_alpha))
        lens_grad.setColorAt(1.0, QColor(20, 48, 92, int(lens_alpha * 0.3)))
        painter.setBrush(QBrush(lens_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)

        # 2. Outer Calibration Dial Ticks (0%, 25%, 50%, 75%, 100%)
        # Sweep is 270 degrees: from 225 deg (135 math angle) down clockwise to -45 deg
        start_deg = 225.0
        total_span = 270.0
        self._tick_pen.setColor(QColor(COLOR_CYAN if self._is_hovered else COLOR_CYAN_DIM))
        painter.setPen(self._tick_pen)

        for i in range(5):
            t_ratio = i / 4.0
            cur_deg = start_deg - t_ratio * total_span
            rad = math.radians(cur_deg)
            r_out = radius + 5.5
            r_in = radius + 2.5
            x1 = center_x + r_out * math.cos(rad)
            y1 = center_y - r_out * math.sin(rad)
            x2 = center_x + r_in * math.cos(rad)
            y2 = center_y - r_in * math.sin(rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 3. Background Track Arc (270 degrees sweep)
        start_angle = 225 * 16
        span_angle = -270 * 16

        self._track_pen.setColor(QColor(0, 240, 255, 45 if not self._is_hovered else 80))
        painter.setPen(self._track_pen)
        painter.drawArc(rect, start_angle, span_angle)

        # 4. Foreground Active Progress Arc with Glowing Lead Node
        primary_color = self._compute_color()
        if self._is_available:
            ratio = (self._value - self.min_val) / max(1e-5, (self.max_val - self.min_val))
            active_span = int(span_angle * ratio)
            self._active_pen.setColor(primary_color)
            painter.setPen(self._active_pen)
            painter.drawArc(rect, start_angle, active_span)

            # Draw Glowing Lead End Node
            if ratio > 0.02:
                lead_deg = start_deg - ratio * total_span
                lead_rad = math.radians(lead_deg)
                node_x = center_x + radius * math.cos(lead_rad)
                node_y = center_y - radius * math.sin(lead_rad)
                painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(node_x, node_y), 3.0, 3.0)

        # 5. Center Value
        painter.setPen(QColor(COLOR_TEXT_PRIMARY if self._is_available else COLOR_TEXT_MUTED))
        painter.setFont(self._font_val)
        if not self._is_available:
            val_str = "N/A"
        elif self.metric_type == "battery" and self._is_charging and self._value >= 99.5:
            val_str = "100%"
        elif self.unit == "%":
            val_str = f"{int(self._value)}{self.unit}"
        else:
            val_str = f"{self._value:.1f}{self.unit}"

        val_rect = QRectF(center_x - radius, center_y - 12, radius * 2.0, 24)
        painter.drawText(val_rect, Qt.AlignmentFlag.AlignCenter, val_str)

        # 6. Gauge Title (with hover illumination)
        painter.setPen(QColor(COLOR_CYAN if not self._is_hovered else COLOR_CYAN_GLOW))
        painter.setFont(self._font_title)
        title_rect = QRectF(0, center_y + radius - 4, width, 14)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, self.title)

        # 7. Subtext Readout (with AC charging indicator)
        sub_text = self.subtext
        if self.metric_type == "battery" and self._is_charging:
            sub_text = "⚡ AC Connected"

        if sub_text:
            painter.setPen(QColor(COLOR_EMERALD if (self.metric_type == "battery" and self._is_charging) else COLOR_TEXT_MUTED))
            painter.setFont(self._font_sub)
            sub_rect = QRectF(0, height - 14, width, 14)
            painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, sub_text)

        painter.end()

