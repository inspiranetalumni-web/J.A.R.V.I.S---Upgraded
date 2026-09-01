"""
jarvis/sensors/biometric_harvester.py — Suit Vital Monitor & Biometric Stress Harvester
Ingests BLE vitals, optical fatigue signals, and voice stress to adapt tone and token budgets.
"""

import time
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

logger = logging.getLogger("jarvis.sensors.biometrics")


@dataclass
class OperatorVitalState:
    heart_rate_bpm: float = 72.0
    hrv_ms: float = 55.0               # Heart Rate Variability (ms)
    blink_rate_per_min: float = 16.0
    eye_fatigue_level: float = 0.1     # 0.0 (fresh) to 1.0 (fatigued)
    voice_stress_score: float = 0.0    # 0.0 (calm) to 1.0 (stressed)
    last_update: float = 0.0

    def __post_init__(self):
        if self.last_update == 0.0:
            self.last_update = time.time()

    def compute_stress_index(self) -> float:
        """
        Calculates composite operator stress index (0.0 = calm, 1.0 = extreme stress/urgency).
        Formula: Stress = 0.4 * HR_factor + 0.3 * (1 - HRV_factor) + 0.3 * Voice_Stress
        """
        hr_factor = min(1.0, max(0.0, (self.heart_rate_bpm - 60.0) / 60.0))
        hrv_factor = min(1.0, max(0.0, self.hrv_ms / 100.0))
        stress = (0.4 * hr_factor) + (0.3 * (1.0 - hrv_factor)) + (0.3 * self.voice_stress_score)
        return round(min(1.0, max(0.0, stress)), 2)


class BiometricHarvester:
    """
    Background collector querying BLE vitals and optical fatigue signals.
    Dynamically falls back to nominal vitals if physical sensors are disconnected.
    """
    def __init__(self):
        self.state = OperatorVitalState()
        self.ble_connected = False

    def update_vitals(
        self,
        heart_rate_bpm: Optional[float] = None,
        hrv_ms: Optional[float] = None,
        eye_fatigue_level: Optional[float] = None,
        voice_stress_score: Optional[float] = None
    ) -> OperatorVitalState:
        """Updates internal operator vitals snapshot."""
        if heart_rate_bpm is not None:
            self.state.heart_rate_bpm = float(heart_rate_bpm)
        if hrv_ms is not None:
            self.state.hrv_ms = float(hrv_ms)
        if eye_fatigue_level is not None:
            self.state.eye_fatigue_level = float(eye_fatigue_level)
        if voice_stress_score is not None:
            self.state.voice_stress_score = float(voice_stress_score)

        self.state.last_update = time.time()
        return self.state

    def get_speech_adaptation_params(self) -> Dict[str, Any]:
        """
        Returns dynamic parameters for LLM prompt caps & TTS synthesis based on operator stress.
        """
        stress = self.state.compute_stress_index()

        if stress >= 0.70:
            return {
                "stress_index": stress,
                "stress_category": "HIGH_URGENCY",
                "mode": "TACTICAL_URGENT",
                "max_llm_tokens": 100,
                "tts_speed": 1.15,
                "hud_color": "RED",
                "directive": "Sir is under high cognitive stress or emergency. Deliver 1 ultra-direct sentence immediately."
            }
        elif stress >= 0.35:
            return {
                "stress_index": stress,
                "stress_category": "MODERATE_STRESS",
                "mode": "CONCISE_ALERT",
                "max_llm_tokens": 250,
                "tts_speed": 1.05,
                "hud_color": "AMBER",
                "directive": "Elevated operator load detected. Keep explanations brief and concise."
            }
        else:
            return {
                "stress_index": stress,
                "stress_category": "NOMINAL",
                "mode": "NOMINAL",
                "max_llm_tokens": 512,
                "tts_speed": 1.0,
                "hud_color": "BLUE",
                "directive": "Operator vitals calm and nominal. Standard conversational depth authorized."
            }

    def get_telemetry_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable telemetry dictionary."""
        return {
            "vitals": asdict(self.state),
            "adaptation": self.get_speech_adaptation_params(),
            "sensor_active": self.ble_connected,
        }


# Singleton instance
biometric_harvester = BiometricHarvester()
