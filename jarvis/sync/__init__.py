"""
jarvis/sync/__init__.py — Cross-Device Satellite Sync & Handoff Package
"""

from .satellite_sync import (
    SatelliteState,
    CrossDeviceSyncEngine,
    satellite_sync_engine,
)

__all__ = [
    "SatelliteState",
    "CrossDeviceSyncEngine",
    "satellite_sync_engine",
]
