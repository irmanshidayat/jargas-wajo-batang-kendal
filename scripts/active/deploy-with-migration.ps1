# Script Deployment dengan Auto-Migration - JALANKAN DI WINDOWS
# Script ini akan deploy kode ke server dan menjalankan migration otomatis

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment dengan Auto-Migration" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if SSH is available
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "SSH tidak ditemukan!" -ForegroundColor Red
    Write-Host "Install OpenSSH Client dari Settings > Apps > Optional Features" -ForegroundColor Yellow
    exit 1
}

Write-Host "Konfigurasi:" -ForegroundColor Yellow
Write-Host "   Server: ${Username}@${ServerIP}" -ForegroundColor Gray
Write-Host "   Path: $ProjectPath" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Lanjutkan deployment? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Deployment dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Pull kode terbaru dari Git..." -ForegroundColor Green
$gitPullCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && git pull origin main'"
try {
    Invoke-Expression $gitPullCmd
    Write-Host "✅ Git pull berhasil" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Git pull gagal atau tidak ada perubahan" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Step 2: Verifikasi file .env production..." -ForegroundColor Green
$checkEnvCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && test -f .env && test -f backend/.env && echo OK || echo MISSING'"
$envStatus = Invoke-Expression $checkEnvCmd
if ($envStatus -notmatch "OK") {
    Write-Host "❌ File .env production tidak ditemukan!" -ForegroundColor Red
    Write-Host "   Pastikan file .env dan backend/.env sudah dibuat" -ForegroundColor Yellow
    Write-Host "   Gunakan script: scripts/setup/setup-env-production.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ File .env production ditemukan" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Rebuild Docker containers..." -ForegroundColor Green
$rebuildCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose --env-file .env build --no-cache'"
try {
    Invoke-Expression $rebuildCmd
    Write-Host "✅ Build berhasil" -ForegroundColor Green
} catch {
    Write-Host "❌ Build gagal!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 4: Stop containers..." -ForegroundColor Green
$stopCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose --env-file .env down'"
Invoke-Expression $stopCmd
Write-Host "✅ Containers stopped" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Start containers (migration akan otomatis berjalan)..." -ForegroundColor Green
$startCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose --env-file .env up -d'"
try {
    Invoke-Expression $startCmd
    Write-Host "✅ Containers started" -ForegroundColor Green
} catch {
    Write-Host "❌ Start containers gagal!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 6: Menunggu backend ready (30 detik)..." -ForegroundColor Green
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "Step 7: Cek status migration..." -ForegroundColor Green
$migrationCheckCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose --env-file .env logs backend --tail 50 | grep -i migration || docker-compose --env-file .env logs backend --tail 50 | Select-String -Pattern \"migration\" -CaseSensitive:`$false'"
try {
    $migrationLogs = Invoke-Expression $migrationCheckCmd
    if ($migrationLogs) {
        Write-Host "📋 Migration logs:" -ForegroundColor Cyan
        Write-Host $migrationLogs -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Tidak ada migration logs (mungkin sudah up-to-date)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek migration logs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 8: Verifikasi tabel database..." -ForegroundColor Green
$verifyCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose --env-file .env exec -T mysql mysql -u root -padmin123 jargas_apbn -e \"SHOW TABLES;\" 2>/dev/null | head -20'"
try {
    $tables = Invoke-Expression $verifyCmd
    if ($tables -and $tables -match "Tables_in_jargas_apbn") {
        Write-Host "✅ Tabel database ditemukan:" -ForegroundColor Green
        Write-Host $tables -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Belum ada tabel atau database masih kosong" -ForegroundColor Yellow
        Write-Host "   Migration mungkin masih berjalan atau perlu dijalankan manual" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa verifikasi tabel (mungkin migration masih berjalan)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 9: Cek health endpoint..." -ForegroundColor Green
$healthCmd = "ssh ${Username}@${ServerIP} 'curl -s http://localhost:8001/health || curl -s http://localhost/api/v1/health'"
try {
    $health = Invoke-Expression $healthCmd
    if ($health -match "ok" -or $health -match "healthy") {
        Write-Host "✅ Health check passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Health check response: $health" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Health check gagal (backend mungkin masih starting)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Cek log backend untuk memastikan migration berhasil:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose --env-file .env logs backend --tail 100'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Jika migration belum berjalan, jalankan manual:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose --env-file .env exec backend alembic upgrade head'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Verifikasi aplikasi:" -ForegroundColor White
Write-Host "   - Frontend: http://jargas.ptkiansantang.com" -ForegroundColor Gray
Write-Host "   - Backend: http://jargas.ptkiansantang.com/api/v1/health" -ForegroundColor Gray
Write-Host ""

