#!/bin/bash
# Instruksi Setup Nginx Host - Copy paste ke server SSH

echo "=========================================="
echo "Setup Nginx Host untuk Jargas APBN"
echo "=========================================="
echo ""

# Step 1: Copy config
echo "Step 1: Copy konfigurasi..."
sudo cp nginx-host/jargas.conf /etc/nginx/sites-available/jargas
echo "✅ Config copied"

# Step 2: Create symlink
echo ""
echo "Step 2: Buat symbolic link..."
if [ -L "/etc/nginx/sites-enabled/jargas" ]; then
    sudo rm /etc/nginx/sites-enabled/jargas
fi
sudo ln -s /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas
echo "✅ Symlink created"

# Step 3: Backup default (optional)
echo ""
read -p "Hapus default nginx config? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "/etc/nginx/sites-available/default" ]; then
        sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)
    fi
    sudo rm -f /etc/nginx/sites-enabled/default
    echo "✅ Default config removed"
fi

# Step 4: Test config
echo ""
echo "Step 3: Test konfigurasi nginx..."
if sudo nginx -t; then
    echo "✅ Nginx config valid"
else
    echo "❌ Nginx config error!"
    exit 1
fi

# Step 5: Reload nginx
echo ""
echo "Step 4: Reload nginx..."
sudo systemctl reload nginx

# Step 6: Check status
echo ""
echo "Step 5: Check nginx status..."
if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
    echo ""
    echo "=========================================="
    echo "✅ Setup selesai!"
    echo "=========================================="
    echo ""
    echo "📋 Langkah selanjutnya:"
    echo "1. Edit domain: sudo nano /etc/nginx/sites-available/jargas"
    echo "   Ubah: server_name _; menjadi server_name your-domain.com;"
    echo ""
    echo "2. Test: curl http://localhost/health"
    echo ""
    echo "3. Setup SSL (jika ada domain):"
    echo "   sudo apt install certbot python3-certbot-nginx -y"
    echo "   sudo certbot --nginx -d your-domain.com"
    echo ""
else
    echo "❌ Nginx tidak berjalan!"
    sudo systemctl status nginx
    exit 1
fi

