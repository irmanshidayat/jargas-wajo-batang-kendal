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
Write-Host "Step 2: Jalankan migration ke head..." -ForegroundColor Green
$migrateCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T backend alembic upgrade head'"
try {
    $result = Invoke-Expression $migrateCmd
    Write-Host $result -ForegroundColor Gray
    Write-Host "✅ Migration berhasil" -ForegroundColor Green
} catch {
    Write-Host "❌ Migration gagal!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Verifikasi migration..." -ForegroundColor Green
$verifyCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T backend alembic current'"
try {
    $verify = Invoke-Expression $verifyCmd
    Write-Host $verify -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Tidak bisa verifikasi" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Verifikasi tabel database..." -ForegroundColor Green
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

