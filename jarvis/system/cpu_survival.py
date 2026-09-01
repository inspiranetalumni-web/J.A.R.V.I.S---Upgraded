"""
jarvis/system/cpu_survival.py — CPU Survival & Performance Mode Governor v3.0
Dynamic compute optimization for Intel Core i7-1255U CPU-only voice execution.
Maintains low idle CPU (<15%) and adjusts thread limits, token budgets, and neural pipelines.
"""

import os
import time
import psutil
import threading
from enum import Enum
from typing import Dict, Any, Optional

class PerformanceMode(Enum):
    TURBO = "TURBO"
    BALANCED = "BALANCED"
    SURVIVAL = "SURVIVAL"

class CPUSurvivalManager:
    """
    Manages CPU performance profiles, thread bounds, and adaptive throttling
    for smooth real-time voice processing on CPU-only hosts.
    """
    def __init__(self, default_mode: str = "BALANCED", auto_governor: bool = True):
        self._mode = PerformanceMode(default_mode.upper())
        self._auto_governor = auto_governor
        self._lock = threading.Lock()
        self._high_cpu_counter = 0
        self._low_cpu_counter = 0

        # Profile configurations
        self._profiles = {
            PerformanceMode.TURBO: {
                "stt_threads": 4,
                "stt_beam_size": 2,
                "vad_use_onnx": True,
                "llm_max_tokens": 1024,
                "yield_sleep_s": 0.001,
                "description": "Full performance compute allocation across all available cores."
            },
            PerformanceMode.BALANCED: {
                "stt_threads": 2,
                "stt_beam_size": 1,
                "vad_use_onnx": True,
                "llm_max_tokens": 256,
                "yield_sleep_s": 0.005,
                "description": "Optimized real-time voice profile with low idle footprint (<15%)."
            },
            PerformanceMode.SURVIVAL: {
                "stt_threads": 1,
                "stt_beam_size": 1,
                "vad_use_onnx": False,  # Pure fast RMS gating to eliminate ONNX inference cycles
                "llm_max_tokens": 128,
                "yield_sleep_s": 0.015,
                "description": "Low-power survival mode minimizing CPU overhead under high host load."
            }
        }

    @property
    def mode(self) -> str:
        """Returns the current performance mode name."""
        with self._lock:
            return self._mode.value

    def set_mode(self, mode_name: str) -> bool:
        """Sets active performance mode (TURBO, BALANCED, SURVIVAL)."""
        mode_upper = mode_name.strip().upper()
        if mode_upper not in PerformanceMode.__members__:
            return False
        with self._lock:
            self._mode = PerformanceMode[mode_upper]
            print(f"[CPU SURVIVAL] Performance mode switched to: {self._mode.value}")
        return True

    def get_profile(self) -> Dict[str, Any]:
        """Returns active profile configuration."""
        with self._lock:
            config = self._profiles[self._mode].copy()
            config["mode"] = self._mode.value
            config["auto_governor"] = self._auto_governor
            return config

    def get_stt_threads(self) -> int:
        """Returns recommended STT CPU worker thread count."""
        with self._lock:
            return self._profiles[self._mode]["stt_threads"]

    def get_llm_max_tokens(self) -> int:
        """Returns recommended LLM token budget ceiling."""
        with self._lock:
            return self._profiles[self._mode]["llm_max_tokens"]

    def is_survival_active(self) -> bool:
        """Returns True if SURVIVAL mode is currently active."""
        with self._lock:
            return self._mode == PerformanceMode.SURVIVAL

    def evaluate_adaptive_governor(self) -> Optional[str]:
        """
        Monitors host CPU utilization and dynamically shifts mode if enabled.
        Engages SURVIVAL if CPU > 85% for sustained periods; restores BALANCED when CPU < 60%.
        """
        if not self._auto_governor:
            return None

        cpu_pct = psutil.cpu_percent(interval=None)

        with self._lock:
            if cpu_pct > 85.0:
                self._high_cpu_counter += 1
                self._low_cpu_counter = 0
                if self._high_cpu_counter >= 3 and self._mode != PerformanceMode.SURVIVAL:
                    self._mode = PerformanceMode.SURVIVAL
                    print(f"[CPU SURVIVAL] High CPU load ({cpu_pct:.1f}%) detected — auto-engaging SURVIVAL mode")
                    return self._mode.value
            elif cpu_pct < 60.0:
                self._low_cpu_counter += 1
                self._high_cpu_counter = 0
                if self._low_cpu_counter >= 5 and self._mode == PerformanceMode.SURVIVAL:
                    self._mode = PerformanceMode.BALANCED
                    print(f"[CPU SURVIVAL] CPU load stabilized ({cpu_pct:.1f}%) — restoring BALANCED mode")
                    return self._mode.value

        return None

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns complete system CPU and survival telemetry."""
        cpu_pct = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        profile = self.get_profile()

        return {
            "mode": self.mode,
            "profile": profile,
            "system_cpu_percent": cpu_pct,
            "system_ram_percent": mem.percent,
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "is_survival_active": self.is_survival_active(),
            "auto_governor": self._auto_governor
        }

cpu_survival_manager = CPUSurvivalManager()
