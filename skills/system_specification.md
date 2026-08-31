# Skill: System Hardware Architecture Specification v4.0
### *"Hardware is the physical foundation upon which artificial general intelligence executes."*

**System Owner:** Dhamodran Prasath C M | **Persona:** Tony Stark's J.A.R.V.I.S.  
**Hardware Platform:** HP Pavilion 14-dv2xxx (Core i7-1255U, 10C/12T, Iris Xe GPU 96 EUs, 16GB DDR4, 1TB NVMe, 36GB Pagefile)  
**Dynamic Specification Loader:** Fully automated Python system auditor (`jarvis/system/spec_loader.py`)

---

## 1. Dynamic System Specification Loader

```python
# jarvis/system/spec_loader.py — Production System Auditor & Hardware Spec Loader
import os, sys, psutil, platform, ctypes, logging
from dataclasses import dataclass, asdict

logger = logging.getLogger("jarvis.system.spec")

@dataclass
class HardwareProfile:
    os_name: str
    os_version: str
    processor_name: str
    logical_cores: int
    physical_cores: int
    total_ram_gb: float
    available_ram_gb: float
    pagefile_total_gb: float
    gpu_name: str

class SystemSpecificationAuditor:
    """
    Audits local host hardware and returns dynamic system capacity constraints.
    """
    def audit_system(self) -> HardwareProfile:
        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        gpu_info = "Intel Iris Xe Graphics (Shared VRAM)"
        if sys.platform == "win32":
            try:
                import wmi
                w = wmi.WMI()
                gpus = [g.Name for g in w.Win32_VideoController()]
                if gpus:
                    gpu_info = ", ".join(gpus)
            except Exception:
                pass

        profile = HardwareProfile(
            os_name=platform.system(),
            os_version=platform.version(),
            processor_name=platform.processor(),
            logical_cores=psutil.cpu_count(logical=True) or 12,
            physical_cores=psutil.cpu_count(logical=False) or 10,
            total_ram_gb=round(ram.total / (1024**3), 2),
            available_ram_gb=round(ram.available / (1024**3), 2),
            pagefile_total_gb=round(swap.total / (1024**3), 2),
            gpu_name=gpu_info
        )
        
        logger.info(f"[SYSTEM SPEC] Hardware Audit Complete: {profile.processor_name} | {profile.total_ram_gb}GB RAM")
        return profile
```

---

## 2. Hardware Resource Budget Table

```
Hardware Resource Allocations:
┌──────────────────────────────────────────────┬────────────────────────┐
│ Component                                    │ Dynamic Allocation     │
├──────────────────────────────────────────────┼────────────────────────┤
│ Ollama LLM VRAM Budget (Llama 3.2 3B)        │ 2.4 GB (Shared DDR4)   │
│ OpenVINO OpenCL Context Buffer               │ 512 MB                 │
│ Process Working Set Memory Ceiling           │ 14.5 GB max            │
│ Thread Affinity Mask                         │ P-Cores: 0x0F | E: 0xF0│
└──────────────────────────────────────────────┴────────────────────────┘
```
