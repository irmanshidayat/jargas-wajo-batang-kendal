# Script untuk fix kolom created_by di database development
# Menjalankan migration yang menambahkan kolom created_by ke tabel users

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal-dev"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fix Created By Column - Development" -ForegroundColor Cyan
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
Write-Host "   Environment: Development" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Lanjutkan fix created_by column? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Fix dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Cek status migration..." -ForegroundColor Green
$checkCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose -f docker-compose.dev.yml --env-file .env.dev exec -T backend alembic current'"
try {
    $current = Invoke-Expression $checkCmd
    Write-Host "Current migration:" -ForegroundColor Cyan
    Write-Host $current -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Tidak bisa cek migration status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Jalankan migration untuk menambahkan kolom created_by..." -ForegroundColor Green
$migrateCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose -f docker-compose.dev.yml --env-file .env.dev exec -T backend alembic upgrade head'"
try {
    Invoke-Expression $migrateCmd
    Write-Host "✅ Migration berhasil dijalankan" -ForegroundColor Green
} catch {
    Write-Host "❌ Migration gagal!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Verifikasi kolom created_by..." -ForegroundColor Green
$verifyCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose -f docker-compose.dev.yml --env-file .env.dev exec -T mysql mysql -u root -padmin123 jargas_apbn_dev -e \"DESCRIBE users;\" 2>/dev/null | grep created_by'"
try {
    $result = Invoke-Expression $verifyCmd
    if ($result -match "created_by") {
        Write-Host "✅ Kolom created_by sudah ada di tabel users" -ForegroundColor Green
        Write-Host $result -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Kolom created_by belum terdeteksi" -ForegroundColor Yellow
        Write-Host "   Coba restart backend container" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa verifikasi kolom" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Restart backend container..." -ForegroundColor Green
$restartCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose -f docker-compose.dev.yml --env-file .env.dev restart backend'"
try {
    Invoke-Expression $restartCmd
    Write-Host "✅ Backend container di-restart" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Restart gagal, coba manual" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fix Created By Column Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host "1. Coba buat akun admin lagi" -ForegroundColor White
Write-Host "2. Jika masih error, cek log backend:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose -f docker-compose.dev.yml --env-file .env.dev logs backend --tail 50'" -ForegroundColor Gray
Write-Host ""

