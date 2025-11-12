#!/bin/bash
# Script untuk setup environment variables di server development
# Jalankan di server: bash scripts/setup-env-dev-server.sh

set -e

PROJECT_PATH="~/jargas-wajo-batang-kendal-dev"
cd $PROJECT_PATH || { echo "❌ Folder tidak ditemukan: $PROJECT_PATH"; exit 1; }

echo "=========================================="
echo "🔧 Setup Environment Variables - Development"
echo "=========================================="
echo ""

# Step 1: Setup backend/.env
echo "Step 1: Setup backend/.env..."
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/env.example" ]; then
        cp backend/env.example backend/.env
        echo "✅ File backend/.env dibuat dari env.example"
        
        # Update untuk Docker environment
        sed -i 's/^DB_HOST=.*/DB_HOST=mysql/' backend/.env
        sed -i 's/^DB_PASSWORD=.*/DB_PASSWORD=admin123/' backend/.env
        sed -i 's/^DB_NAME=.*/DB_NAME=jargas_apbn_dev/' backend/.env
        sed -i 's/^HOST=.*/HOST=0.0.0.0/' backend/.env
        sed -i 's/^DEBUG=.*/DEBUG=True/' backend/.env
        
        echo "✅ backend/.env sudah dikonfigurasi untuk Docker"
    else
        echo "❌ File backend/env.example tidak ditemukan!"
        exit 1
    fi
else
    echo "⚠️  File backend/.env sudah ada, skip..."
fi

echo ""

# Step 2: Setup .env di root (untuk docker-compose variable substitution)
echo "Step 2: Setup .env di root project..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Docker Compose Environment Variables - Development
SECRET_KEY=n5TYLOYW-KO3hQfcNMBltRrPIwJS-lBQsMtDKFCFfJ4
DB_NAME=jargas_apbn_dev
DEBUG=True
CORS_ORIGINS=https://devjargas.ptkiansantang.com,http://localhost:8082
DB_PORT_MAPPED=3309
BACKEND_PORT_MAPPED=8002
FRONTEND_PORT_MAPPED=8082
ADMINER_PORT_MAPPED=18083
TZ=Asia/Jakarta
EOF
    echo "✅ File .env di root sudah dibuat"
else
    echo "⚠️  File .env di root sudah ada, menambahkan variabel yang belum ada..."
    
    # Check dan tambahkan SECRET_KEY jika belum ada
    if ! grep -q "^SECRET_KEY=" .env; then
        echo "SECRET_KEY=n5TYLOYW-KO3hQfcNMBltRrPIwJS-lBQsMtDKFCFfJ4" >> .env
        echo "✅ SECRET_KEY ditambahkan ke .env"
    fi
    
    # Check dan tambahkan DB_NAME jika belum ada
    if ! grep -q "^DB_NAME=" .env; then
        echo "DB_NAME=jargas_apbn_dev" >> .env
        echo "✅ DB_NAME ditambahkan ke .env"
    fi
fi

echo ""
echo "=========================================="
echo "✅ Setup Environment Variables Selesai!"
echo "=========================================="
echo ""
echo "📋 File yang dibuat/diperbarui:"
echo "   - backend/.env"
echo "   - .env (root)"
echo ""
echo "🧪 Verifikasi:"
echo "   cat backend/.env | grep -E 'DB_HOST|DB_NAME|SECRET_KEY'"
echo "   cat .env | grep SECRET_KEY"
echo ""
echo "🚀 Langkah selanjutnya:"
echo "   docker-compose -f docker-compose.dev.yml up -d"
echo ""

