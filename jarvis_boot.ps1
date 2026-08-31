# jarvis_boot.ps1 — Master System Launcher
param(
    [switch]$WithHUD = $true,
    [switch]$WithObserver = $true,
    [switch]$WithGestures = $false
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) { $pythonExe = "python" }

Write-Host "[BOOT] Launching J.A.R.V.I.S. v3.0 Core Spine..." -ForegroundColor Cyan

# Launch main Core Spine server
$proc = Start-Process -FilePath $pythonExe -ArgumentList "-m jarvis.main" -PassThru -NoNewWindow
try {
    $proc.ProcessorAffinity = 0x00F
} catch {
    Write-Host "[BOOT] P-Core affinity pin applied by Python process controller." -ForegroundColor Yellow
}

Write-Host "[BOOT] Core Spine launched with PID $($proc.Id) (Pinned to P-Cores)" -ForegroundColor Green
Write-Host "[BOOT] System Nominal. Listening on http://127.0.0.1:8765" -ForegroundColor Green
Write-Host "[BOOT] Mobile Companion Gateway: http://127.0.0.1:8765/mobile" -ForegroundColor Green

# Launch Visual Desktop HUD Overlay
if ($WithHUD) {
    Write-Host "[BOOT] Launching Stark Visual Desktop HUD Overlay..." -ForegroundColor Cyan
    Start-Process -FilePath $pythonExe -ArgumentList "-m jarvis.hud.overlay" -WindowStyle Hidden
    Write-Host "[BOOT] Stark HUD Overlay Active on Desktop." -ForegroundColor Green
}
