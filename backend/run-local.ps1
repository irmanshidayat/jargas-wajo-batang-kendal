# Script untuk menjalankan Backend tanpa Docker (Development Lokal)
# Script ini akan mengaktifkan virtual environment dan menjalankan backend

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Jalankan Backend - Development Lokal" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if venv exists
$venvPath = Join-Path $scriptPath "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "❌ Virtual environment tidak ditemukan!" -ForegroundColor Red
    Write-Host "   Jalankan setup terlebih dahulu:" -ForegroundColor Yellow
    Write-Host "   .\setup-venv.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate venv
Write-Host "Mengaktifkan virtual environment..." -ForegroundColor Green
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "❌ Script aktivasi tidak ditemukan!" -ForegroundColor Red
    exit 1
}

& $activateScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Gagal mengaktifkan virtual environment!" -ForegroundColor Red
    Write-Host "   Jika error tentang execution policy, jalankan:" -ForegroundColor Yellow
    Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists (optional, settings will use defaults or root .env)
$rootEnvDev = Join-Path (Split-Path -Parent $scriptPath) ".env.dev"
$rootEnv = Join-Path (Split-Path -Parent $scriptPath) ".env"

if (-not (Test-Path $rootEnvDev) -and -not (Test-Path $rootEnv)) {
    Write-Host ""
    Write-Host "⚠️  File .env tidak ditemukan di root project" -ForegroundColor Yellow
    Write-Host "   Backend akan menggunakan default settings atau environment variables" -ForegroundColor Yellow
    Write-Host "   Untuk konfigurasi database XAMPP, buat file .env.dev di root project" -ForegroundColor Yellow
    Write-Host ""
}

# Check database connection (optional)
Write-Host "Memeriksa konfigurasi..." -ForegroundColor Green
Write-Host "   Backend akan berjalan di: http://localhost:8000" -ForegroundColor Gray
Write-Host "   API Documentation: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

# Run the application
Write-Host "Menjalankan Backend..." -ForegroundColor Green
Write-Host "   Tekan Ctrl+C untuk menghentikan" -ForegroundColor Gray
Write-Host ""

python run.py

