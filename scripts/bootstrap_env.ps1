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

Write-Host "[SETUP] Installing J.A.R.V.I.S. v3.0 Core Python Dependencies..." -ForegroundColor Yellow
& $pipExe install fastapi uvicorn pydantic requests httpx websockets psutil wmi pywin32 comtypes pytest pytest-asyncio -q

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   BOOTSTRAP COMPLETE — System ready for Phase 1 testing" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
