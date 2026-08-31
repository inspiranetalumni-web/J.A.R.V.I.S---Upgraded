# jarvis_shutdown.ps1 — Graceful System Shutdown Script
$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   J.A.R.V.I.S. v3.0 SYSTEM SHUTDOWN PROTOCOL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "[SHUTDOWN] Searching for active J.A.R.V.I.S. Core Spine processes..." -ForegroundColor Yellow

$procs = Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like "*jarvis.main*" }

if ($procs) {
    foreach ($proc in $procs) {
        Write-Host "[SHUTDOWN] Terminating process PID $($proc.ProcessId)..." -ForegroundColor Yellow
        Stop-Process -Id $proc.ProcessId -Force
    }
    Write-Host "[SHUTDOWN] Core Spine server terminated successfully." -ForegroundColor Green
} else {
    Write-Host "[SHUTDOWN] No active J.A.R.V.I.S. Core Spine process found." -ForegroundColor Gray
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   J.A.R.V.I.S. SHUTDOWN COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
