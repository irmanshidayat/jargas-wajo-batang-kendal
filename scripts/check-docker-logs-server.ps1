# Script untuk cek log docker di server
# Menampilkan error lengkap dari container backend

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal",
    [int]$Lines = 200,
    [switch]$Follow = $false,
    [switch]$ErrorsOnly = $false
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Cek Log Docker di Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Konfigurasi:" -ForegroundColor Yellow
Write-Host "   Server: ${Username}@${ServerIP}" -ForegroundColor Gray
Write-Host "   Path: $ProjectPath" -ForegroundColor Gray
Write-Host "   Lines: $Lines" -ForegroundColor Gray
Write-Host ""

# Cek status container
Write-Host "Step 1: Cek status container backend..." -ForegroundColor Green
$statusCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose ps backend'"
try {
    $status = Invoke-Expression $statusCmd
    Write-Host $status -ForegroundColor Gray
    
    if ($status -match "Up" -or $status -match "running") {
        Write-Host "✅ Backend container running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backend container tidak running!" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek status container" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Cek log backend (error dan warning)..." -ForegroundColor Green
if ($ErrorsOnly) {
    $logCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs --tail=$Lines backend 2>&1 | grep -iE \"(error|exception|failed|traceback|critical|fatal)\"'"
} else {
    $logCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs --tail=$Lines backend 2>&1'"
}

try {
    if ($Follow) {
        Write-Host "Menampilkan log real-time (Ctrl+C untuk stop)..." -ForegroundColor Yellow
        Write-Host ""
        $followCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs -f backend 2>&1'"
        Invoke-Expression $followCmd
    } else {
        Write-Host "Mengambil log terakhir $Lines baris..." -ForegroundColor Gray
        Write-Host ""
        $logs = Invoke-Expression $logCmd
        Write-Host $logs -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error saat mengambil log: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 3: Cek log migration khusus..." -ForegroundColor Green
$migrationLogCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs --tail=$Lines backend 2>&1 | grep -iE \"(migration|alembic|upgrade|downgrade|error|exception)\"'"
try {
    $migrationLogs = Invoke-Expression $migrationLogCmd
    if ($migrationLogs) {
        Write-Host $migrationLogs -ForegroundColor Gray
    } else {
        Write-Host "Tidak ada log migration ditemukan" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek log migration" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Cek apakah container restart terus..." -ForegroundColor Green
$restartCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose ps backend | grep -i restart'"
try {
    $restartInfo = Invoke-Expression $restartCmd
    if ($restartInfo) {
        Write-Host "⚠️  Container restart terdeteksi:" -ForegroundColor Yellow
        Write-Host $restartInfo -ForegroundColor Gray
    } else {
        Write-Host "✅ Tidak ada restart loop terdeteksi" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek restart info" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  - Gunakan -Follow untuk log real-time" -ForegroundColor Gray
Write-Host "  - Gunakan -ErrorsOnly untuk hanya error" -ForegroundColor Gray
Write-Host "  - Contoh: .\check-docker-logs-server.ps1 -Follow" -ForegroundColor Gray
Write-Host ""

