"""
jarvis/control_center/widgets/voice_orb.py — Next-Gen Authentic MCU J.A.R.V.I.S. 3D Holographic Neural Sphere & Code Graph Engine
Elevated cinematic 3D holographic rendering featuring:
- Mode 1: 3D Holographic Voice Orb (48-band radial audio waveform + 32-node quantum particle constellation)
- Mode 2: 3D Holographic Code Graph (Real AST repository nodes, dependency filaments, cluster colors, and blast-radius tracing)
- Mode 3: 3D Hybrid Mode (Blends real-time speech amplitude pulses radiating through active code graph branches)
- Full 2D/3D Canvas Navigation: Left-Drag Orbit, Right-Drag Pan, Mouse-Centered Smooth Zoom (0.3x to 5.0x)
- Freeze on Hover (rotation smoothly pauses on hover for precise node inspection)
- Double-Click AST Node Inspection Dialog launcher
- On-Canvas Floating Glass Control Dock (Zoom In, Zoom Out, Reset Camera, Mode Toggle)
- Non-overlapping anchored Stark HUD telemetry readouts
"""

import math
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QRadialGradient, QBrush, QFont,
    QMouseEvent, QEnterEvent, QWheelEvent
)
from jarvis.control_center.state import AssistantState
from jarvis.control_center.theme import (
    COLOR_CYAN, COLOR_CYAN_GLOW, COLOR_CYAN_DIM, COLOR_BLUE,
    COLOR_EMERALD, COLOR_AMBER, COLOR_VERONICA_RED, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED
)
from jarvis.analysis.code_graph import code_graph_engine, CodeGraphNode

class OrbDisplayMode(str, Enum):
    VOICE_ORB = "VOICE_ORB"
    CODE_GRAPH = "CODE_GRAPH"
    HYBRID = "HYBRID"

class VoiceOrbWidget(QWidget):
    """
    Cinematic MCU J.A.R.V.I.S. 3D Holographic Neural Sphere and Interactive Code Graph Centerpiece.
    """
    node_selected = Signal(str)         # Emits node_id on single click
    node_double_clicked = Signal(str)   # Emits node_id on double click to open Rich Detail Dialog

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state: AssistantState = AssistantState.IDLE
        self._display_mode: OrbDisplayMode = OrbDisplayMode.VOICE_ORB
        self._time_sec: float = 0.0
        
        # 3D Euler angles
        self._yaw: float = 0.0
        self._pitch: float = 0.32
        self._roll: float = 0.0
        
        # Inner sphere counter-rotation
        self._inner_yaw: float = 0.0
        self._inner_pitch: float = -0.25
        
        # HUD rotation & pulse
        self._hud_angle: float = 0.0
        self._pulse_phase: float = 0.0
        self._amplitude: float = 0.0
        self._is_hovered: bool = False
        
        # Interactive Zoom Scale & Canvas Pan Offsets
        self._zoom_scale: float = 1.0
        self._pan_x: float = 0.0
        self._pan_y: float = 0.0
        
        # Mouse Drag & Pan Tracking
        self._is_dragging_orbit: bool = False
        self._is_panning: bool = False
        self._drag_last_pos: QPointF = QPointF(0, 0)
        self._mouse_pos: QPointF = QPointF(-100, -100)
        
        # Cursor tilt parallax target & current
        self._mouse_target_pitch: float = 0.32
        self._mouse_target_roll: float = 0.0
        
        # Click ripples & particle shockwave
        self._click_ripple: float = 0.0
        self._click_shockwave_2: float = 0.0
        
        # Code Graph interactive hover and cascade pulse
        self._hovered_node_id: Optional[str] = None
        self._selected_node_id: Optional[str] = None
        self._cascade_pulse: float = 0.0
        self._projected_nodes_cache: List[Tuple[str, float, float, float, CodeGraphNode]] = []
        
        self.setMinimumSize(320, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

        # Pre-cached typography
        self._font_center = QFont("Segoe UI", 9, QFont.Weight.Bold)
        self._font_telemetry = QFont("Consolas", 6, QFont.Weight.Bold)
        self._font_micro = QFont("Consolas", 6, QFont.Weight.Bold)
        self._font_node_tag = QFont("Segoe UI", 7, QFont.Weight.Bold)
        self._font_btn = QFont("Segoe UI", 8, QFont.Weight.Bold)

        # Generate 32 quantum particle coordinates on 4 distinct 3D orbital shells
        self._particles: List[Tuple[float, float, float, int]] = []
        for i in range(32):
            shell_id = i % 4
            ang = (i / 8.0) * math.pi * 2.0 + (shell_id * 0.4)
            r = 0.92 + 0.18 * ((i * 7) % 5) / 5.0
            
            if shell_id == 0:
                x = r * math.cos(ang)
                y = r * math.sin(ang) * 0.35
                z = r * math.sin(ang) * 0.92
            elif shell_id == 1:
                x = r * math.cos(ang) * 0.85
                y = r * math.sin(ang) * 0.90
                z = r * math.cos(ang) * 0.45
            elif shell_id == 2:
                x = r * math.sin(ang) * 0.75
                y = r * math.cos(ang) * 0.70
                z = r * math.sin(ang) * 0.75
            else:
                x = r * math.cos(ang) * 0.50
                y = r * math.sin(ang) * 0.95
                z = r * math.sin(ang) * 0.50
            self._particles.append((x, y, z, shell_id))

        # Peak indicators for 48 audio spectrum bars
        self._spectrum_peaks: List[float] = [0.0] * 48
        self._live_bands: List[float] = [0.0] * 48
        self._spectral_centroid: float = 0.5
        
        # Dynamic Persona & Biometric Themes
        self._persona_name: str = "J.A.R.V.I.S."
        self._persona_accent_color: Optional[str] = None
        self._stress_level: float = 0.0
        self._stress_color: Optional[str] = None

        # Dynamic Animation Timer: 15 FPS when Idle, 30 FPS Active, 45 FPS Hovered/Speaking
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(66)

    def set_spectrum_data(self, bands: List[float], amplitude: float, centroid: float = 0.5):
        """Ingests live 48-band FFT spectrum energy from physical audio/mic stream."""
        if bands:
            self._live_bands = list(bands)[:48]
            if len(self._live_bands) < 48:
                self._live_bands.extend([0.0] * (48 - len(self._live_bands)))
        self._amplitude = max(0.0, min(1.0, float(amplitude)))
        self._spectral_centroid = max(0.0, min(1.0, float(centroid)))
        self.update()

    def set_active_persona(self, persona_name: str, accent_color: Optional[str] = None):
        """Dynamically updates active persona name (J.A.R.V.I.S., F.R.I.D.A.Y., E.D.I.T.H.) and color theme."""
        p_clean = persona_name.upper().strip()
        if "FRIDAY" in p_clean:
            self._persona_name = "F.R.I.D.A.Y."
            self._persona_accent_color = accent_color or "#FFB300"  # Stark Gold/Amber
        elif "EDITH" in p_clean:
            self._persona_name = "E.D.I.T.H."
            self._persona_accent_color = accent_color or "#00FF88"  # Cyber Emerald
        else:
            self._persona_name = "J.A.R.V.I.S."
            self._persona_accent_color = accent_color or "#00F0FF"  # Electric Cyan
        self.update()

    def set_stress_level(self, stress_score: float, hud_color: Optional[str] = None):
        """Sets operator stress index (0.0 to 1.0) and HUD alarm color."""
        self._stress_level = max(0.0, min(1.0, float(stress_score)))
        if hud_color:
            self._stress_color = hud_color
        elif self._stress_level > 0.65:
            self._stress_color = COLOR_VERONICA_RED
        elif self._stress_level > 0.35:
            self._stress_color = COLOR_AMBER
        else:
            self._stress_color = None
        self.update()

    def set_display_mode(self, mode: OrbDisplayMode | str):
        """Switches between VOICE_ORB, CODE_GRAPH, and HYBRID modes."""
        if isinstance(mode, str):
            try:
                mode = OrbDisplayMode(mode.upper())
            except ValueError:
                mode = OrbDisplayMode.VOICE_ORB
        self._display_mode = mode
        self.update()

    def toggle_display_mode(self):
        """Cycles through display modes."""
        if self._display_mode == OrbDisplayMode.VOICE_ORB:
            self.set_display_mode(OrbDisplayMode.CODE_GRAPH)
        elif self._display_mode == OrbDisplayMode.CODE_GRAPH:
            self.set_display_mode(OrbDisplayMode.HYBRID)
        else:
            self.set_display_mode(OrbDisplayMode.VOICE_ORB)

    def reset_view(self):
        """Resets zoom scale, pan position, and orientation."""
        self._zoom_scale = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._pitch = 0.32
        self._roll = 0.0
        self.update()

    def zoom_in(self):
        self._zoom_scale = min(5.0, self._zoom_scale * 1.25)
        self.update()

    def zoom_out(self):
        self._zoom_scale = max(0.3, self._zoom_scale / 1.25)
        self.update()

    def set_state(self, state: AssistantState | str):
        if isinstance(state, str):
            try:
                state = AssistantState(state.capitalize())
            except ValueError:
                state = AssistantState.IDLE
        self._state = state
        self._update_fps_throttling()
        self.update()

    def set_amplitude(self, amp: float):
        self._amplitude = max(0.0, min(1.0, float(amp)))
        self.update()

    def _update_fps_throttling(self):
        """Dynamic FPS management: 15 FPS Idle, 30 FPS Listening/Thinking, 45 FPS Speaking/Hovered."""
        if self._is_hovered or self._state in [AssistantState.SPEAKING, AssistantState.EXECUTING] or self._display_mode != OrbDisplayMode.VOICE_ORB:
            target_interval = 22  # ~45 FPS
        elif self._state in [AssistantState.LISTENING, AssistantState.THINKING]:
            target_interval = 33  # ~30 FPS
        else:
            target_interval = 66  # ~15 FPS
        if self._timer.interval() != target_interval:
            self._timer.setInterval(target_interval)

    def wheelEvent(self, event: QWheelEvent):
        """Interactive Zoom In / Zoom Out via Mouse Scroll Wheel centered on cursor."""
        delta = event.angleDelta().y()
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        m_pos = event.position()

        old_scale = self._zoom_scale
        if delta > 0:
            self._zoom_scale = min(5.0, self._zoom_scale * 1.15)
        elif delta < 0:
            self._zoom_scale = max(0.3, self._zoom_scale / 1.15)

        # Shift pan offset so zoom occurs relative to cursor position
        factor = self._zoom_scale / old_scale
        self._pan_x = (self._pan_x + cx - m_pos.x()) * factor - (cx - m_pos.x())
        self._pan_y = (self._pan_y + cy - m_pos.y()) * factor - (cy - m_pos.y())

        self.update()
        event.accept()

    def enterEvent(self, event: QEnterEvent):
        self._is_hovered = True
        self._update_fps_throttling()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self._is_dragging_orbit = False
        self._is_panning = False
        self._mouse_target_pitch = 0.32
        self._mouse_target_roll = 0.0
        self._hovered_node_id = None
        self._mouse_pos = QPointF(-100, -100)
        self._update_fps_throttling()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        self._mouse_pos = pos
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0

        if self._is_dragging_orbit:
            # Free 3D Orbiting
            dx = pos.x() - self._drag_last_pos.x()
            dy = pos.y() - self._drag_last_pos.y()
            self._yaw += dx * 0.008
            self._pitch = max(-1.3, min(1.3, self._pitch - dy * 0.008))
            self._drag_last_pos = pos
            self.update()
            return
        elif self._is_panning:
            # 2D Canvas Panning
            dx = pos.x() - self._drag_last_pos.x()
            dy = pos.y() - self._drag_last_pos.y()
            self._pan_x += dx
            self._pan_y += dy
            self._drag_last_pos = pos
            self.update()
            return

        # Cursor parallax tilt tracking when not dragging
        dx = (pos.x() - cx) / cx
        dy = (pos.y() - cy) / cy
        self._mouse_target_pitch = 0.32 - (dy * 0.25)
        self._mouse_target_roll = dx * 0.20

        # Hit test 3D projected code nodes
        if self._display_mode in [OrbDisplayMode.CODE_GRAPH, OrbDisplayMode.HYBRID]:
            closest_node = None
            min_dist_sq = (18.0 * self._zoom_scale) ** 2
            for n_id, sx, sy, zdepth, node in self._projected_nodes_cache:
                if zdepth < -0.3:
                    continue
                d2 = (pos.x() - sx)**2 + (pos.y() - sy)**2
                if d2 < min_dist_sq:
                    min_dist_sq = d2
                    closest_node = n_id
            self._hovered_node_id = closest_node

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position()

        if event.button() == Qt.MouseButton.RightButton or (event.button() == Qt.MouseButton.LeftButton and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
            # Right Click or Shift+Left Click -> Pan Canvas
            self._is_panning = True
            self._drag_last_pos = pos
        elif event.button() == Qt.MouseButton.LeftButton:
            if self._hovered_node_id:
                # Clicked on a node -> select & emit
                self._selected_node_id = self._hovered_node_id
                self._cascade_pulse = 0.05
                self.node_selected.emit(self._hovered_node_id)
            else:
                # Clicked background -> Drag Orbit
                self._is_dragging_orbit = True
                self._drag_last_pos = pos
                self._click_ripple = 0.05
                self._click_shockwave_2 = 0.01

        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._is_dragging_orbit = False
        self._is_panning = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._hovered_node_id:
                # Open rich AST detail dialog for double-clicked node
                self.node_double_clicked.emit(self._hovered_node_id)
            else:
                # Double clicking blank canvas resets view
                self.reset_view()
        super().mouseDoubleClickEvent(event)

    def _on_tick(self):
        dt = 0.022 if self._timer.interval() == 22 else (0.033 if self._timer.interval() == 33 else 0.066)
        self._time_sec += dt

        # FREEZE ON HOVER: When hovering over any code node or dragging, pause auto rotation
        if self._is_dragging_orbit or self._is_panning or (self._is_hovered and self._hovered_node_id is not None):
            speed_mult = 0.0
        elif self._is_hovered:
            speed_mult = 0.35  # Slow gentle rotation when hovering on empty canvas
        else:
            speed_mult = 1.0  # Nominal rotation when cursor is outside

        if self._state == AssistantState.THINKING and speed_mult > 0.0:
            speed_mult *= 2.0
        elif self._state == AssistantState.SPEAKING and speed_mult > 0.0:
            speed_mult *= 1.6

        # 3D Euler angle updates
        if speed_mult > 0.0:
            self._yaw += 0.025 * speed_mult
            self._inner_yaw -= 0.038 * speed_mult
            if not self._is_dragging_orbit:
                self._pitch += (self._mouse_target_pitch + 0.08 * math.sin(self._time_sec * 0.7) - self._pitch) * 0.12
                self._roll += (self._mouse_target_roll + 0.05 * math.cos(self._time_sec * 0.5) - self._roll) * 0.12
            self._inner_pitch = -self._pitch * 0.8
            self._hud_angle = (self._hud_angle + 0.5 * speed_mult) % 360.0
        
        self._pulse_phase += 0.08

        # Click shockwaves decay
        if self._click_ripple > 0.0:
            self._click_ripple += 0.055
            if self._click_ripple > 1.0:
                self._click_ripple = 0.0

        if self._click_shockwave_2 > 0.0:
            self._click_shockwave_2 += 0.042
            if self._click_shockwave_2 > 1.0:
                self._click_shockwave_2 = 0.0

        if self._cascade_pulse > 0.0:
            self._cascade_pulse += 0.045
            if self._cascade_pulse > 1.0:
                self._cascade_pulse = 0.0

        # Dynamic amplitude simulation
        if self._state == AssistantState.LISTENING:
            self._amplitude = 0.40 + 0.35 * math.sin(self._time_sec * 8.0)
        elif self._state == AssistantState.SPEAKING:
            self._amplitude = 0.60 + 0.38 * math.sin(self._time_sec * 12.0)
        elif self._state == AssistantState.THINKING:
            self._amplitude = 0.28 + 0.22 * math.sin(self._time_sec * 6.0)
        elif not self._is_hovered:
            self._amplitude = max(0.0, self._amplitude - 0.03)

        # Update 48 audio spectrum peaks
        for i in range(48):
            bar_phase = self._time_sec * 6.0 + i * 0.55
            cur_h = 3.0 + self._amplitude * 16.0 * (0.5 + 0.5 * math.sin(bar_phase))
            if cur_h > self._spectrum_peaks[i]:
                self._spectrum_peaks[i] = cur_h
            else:
                self._spectrum_peaks[i] = max(cur_h, self._spectrum_peaks[i] - 0.5)

        self.update()

    def _project_3d(self, x: float, y: float, z: float, cx: float, cy: float, radius: float,
                    yaw: float = None, pitch: float = None, roll: float = None) -> Tuple[float, float, float]:
        """Projects 3D point with yaw/pitch/roll, zoom scale, and pan offsets onto 2D canvas coordinates."""
        cur_yaw = self._yaw if yaw is None else yaw
        cur_pitch = self._pitch if pitch is None else pitch
        cur_roll = self._roll if roll is None else roll

        effective_r = radius * self._zoom_scale

        # 1. Yaw around Y axis
        cyaw, syaw = math.cos(cur_yaw), math.sin(cur_yaw)
        x1 = x * cyaw + z * syaw
        z1 = -x * syaw + z * cyaw

        # 2. Pitch around X axis
        cpitch, spitch = math.cos(cur_pitch), math.sin(cur_pitch)
        y2 = y * cpitch - z1 * spitch
        z2 = y * spitch + z1 * cpitch

        # 3. Roll around Z axis
        croll, sroll = math.cos(cur_roll), math.sin(cur_roll)
        x3 = x1 * croll - y2 * sroll
        y3 = x1 * sroll + y2 * croll

        # Perspective projection scaling
        d = 3.8
        scale = d / (d - z2 * 0.38)
        sx = (cx + self._pan_x) + x3 * effective_r * scale
        sy = (cy + self._pan_y) + y3 * effective_r * scale
        return sx, sy, z2

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        center_x = cx + self._pan_x
        center_y = cy + self._pan_y
        
        # Enlarge base sphere size to fill 75% of viewport
        sphere_r = min(w, h) * 0.36

        # State and Persona based primary and glow colors
        if self._stress_color:
            primary_col = QColor(self._stress_color)
            glow_col = QColor(self._stress_color)
        elif self._state == AssistantState.ERROR:
            primary_col = QColor(COLOR_VERONICA_RED)
            glow_col = QColor(COLOR_VERONICA_RED)
        elif self._state == AssistantState.MUTED:
            primary_col = QColor(COLOR_AMBER)
            glow_col = QColor(COLOR_AMBER)
        elif self._persona_accent_color:
            primary_col = QColor(self._persona_accent_color)
            glow_col = QColor(self._persona_accent_color)
        elif self._state in [AssistantState.SPEAKING, AssistantState.EXECUTING]:
            primary_col = QColor(COLOR_EMERALD)
            glow_col = QColor(COLOR_CYAN)
        else:
            primary_col = QColor(COLOR_CYAN)
            glow_col = QColor(COLOR_CYAN_GLOW)

        # 1. Outer Holographic Ambient Atmosphere
        ambient_r = sphere_r * self._zoom_scale * 1.55
        ambient_grad = QRadialGradient(center_x, center_y, ambient_r)
        ambient_grad.setColorAt(0.0, QColor(glow_col.red(), glow_col.green(), glow_col.blue(), 50))
        ambient_grad.setColorAt(0.45, QColor(primary_col.red(), primary_col.green(), primary_col.blue(), 18))
        ambient_grad.setColorAt(0.85, QColor(primary_col.red(), primary_col.green(), primary_col.blue(), 4))
        ambient_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(ambient_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center_x, center_y), ambient_r, ambient_r)

        # 2. Outer Stark HUD Compass Ring & Calibration Ticks
        hud_r = sphere_r * self._zoom_scale * 1.38
        painter.setPen(QPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), 70), 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(center_x, center_y), hud_r, hud_r)

        # 48 Compass Calibration Ticks
        for i in range(48):
            ang_deg = i * (360.0 / 48.0) + self._hud_angle * 0.25
            rad = math.radians(ang_deg)
            is_major = (i % 6 == 0)
            t_len = 5.5 if is_major else 2.5
            t_r1 = hud_r - t_len
            t_r2 = hud_r
            alpha = 180 if is_major else 65
            painter.setPen(QPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), alpha), 1.2 if is_major else 0.8))
            painter.drawLine(
                QPointF(center_x + t_r1 * math.cos(rad), center_y + t_r1 * math.sin(rad)),
                QPointF(center_x + t_r2 * math.cos(rad), center_y + t_r2 * math.sin(rad))
            )

        # Counter-Rotating HUD Bracket Arcs
        bracket_r = sphere_r * self._zoom_scale * 1.24
        painter.setPen(QPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), 130), 1.5))
        bracket_rect = QRectF(center_x - bracket_r, center_y - bracket_r, bracket_r * 2.0, bracket_r * 2.0)
        base_a = int(self._hud_angle * 16.0)
        painter.drawArc(bracket_rect, base_a + 30 * 16, 45 * 16)
        painter.drawArc(bracket_rect, base_a + 120 * 16, 45 * 16)
        painter.drawArc(bracket_rect, base_a + 210 * 16, 45 * 16)
        painter.drawArc(bracket_rect, base_a + 300 * 16, 45 * 16)

        # 3. DEDICATED NON-OVERLAPPING CORNER HUD TELEMETRY
        painter.setFont(self._font_micro)
        painter.setPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), 160))
        yaw_deg = int(math.degrees(self._yaw) % 360)
        pitch_deg = int(math.degrees(self._pitch))

        # Top-Left Telemetry Anchor
        painter.drawText(QRectF(10, 10, 140, 12), Qt.AlignmentFlag.AlignLeft, f"YAW: {yaw_deg:03d}°  PITCH: {pitch_deg:+03d}°")
        painter.drawText(QRectF(10, 24, 140, 12), Qt.AlignmentFlag.AlignLeft, f"PERSONA: {self._persona_name} // {self._state.value.upper()}")

        # Top-Right Telemetry Anchor
        mode_str = f"MODE: {self._display_mode.value}"
        nodes_str = f"AST: {len(code_graph_engine.nodes)} NODES // {len(code_graph_engine.edges)} EDGES"
        painter.drawText(QRectF(w - 150, 10, 140, 12), Qt.AlignmentFlag.AlignRight, mode_str)
        painter.drawText(QRectF(w - 150, 24, 140, 12), Qt.AlignmentFlag.AlignRight, nodes_str)

        # 4. Mode-Specific Render Pipeline
        if self._display_mode in [OrbDisplayMode.VOICE_ORB, OrbDisplayMode.HYBRID]:
            self._render_voice_spectrum(painter, cx, cy, sphere_r, primary_col, glow_col)
            self._render_geodesic_wireframes(painter, cx, cy, sphere_r, primary_col, glow_col)
            self._render_quantum_particles(painter, cx, cy, sphere_r, primary_col, glow_col)

        if self._display_mode in [OrbDisplayMode.CODE_GRAPH, OrbDisplayMode.HYBRID]:
            self._render_code_graph_hologram(painter, cx, cy, sphere_r, primary_col, glow_col)

        # 5. Dual Multi-Stage Click Shockwave & Quantum Ripple
        if self._click_ripple > 0.0:
            rip_r1 = sphere_r * self._zoom_scale * (0.2 + 1.6 * self._click_ripple)
            rip_alpha1 = max(0, min(255, int(240 * (1.0 - self._click_ripple))))
            painter.setPen(QPen(QColor(glow_col.red(), glow_col.green(), glow_col.blue(), rip_alpha1), 2.0))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), rip_r1, rip_r1)

        if self._click_shockwave_2 > 0.0:
            rip_r2 = sphere_r * self._zoom_scale * (0.1 + 1.2 * self._click_shockwave_2)
            rip_alpha2 = max(0, min(255, int(180 * (1.0 - self._click_shockwave_2))))
            painter.setPen(QPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), rip_alpha2), 1.3, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), rip_r2, rip_r2)

        # 6. Central Luminous Neural Epicenter
        core_r = sphere_r * self._zoom_scale * 0.32
        core_grad = QRadialGradient(center_x, center_y, core_r)
        
        if self._display_mode == OrbDisplayMode.CODE_GRAPH:
            # Translucent sapphire cyber-core so center graph nodes are not blocked
            core_grad.setColorAt(0.0, QColor(0, 240, 255, 55))
            core_grad.setColorAt(0.50, QColor(15, 35, 71, 35))
            core_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        else:
            core_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
            core_grad.setColorAt(0.30, QColor(glow_col.red(), glow_col.green(), glow_col.blue(), 210))
            core_grad.setColorAt(0.70, QColor(primary_col.red(), primary_col.green(), primary_col.blue(), 120))
            core_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center_x, center_y), core_r, core_r)

        # 7. State & Dynamic Persona Text Badge (Only rendered in Voice Orb mode)
        if self._display_mode == OrbDisplayMode.VOICE_ORB:
            painter.setFont(self._font_center)
            painter.setPen(QColor("#ffffff" if self._is_hovered else COLOR_TEXT_PRIMARY))
            painter.drawText(QRectF(center_x - 70, center_y - 14, 140, 16), Qt.AlignmentFlag.AlignCenter, self._persona_name)
            painter.setFont(self._font_micro)
            painter.setPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), 210))
            state_sub = self._state.value.upper()
            painter.drawText(QRectF(center_x - 60, center_y + 3, 120, 12), Qt.AlignmentFlag.AlignCenter, state_sub)

        # 8. Docked Non-Overlapping Bottom Hover Tooltip Card
        if self._hovered_node_id and self._hovered_node_id in code_graph_engine.nodes:
            self._render_node_tooltip(painter, w, h, code_graph_engine.nodes[self._hovered_node_id])

        painter.end()

    def _render_voice_spectrum(self, painter: QPainter, cx: float, cy: float, sphere_r: float, primary_col: QColor, glow_col: QColor):
        center_x = cx + self._pan_x
        center_y = cy + self._pan_y
        num_bars = 48
        for i in range(num_bars):
            ang = (i / float(num_bars)) * math.pi * 2.0 + self._yaw * 0.4
            
            # Use real 48-band FFT energy if available, otherwise gentle idle waveform
            band_energy = self._live_bands[i] if i < len(self._live_bands) else 0.0
            if band_energy > 0.02 or self._amplitude > 0.04:
                cur_h = 2.0 + (band_energy * 26.0 + self._amplitude * 10.0) * self._zoom_scale
            else:
                cur_h = 2.0 + (0.5 + 0.5 * math.sin(self._time_sec * 3.5 + i * 0.45)) * 2.8 * self._zoom_scale

            r_inner = sphere_r * self._zoom_scale * 1.05
            r_outer = r_inner + cur_h
            
            bx1 = center_x + r_inner * math.cos(ang)
            by1 = center_y + r_inner * math.sin(ang)
            bx2 = center_x + r_outer * math.cos(ang)
            by2 = center_y + r_outer * math.sin(ang)
            
            b_alpha = max(0, min(255, int(90 + 165 * min(1.0, cur_h / (28.0 * self._zoom_scale)))))
            painter.setPen(QPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), b_alpha), 1.6))
            painter.drawLine(QPointF(bx1, by1), QPointF(bx2, by2))
            
            # Peak hold dot with physics decay
            peak_val = max(cur_h, self._spectrum_peaks[i] * 0.93)
            self._spectrum_peaks[i] = peak_val
            peak_r = r_inner + peak_val + 2.0
            px = center_x + peak_r * math.cos(ang)
            py = center_y + peak_r * math.sin(ang)
            p_alpha = max(0, min(255, int(130 + 125 * min(1.0, peak_val / (28.0 * self._zoom_scale)))))
            painter.setPen(QPen(QColor(glow_col.red(), glow_col.green(), glow_col.blue(), p_alpha), 2.0))
            painter.drawPoint(QPointF(px, py))

    def _render_geodesic_wireframes(self, painter: QPainter, cx: float, cy: float, sphere_r: float, primary_col: QColor, glow_col: QColor):
        latitudes = [-65, -40, -15, 15, 40, 65]
        num_samples = 32
        for lat_deg in latitudes:
            lat_rad = math.radians(lat_deg)
            r_lat = math.cos(lat_rad)
            y_lat = math.sin(lat_rad)
            pts_2d = []
            for j in range(num_samples + 1):
                lon_rad = (j / float(num_samples)) * math.pi * 2.0
                x3d = r_lat * math.cos(lon_rad)
                z3d = r_lat * math.sin(lon_rad)
                y3d = y_lat
                sx, sy, zdepth = self._project_3d(x3d, y3d, z3d, cx, cy, sphere_r)
                pts_2d.append((sx, sy, zdepth))

            for k in range(len(pts_2d) - 1):
                p1 = pts_2d[k]
                p2 = pts_2d[k+1]
                avg_z = (p1[2] + p2[2]) / 2.0
                if avg_z >= 0:
                    alpha = max(0, min(255, int(130 + 125 * min(1.0, avg_z))))
                    painter.setPen(QPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), alpha), 1.5))
                else:
                    alpha = max(0, min(255, int(35 + 45 * max(0.0, 1.0 + avg_z))))
                    painter.setPen(QPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), alpha), 0.8, Qt.PenStyle.DashLine))
                painter.drawLine(QPointF(p1[0], p1[1]), QPointF(p2[0], p2[1]))

        # Meridians
        longitudes = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5]
        for lon_deg in longitudes:
            lon_rad = math.radians(lon_deg)
            pts_lon = []
            for j in range(num_samples + 1):
                lat_rad = (j / float(num_samples)) * math.pi * 2.0
                x3d = math.cos(lat_rad) * math.cos(lon_rad)
                z3d = math.cos(lat_rad) * math.sin(lon_rad)
                y3d = math.sin(lat_rad)
                sx, sy, zdepth = self._project_3d(x3d, y3d, z3d, cx, cy, sphere_r)
                pts_lon.append((sx, sy, zdepth))

            for k in range(len(pts_lon) - 1):
                p1 = pts_lon[k]
                p2 = pts_lon[k+1]
                avg_z = (p1[2] + p2[2]) / 2.0
                if avg_z >= 0:
                    alpha = max(0, min(255, int(110 + 120 * min(1.0, avg_z))))
                    painter.setPen(QPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), alpha), 1.3))
                else:
                    alpha = max(0, min(255, int(30 + 40 * max(0.0, 1.0 + avg_z))))
                    painter.setPen(QPen(QColor(primary_col.red(), primary_col.green(), primary_col.blue(), alpha), 0.8))
                painter.drawLine(QPointF(p1[0], p1[1]), QPointF(p2[0], p2[1]))

    def _render_quantum_particles(self, painter: QPainter, cx: float, cy: float, sphere_r: float, primary_col: QColor, glow_col: QColor):
        projected = []
        for x, y, z, shell_id in self._particles:
            sx, sy, zdepth = self._project_3d(x, y, z, cx, cy, sphere_r * 1.08)
            projected.append((sx, sy, zdepth, shell_id))

        projected.sort(key=lambda p: p[2])

        synapse_dist_sq = (sphere_r * self._zoom_scale * 0.72) ** 2
        for i in range(len(projected)):
            p1 = projected[i]
            if p1[2] < -0.3:
                continue
            for j in range(i + 1, len(projected)):
                p2 = projected[j]
                if p2[2] < -0.3:
                    continue
                d2 = (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2
                if d2 < synapse_dist_sq:
                    dist_ratio = 1.0 - (d2 / synapse_dist_sq)
                    avg_z = (p1[2] + p2[2]) / 2.0
                    syn_alpha = max(0, min(255, int(140 * dist_ratio * max(0.2, (avg_z + 1.0) / 2.0))))
                    painter.setPen(QPen(QColor(glow_col.red(), glow_col.green(), glow_col.blue(), syn_alpha), 1.1))
                    painter.drawLine(QPointF(p1[0], p1[1]), QPointF(p2[0], p2[1]))

        for sx, sy, zdepth, shell_id in projected:
            norm_z = max(0.0, min(1.0, (zdepth + 1.0) / 2.0))
            p_size = (2.2 + 2.0 * norm_z) * self._zoom_scale
            p_alpha = max(0, min(255, int(100 + 155 * norm_z)))
            
            if shell_id == 1:
                node_col = QColor(COLOR_EMERALD)
            elif shell_id == 2:
                node_col = QColor(COLOR_CYAN_GLOW)
            else:
                node_col = QColor(COLOR_CYAN)
            node_col.setAlpha(p_alpha)

            painter.setBrush(QBrush(node_col))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(sx, sy), p_size, p_size)

    def _render_code_graph_hologram(self, painter: QPainter, cx: float, cy: float, sphere_r: float, primary_col: QColor, glow_col: QColor):
        """Renders the AST-extracted code graph in true 3D holographic projection."""
        self._projected_nodes_cache.clear()
        
        # 1. Project all nodes with current zoom scale and pan
        nodes_pos: Dict[str, Tuple[float, float, float, CodeGraphNode]] = {}
        for n_id, node in code_graph_engine.nodes.items():
            sx, sy, zdepth = self._project_3d(node.x, node.y, node.z, cx, cy, sphere_r * 1.15)
            nodes_pos[n_id] = (sx, sy, zdepth, node)
            self._projected_nodes_cache.append((n_id, sx, sy, zdepth, node))

        # 2. Render Directed Edges
        active_pulse_target = self._hovered_node_id or self._selected_node_id
        for edge in code_graph_engine.edges:
            if edge.source in nodes_pos and edge.target in nodes_pos:
                s_pos = nodes_pos[edge.source]
                t_pos = nodes_pos[edge.target]
                
                is_active_edge = (edge.source == active_pulse_target or edge.target == active_pulse_target)
                avg_z = (s_pos[2] + t_pos[2]) / 2.0
                
                if is_active_edge:
                    edge_alpha = max(0, min(255, int(210 + 45 * math.sin(self._time_sec * 10.0))))
                    edge_col = QColor(COLOR_EMERALD if edge.source == active_pulse_target else COLOR_CYAN_GLOW)
                    edge_col.setAlpha(edge_alpha)
                    painter.setPen(QPen(edge_col, 2.0))
                elif avg_z >= 0:
                    edge_alpha = max(0, min(255, int(45 + 55 * avg_z)))
                    edge_col = QColor(COLOR_CYAN_DIM)
                    edge_col.setAlpha(edge_alpha)
                    painter.setPen(QPen(edge_col, 0.9))
                else:
                    edge_alpha = max(0, min(255, int(15 + 25 * (avg_z + 1.0))))
                    edge_col = QColor(primary_col.red(), primary_col.green(), primary_col.blue(), edge_alpha)
                    painter.setPen(QPen(edge_col, 0.6, Qt.PenStyle.DotLine))
                
                painter.drawLine(QPointF(s_pos[0], s_pos[1]), QPointF(t_pos[0], t_pos[1]))

        # 3. Sort nodes back-to-front
        sorted_nodes = sorted(nodes_pos.values(), key=lambda n: n[2])

        # 4. Render Nodes with Cluster Colors
        for sx, sy, zdepth, node in sorted_nodes:
            norm_z = max(0.0, min(1.0, (zdepth + 1.0) / 2.0))
            is_hovered = (node.node_id == self._hovered_node_id)
            is_selected = (node.node_id == self._selected_node_id)
            
            cluster_hex = code_graph_engine.CLUSTER_COLORS.get(node.cluster, COLOR_CYAN)
            node_col = QColor(cluster_hex)
            
            if is_hovered or is_selected:
                r_size = (6.0 + 2.0 * math.sin(self._time_sec * 8.0)) * self._zoom_scale
                node_alpha = 255
                painter.setPen(QPen(QColor("#ffffff"), 2.0))
            else:
                r_size = (2.4 + 2.4 * norm_z) * self._zoom_scale
                node_alpha = max(0, min(255, int(80 + 175 * norm_z)))
                painter.setPen(Qt.PenStyle.NoPen)

            node_col.setAlpha(node_alpha)
            painter.setBrush(QBrush(node_col))
            painter.drawEllipse(QPointF(sx, sy), r_size, r_size)

            # Node Label for front-facing / hovered nodes
            if is_hovered or is_selected or (zdepth > 0.35 and self._zoom_scale > 0.75):
                painter.setFont(self._font_node_tag)
                painter.setPen(QColor("#ffffff" if is_hovered else COLOR_TEXT_PRIMARY))
                painter.drawText(QRectF(sx - 45, sy - 15, 90, 12), Qt.AlignmentFlag.AlignCenter, node.label)

    def _render_node_tooltip(self, painter: QPainter, w: int, h: int, node: CodeGraphNode):
        """Displays non-overlapping docked bottom HUD card for the currently inspected AST node."""
        blast = code_graph_engine.get_blast_radius(node.node_id)
        cluster_hex = code_graph_engine.CLUSTER_COLORS.get(node.cluster, COLOR_CYAN)
        
        card_w = min(320, w - 24)
        card_h = 46
        card_x = (w - card_w) / 2.0
        card_y = h - card_h - 8
        
        painter.setBrush(QBrush(QColor(11, 25, 52, 240)))
        painter.setPen(QPen(QColor(cluster_hex), 1.3))
        painter.drawRoundedRect(QRectF(card_x, card_y, card_w, card_h), 6, 6)
        
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(QRectF(card_x + 8, card_y + 4, card_w - 16, 13), Qt.AlignmentFlag.AlignLeft, f"📦 {node.label}.py  [{node.cluster.upper()}]")
        
        painter.setFont(QFont("Consolas", 7))
        painter.setPen(QColor(COLOR_CYAN))
        painter.drawText(QRectF(card_x + 8, card_y + 18, card_w - 16, 11), Qt.AlignmentFlag.AlignLeft, f"{node.line_count} lines  |  {len(node.classes)} classes  |  {len(node.functions)} fn")
        
        painter.setPen(QColor(COLOR_EMERALD))
        painter.drawText(QRectF(card_x + 8, card_y + 30, card_w - 16, 11), Qt.AlignmentFlag.AlignLeft, f"Impact: {blast['total_impact_count']} links // Double-Click for Full AST")



