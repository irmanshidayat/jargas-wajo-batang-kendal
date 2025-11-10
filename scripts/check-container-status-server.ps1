# Script untuk cek status container di server
# Menampilkan status semua container dan restart count

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Cek Status Container di Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Konfigurasi:" -ForegroundColor Yellow
Write-Host "   Server: ${Username}@${ServerIP}" -ForegroundColor Gray
Write-Host "   Path: $ProjectPath" -ForegroundColor Gray
Write-Host ""

# Cek status semua container
Write-Host "Step 1: Status semua container..." -ForegroundColor Green
$statusCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose ps'"
try {
    $status = Invoke-Expression $statusCmd
    Write-Host $status -ForegroundColor Gray
} catch {
    Write-Host "❌ Error saat cek status: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 2: Detail status backend container..." -ForegroundColor Green
$backendStatusCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker inspect jargas_backend --format=\"{{.State.Status}} | Restart Count: {{.RestartCount}} | Started: {{.State.StartedAt}} | Finished: {{.State.FinishedAt}}\"'"
try {
    $backendStatus = Invoke-Expression $backendStatusCmd
    Write-Host $backendStatus -ForegroundColor Gray
    
    # Cek restart count
    $restartCountCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker inspect jargas_backend --format=\"{{.RestartCount}}\"'"
    $restartCount = Invoke-Expression $restartCountCmd
    $restartCount = [int]$restartCount.Trim()
    
    if ($restartCount -gt 10) {
        Write-Host "⚠️  WARNING: Container sudah restart $restartCount kali!" -ForegroundColor Red
        Write-Host "   Kemungkinan ada masalah dengan aplikasi atau migration" -ForegroundColor Yellow
    } elseif ($restartCount -gt 5) {
        Write-Host "⚠️  Container sudah restart $restartCount kali" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Restart count: $restartCount (normal)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek detail backend: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Cek health status backend..." -ForegroundColor Green
$healthCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker inspect jargas_backend --format=\"{{.State.Health.Status}}\"'"
try {
    $health = Invoke-Expression $healthCmd
    $health = $health.Trim()
    if ($health -eq "healthy") {
        Write-Host "✅ Health status: $health" -ForegroundColor Green
    } elseif ($health -eq "unhealthy") {
        Write-Host "❌ Health status: $health" -ForegroundColor Red
        Write-Host "   Container tidak sehat, cek log untuk detail" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  Health status: $health" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek health status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Cek log terakhir (10 baris) untuk error..." -ForegroundColor Green
$lastLogCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs --tail=10 backend 2>&1'"
try {
    $lastLogs = Invoke-Expression $lastLogCmd
    Write-Host $lastLogs -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Tidak bisa cek log" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

