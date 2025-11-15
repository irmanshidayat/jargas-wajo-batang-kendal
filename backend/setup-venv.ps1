# Script Setup Virtual Environment untuk Backend (Tanpa Docker)
# Jalankan script ini untuk setup virtual environment dan install dependencies

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Virtual Environment - Backend" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check Python version
Write-Host "Step 1: Memeriksa Python..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python tidak ditemukan!" -ForegroundColor Red
    Write-Host "   Install Python 3.11 atau lebih tinggi dari https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# Check Python version number
$versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
if ($versionMatch) {
    $majorVersion = [int]$matches[1]
    $minorVersion = [int]$matches[2]
    if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 11)) {
        Write-Host "⚠️  Python 3.11 atau lebih tinggi direkomendasikan" -ForegroundColor Yellow
        Write-Host "   Versi saat ini: Python $majorVersion.$minorVersion" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Step 2: Setup Virtual Environment..." -ForegroundColor Green

# Check if venv already exists
$venvPath = Join-Path $scriptPath "venv"
if (Test-Path $venvPath) {
    Write-Host "⚠️  Virtual environment sudah ada di: $venvPath" -ForegroundColor Yellow
    $recreate = Read-Host "   Hapus dan buat ulang? (y/n)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Write-Host "   Menghapus virtual environment lama..." -ForegroundColor Gray
        Remove-Item -Path $venvPath -Recurse -Force
        Write-Host "✅ Virtual environment lama dihapus" -ForegroundColor Green
    } else {
        Write-Host "   Menggunakan virtual environment yang sudah ada" -ForegroundColor Gray
    }
}

# Create venv if not exists
if (-not (Test-Path $venvPath)) {
    Write-Host "   Membuat virtual environment..." -ForegroundColor Gray
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Gagal membuat virtual environment!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment dibuat" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 3: Mengaktifkan Virtual Environment..." -ForegroundColor Green
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "❌ Script aktivasi tidak ditemukan!" -ForegroundColor Red
    exit 1
}

# Activate venv
& $activateScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Gagal mengaktifkan virtual environment!" -ForegroundColor Red
    Write-Host "   Jika error tentang execution policy, jalankan:" -ForegroundColor Yellow
    Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Virtual environment diaktifkan" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Upgrade pip..." -ForegroundColor Green
python -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: Gagal upgrade pip, melanjutkan..." -ForegroundColor Yellow
} else {
    Write-Host "✅ pip di-upgrade" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 5: Install Dependencies..." -ForegroundColor Green
$requirementsPath = Join-Path $scriptPath "requirements.txt"

if (-not (Test-Path $requirementsPath)) {
    Write-Host "❌ File requirements.txt tidak ditemukan!" -ForegroundColor Red
    exit 1
}

Write-Host "   Menginstall dependencies dari requirements.txt..." -ForegroundColor Gray
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Gagal install dependencies!" -ForegroundColor Red
    Write-Host "   Periksa error di atas dan pastikan:" -ForegroundColor Yellow
    Write-Host "   - MySQL development libraries terinstall (untuk pymysql)" -ForegroundColor Yellow
    Write-Host "   - Koneksi internet stabil" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Dependencies terinstall" -ForegroundColor Green

Write-Host ""
Write-Host "Step 6: Verifikasi Instalasi..." -ForegroundColor Green
$packages = @("fastapi", "uvicorn", "sqlalchemy", "pymysql", "alembic")
$allInstalled = $true

foreach ($package in $packages) {
    $result = pip show $package 2>&1
    if ($LASTEXITCODE -eq 0) {
        $version = ($result | Select-String "Version:").ToString().Replace("Version:", "").Trim()
        Write-Host "   ✅ $package ($version)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $package tidak terinstall" -ForegroundColor Red
        $allInstalled = $false
    }
}

if (-not $allInstalled) {
    Write-Host ""
    Write-Host "⚠️  Beberapa package tidak terinstall dengan benar" -ForegroundColor Yellow
    Write-Host "   Coba jalankan: pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Virtual Environment Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Setup file .env:" -ForegroundColor White
Write-Host "   - Copy .env.dev dari root project ke backend/.env (opsional)" -ForegroundColor Gray
Write-Host "   - Atau buat file .env di root project dengan konfigurasi database XAMPP" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Pastikan XAMPP MySQL berjalan:" -ForegroundColor White
Write-Host "   - Start MySQL di XAMPP Control Panel" -ForegroundColor Gray
Write-Host "   - Pastikan database sudah dibuat (jargas_apbn atau jargas_apbn_dev)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Jalankan backend:" -ForegroundColor White
Write-Host "   .\run-local.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Untuk mengaktifkan virtual environment di terminal baru:" -ForegroundColor Cyan
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""

