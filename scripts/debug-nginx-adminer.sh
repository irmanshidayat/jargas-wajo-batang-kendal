#!/bin/bash
# Script untuk debug konfigurasi nginx adminer

echo "=== Debugging Nginx Adminer Configuration ==="
echo ""

cd ~/jargas-wajo-batang-kendal-dev

echo "1. Checking local file..."
if grep -q "location.*adminer" nginx-host/jargas-dev.conf; then
    echo "   ✓ Local file contains adminer config"
    echo "   Location block:"
    grep -A 3 "location.*adminer" nginx-host/jargas-dev.conf | head -5
else
    echo "   ✗ Local file does NOT contain adminer config"
fi

echo ""
echo "2. Checking server file..."
if sudo grep -q "location.*adminer" /etc/nginx/sites-available/jargas-dev; then
    echo "   ✓ Server file contains adminer config"
    echo "   Location block:"
    sudo grep -A 3 "location.*adminer" /etc/nginx/sites-available/jargas-dev | head -5
else
    echo "   ✗ Server file does NOT contain adminer config"
    echo "   File line count: $(sudo wc -l < /etc/nginx/sites-available/jargas-dev)"
fi

echo ""
echo "3. Checking active nginx configuration..."
if sudo nginx -T 2>/dev/null | grep -q "location.*adminer"; then
    echo "   ✓ Adminer location is active"
    echo "   Active location block:"
    sudo nginx -T 2>/dev/null | grep -A 5 "location.*adminer" | head -10
else
    echo "   ✗ Adminer location is NOT active in nginx"
    echo "   All location blocks:"
    sudo nginx -T 2>/dev/null | grep "location" | head -10
fi

echo ""
echo "4. Testing adminer container directly..."
if curl -s http://localhost:8083 | grep -q "Adminer\|Login"; then
    echo "   ✓ Adminer container is accessible"
    curl -s http://localhost:8083 | grep -i "title" | head -1
else
    echo "   ✗ Adminer container is NOT accessible"
fi

echo ""
echo "5. Testing via nginx..."
response=$(curl -sI https://devjargas.ptkiansantang.com/adminer 2>&1)
content_length=$(echo "$response" | grep -i "content-length" | awk '{print $2}' | tr -d '\r')

echo "   Response headers:"
echo "$response" | head -5
echo "   Content-Length: $content_length bytes"

if [ ! -z "$content_length" ] && [ "$content_length" -lt 500 ]; then
    echo "   ⚠ Warning: Content-Length is too small (likely frontend, not adminer)"
    echo "   Response content:"
    curl -s https://devjargas.ptkiansantang.com/adminer 2>/dev/null | head -3
fi

echo ""
echo "=== Debug Complete ==="

