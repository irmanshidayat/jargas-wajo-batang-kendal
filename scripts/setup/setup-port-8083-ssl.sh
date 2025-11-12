#!/bin/bash
# Script Setup Port 8083 dan SSL untuk Adminer - Development Environment
# Domain: devjargas.ptkiansantang.com
# Jalankan di server dengan: bash scripts/setup-port-8083-ssl.sh

set -e

DOMAIN="devjargas.ptkiansantang.com"
PORT="8083"

echo "=========================================="
echo "🔒 Setup Port 8083 dan SSL Certificate"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
echo "Port: $PORT"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Script ini memerlukan akses root/sudo"
    echo "   Jalankan dengan: sudo bash scripts/setup-port-8083-ssl.sh"
    exit 1
fi

SUDO=""

# Step 1: Setup Firewall (UFW)
echo "🔥 Step 1: Setup Firewall (UFW) untuk port $PORT..."
echo ""

# Check if UFW is installed
if ! command -v ufw &> /dev/null; then
    echo "   ⚠️  UFW tidak terinstall, menginstall..."
    apt update
    apt install ufw -y
fi

# Check UFW status
if ufw status | grep -q "Status: active"; then
    echo "   ✅ UFW sudah aktif"
else
    echo "   ⚠️  UFW belum aktif, mengaktifkan..."
    ufw --force enable
fi

# Check if port 8083 is already allowed
if ufw status | grep -q "$PORT"; then
    echo "   ✅ Port $PORT sudah diizinkan di firewall"
else
    echo "   📝 Menambahkan port $PORT ke firewall..."
    ufw allow $PORT/tcp comment "Adminer HTTPS - Development"
    echo "   ✅ Port $PORT berhasil ditambahkan"
fi

# Also ensure ports 80, 443 are open (for Let's Encrypt)
echo ""
echo "   📝 Memastikan port 80 dan 443 terbuka (untuk Let's Encrypt)..."
ufw allow 80/tcp comment "HTTP - Let's Encrypt" 2>/dev/null || true
ufw allow 443/tcp comment "HTTPS - Main" 2>/dev/null || true

# Show current UFW status
echo ""
echo "   📊 Status Firewall:"
ufw status | grep -E "(Status|$PORT|80|443)" || ufw status numbered

echo ""
echo "✅ Step 1 selesai: Firewall sudah dikonfigurasi"
echo ""

# Step 2: Check SSL Certificate
echo "🔐 Step 2: Memeriksa SSL Certificate..."
echo ""

CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
CERT_FILE="$CERT_PATH/fullchain.pem"
KEY_FILE="$CERT_PATH/privkey.pem"

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "   ⚠️  Certbot tidak terinstall"
    echo "   📝 Menginstall certbot..."
    apt update
    apt install certbot python3-certbot-nginx -y
    echo "   ✅ Certbot terinstall"
fi

# Check if certificate exists
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "   ✅ Sertifikat SSL ditemukan di: $CERT_PATH"
    
    # Check certificate details
    echo ""
    echo "   📋 Detail Sertifikat:"
    openssl x509 -in "$CERT_FILE" -noout -subject -dates 2>/dev/null || echo "   ⚠️  Tidak bisa membaca detail sertifikat"
    
    # Check certificate expiry
    EXPIRY_DATE=$(openssl x509 -in "$CERT_FILE" -noout -enddate 2>/dev/null | cut -d= -f2)
    if [ ! -z "$EXPIRY_DATE" ]; then
        EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s 2>/dev/null || echo "0")
        CURRENT_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
        
        if [ $DAYS_LEFT -gt 30 ]; then
            echo "   ✅ Sertifikat valid hingga: $EXPIRY_DATE ($DAYS_LEFT hari tersisa)"
        elif [ $DAYS_LEFT -gt 0 ]; then
            echo "   ⚠️  Sertifikat akan kadaluarsa dalam $DAYS_LEFT hari: $EXPIRY_DATE"
            echo "   💡 Jalankan: certbot renew"
        else
            echo "   ❌ Sertifikat sudah kadaluarsa: $EXPIRY_DATE"
            echo "   💡 Jalankan: certbot --nginx -d $DOMAIN"
        fi
    fi
    
    # Verify certificate is valid for domain
    CERT_DOMAIN=$(openssl x509 -in "$CERT_FILE" -noout -text 2>/dev/null | grep -oP "DNS:\K[^,]*" | head -1 || echo "")
    if [ ! -z "$CERT_DOMAIN" ]; then
        if [ "$CERT_DOMAIN" = "$DOMAIN" ]; then
            echo "   ✅ Sertifikat valid untuk domain: $DOMAIN"
        else
            echo "   ⚠️  Sertifikat untuk domain lain: $CERT_DOMAIN"
        fi
    fi
    
    echo ""
    echo "✅ Step 2 selesai: Sertifikat SSL sudah terpasang"
    
else
    echo "   ❌ Sertifikat SSL TIDAK ditemukan di: $CERT_PATH"
    echo ""
    echo "   📝 Langkah-langkah untuk setup SSL:"
    echo ""
    echo "   1. Pastikan DNS A record sudah pointing ke server:"
    echo "      Type: A"
    echo "      Name: devjargas"
    echo "      Value: [IP Server Anda]"
    echo ""
    echo "   2. Pastikan domain bisa diakses via HTTP:"
    echo "      curl -H 'Host: $DOMAIN' http://localhost/health"
    echo ""
    echo "   3. Generate SSL certificate dengan certbot:"
    echo "      certbot --nginx -d $DOMAIN"
    echo ""
    echo "   4. Atau jika ingin standalone (tanpa nginx):"
    echo "      certbot certonly --standalone -d $DOMAIN"
    echo ""
    echo "   ⚠️  Setelah SSL terpasang, jalankan script ini lagi untuk verifikasi"
    echo ""
    exit 1
fi

# Step 3: Verify nginx config can use the certificate
echo ""
echo "🔍 Step 3: Memverifikasi konfigurasi nginx..."
echo ""

NGINX_CONFIG="/etc/nginx/sites-available/jargas-dev"

if [ -f "$NGINX_CONFIG" ]; then
    echo "   ✅ File konfigurasi nginx ditemukan: $NGINX_CONFIG"
    
    # Check if port 8083 is configured
    if grep -q "listen 8083" "$NGINX_CONFIG"; then
        echo "   ✅ Port 8083 sudah dikonfigurasi di nginx"
    else
        echo "   ⚠️  Port 8083 belum dikonfigurasi di nginx"
        echo "   💡 Pastikan file jargas-dev.conf sudah di-copy ke server"
    fi
    
    # Check if SSL certificate path is correct
    if grep -q "$CERT_FILE" "$NGINX_CONFIG"; then
        echo "   ✅ Path sertifikat SSL sudah benar di konfigurasi nginx"
    else
        echo "   ⚠️  Path sertifikat SSL mungkin belum benar di konfigurasi nginx"
        echo "   💡 Pastikan konfigurasi menggunakan:"
        echo "      ssl_certificate $CERT_FILE;"
        echo "      ssl_certificate_key $KEY_FILE;"
    fi
    
    # Test nginx configuration
    echo ""
    echo "   🧪 Testing konfigurasi nginx..."
    if nginx -t 2>&1 | grep -q "successful"; then
        echo "   ✅ Konfigurasi nginx valid"
    else
        echo "   ❌ Konfigurasi nginx ada error!"
        nginx -t
        exit 1
    fi
    
else
    echo "   ⚠️  File konfigurasi nginx tidak ditemukan: $NGINX_CONFIG"
    echo "   💡 Copy file nginx-host/jargas-dev.conf ke server:"
    echo "      sudo cp nginx-host/jargas-dev.conf $NGINX_CONFIG"
    echo "      sudo ln -s $NGINX_CONFIG /etc/nginx/sites-enabled/jargas-dev"
fi

echo ""
echo "✅ Step 3 selesai: Konfigurasi nginx sudah diverifikasi"
echo ""

# Step 4: Reload nginx if needed
echo "🔄 Step 4: Reload nginx..."
if systemctl is-active --quiet nginx; then
    systemctl reload nginx
    echo "   ✅ Nginx berhasil di-reload"
else
    echo "   ⚠️  Nginx tidak berjalan, mencoba start..."
    systemctl start nginx
    echo "   ✅ Nginx berhasil di-start"
fi

echo ""
echo "=========================================="
echo "✅ Setup Port 8083 dan SSL Selesai!"
echo "=========================================="
echo ""
echo "📋 Ringkasan:"
echo ""
echo "✅ Firewall: Port $PORT sudah diizinkan"
echo "✅ SSL Certificate: Terpasang untuk $DOMAIN"
echo "✅ Nginx: Konfigurasi valid dan reloaded"
echo ""
echo "🌐 Akses Adminer:"
echo "   https://$DOMAIN:$PORT/"
echo ""
echo "🧪 Test akses:"
echo "   curl -k https://$DOMAIN:$PORT/"
echo ""
echo "📝 Catatan:"
echo "   - Pastikan docker container adminer sudah running"
echo "   - Pastikan port mapping di docker-compose.dev.yml sudah benar (18083:8080)"
echo "   - Jika ada masalah, cek log:"
echo "     sudo tail -f /var/log/nginx/jargas_dev_adminer_error.log"
echo ""

