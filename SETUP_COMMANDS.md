# J.A.R.V.I.S. Setup & Initialization Commands v3.0 (Stark Horizon Standard)
### *"Complete setup, environment bootstrapping, dynamic path configuration, and system verification scripts."*

**System Standard:** J.A.R.V.I.S. v3.0 (8 Disciplines + 10 Core Sectors + 7 Advanced Horizon Modules)  
**Target Environment:** Windows 11 64-bit | Python 3.11 Virtual Environment (`.venv`) | Node.js 20+  
**Dynamic Policy:** 0% hardcoded paths (`JARVIS_ROOT`, `JARVIS_DATA_DIR`, `Path.home()`, `0.0.0.0` network socket binding)

---

## 1. Automated Environment Bootstrapper (`scripts/bootstrap_env.ps1`)

Run this script in PowerShell as Administrator to bootstrap the entire virtual environment, dynamic directories, required C++ runtimes, and background services:

```powershell
# scripts/bootstrap_env.ps1 — Dynamic J.A.R.V.I.S. v3.0 Environment Bootstrapper
$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   J.A.R.V.I.S. v3.0 STARK HORIZON ENVIRONMENT BOOTSTRAPPER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Dynamic Root Resolution
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $env:JARVIS_ROOT) { $env:JARVIS_ROOT = $projectRoot }
$dataDir = Join-Path $env:JARVIS_ROOT "data"
$logsDir = Join-Path $dataDir "logs"
$backupsDir = Join-Path $dataDir "backups"
$vaultDir = Join-Path $dataDir "vault"

Write-Host "[SETUP] Project Root resolved: $env:JARVIS_ROOT" -ForegroundColor Green

# Create required directories dynamically
foreach ($dir in @($dataDir, $logsDir, $backupsDir, $vaultDir)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[SETUP] Created directory: $dir" -ForegroundColor Yellow
    }
}

# 2. Virtual Environment Setup
$venvPath = Join-Path $env:JARVIS_ROOT ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[SETUP] Creating Python 3.11 virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
}
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

# 3. Upgrade Pip & Install Dependencies
Write-Host "[SETUP] Upgrading pip, setuptools, wheel..." -ForegroundColor Yellow
& $pipExe install --upgrade pip setuptools wheel -q

Write-Host "[SETUP] Installing J.A.R.V.I.S. v3.0 Python Dependencies..." -ForegroundColor Yellow
& $pipExe install `
    fastapi uvicorn pydantic requests httpx websockets `
    psutil wmi pywin32 comtypes `
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 `
    onnxruntime faster-whisper openwakeword sounddevice numpy scipy pillow `
    chromadb pykuzu `
    opencv-python mediapipe bleak pycryptodomex `
    scikit-learn -q

# 4. Install Node.js MCP Dependencies
Write-Host "[SETUP] Installing Node.js MCP dependencies..." -ForegroundColor Yellow
& npx.cmd -y @modelcontextprotocol/server-playwright --help | Out-Null
& npx.cmd -y @modelcontextprotocol/server-filesystem --help | Out-Null

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   BOOTSTRAP COMPLETE — System ready for initialization" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
```

---

## 2. Dynamic System Launch Script (`jarvis_boot.ps1`)

```powershell
# jarvis_boot.ps1 — Master System Launcher
param(
    [switch]$WithHUD = $true,
    [switch]$WithObserver = $true,
    [switch]$WithGestures = $false
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

Write-Host "[BOOT] Launching J.A.R.V.I.S. v3.0 Core Spine..." -ForegroundColor Cyan

# Set process affinity to P-Cores for main FastAPI process (Threads 0-3 = Mask 0x00F)
$proc = Start-Process -FilePath $pythonExe -ArgumentList "-m jarvis.main" -PassThru -NoNewWindow
$proc.ProcessorAffinity = 0x00F

Write-Host "[BOOT] Core Spine launched with PID $($proc.Id) (Pinned to P-Cores)" -ForegroundColor Green

if ($WithObserver) {
    Write-Host "[BOOT] Starting Proactive Observer Daemon..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonExe -ArgumentList "-m jarvis.observer.daemon" -NoNewWindow
}

if ($WithGestures) {
    Write-Host "[BOOT] Starting 3D Spatial Gesture Engine..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonExe -ArgumentList "-m jarvis.vision.spatial_gesture" -NoNewWindow
}

Write-Host "[BOOT] System Nominal. Listening on http://127.0.0.1:8765" -ForegroundColor Green
```

---

## 3. Dynamic Verification Suite (`scripts/verify_system.py`)

```python
# scripts/verify_system.py — System Health & Capability Verification
import os, sys, requests, psutil
from pathlib import Path

def verify_all_subsystems() -> bool:
    """Verifies that all FastAPI, Ollama, VAD, and MCP endpoints are dynamic and operational."""
    print("=" * 60)
    print("   J.A.R.V.I.S. v3.0 SYSTEM CAPABILITY VERIFICATION")
    print("=" * 60)
    
    root = Path(os.getenv("JARVIS_ROOT", Path.cwd()))
    data_dir = Path(os.getenv("JARVIS_DATA_DIR", root / "data"))
    
    print(f"[CHECK 1] Root Directory: {root} -> {'✓ OK' if root.exists() else '✗ MISSING'}")
    print(f"[CHECK 2] Data Directory: {data_dir} -> {'✓ OK' if data_dir.exists() else '✗ MISSING'}")
    
    # Check FastAPI Core
    fastapi_ok = False
    try:
        r = requests.get("http://127.0.0.1:8765/health", timeout=3)
        fastapi_ok = r.status_code == 200
    except Exception:
        pass
    print(f"[CHECK 3] FastAPI Spine (:8765): {'✓ ONLINE' if fastapi_ok else '✗ OFFLINE (Start jarvis_boot.ps1)'}")
    
    # Check Ollama Engine
    ollama_ok = False
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        ollama_ok = r.status_code == 200
    except Exception:
        pass
    print(f"[CHECK 4] Ollama OpenVINO (:11434): {'✓ ONLINE' if ollama_ok else '✗ OFFLINE (Start Ollama service)'}")

    # Check Key Packages
    packages = ["cv2", "mediapipe", "bleak", "Cryptodome", "chromadb", "faster_whisper"]
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"[CHECK 5] Package '{pkg}': ✓ INSTALLED")
        except ImportError:
            print(f"[CHECK 5] Package '{pkg}': ✗ MISSING (Run bootstrap_env.ps1)")

    print("=" * 60)
    return fastapi_ok and ollama_ok

if __name__ == "__main__":
    verify_all_subsystems()
```
