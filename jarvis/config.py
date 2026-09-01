"""
jarvis/config.py — Dynamic System Topology & Environment Discovery
0% Hardcoded paths policy. Dynamically profiles host capabilities and environment variables.
"""

import os
import sys
import platform
import socket
from pathlib import Path
import psutil

class DynamicSystemConfig:
    """
    Dynamic environment resolver. Eliminates static hardcoding of paths, usernames,
    IP addresses, and hardware limits. Automatically profiles host capabilities.
    """
    def __init__(self):
        # 1. Dynamic Directory Resolution
        # Default root is parent of the jarvis directory (project root)
        default_root = Path(__file__).resolve().parent.parent
        self.root_dir = Path(os.getenv("JARVIS_ROOT", default_root))
        self.data_dir = Path(os.getenv("JARVIS_DATA_DIR", self.root_dir / "data"))
        self.logs_dir = Path(os.getenv("JARVIS_LOG_DIR", self.data_dir / "logs"))
        self.backups_dir = Path(os.getenv("JARVIS_BACKUP_DIR", self.data_dir / "backups"))
        self.vault_dir = Path(os.getenv("JARVIS_VAULT_DIR", self.data_dir / "vault"))
        self.user_home = Path.home()

        # Backward/convenience aliases
        self.log_dir = self.logs_dir
        self.backup_dir = self.backups_dir

        # Create required directories dynamically
        for folder in [self.data_dir, self.logs_dir, self.backups_dir, self.vault_dir]:
            folder.mkdir(parents=True, exist_ok=True)

        # 2. Dynamic Network Resolution
        self.host_ip = os.getenv("JARVIS_HOST", "127.0.0.1")
        self.fastapi_port = int(os.getenv("JARVIS_PORT", "8765"))
        self.ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
        self.n8n_port = int(os.getenv("N8N_PORT", "5678"))
        self.local_lan_ip = self._discover_lan_ip()

        # 3. Dynamic Hardware Profile
        self.cpu_logical = psutil.cpu_count(logical=True) or 1
        self.cpu_physical = psutil.cpu_count(logical=False) or 1
        mem = psutil.virtual_memory()
        self.total_ram_gb = round(mem.total / (1024**3), 2)
        self.available_ram_gb = round(mem.available / (1024**3), 2)
        
        # Calculated RAM Allocation Ceiling (Leaves 1.5 GB for OS)
        self.ram_ceiling_gb = max(4.0, round(self.total_ram_gb - 1.5, 2))

        # 4. Feature Flags & UI Config
        self.enable_control_center = os.getenv("JARVIS_ENABLE_CONTROL_CENTER", "true").lower() in ("1", "true", "yes")

    def _discover_lan_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def to_dict(self) -> dict:
        return {
            "root_dir": str(self.root_dir),
            "data_dir": str(self.data_dir),
            "logs_dir": str(self.logs_dir),
            "backups_dir": str(self.backups_dir),
            "vault_dir": str(self.vault_dir),
            "user_home": str(self.user_home),
            "host_ip": self.host_ip,
            "lan_ip": self.local_lan_ip,
            "fastapi_port": self.fastapi_port,
            "fastapi_endpoint": f"http://{self.host_ip}:{self.fastapi_port}",
            "ollama_endpoint": f"http://{self.host_ip}:{self.ollama_port}",
            "n8n_endpoint": f"http://{self.host_ip}:{self.n8n_port}",
            "cpu_topology": f"{self.cpu_physical} Physical / {self.cpu_logical} Logical",
            "ram_total_gb": self.total_ram_gb,
            "ram_available_gb": self.available_ram_gb,
            "ram_ceiling_gb": self.ram_ceiling_gb,
            "enable_control_center": self.enable_control_center
        }

config = DynamicSystemConfig()
