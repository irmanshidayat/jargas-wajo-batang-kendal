#!/bin/bash

# Script untuk setup Nginx Host sebagai Reverse Proxy
# Best Practice untuk Production Deployment

set -e

echo "🚀 Setup Nginx Host untuk Jargas APBN"
echo "======================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Silakan jalankan dengan sudo"
    exit 1
fi

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx tidak terinstall. Install dulu dengan: apt install nginx -y"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if config file exists
CONFIG_FILE="$SCRIPT_DIR/jargas.conf"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ File konfigurasi tidak ditemukan: $CONFIG_FILE"
    exit 1
fi

echo ""
echo "📋 Langkah-langkah setup:"
echo "1. Copy konfigurasi ke /etc/nginx/sites-available/"
echo "2. Buat symbolic link ke /etc/nginx/sites-enabled/"
echo "3. Backup default config (jika ada)"
echo "4. Test konfigurasi nginx"
echo "5. Reload nginx"
echo ""

# Backup existing config if exists
if [ -f "/etc/nginx/sites-available/jargas" ]; then
    echo "⚠️  Konfigurasi jargas sudah ada, membuat backup..."
    cp /etc/nginx/sites-available/jargas /etc/nginx/sites-available/jargas.backup.$(date +%Y%m%d_%H%M%S)
fi

# Copy config file
echo "📝 Copy konfigurasi..."
cp "$CONFIG_FILE" /etc/nginx/sites-available/jargas

# Create symbolic link
if [ -L "/etc/nginx/sites-enabled/jargas" ]; then
    echo "⚠️  Symbolic link sudah ada, menghapus..."
    rm /etc/nginx/sites-enabled/jargas
fi

echo "🔗 Membuat symbolic link..."
ln -s /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas

# Backup and remove default config (optional)
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    read -p "Hapus konfigurasi default nginx? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Backup default config..."
        cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)
        rm /etc/nginx/sites-enabled/default
        echo "✅ Default config dihapus"
    fi
fi

# Test nginx configuration
echo ""
echo "🧪 Test konfigurasi nginx..."
if nginx -t; then
    echo "✅ Konfigurasi nginx valid"
else
    echo "❌ Konfigurasi nginx tidak valid!"
    exit 1
fi

# Reload nginx
echo ""
echo "🔄 Reload nginx..."
systemctl reload nginx

# Check nginx status
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx berhasil di-reload"
else
    echo "❌ Nginx tidak berjalan!"
    systemctl status nginx
    exit 1
fi

echo ""
echo "✅ Setup selesai!"
echo ""
echo "📋 Langkah selanjutnya:"
echo "1. Edit /etc/nginx/sites-available/jargas dan ubah 'server_name _;' menjadi domain Anda"
echo "2. Test dengan: curl http://localhost/health"
echo "3. Setup SSL dengan: sudo certbot --nginx -d your-domain.com"
echo ""
echo "📖 Dokumentasi lengkap: nginx-host/README.md"
echo ""

