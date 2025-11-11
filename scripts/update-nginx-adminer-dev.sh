#!/bin/bash
# Script untuk update konfigurasi nginx adminer di server dev

set -e

echo "=== Update Nginx Configuration for Adminer ==="
echo ""

# Navigate to project directory
cd ~/jargas-wajo-batang-kendal-dev

# Check if local file has adminer config
echo "1. Checking local file for adminer configuration..."
if grep -q "location.*adminer" nginx-host/jargas-dev.conf; then
    echo "   ✓ Local file contains adminer configuration"
    grep -A 3 "location.*adminer" nginx-host/jargas-dev.conf | head -5
else
    echo "   ✗ Local file does NOT contain adminer configuration"
    exit 1
fi

echo ""
echo "2. Backing up current nginx config..."
sudo cp /etc/nginx/sites-available/jargas-dev /etc/nginx/sites-available/jargas-dev.backup.$(date +%Y%m%d_%H%M%S)
echo "   ✓ Backup created"

echo ""
echo "3. Copying new configuration to nginx..."
sudo cp nginx-host/jargas-dev.conf /etc/nginx/sites-available/jargas-dev
echo "   ✓ File copied"

echo ""
echo "4. Verifying file in server..."
if sudo grep -q "location.*adminer" /etc/nginx/sites-available/jargas-dev; then
    echo "   ✓ Server file contains adminer configuration"
    sudo grep -A 3 "location.*adminer" /etc/nginx/sites-available/jargas-dev | head -5
else
    echo "   ✗ Server file does NOT contain adminer configuration"
    exit 1
fi

echo ""
echo "5. Testing nginx configuration..."
if sudo nginx -t; then
    echo "   ✓ Nginx configuration test passed"
else
    echo "   ✗ Nginx configuration test failed"
    exit 1
fi

echo ""
echo "6. Reloading nginx..."
sudo systemctl reload nginx
echo "   ✓ Nginx reloaded"

echo ""
echo "7. Verifying active configuration..."
if sudo nginx -T 2>/dev/null | grep -q "location.*adminer"; then
    echo "   ✓ Adminer location is active in nginx"
    sudo nginx -T 2>/dev/null | grep -A 5 "location.*adminer" | head -10
else
    echo "   ✗ Adminer location is NOT active in nginx"
    exit 1
fi

echo ""
echo "8. Testing adminer access..."
echo "   Testing: curl -I https://devjargas.ptkiansantang.com/adminer"
response=$(curl -sI https://devjargas.ptkiansantang.com/adminer 2>&1)
content_length=$(echo "$response" | grep -i "content-length" | awk '{print $2}' | tr -d '\r')

if [ ! -z "$content_length" ] && [ "$content_length" -gt 1000 ]; then
    echo "   ✓ Adminer is accessible (Content-Length: $content_length bytes)"
else
    echo "   ⚠ Warning: Content-Length is $content_length bytes (expected > 1000)"
    echo "   Response headers:"
    echo "$response" | head -10
fi

echo ""
echo "=== Update Complete ==="
echo ""
echo "You can now access adminer at: https://devjargas.ptkiansantang.com/adminer"
echo ""

