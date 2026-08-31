# J.A.R.V.I.S. Master System Specification v3.0 (Stark Horizon Architecture)
### *"The Mark LXXXV Specification: Dynamic, Sovereign, Multi-Agent Swarm, 3D Spatial & Scale-Out Mesh System"*

**System Name:** J.A.R.V.I.S. (Just A Rather Very Intelligent System)  
**System Owner:** Dhamodran Prasath C M | **Persona Standard:** Tony Stark's J.A.R.V.I.S.  
**Architecture Standard:** 8 Systems Engineering Disciplines + 10 Core Stark Sectors + 7 Advanced Horizon Capabilities  
**Hardware Host Baseline:** Intel Core i7-1255U (2 P-Cores + 8 E-Cores, 12 Threads) | Intel Iris Xe GPU (96 EUs) | 16 GB Shared DDR4 | 1 TB NVMe SSD  
**Scalability Engine:** Dynamic Single-Node to Multi-Node Local Mesh (P2P LAN / Wi-Fi 6 RPC compute scaling)  
**Dynamic Policy:** 0% hardcoded paths/IPs (`JARVIS_ROOT`, `JARVIS_DATA_DIR`, `Path.home()`, `0.0.0.0` socket binding)

---

## 1. Dynamic Environment & Scalable System Topology

J.A.R.V.I.S. initializes through an environment-aware, dynamic discovery layer that adapts automatically to any host environment without hardcoded configuration paths:

```mermaid
flowchart TB
    subgraph Layer1_Sensory ["1. Multimodal & Spatial Sensory Ingestion Layer"]
        MIC[("Acoustic Array\n(16kHz 16-bit PCM)")] --> VAD["Silero VAD ONNX\n(Thread 4 E-Core)"]
        VAD --> WAKE["openWakeWord ONNX\n(Thread 5 E-Core)"]
        WAKE --> STT["faster-whisper INT8\n(Threads 0-1 P-Core)"]
        CAM[("Optical Camera\n(30/60 FPS Video)")] --> GESTURE["MediaPipe 3D Hand Landmarks\n(Spatial Air Gestures)"]
        CAM --> SCRCAP["DXGI Desktop Duplication\n(pHash Delta Tiling)"]
        BLE[("BLE Wearable Sensor")] --> VITAL["Biometric Harvester\n(Stress Index Engine)"]
    end

    subgraph Layer2_Spine ["2. Dynamic Central Spine (FastAPI @ :8765)"]
        STT --> ROUTER["3-Stage Hybrid Intent Router\n(Regex < 0.1ms → Score < 0.5ms → LLM ~30ms)"]
        GESTURE --> ROUTER
        VITAL --> ROUTER
        SCRCAP --> ROUTER
        
        ROUTER --> CTX["Context Compaction Engine\n(10/15/25/35/15 Token Budget)"]
        ROUTER --> SWARM["Swarm Sub-Agent Orchestrator\n(House Party Protocol)"]
        ROUTER --> SECURITY["Security Guardrail Agent\n(4-Layer Defense + HMAC Escrow)"]
        
        STATE["PySide6 Ghost HUD State Engine"] <--> ROUTER
        APSCHED["APScheduler Daemon (02:00 AM)"] --> MEM_CLEAN["Memory Consolidation & TTL Cleaner"]
        SELF_LEARN["Self-Learning & Evolution Engine"] <--> STATE
    end

    subgraph Layer3_Cognitive ["3. Cognitive Core & Multi-Persona (Ollama @ :11434)"]
        ROUTER <--> LLAMA["Llama-3.2-3B-Instruct\n(Conversational Persona)"]
        ROUTER <--> QWEN["Qwen-2.5-Coder-1.5B\n(Code & Upgrade Engine)"]
        ROUTER <--> MOON["moondream\n(Vision Grounding)"]
        PERSONA["Persona Manager\n(JARVIS / FRIDAY / EDITH)"] <--> ROUTER
    end

    subgraph Layer4_Memory ["4. Authenticated Long-Term Memory Vault"]
        ROUTER --> DISTILL["Async Post-Turn Fact Distiller"]
        DISTILL --> AES_VAULT["Quantum Shield AES-256-GCM Vault"]
        AES_VAULT --> CHROMA[("ChromaDB Vector Store\n(Cosine Similarity)")]
        AES_VAULT --> KUZU[("KùzuDB Knowledge Graph\n(Property Triples)")]
        CHROMA --> CONTEXT_INJECT["Time-Weighted Recency Ranking"]
        KUZU --> CONTEXT_INJECT
        CONTEXT_INJECT --> ROUTER
    end

    subgraph Layer5_Hands ["5. Execution Hands & Scale-Out Mesh"]
        SECURITY --> MCP_PROXY["MCP Tool Proxy"]
        MCP_PROXY --> FS_MCP["Filesystem MCP Server"]
        MCP_PROXY --> PW_MCP["Playwright MCP Server"]
        MCP_PROXY --> ES_CLI["Everything CLI (es.exe < 5ms)"]
        MCP_PROXY --> GIT_AUTO["Stark Auto-Engineer Git Pipeline"]
        MCP_PROXY --> OS_ACT["Windows UIAutomation + HA Smart Home"]
        SWARM --> P2P_MESH["P2P LAN Mesh Offloader\n(Wi-Fi 6 RPC to Peer Nodes)"]
    end

    subgraph Layer6_Output ["6. Multi-Voice Output & Spatial HUD"]
        STATE --> WS_STREAM["WebSocket /ws/status Stream"]
        WS_STREAM --> GHOST_HUD["Holographic Ghost HUD\n(PySide6 Frameless Overlay)"]
        ROUTER --> TTS["Kokoro-82M ONNX Persona Voice\n(24kHz Clause Streaming)"]
        TTS --> AUDIO_OUT[("Realtek Soundcard PCM")]
        MIC -.->|"Barge-in Cut-off"| TTS
    end
```

---

## 2. Dynamic Hardware & Environment Discovery Module

```python
# jarvis/config_dynamic.py — Dynamic System Topology & Environment Discovery
import os, sys, platform, psutil, socket, ctypes
from pathlib import Path

class DynamicSystemConfig:
    """
    Dynamic environment resolver. Eliminates static hardcoding of paths, usernames,
    IP addresses, and hardware limits. Automatically profiles host capabilities.
    """
    def __init__(self):
        # Dynamic Directory Resolution
        self.root_dir = Path(os.getenv("JARVIS_ROOT", Path(__file__).resolve().parent.parent))
        self.data_dir = Path(os.getenv("JARVIS_DATA_DIR", self.root_dir / "data"))
        self.logs_dir = Path(os.getenv("JARVIS_LOG_DIR", self.data_dir / "logs"))
        self.backups_dir = Path(os.getenv("JARVIS_BACKUP_DIR", self.data_dir / "backups"))
        self.vault_dir = Path(os.getenv("JARVIS_VAULT_DIR", self.data_dir / "vault"))
        self.user_home = Path.home()

        # Create required directories dynamically
        for folder in [self.data_dir, self.logs_dir, self.backups_dir, self.vault_dir]:
            folder.mkdir(parents=True, exist_ok=True)

        # Dynamic Network Resolution
        self.host_ip = os.getenv("JARVIS_HOST", "127.0.0.1")
        self.fastapi_port = int(os.getenv("JARVIS_PORT", "8765"))
        self.ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
        self.n8n_port = int(os.getenv("N8N_PORT", "5678"))
        self.local_lan_ip = self._discover_lan_ip()

        # Dynamic Hardware Profile
        self.cpu_logical = psutil.cpu_count(logical=True)
        self.cpu_physical = psutil.cpu_count(logical=False)
        self.total_ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        self.available_ram_gb = round(psutil.virtual_memory().available / (1024**3), 2)
        
        # Calculated RAM Allocation Ceiling (Leaves 1.5 GB for OS)
        self.ram_ceiling_gb = max(4.0, self.total_ram_gb - 1.5)

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
            "host_ip": self.host_ip,
            "lan_ip": self.local_lan_ip,
            "fastapi_endpoint": f"http://{self.host_ip}:{self.fastapi_port}",
            "ollama_endpoint": f"http://{self.host_ip}:{self.ollama_port}",
            "n8n_endpoint": f"http://{self.host_ip}:{self.n8n_port}",
            "cpu_topology": f"{self.cpu_physical} Physical / {self.cpu_logical} Logical",
            "ram_total": f"{self.total_ram_gb} GB",
            "ram_ceiling": f"{self.ram_ceiling_gb} GB"
        }

config = DynamicSystemConfig()
```

---

## 3. Future Scalability Blueprint (Tony Stark Scale-Out Model)

J.A.R.V.I.S. v3.0 is engineered with a **Modular Scale-Out Design Pattern**, enabling frictionless expansion across 3 scalability tiers:

```
[Tier 1: Single-Node Sovereign Assistant]
  - Physical Laptop (HP Pavilion i7-1255U / 16GB RAM)
  - Runs local SLMs (Llama 3.2 3B, Qwen 2.5 Coder 1.5B)
  - Local stdio MCP tools + Everything CLI + PySide6 HUD
  
                       │ Scale-Out Expansion (Zero Code Rewrite)
                       ▼
[Tier 2: LAN Multi-Node Compute Mesh]
  - Primary Host (Laptop) + Secondary GPU Node (Desktop NVIDIA GPU)
  - Auto mDNS peer discovery over Wi-Fi 6 / 2.5GbE LAN
  - Thermal / RAM pressure triggers RPC offloading (< 8ms hop)
  
                       │ Scale-Out Expansion (Enterprise Cluster)
                       ▼
[Tier 3: Multi-Agent Distributed Swarm Cluster]
  - Swarm sub-agents execute across 10+ worker nodes in parallel
  - House Party Protocol DAG orchestrator
  - High-throughput vector/graph sharding across nodes
```

### Scalability Principles Applied:
1. **Stateless Agent Worker Pattern**: All specialized agents communicate via standard REST/WebSocket or JSON-RPC 2.0 interfaces, allowing any agent to be moved to a remote process or remote machine without breaking system state.
2. **Dynamic Service Discovery**: Tools and secondary nodes auto-register at startup via standard mDNS / stdio manifests, requiring zero code changes to add new capability modules.
3. **Pluggable Skill/Agent Architecture**: Adding a new skill requires only placing a new `.md` file in `skills/` or a new agent file in `agents/`; the system auto-indexes and binds it via `HybridIntentRouter`.

---

## 4. Complete System Inventory (57 Specifications)

- **Foundation Specifications**: [SETUP_COMMANDS.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/SETUP_COMMANDS.md), [SYSTEM_SPECIFICATION.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/SYSTEM_SPECIFICATION.md)
- **Master Blueprint**: [systems_engineering_master_blueprint.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/systems_engineering_master_blueprint.md)
- **Master Skill Index (28 Skills)**: [skills.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/skills/skills.md)
- **Master Agent Index (25 Agents)**: [agents.md](file:///e:/J.A.R.V.I.S%20-%20Upgraded/agents/agents.md)
- **Task Tracker**: [task.md](file:///C:/Users/dhamo/.gemini/antigravity-ide/brain/7b92c801-c1c4-4929-8413-52a6c989fd73/task.md)
