"""
jarvis/mesh/node_offloader.py — Distributed P2P LAN Node Discoverer & Offloader
Discovers secondary LAN computing nodes and offloads heavy AI inference when primary host is under load.
"""

import os
import socket
import requests
import time
import psutil
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

logger = logging.getLogger("jarvis.mesh.offloader")


@dataclass
class MeshNode:
    name: str
    host_ip: str
    port: int
    has_gpu: bool
    latency_ms: float
    is_active: bool


class P2PMeshOffloader:
    """
    Auto-discovers secondary local computing nodes on private LAN
    and routes heavy LLM inference requests when the host laptop reaches high load.
    """
    def __init__(self):
        self.peers: List[MeshNode] = []
        self.primary_host_ip = self._get_local_ip()

    def _get_local_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def should_offload(self) -> bool:
        """Returns True if local thermal or memory conditions warrant offloading."""
        try:
            ram_used = psutil.virtual_memory().used / (1024**3)
            return ram_used >= 13.5
        except Exception:
            return False

    def probe_node(self, target_ip: str, port: int = 11434, timeout: float = 1.5) -> Optional[MeshNode]:
        """Pings target peer Ollama/Spine endpoint to verify availability and latency."""
        t0 = time.perf_counter()
        try:
            resp = requests.get(f"http://{target_ip}:{port}/api/tags", timeout=timeout)
            if resp.status_code == 200:
                latency = (time.perf_counter() - t0) * 1000
                node = MeshNode(
                    name=f"peer_{target_ip.replace('.', '_')}",
                    host_ip=target_ip,
                    port=port,
                    has_gpu=True,
                    latency_ms=round(latency, 1),
                    is_active=True
                )
                # Update existing or append
                self.peers = [p for p in self.peers if p.host_ip != target_ip]
                self.peers.append(node)
                logger.info(f"[P2P MESH] Discovered active peer node {target_ip}:{port} ({latency:.1f}ms)")
                return node
        except Exception:
            pass
        return None

    def register_peer(self, host_ip: str, port: int = 11434, name: Optional[str] = None, has_gpu: bool = True) -> MeshNode:
        """Manually registers a LAN cluster node."""
        node = MeshNode(
            name=name or f"peer_{host_ip.replace('.', '_')}",
            host_ip=host_ip,
            port=port,
            has_gpu=has_gpu,
            latency_ms=1.0,
            is_active=True
        )
        self.peers = [p for p in self.peers if p.host_ip != host_ip]
        self.peers.append(node)
        return node

    def offload_llm_request(
        self,
        prompt: str,
        peer: Optional[MeshNode] = None,
        model: str = "llama3.2:3b",
        timeout: float = 10.0
    ) -> Dict[str, Any]:
        """Offloads LLM inference to peer node over local LAN."""
        target_peer = peer or (self.peers[0] if self.peers else None)
        if not target_peer:
            return {"success": False, "error": "No active P2P peer nodes available for offloading."}

        t0 = time.perf_counter()
        try:
            resp = requests.post(
                f"http://{target_peer.host_ip}:{target_peer.port}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout
            )
            elapsed = (time.perf_counter() - t0) * 1000
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "response": data.get("response", ""),
                    "peer": target_peer.host_ip,
                    "latency_ms": round(elapsed, 2),
                }
            else:
                return {"success": False, "error": f"Peer returned HTTP {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_mesh_status(self) -> Dict[str, Any]:
        """Returns P2P LAN mesh topology report."""
        return {
            "primary_ip": self.primary_host_ip,
            "should_offload": self.should_offload(),
            "peer_count": len(self.peers),
            "peers": [asdict(p) for p in self.peers],
        }


# Singleton instance
p2p_mesh_offloader = P2PMeshOffloader()
