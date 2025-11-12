# Script untuk menjalankan migration di server dari Windows
# Digunakan jika auto-migrate tidak berjalan atau perlu manual migration

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Jalankan Database Migration di Server" -ForegroundColor Cyan
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

$confirm = Read-Host "Lanjutkan migration? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Migration dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Cek status migration saat ini..." -ForegroundColor Green
$currentCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T backend alembic current'"
try {
    $current = Invoke-Expression $currentCmd
    Write-Host $current -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Belum ada migration yang dijalankan atau error" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Cek apakah backend container running..." -ForegroundColor Green
$checkBackendCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose ps backend'"
try {
    $backendStatus = Invoke-Expression $checkBackendCmd
    if ($backendStatus -match "Up" -or $backendStatus -match "running") {
        Write-Host "✅ Backend container running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backend container tidak running, mencoba start..." -ForegroundColor Yellow
        $startCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose up -d backend'"
        Invoke-Expression $startCmd
        Write-Host "⏳ Menunggu backend ready (30 detik)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek status backend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Jalankan migration ke head..." -ForegroundColor Green
$migrateCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T backend alembic upgrade head'"
try {
    Write-Host "Menjalankan migration (ini mungkin memakan waktu beberapa menit)..." -ForegroundColor Gray
    $result = Invoke-Expression $migrateCmd 2>&1
    Write-Host $result -ForegroundColor Gray
    
    # Cek apakah ada error
    if ($LASTEXITCODE -eq 0 -or $result -match "INFO" -or $result -match "Running upgrade") {
        Write-Host "✅ Migration berhasil" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Migration mungkin ada warning, cek output di atas" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Migration gagal!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Coba jalankan manual di server:" -ForegroundColor Yellow
    Write-Host "   ssh ${Username}@${ServerIP}" -ForegroundColor Gray
    Write-Host "   cd $ProjectPath" -ForegroundColor Gray
    Write-Host "   docker-compose exec backend alembic upgrade head" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "Step 4: Verifikasi migration..." -ForegroundColor Green
$verifyCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T backend alembic current'"
try {
    $verify = Invoke-Expression $verifyCmd
    Write-Host $verify -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Tidak bisa verifikasi" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 5: Verifikasi tabel database..." -ForegroundColor Green
$tablesCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T mysql mysql -u root -padmin123 jargas_apbn -e \"SHOW TABLES;\" 2>/dev/null'"
try {
    $tables = Invoke-Expression $tablesCmd
    if ($tables) {
        Write-Host "✅ Tabel database:" -ForegroundColor Green
        Write-Host $tables -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Tidak ada tabel atau database masih kosong" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa verifikasi tabel" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Migration selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

