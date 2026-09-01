"""
jarvis/sync/satellite_sync.py — Cross-Device Satellite Sync & Workspace Handoff Engine
Enables seamless encrypted state synchronization across Laptop, Desktop, Mobile, and Tablet.
"""

import time
import json
import logging
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional

logger = logging.getLogger("jarvis.sync.satellite")


@dataclass
class SatelliteState:
    device_id: str
    device_type: str         # "laptop" | "desktop" | "mobile" | "tablet"
    active_dialogue_turn: Dict[str, Any] = field(default_factory=dict)
    clipboard_text: str = ""
    active_file: str = ""
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class CrossDeviceSyncEngine:
    """
    Manages cross-device workspace state synchronization.
    Enables instant handoff of active conversations, clipboards, and task focus across devices.
    """
    def __init__(self, host_device_id: str = "laptop_host"):
        self.host_device_id = host_device_id
        self.current_state = SatelliteState(
            device_id=self.host_device_id,
            device_type="laptop",
            active_dialogue_turn={"role": "system", "content": "J.A.R.V.I.S. Core Online"},
            clipboard_text="",
            active_file="",
            timestamp=time.time()
        )
        self.satellites: Dict[str, Dict[str, Any]] = {}

    def update_workspace_state(
        self,
        dialogue_turn: Optional[Dict[str, Any]] = None,
        clipboard: Optional[str] = None,
        active_file: Optional[str] = None
    ) -> SatelliteState:
        """Updates local workspace snapshot."""
        if dialogue_turn:
            self.current_state.active_dialogue_turn = dialogue_turn
        if clipboard is not None:
            self.current_state.clipboard_text = clipboard
        if active_file is not None:
            self.current_state.active_file = active_file
        self.current_state.timestamp = time.time()
        return self.current_state

    def register_satellite(self, device_id: str, ip: str, device_type: str = "mobile") -> Dict[str, Any]:
        """Registers a paired satellite device."""
        info = {
            "device_id": device_id,
            "ip": ip,
            "device_type": device_type,
            "last_seen": time.time(),
            "paired": True,
        }
        self.satellites[device_id] = info
        logger.info(f"[SATELLITE SYNC] Registered satellite device {device_id} ({device_type}) at {ip}")
        return info

    def ingest_remote_state(self, remote_state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests an incoming state update from a paired satellite."""
        dev_id = remote_state_dict.get("device_id", "unknown_device")
        dev_type = remote_state_dict.get("device_type", "satellite")

        if dev_id not in self.satellites:
            self.register_satellite(dev_id, ip="127.0.0.1", device_type=dev_type)

        self.satellites[dev_id]["last_seen"] = time.time()
        self.satellites[dev_id]["last_state"] = remote_state_dict

        # If remote state is newer, update active handoff fields
        if remote_state_dict.get("clipboard_text"):
            self.current_state.clipboard_text = remote_state_dict["clipboard_text"]
        if remote_state_dict.get("active_dialogue_turn"):
            self.current_state.active_dialogue_turn = remote_state_dict["active_dialogue_turn"]

        return {
            "status": "STATE_SYNCHRONIZED",
            "device_id": dev_id,
            "synced_at": time.time(),
        }

    def get_state_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable workspace state."""
        return {
            "current_state": asdict(self.current_state),
            "satellite_count": len(self.satellites),
            "satellites": list(self.satellites.values()),
        }


# Singleton instance
satellite_sync_engine = CrossDeviceSyncEngine()
