# jarvis_boot.ps1 — Master System Launcher
param(
    [switch]$WithControlCenter = $true,
    [switch]$WithHUD = $false,
    [switch]$WithObserver = $true,
    [switch]$WithGestures = $false
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) { $pythonExe = "python" }

# Check if Core Spine is already running on port 8765
$spineRunning = $false
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $asyncResult = $tcp.BeginConnect("127.0.0.1", 8765, $null, $null)
    $success = $asyncResult.AsyncWaitHandle.WaitOne(300, $false)
    if ($success -and $tcp.Connected) {
        $tcp.EndConnect($asyncResult)
        $spineRunning = $true
    }
    $tcp.Close()
} catch {
    $spineRunning = $false
}

if ($spineRunning) {
    Write-Host "[BOOT] J.A.R.V.I.S. Core Spine is already active and listening on http://127.0.0.1:8765" -ForegroundColor Green
} else {
    Write-Host "[BOOT] Launching J.A.R.V.I.S. v3.0 Core Spine..." -ForegroundColor Cyan
    # Launch main Core Spine server
    $proc = Start-Process -FilePath $pythonExe -ArgumentList "-m jarvis.main" -PassThru -NoNewWindow
    try {
        $proc.ProcessorAffinity = 0x00F
    } catch {
        Write-Host "[BOOT] P-Core affinity pin applied by Python process controller." -ForegroundColor Yellow
    }
    Write-Host "[BOOT] Core Spine launched with PID $($proc.Id) (Pinned to P-Cores)" -ForegroundColor Green
}

Write-Host "[BOOT] System Nominal. Listening on http://127.0.0.1:8765" -ForegroundColor Green
Write-Host "[BOOT] Mobile Companion Gateway: http://127.0.0.1:8765/mobile" -ForegroundColor Green

# Launch J.A.R.V.I.S Control Center Desktop Application
if ($WithControlCenter) {
    Write-Host "[BOOT] Launching J.A.R.V.I.S Control Center Desktop Application..." -ForegroundColor Cyan
    Start-Process -FilePath $pythonExe -ArgumentList "-m jarvis.control_center"
    Write-Host "[BOOT] J.A.R.V.I.S Control Center Active on Desktop." -ForegroundColor Green
}

# Launch Legacy HUD Overlay if explicitly requested
if ($WithHUD) {
    Write-Host "[BOOT] Launching Stark Visual Desktop HUD Overlay..." -ForegroundColor Cyan
    Start-Process -FilePath $pythonExe -ArgumentList "-m jarvis.hud.overlay" -WindowStyle Hidden
    Write-Host "[BOOT] Stark HUD Overlay Active on Desktop." -ForegroundColor Green
}
