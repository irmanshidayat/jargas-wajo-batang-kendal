#!/bin/bash
# Script Setup Domain Otomatis - JALANKAN DI SERVER SSH
# Setup domain jargas.ptkiansantang.com untuk Jargas APBN

set -e

DOMAIN="jargas.ptkiansantang.com"
SERVER_IP="72.61.142.109"

echo "=========================================="
echo "🌐 Setup Domain untuk Jargas APBN"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
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
echo "1. Update konfigurasi nginx dengan domain"
echo "2. Test konfigurasi nginx"
echo "3. Reload nginx"
echo "4. Test akses domain"
echo "5. Informasi setup DNS dan SSL"
echo ""

# Step 1: Copy config
echo "📝 Step 1: Update konfigurasi nginx..."
$SUDO cp "$CONFIG_FILE" /etc/nginx/sites-available/jargas
echo "   ✅ Konfigurasi diupdate"

# Step 2: Create symlink (if not exists)
if [ ! -L "/etc/nginx/sites-enabled/jargas" ]; then
    echo ""
    echo "🔗 Step 1.5: Buat symbolic link..."
    $SUDO ln -s /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas
    echo "   ✅ Symlink created"
fi

# Step 3: Test config
echo ""
echo "🧪 Step 2: Test konfigurasi nginx..."
if $SUDO nginx -t; then
    echo "   ✅ Konfigurasi valid"
else
    echo "   ❌ Konfigurasi error!"
    exit 1
fi

# Step 4: Reload nginx
echo ""
echo "🔄 Step 3: Reload nginx..."
$SUDO systemctl reload nginx
echo "   ✅ Nginx reloaded"

# Step 5: Check status
echo ""
echo "📊 Step 4: Check nginx status..."
if $SUDO systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx is running"
    
    # Test health endpoint
    echo ""
    echo "🏥 Step 5: Testing health endpoint..."
    sleep 2
    if curl -s -H "Host: $DOMAIN" http://localhost/health > /dev/null; then
        echo "   ✅ Health check passed"
    else
        echo "   ⚠️  Health check failed (container mungkin belum ready)"
    fi
    
    echo ""
    echo "=========================================="
    echo "✅ Setup Domain Selesai!"
    echo "=========================================="
    echo ""
    echo "📋 Langkah Selanjutnya:"
    echo ""
    echo "1. Setup DNS Record di penyedia hosting domain:" -ForegroundColor White
    echo "   Type: A"
    echo "   Name: jargas"
    echo "   Value: $SERVER_IP"
    echo "   TTL: 3600"
    echo ""
    echo "2. Tunggu DNS propagation (5-15 menit, maksimal 48 jam)"
    echo ""
    echo "3. Test DNS dari lokal:"
    echo "   nslookup $DOMAIN"
    echo "   ping $DOMAIN"
    echo ""
    echo "4. Setup SSL dengan Let's Encrypt (setelah DNS ready):"
    echo "   $SUDO apt update"
    echo "   $SUDO apt install certbot python3-certbot-nginx -y"
    echo "   $SUDO certbot --nginx -d $DOMAIN"
    echo ""
    echo "5. Test akses domain:"
    echo "   http://$DOMAIN"
    echo "   http://$DOMAIN/health"
    echo ""
else
    echo "   ❌ Nginx tidak berjalan!"
    $SUDO systemctl status nginx
    exit 1
fi

