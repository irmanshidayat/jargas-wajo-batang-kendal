#!/bin/bash
# Script Setup Otomatis Nginx Host - JALANKAN DI SERVER SSH

set -e

echo "=========================================="
echo "🚀 Setup Nginx Host untuk Jargas APBN"
echo "=========================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Menjalankan dengan sudo..."
    SUDO="sudo"
else
    SUDO=""
fi

# Get current directory
CURRENT_DIR=$(pwd)
CONFIG_FILE="$CURRENT_DIR/nginx-host/jargas.conf"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ File konfigurasi tidak ditemukan: $CONFIG_FILE"
    echo "   Pastikan Anda berada di direktori project root"
    exit 1
fi

echo "📋 Langkah-langkah:"
echo "1. Copy konfigurasi ke /etc/nginx/sites-available/"
echo "2. Buat symbolic link ke /etc/nginx/sites-enabled/"
echo "3. Backup default config (jika ada)"
echo "4. Test konfigurasi nginx"
echo "5. Reload nginx"
echo ""

# Step 1: Copy config
echo "📝 Step 1: Copy konfigurasi..."
$SUDO cp "$CONFIG_FILE" /etc/nginx/sites-available/jargas
echo "   ✅ Config copied to /etc/nginx/sites-available/jargas"

# Step 2: Create symlink
echo ""
echo "🔗 Step 2: Buat symbolic link..."
if [ -L "/etc/nginx/sites-enabled/jargas" ]; then
    echo "   ⚠️  Symlink sudah ada, menghapus..."
    $SUDO rm /etc/nginx/sites-enabled/jargas
fi
$SUDO ln -s /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas
echo "   ✅ Symlink created"

# Step 3: Backup and remove default
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    echo ""
    echo "📦 Step 3: Backup default config..."
    if [ -f "/etc/nginx/sites-available/default" ]; then
        $SUDO cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)
    fi
    $SUDO rm -f /etc/nginx/sites-enabled/default
    echo "   ✅ Default config removed"
fi

# Step 4: Test config
echo ""
echo "🧪 Step 4: Test konfigurasi nginx..."
if $SUDO nginx -t; then
    echo "   ✅ Nginx configuration is valid"
else
    echo "   ❌ Nginx configuration error!"
    exit 1
fi

# Step 5: Reload nginx
echo ""
echo "🔄 Step 5: Reload nginx..."
$SUDO systemctl reload nginx
echo "   ✅ Nginx reloaded"

# Step 6: Check status
echo ""
echo "📊 Step 6: Check nginx status..."
if $SUDO systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx is running"
    
    # Test health endpoint
    echo ""
    echo "🏥 Testing health endpoint..."
    if curl -s http://localhost/health > /dev/null; then
        echo "   ✅ Health check passed"
    else
        echo "   ⚠️  Health check failed (container mungkin belum ready)"
    fi
    
    echo ""
    echo "=========================================="
    echo "✅ Setup selesai!"
    echo "=========================================="
    echo ""
    echo "📋 Langkah selanjutnya:"
    echo ""
    echo "1. Edit domain (jika ada):"
    echo "   $SUDO nano /etc/nginx/sites-available/jargas"
    echo "   Ubah: server_name _; menjadi server_name your-domain.com;"
    echo ""
    echo "2. Test akses:"
    echo "   curl http://localhost/health"
    echo "   curl http://localhost/"
    echo ""
    echo "3. Setup SSL (jika ada domain):"
    echo "   $SUDO apt install certbot python3-certbot-nginx -y"
    echo "   $SUDO certbot --nginx -d your-domain.com"
    echo ""
    echo "4. Rebuild container frontend (untuk apply healthcheck fix):"
    echo "   docker-compose build frontend"
    echo "   docker-compose up -d frontend"
    echo ""
    echo "📖 Dokumentasi lengkap: SETUP_NGINX_HOST.md"
    echo ""
else
    echo "   ❌ Nginx tidak berjalan!"
    $SUDO systemctl status nginx
    exit 1
fi

