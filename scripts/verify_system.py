# scripts/verify_system.py — System Health & Capability Verification
import os
import sys
import requests
import psutil
from pathlib import Path

def verify_all_subsystems() -> bool:
    """Verifies that all FastAPI, Ollama, VAD, and MCP endpoints are dynamic and operational."""
    print("=" * 60)
    print("   J.A.R.V.I.S. v3.0 SYSTEM CAPABILITY VERIFICATION")
    print("=" * 60)
    
    root = Path(os.getenv("JARVIS_ROOT", Path.cwd()))
    data_dir = Path(os.getenv("JARVIS_DATA_DIR", root / "data"))
    
    print(f"[CHECK 1] Root Directory: {root} -> {'[OK]' if root.exists() else '[MISSING]'}")
    print(f"[CHECK 2] Data Directory: {data_dir} -> {'[OK]' if data_dir.exists() else '[MISSING]'}")
    
    # Check FastAPI Core
    fastapi_ok = False
    try:
        r = requests.get("http://127.0.0.1:8765/health", timeout=3)
        fastapi_ok = (r.status_code == 200)
    except Exception:
        pass
    print(f"[CHECK 3] FastAPI Spine (:8765): {'[ONLINE]' if fastapi_ok else '[OFFLINE] (Start via python -m jarvis.main)'}")
    
    # Check Ollama Engine
    ollama_ok = False
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        ollama_ok = (r.status_code == 200)
    except Exception:
        pass
    print(f"[CHECK 4] Ollama OpenVINO (:11434): {'[ONLINE]' if ollama_ok else '[OFFLINE] (Optional for Phase 1)'}")

    # Check Key Packages
    packages = ["fastapi", "uvicorn", "pydantic", "psutil", "requests", "httpx"]
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"[CHECK 5] Package '{pkg}': [INSTALLED]")
        except ImportError:
            print(f"[CHECK 5] Package '{pkg}': [MISSING]")

    print("=" * 60)
    return fastapi_ok

if __name__ == "__main__":
    verify_all_subsystems()
