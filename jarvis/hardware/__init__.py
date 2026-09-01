"""
jarvis/hardware/__init__.py — J.A.R.V.I.S. Direct Silicon & NPU Acceleration Package
"""

from .npu_engine import NPUSiliconEngine, npu_engine

__all__ = [
    "NPUSiliconEngine",
    "npu_engine",
]
