# Script untuk setup environment variables Production
# Jalankan script ini untuk membuat file .env production dari template

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Environment Variables - PRODUCTION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendPath = Join-Path $rootPath "backend"

# Step 1: Setup root .env (Production)
Write-Host "Step 1: Setup .env di root (Production)..." -ForegroundColor Green
$rootEnvPath = Join-Path $rootPath ".env"
$rootEnvExamplePath = Join-Path $rootPath ".env.example"

if (-not (Test-Path $rootEnvExamplePath)) {
    Write-Host "⚠️  File .env.example tidak ditemukan di root!" -ForegroundColor Yellow
    Write-Host "   Membuat template .env.example..." -ForegroundColor Yellow
    
    $envContent = @"
# ============================================
# JARGAS APBN - Docker Compose Environment Variables (PRODUCTION)
# ============================================
# Copy file ini ke .env dan sesuaikan nilai-nilainya
# Jangan commit file .env ke repository!
# 
# Untuk Production: jargas.ptkiansantang.com

# ============================================
# SECURITY CONFIGURATION
# ============================================
# Generate SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))"
# WAJIB: Generate secret key yang berbeda untuk production!
SECRET_KEY=your-production-secret-key-here

# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_NAME=jargas_apbn

# ============================================
# APPLICATION CONFIGURATION
# ============================================
# Production: DEBUG harus False
DEBUG=False

# ============================================
# SERVER CONFIGURATION
# ============================================
# Backend tanpa Docker akan berjalan di port ini
# Production: 8010 (sesuai standar deployment)
HOST=0.0.0.0
PORT=8010

# ============================================
# CORS CONFIGURATION
# ============================================
# Format: comma-separated tanpa spasi
# Production: domain production dan frontend Docker (jika digunakan)
# Frontend Docker: http://localhost:8900 (sesuai standar deployment)
CORS_ORIGINS=https://jargas.ptkiansantang.com,http://localhost:8900

# ============================================
# FRONTEND DOCKER CONFIGURATION (Optional)
# ============================================
# Port untuk frontend Docker container (jika menggunakan Docker)
# Default: 8080
# Hanya diperlukan jika menggunakan docker-compose.frontend.yml
FRONTEND_PORT_MAPPED=8900

# ============================================
# TIMEZONE
# ============================================
TZ=Asia/Jakarta
"@
    Set-Content -Path $rootEnvExamplePath -Value $envContent
    Write-Host "✅ File .env.example dibuat" -ForegroundColor Green
}

if (-not (Test-Path $rootEnvPath)) {
    Copy-Item $rootEnvExamplePath $rootEnvPath
    Write-Host "✅ File .env dibuat dari .env.example" -ForegroundColor Green
    Write-Host "⚠️  PENTING: Edit file .env dan sesuaikan nilai-nilainya!" -ForegroundColor Yellow
    Write-Host "   - Generate SECRET_KEY yang unik" -ForegroundColor Yellow
    Write-Host "   - Set DB_PASSWORD yang kuat" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  File .env sudah ada, skip..." -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Setup backend/.env (Production)
Write-Host "Step 2: Setup backend/.env (Production)..." -ForegroundColor Green
$backendEnvPath = Join-Path $backendPath ".env"
$backendEnvExamplePath = Join-Path $backendPath "env.example"

if (-not (Test-Path $backendEnvExamplePath)) {
    Write-Host "❌ File backend/env.example tidak ditemukan!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $backendEnvPath)) {
    Copy-Item $backendEnvExamplePath $backendEnvPath
    Write-Host "✅ File backend/.env dibuat dari env.example" -ForegroundColor Green
    Write-Host "⚠️  PENTING: Edit file backend/.env dan sesuaikan nilai-nilainya!" -ForegroundColor Yellow
    Write-Host "   - Set DB_PASSWORD yang kuat" -ForegroundColor Yellow
    Write-Host "   - Set SECRET_KEY sama dengan root .env" -ForegroundColor Yellow
    Write-Host "   - Set DEBUG=False untuk production" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  File backend/.env sudah ada, skip..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Environment Production Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host "1. Edit file .env di root dan backend/.env" -ForegroundColor White
Write-Host "2. Generate SECRET_KEY yang unik untuk production" -ForegroundColor White
Write-Host "3. Set password database yang kuat" -ForegroundColor White
Write-Host "4. Pastikan DEBUG=False untuk production" -ForegroundColor White
Write-Host ""

