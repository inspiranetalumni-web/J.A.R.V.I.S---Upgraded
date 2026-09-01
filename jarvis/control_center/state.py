"""
jarvis/control_center/state.py — Central Reactive State Store for Control Center
Manages assistant perception states, operating performance modes, transcript history,
and permission escrow requests with PySide6 Qt Signals.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal

class AssistantState(str, Enum):
    IDLE = "Idle"
    LISTENING = "Listening"
    THINKING = "Thinking"
    SPEAKING = "Speaking"
    EXECUTING = "Executing"
    MUTED = "Muted"
    ERROR = "Error"

class OperatingMode(str, Enum):
    BALANCED = "BALANCED"
    SURVIVAL = "SURVIVAL"
    TURBO = "TURBO"
    AUTO = "AUTO"

class ControlCenterStateManager(QObject):
    """
    Thread-safe reactive state manager with Qt Signals for responsive UI updates.
    """
    state_changed = Signal(str)
    mode_changed = Signal(str)
    online_status_changed = Signal(bool)
    active_task_changed = Signal(str)
    welcome_message_changed = Signal(str)
    persona_changed = Signal(str, str)  # persona_name, accent_color
    spectrum_updated = Signal(list, float, float)  # bands, amplitude, centroid
    stress_updated = Signal(float, str)  # stress_score, hud_color
    transcript_added = Signal(str, str)  # speaker ("user" | "jarvis"), text
    action_escrow_requested = Signal(str, str)  # action_id, description
    action_escrow_resolved = Signal(str, bool)  # action_id, approved
    safety_alert_emitted = Signal(str, str)  # level ("INFO", "WARN", "ALERT", "VERONICA"), message
    last_command_updated = Signal(dict)  # command info dict

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._assistant_state: AssistantState = AssistantState.IDLE
        self._operating_mode: OperatingMode = OperatingMode.BALANCED
        self._active_persona: str = "J.A.R.V.I.S."
        self._persona_color: str = "#00F0FF"
        self._stress_level: float = 0.0
        self._stress_color: str = "#00F0FF"
        self._is_online: bool = False
        self._active_task: str = "Awaiting voice or keyboard instruction..."
        self._welcome_message: str = "Good day, Sir. All local sovereign systems operational."
        self._transcript_history: List[Dict[str, str]] = [
            {"speaker": "jarvis", "text": "J.A.R.V.I.S. Control Center v3.0 online. P-Cores pinned and ready."}
        ]
        self._current_escrow: Optional[Dict[str, str]] = None
        self._last_command: Dict[str, Any] = {
            "command": "system_boot",
            "result": "OK (0 ms)",
            "status": "success",
            "timestamp": "boot"
        }

    # Properties
    @property
    def assistant_state(self) -> AssistantState:
        return self._assistant_state

    @property
    def operating_mode(self) -> OperatingMode:
        return self._operating_mode

    @property
    def is_online(self) -> bool:
        return self._is_online

    @property
    def active_task(self) -> str:
        return self._active_task

    @property
    def welcome_message(self) -> str:
        return self._welcome_message

    @property
    def transcript_history(self) -> List[Dict[str, str]]:
        return list(self._transcript_history)

    @property
    def current_escrow(self) -> Optional[Dict[str, str]]:
        return self._current_escrow

    @property
    def active_persona(self) -> str:
        return self._active_persona

    @property
    def persona_color(self) -> str:
        return self._persona_color

    @property
    def stress_level(self) -> float:
        return self._stress_level

    @property
    def stress_color(self) -> str:
        return self._stress_color

    # State Mutators
    def set_active_persona(self, persona_name: str, accent_color: Optional[str] = None):
        """Sets active assistant persona (J.A.R.V.I.S., F.R.I.D.A.Y., E.D.I.T.H.) and emits change."""
        p_clean = persona_name.upper().strip()
        if "FRIDAY" in p_clean:
            self._active_persona = "F.R.I.D.A.Y."
            self._persona_color = accent_color or "#FFB300"
        elif "EDITH" in p_clean:
            self._active_persona = "E.D.I.T.H."
            self._persona_color = accent_color or "#00FF88"
        else:
            self._active_persona = "J.A.R.V.I.S."
            self._persona_color = accent_color or "#00F0FF"
        self.persona_changed.emit(self._active_persona, self._persona_color)

    def set_spectrum(self, bands: List[float], amplitude: float, centroid: float = 0.5):
        """Emits real-time 48-band FFT spectrum update."""
        self.spectrum_updated.emit(bands, amplitude, centroid)

    def set_stress(self, stress_score: float, hud_color: Optional[str] = None):
        """Updates operator stress level and HUD tint."""
        self._stress_level = max(0.0, min(1.0, float(stress_score)))
        self._stress_color = hud_color or ("#FF2A2A" if self._stress_level > 0.65 else ("#FFB300" if self._stress_level > 0.35 else "#00F0FF"))
        self.stress_updated.emit(self._stress_level, self._stress_color)

    def set_assistant_state(self, state: AssistantState | str):
        if isinstance(state, str):
            try:
                state = AssistantState(state.capitalize())
            except ValueError:
                state = AssistantState.IDLE
        if self._assistant_state != state:
            self._assistant_state = state
            self.state_changed.emit(self._assistant_state.value)

    def set_operating_mode(self, mode: OperatingMode | str):
        if isinstance(mode, str):
            try:
                mode = OperatingMode(mode.upper())
            except ValueError:
                mode = OperatingMode.BALANCED
        if self._operating_mode != mode:
            self._operating_mode = mode
            self.mode_changed.emit(self._operating_mode.value)

    def set_online_status(self, is_online: bool):
        if self._is_online != is_online:
            self._is_online = is_online
            self.online_status_changed.emit(self._is_online)

    def set_active_task(self, task_description: str):
        self._active_task = task_description
        self.active_task_changed.emit(self._active_task)

    def set_welcome_message(self, message: str):
        self._welcome_message = message
        self.welcome_message_changed.emit(self._welcome_message)

    def add_transcript_entry(self, speaker: str, text: str):
        entry = {"speaker": speaker.lower(), "text": text.strip()}
        self._transcript_history.append(entry)
        if len(self._transcript_history) > 50:
            self._transcript_history.pop(0)
        self.transcript_added.emit(entry["speaker"], entry["text"])

    def request_action_escrow(self, action_id: str, description: str):
        self._current_escrow = {"id": action_id, "description": description}
        self.action_escrow_requested.emit(action_id, description)

    def resolve_action_escrow(self, action_id: str, approved: bool):
        if self._current_escrow and self._current_escrow.get("id") == action_id:
            self._current_escrow = None
        self.action_escrow_resolved.emit(action_id, approved)

    def emit_safety_alert(self, level: str, message: str):
        self.safety_alert_emitted.emit(level.upper(), message)

    def set_last_command(self, cmd_info: Dict[str, Any]):
        self._last_command = cmd_info
        self.last_command_updated.emit(self._last_command)

# Global shared instance
state_manager = ControlCenterStateManager()
