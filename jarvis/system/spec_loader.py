"""
jarvis/system/spec_loader.py — Dynamic Hardware Auditor & Acceleration Prober
Profiles host CPU core topology, GPU devices via WMI/Win32/PyTorch, RAM allocation ceilings,
and runtime execution providers (OpenVINO, PyTorch CUDA, ONNX Runtime).
"""

import os
import sys
import platform
import psutil
from typing import Dict, Any, List
from jarvis.config import config

class HardwareAuditor:
    """
    Probes host hardware capabilities dynamically, reserving OS headroom while maximizing AI compute.
    """
    def __init__(self):
        self.os_name = platform.system()
        self.os_release = platform.release()
        self.architecture = platform.machine()

    def audit_cpu(self) -> Dict[str, Any]:
        logical = psutil.cpu_count(logical=True) or 1
        physical = psutil.cpu_count(logical=False) or 1
        freq = psutil.cpu_freq()
        
        # Intel hybrid architecture P-Core / E-Core estimation (e.g. Core i7-1255U: 2 P-Cores, 8 E-Cores = 12 Threads)
        has_hybrid = False
        p_cores = physical
        e_cores = 0
        if logical > physical * 2:
            # Multi-threading active
            pass
        elif physical == 10 and logical == 12:
            # Standard i7-1255U layout
            has_hybrid = True
            p_cores = 2
            e_cores = 8

        return {
            "processor": platform.processor(),
            "architecture": self.architecture,
            "physical_cores": physical,
            "logical_cores": logical,
            "estimated_p_cores": p_cores,
            "estimated_e_cores": e_cores,
            "is_hybrid_architecture": has_hybrid,
            "frequency_mhz": round(freq.current, 2) if freq else 0.0
        }

    def audit_gpu(self) -> List[Dict[str, Any]]:
        gpus = []
        # Attempt WMI query on Windows
        if self.os_name == "Windows":
            try:
                import wmi
                w = wmi.WMI()
                for gpu in w.Win32_VideoController():
                    gpus.append({
                        "name": gpu.Name,
                        "driver_version": getattr(gpu, "DriverVersion", "Unknown"),
                        "vram_mb": round(int(getattr(gpu, "AdapterRAM", 0) or 0) / (1024**2), 2),
                        "status": getattr(gpu, "Status", "OK")
                    })
            except Exception:
                pass

        # Fallback/Supplemental check using PyTorch CUDA if installed
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    gpu_name = torch.cuda.get_device_name(i)
                    if not any(g["name"] == gpu_name for g in gpus):
                        gpus.append({
                            "name": gpu_name,
                            "driver_version": "CUDA Driver",
                            "vram_mb": round(torch.cuda.get_device_properties(i).total_memory / (1024**2), 2),
                            "status": "CUDA Active"
                        })
        except Exception:
            pass

        if not gpus:
            gpus.append({
                "name": "Generic Host GPU / Integrated Display",
                "driver_version": "N/A",
                "vram_mb": 0.0,
                "status": "Fallback"
            })

        return gpus

    def audit_memory(self) -> Dict[str, Any]:
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024**3), 2)
        available_gb = round(mem.available / (1024**3), 2)
        used_percent = mem.percent
        
        # Calculate dynamic RAM ceiling for AI inference processes (leaves 1.5 GB for Windows kernel/OS)
        ram_ceiling_gb = max(4.0, round(total_gb - 1.5, 2))

        return {
            "total_ram_gb": total_gb,
            "available_ram_gb": available_gb,
            "used_percent": used_percent,
            "ram_ceiling_gb": ram_ceiling_gb
        }

    def audit_accelerators(self) -> Dict[str, Any]:
        accelerators = {
            "cuda_available": False,
            "cuda_device_count": 0,
            "onnx_providers": [],
            "openvino_available": False
        }

        # Check PyTorch CUDA
        try:
            import torch
            accelerators["cuda_available"] = torch.cuda.is_available()
            accelerators["cuda_device_count"] = torch.cuda.device_count() if torch.cuda.is_available() else 0
        except ImportError:
            pass

        # Check ONNX Runtime execution providers
        try:
            import onnxruntime as ort
            accelerators["onnx_providers"] = ort.get_available_providers()
        except ImportError:
            pass

        # Check OpenVINO
        try:
            import openvino as ov
            core = ov.Core()
            accelerators["openvino_available"] = True
            accelerators["openvino_devices"] = core.available_devices
        except ImportError:
            accelerators["openvino_available"] = False
            accelerators["openvino_devices"] = []

        return accelerators

    def audit(self) -> Dict[str, Any]:
        return {
            "system_os": f"{self.os_name} {self.os_release}",
            "cpu": self.audit_cpu(),
            "gpu": self.audit_gpu(),
            "memory": self.audit_memory(),
            "accelerators": self.audit_accelerators(),
            "env_config": config.to_dict()
        }

auditor = HardwareAuditor()

def audit_hardware() -> Dict[str, Any]:
    return auditor.audit()
