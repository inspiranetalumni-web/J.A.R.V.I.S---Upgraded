# scripts/build_jarvis_exe.ps1 — Standalone Executable Packager
$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   J.A.R.V.I.S. v3.0 STANDALONE EXE COMPILATION PIPELINE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $env:JARVIS_ROOT) { $env:JARVIS_ROOT = $projectRoot }

$specFile = Join-Path $projectRoot "build\jarvis.spec"

Write-Host "[BUILD] Installing/Verifying PyInstaller in environment..." -ForegroundColor Yellow
& python -m pip install pyinstaller -q

Write-Host "[BUILD] Compiling J.A.R.V.I.S. Standalone Executable..." -ForegroundColor Yellow
& python -m PyInstaller $specFile --noconfirm --clean

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   COMPILATION COMPLETE - Standalone binary ready at dist/jarvis.exe" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
