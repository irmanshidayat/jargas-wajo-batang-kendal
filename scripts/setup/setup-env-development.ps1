# Script untuk setup environment variables Development
# Jalankan script ini untuk membuat file .env development dari template

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Environment Variables - DEVELOPMENT" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendPath = Join-Path $rootPath "backend"

# Step 1: Setup root .env.dev (Development)
Write-Host "Step 1: Setup .env.dev di root (Development)..." -ForegroundColor Green
$rootEnvDevPath = Join-Path $rootPath ".env.dev"
$rootEnvDevExamplePath = Join-Path $rootPath ".env.dev.example"

if (-not (Test-Path $rootEnvDevExamplePath)) {
    Write-Host "⚠️  File .env.dev.example tidak ditemukan di root!" -ForegroundColor Yellow
    Write-Host "   Membuat template .env.dev.example..." -ForegroundColor Yellow
    
    $envContent = @"
# ============================================
# JARGAS APBN - Docker Compose Environment Variables (DEVELOPMENT)
# ============================================
# Copy file ini ke .env.dev dan sesuaikan nilai-nilainya
# Jangan commit file .env.dev ke repository!
# 
# Untuk Development: devjargas.ptkiansantang.com

# ============================================
# SECURITY CONFIGURATION
# ============================================
# Generate SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))"
# WAJIB: Generate secret key yang berbeda dari production!
SECRET_KEY=your-development-secret-key-here

# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_NAME=jargas_apbn_dev

# ============================================
# APPLICATION CONFIGURATION
# ============================================
# Development: DEBUG boleh True untuk debugging
DEBUG=True

# ============================================
# CORS CONFIGURATION
# ============================================
# Format: comma-separated tanpa spasi
# Development: domain development, frontend Docker, dan dev server
# Frontend Docker default: http://localhost:8080
# Vite dev server default: http://localhost:5173
CORS_ORIGINS=https://devjargas.ptkiansantang.com,http://localhost:8080,http://localhost:5173,http://localhost:3000

# ============================================
# FRONTEND DOCKER CONFIGURATION (Optional)
# ============================================
# Port untuk frontend Docker container (jika menggunakan Docker)
# Default: 8080
# Hanya diperlukan jika menggunakan docker-compose.frontend.yml
FRONTEND_PORT_MAPPED=8080

# ============================================
# TIMEZONE
# ============================================
TZ=Asia/Jakarta
"@
    Set-Content -Path $rootEnvDevExamplePath -Value $envContent
    Write-Host "✅ File .env.dev.example dibuat" -ForegroundColor Green
}

if (-not (Test-Path $rootEnvDevPath)) {
    Copy-Item $rootEnvDevExamplePath $rootEnvDevPath
    Write-Host "✅ File .env.dev dibuat dari .env.dev.example" -ForegroundColor Green
    Write-Host "⚠️  PENTING: Edit file .env.dev dan sesuaikan nilai-nilainya!" -ForegroundColor Yellow
    Write-Host "   - Generate SECRET_KEY yang unik (berbeda dari production)" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  File .env.dev sudah ada, skip..." -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Setup backend/.env.dev (Development)
Write-Host "Step 2: Setup backend/.env.dev (Development)..." -ForegroundColor Green
$backendEnvDevPath = Join-Path $backendPath ".env.dev"
$backendEnvDevExamplePath = Join-Path $backendPath ".env.dev.example"

if (-not (Test-Path $backendEnvDevExamplePath)) {
    Write-Host "⚠️  File backend/.env.dev.example tidak ditemukan!" -ForegroundColor Yellow
    Write-Host "   Membuat template .env.dev.example..." -ForegroundColor Yellow
    
    $envContent = @"
# ============================================
# JARGAS APBN - Backend Environment Variables (DEVELOPMENT)
# ============================================
# Copy file ini ke .env.dev dan sesuaikan nilai-nilainya
# Jangan commit file .env.dev ke repository!
# 
# Untuk Development Environment: devjargas.ptkiansantang.com

# ============================================
# DATABASE CONFIGURATION
# ============================================
# Untuk Docker: DB_HOST=mysql, DB_PASSWORD=admin123
# Untuk Development XAMPP: DB_HOST=localhost, DB_PASSWORD bisa kosong
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=admin123
DB_NAME=jargas_apbn_dev

# ============================================
# SECURITY CONFIGURATION
# ============================================
# Generate SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))"
# WAJIB: Generate secret key yang berbeda dari production!
# Harus sama dengan SECRET_KEY di root .env.dev
SECRET_KEY=your-development-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# APPLICATION CONFIGURATION
# ============================================
APP_NAME=Jargas APBN API (Dev)
APP_VERSION=1.0.0-dev
# Development: DEBUG boleh True untuk debugging
DEBUG=True

# ============================================
# SERVER CONFIGURATION
# ============================================
# Untuk Development: HOST=127.0.0.1
# Untuk Docker: HOST=0.0.0.0
HOST=0.0.0.0
PORT=8000

# ============================================
# CORS CONFIGURATION
# ============================================
# Format: comma-separated tanpa spasi
# Development: termasuk localhost untuk testing
CORS_ORIGINS=https://devjargas.ptkiansantang.com,http://localhost:8082,http://localhost:5173

# ============================================
# FILE UPLOAD CONFIGURATION
# ============================================
UPLOAD_DIR=uploads/evidence
MAX_FILE_SIZE=5242880
# Format: comma-separated tanpa spasi
ALLOWED_FILE_TYPES=image/jpeg,image/jpg,image/png,application/pdf

# ============================================
# DATABASE MIGRATION CONFIGURATION
# ============================================
# Auto-migrate saat aplikasi startup
# True = otomatis migrate saat backend start (RECOMMENDED untuk development)
# False = manual migration (gunakan: docker-compose exec backend alembic upgrade head)
AUTO_MIGRATE=True
# Hanya migrate jika ada pending migration (True = recommended, lebih aman)
AUTO_MIGRATE_ONLY_IF_PENDING=True
# Migration Mode: "sequential" (default, recommended), "head" (fallback), "auto" (smart selection)
# sequential = upgrade satu per satu dengan validasi (paling aman)
# head = upgrade langsung ke head (fallback jika sequential gagal)
# auto = otomatis pilih mode terbaik
MIGRATION_MODE=sequential
# Validasi migration chain sebelum upgrade (True = recommended)
MIGRATION_VALIDATE_BEFORE_UPGRADE=True
# Stop migration jika ada error (True = recommended untuk safety)
MIGRATION_STOP_ON_ERROR=True
"@
    Set-Content -Path $backendEnvDevExamplePath -Value $envContent
    Write-Host "✅ File backend/.env.dev.example dibuat" -ForegroundColor Green
}

if (-not (Test-Path $backendEnvDevPath)) {
    Copy-Item $backendEnvDevExamplePath $backendEnvDevPath
    Write-Host "✅ File backend/.env.dev dibuat dari .env.dev.example" -ForegroundColor Green
    Write-Host "⚠️  PENTING: Edit file backend/.env.dev dan sesuaikan nilai-nilainya!" -ForegroundColor Yellow
    Write-Host "   - Set SECRET_KEY sama dengan root .env.dev" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  File backend/.env.dev sudah ada, skip..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Environment Development Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host "1. Edit file .env.dev di root dan backend/.env.dev" -ForegroundColor White
Write-Host "2. Generate SECRET_KEY yang unik untuk development" -ForegroundColor White
Write-Host "3. Pastikan SECRET_KEY sama antara root .env.dev dan backend/.env.dev" -ForegroundColor White
Write-Host ""

