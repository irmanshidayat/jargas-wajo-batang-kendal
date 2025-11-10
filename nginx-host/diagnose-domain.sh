#!/bin/bash
# Script Diagnostik Domain - Cek masalah domain jargas.ptkiansantang.com

set -e

DOMAIN="jargas.ptkiansantang.com"
EXPECTED_IP="72.61.142.109"

echo "=========================================="
echo "🔍 Diagnostik Domain: $DOMAIN"
echo "=========================================="
echo ""

# 1. Cek DNS Resolution
echo "1️⃣  Cek DNS Resolution..."
echo ""
RESOLVED_IP=$(dig +short $DOMAIN @8.8.8.8 | tail -n1)
echo "   DNS Resolution (Google DNS): $RESOLVED_IP"
if [ "$RESOLVED_IP" = "$EXPECTED_IP" ]; then
    echo "   ✅ DNS mengarah ke IP yang benar"
else
    echo "   ❌ DNS mengarah ke IP yang SALAH!"
    echo "   Expected: $EXPECTED_IP"
    echo "   Actual: $RESOLVED_IP"
fi
echo ""

# 2. Cek Web Server yang Running
echo "2️⃣  Cek Web Server yang Running..."
echo ""
if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx is running"
else
    echo "   ❌ Nginx is NOT running!"
fi

if systemctl is-active --quiet litespeed; then
    echo "   ⚠️  LiteSpeed is running (KONFLIK!)"
elif systemctl list-units --type=service | grep -q litespeed; then
    echo "   ⚠️  LiteSpeed service exists (mungkin terinstall)"
else
    echo "   ✅ LiteSpeed tidak terdeteksi"
fi

if systemctl is-active --quiet apache2; then
    echo "   ⚠️  Apache2 is running (KONFLIK!)"
elif systemctl list-units --type=service | grep -q apache2; then
    echo "   ⚠️  Apache2 service exists (mungkin terinstall)"
else
    echo "   ✅ Apache2 tidak terdeteksi"
fi
echo ""

# 3. Cek Port 80
echo "3️⃣  Cek Port 80..."
echo ""
PORT_80=$(sudo netstat -tulpn | grep :80 | head -1)
if [ -z "$PORT_80" ]; then
    echo "   ❌ Tidak ada service listening di port 80!"
else
    echo "   Service listening di port 80:"
    echo "   $PORT_80"
    if echo "$PORT_80" | grep -q nginx; then
        echo "   ✅ Nginx listening di port 80"
    else
        echo "   ⚠️  Bukan Nginx yang listening di port 80!"
    fi
fi
echo ""

# 4. Cek Konfigurasi Nginx
echo "4️⃣  Cek Konfigurasi Nginx..."
echo ""
if [ -f "/etc/nginx/sites-enabled/jargas" ]; then
    echo "   ✅ Konfigurasi jargas ditemukan"
    
    # Cek server_name
    SERVER_NAME=$(grep -E "^\s*server_name" /etc/nginx/sites-enabled/jargas | head -1)
    echo "   Server name: $SERVER_NAME"
    
    if echo "$SERVER_NAME" | grep -q "$DOMAIN"; then
        echo "   ✅ Domain $DOMAIN dikonfigurasi dengan benar"
    else
        echo "   ⚠️  Domain $DOMAIN tidak ditemukan di konfigurasi"
    fi
else
    echo "   ❌ Konfigurasi jargas tidak ditemukan!"
fi
echo ""

# 5. Test Nginx Config
echo "5️⃣  Test Konfigurasi Nginx..."
echo ""
if sudo nginx -t 2>&1 | grep -q "successful"; then
    echo "   ✅ Konfigurasi nginx valid"
else
    echo "   ❌ Konfigurasi nginx error!"
    sudo nginx -t
fi
echo ""

# 6. Test Local Access
echo "6️⃣  Test Local Access..."
echo ""
HEALTH_RESPONSE=$(curl -s -H "Host: $DOMAIN" http://localhost/health || echo "FAILED")
if [ "$HEALTH_RESPONSE" = "healthy" ]; then
    echo "   ✅ Health check berhasil"
else
    echo "   ❌ Health check gagal: $HEALTH_RESPONSE"
fi

FRONTEND_RESPONSE=$(curl -s -I -H "Host: $DOMAIN" http://localhost/ | head -1)
echo "   Frontend response: $FRONTEND_RESPONSE"
echo ""

# 7. Cek Container Docker
echo "7️⃣  Cek Container Docker..."
echo ""
if command -v docker-compose &> /dev/null; then
    cd ~/jargas-wajo-batang-kendal 2>/dev/null || cd /root/jargas-wajo-batang-kendal 2>/dev/null || echo "   ⚠️  Project directory tidak ditemukan"
    
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        echo "   ✅ Container Docker running"
        docker-compose ps | grep -E "NAME|jargas"
    else
        echo "   ❌ Container Docker tidak running!"
    fi
else
    echo "   ⚠️  docker-compose tidak ditemukan"
fi
echo ""

# 8. Rekomendasi
echo "=========================================="
echo "📋 Rekomendasi:"
echo "=========================================="
echo ""

if [ "$RESOLVED_IP" != "$EXPECTED_IP" ]; then
    echo "❌ MASALAH: DNS masih mengarah ke IP yang salah!"
    echo "   Solusi: Update DNS record di panel hosting domain"
    echo "   - Type: A"
    echo "   - Name: jargas"
    echo "   - Value: $EXPECTED_IP"
    echo "   - TTL: 3600"
    echo ""
fi

if systemctl is-active --quiet litespeed || systemctl is-active --quiet apache2; then
    echo "❌ MASALAH: Ada web server lain yang running (konflik dengan Nginx)!"
    echo "   Solusi: Stop web server lain"
    echo "   sudo systemctl stop litespeed"
    echo "   sudo systemctl stop apache2"
    echo "   sudo systemctl disable litespeed"
    echo "   sudo systemctl disable apache2"
    echo ""
fi

if ! systemctl is-active --quiet nginx; then
    echo "❌ MASALAH: Nginx tidak running!"
    echo "   Solusi: Start nginx"
    echo "   sudo systemctl start nginx"
    echo "   sudo systemctl enable nginx"
    echo ""
fi

if [ -z "$PORT_80" ] || ! echo "$PORT_80" | grep -q nginx; then
    echo "❌ MASALAH: Nginx tidak listening di port 80!"
    echo "   Solusi: Restart nginx"
    echo "   sudo systemctl restart nginx"
    echo ""
fi

echo "✅ Jika semua sudah benar, tunggu beberapa menit untuk DNS propagation"
echo ""

