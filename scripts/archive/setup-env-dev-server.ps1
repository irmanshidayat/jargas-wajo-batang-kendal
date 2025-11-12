# PowerShell Script untuk Setup Environment Variables di Server Development
# Script ini akan setup file .env yang diperlukan di server

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal-dev"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔧 Setup Environment Variables - Development" -ForegroundColor Cyan
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

$confirm = Read-Host "Lanjutkan setup environment variables? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Setup dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Upload script setup ke server..." -ForegroundColor Green

# Check if script exists locally
$localScript = "scripts/setup-env-dev-server.sh"
if (-not (Test-Path $localScript)) {
    Write-Host "❌ Script tidak ditemukan: $localScript" -ForegroundColor Red
    exit 1
}

# Upload script to server
$remoteScriptPath = "~/setup-env-dev-server.sh"
try {
    $scpCmd = "scp $localScript ${Username}@${ServerIP}:$remoteScriptPath"
    Invoke-Expression $scpCmd
    Write-Host "✅ Script berhasil di-upload" -ForegroundColor Green
} catch {
    Write-Host "❌ Upload script gagal!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Menjalankan script setup di server..." -ForegroundColor Green

# Make script executable and run
$runCmd = "ssh ${Username}@${ServerIP} 'chmod +x $remoteScriptPath && bash $remoteScriptPath'"
try {
    Invoke-Expression $runCmd
    Write-Host "✅ Setup environment variables berhasil" -ForegroundColor Green
} catch {
    Write-Host "❌ Setup gagal!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Verifikasi file .env..." -ForegroundColor Green

# Verify .env file exists
$verifyCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && test -f .env && echo \"✅ .env exists\" && grep SECRET_KEY .env || echo \"❌ SECRET_KEY not found\"'"
try {
    $result = Invoke-Expression $verifyCmd
    Write-Host $result -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Verifikasi gagal" -ForegroundColor Yellow
}

# Verify backend/.env file exists
$verifyBackendCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && test -f backend/.env && echo \"✅ backend/.env exists\" || echo \"❌ backend/.env not found\"'"
try {
    $result = Invoke-Expression $verifyBackendCmd
    Write-Host $result -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Verifikasi backend/.env gagal" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Environment Variables Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Langkah selanjutnya:" -ForegroundColor Yellow
Write-Host "   docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor White
Write-Host ""
Write-Host "   Atau jalankan dari Windows:" -ForegroundColor Yellow
Write-Host "   .\scripts\deploy-dev.ps1" -ForegroundColor White
Write-Host ""

