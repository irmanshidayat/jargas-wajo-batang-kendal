#!/bin/bash
# Script Setup SSL Certificate dengan Let's Encrypt
# JALANKAN DI SERVER SSH setelah domain sudah pointing dan nginx config sudah terpasang

set -e

DOMAIN="jargas.ptkiansantang.com"
EMAIL="admin@ptkiansantang.com"  # Ganti dengan email Anda untuk Let's Encrypt

echo "=========================================="
echo "🔒 Setup SSL Certificate untuk Jargas APBN"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Script ini memerlukan sudo privileges"
    echo "   Jalankan dengan: sudo bash setup-ssl.sh"
    exit 1
fi

# Prerequisites check
echo "📋 Checking prerequisites..."
echo ""

# Check if domain is accessible
echo "1. Checking domain accessibility..."
if curl -s --max-time 5 "http://$DOMAIN" > /dev/null 2>&1; then
    echo "   ✅ Domain $DOMAIN dapat diakses"
else
    echo "   ❌ Domain $DOMAIN tidak dapat diakses"
    echo "   Pastikan:"
    echo "   - DNS A record sudah pointing ke server"
    echo "   - Port 80 terbuka di firewall"
    echo "   - Nginx sudah running dan config sudah terpasang"
    exit 1
fi

# Check if nginx is running
echo ""
echo "2. Checking nginx status..."
if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx is running"
else
    echo "   ❌ Nginx tidak berjalan!"
    echo "   Jalankan: sudo systemctl start nginx"
    exit 1
fi

# Check if nginx config exists
echo ""
echo "3. Checking nginx configuration..."
if [ -f "/etc/nginx/sites-available/jargas" ]; then
    echo "   ✅ Nginx config found"
else
    echo "   ❌ Nginx config tidak ditemukan"
    echo "   Jalankan setup-domain.sh terlebih dahulu"
    exit 1
fi

# Install certbot if not installed
echo ""
echo "4. Checking certbot installation..."
if command -v certbot &> /dev/null; then
    echo "   ✅ Certbot sudah terinstall"
    CERTBOT_VERSION=$(certbot --version | head -n 1)
    echo "   Version: $CERTBOT_VERSION"
else
    echo "   ⚠️  Certbot belum terinstall"
    echo "   Installing certbot..."
    apt update
    apt install certbot python3-certbot-nginx -y
    echo "   ✅ Certbot installed"
fi

# Check if certificate already exists
echo ""
echo "5. Checking existing certificate..."
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "   ⚠️  Certificate sudah ada untuk domain $DOMAIN"
    echo "   Certificate info:"
    certbot certificates | grep -A 5 "$DOMAIN" || true
    echo ""
    read -p "   Apakah Anda ingin renew certificate? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Renewing certificate..."
        certbot renew --cert-name "$DOMAIN"
        echo "   ✅ Certificate renewed"
    else
        echo "   Skipping certificate generation"
        exit 0
    fi
else
    echo "   ℹ️  Certificate belum ada, akan dibuat baru"
fi

# Generate SSL certificate
echo ""
echo "6. Generating SSL certificate..."
echo "   Domain: $DOMAIN"
echo "   Email: $EMAIL"
echo ""
echo "   Certbot akan:"
echo "   - Generate SSL certificate dari Let's Encrypt"
echo "   - Update nginx config untuk HTTPS"
echo "   - Setup auto-renewal"
echo ""

# Run certbot
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "$EMAIL" --redirect

if [ $? -eq 0 ]; then
    echo "   ✅ SSL certificate berhasil dibuat!"
else
    echo "   ❌ Gagal membuat SSL certificate"
    echo "   Pastikan:"
    echo "   - Domain sudah pointing ke server (DNS A record)"
    echo "   - Port 80 dan 443 terbuka di firewall"
    echo "   - Nginx config sudah terpasang"
    exit 1
fi

# Test nginx config
echo ""
echo "7. Testing nginx configuration..."
if nginx -t; then
    echo "   ✅ Nginx config valid"
else
    echo "   ❌ Nginx config error!"
    exit 1
fi

# Reload nginx
echo ""
echo "8. Reloading nginx..."
systemctl reload nginx
echo "   ✅ Nginx reloaded"

# Test SSL certificate
echo ""
echo "9. Testing SSL certificate..."
sleep 2
if curl -s --max-time 5 "https://$DOMAIN" > /dev/null 2>&1; then
    echo "   ✅ HTTPS berhasil diakses"
else
    echo "   ⚠️  HTTPS belum dapat diakses (mungkin perlu beberapa saat)"
fi

# Test auto-renewal
echo ""
echo "10. Testing auto-renewal..."
if certbot renew --dry-run > /dev/null 2>&1; then
    echo "   ✅ Auto-renewal setup berhasil"
else
    echo "   ⚠️  Auto-renewal test gagal (tapi mungkin masih OK)"
fi

# Summary
echo ""
echo "=========================================="
echo "✅ SSL Setup Selesai!"
echo "=========================================="
echo ""
echo "📋 Informasi:"
echo "   - Domain: $DOMAIN"
echo "   - HTTPS: https://$DOMAIN"
echo "   - Certificate: /etc/letsencrypt/live/$DOMAIN/"
echo "   - Auto-renewal: Sudah diaktifkan"
echo ""
echo "🔍 Verifikasi:"
echo "   - Test HTTPS: curl -I https://$DOMAIN"
echo "   - Check certificate: sudo certbot certificates"
echo "   - Test renewal: sudo certbot renew --dry-run"
echo ""
echo "📝 Catatan:"
echo "   - Certificate akan auto-renew setiap 90 hari"
echo "   - Certificate disimpan di /etc/letsencrypt/live/$DOMAIN/"
echo "   - Nginx config sudah diupdate otomatis oleh certbot"
echo ""

