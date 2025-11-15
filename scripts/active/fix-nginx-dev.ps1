# PowerShell Script untuk Fix Nginx Development Setup
# Script ini akan memeriksa dan memperbaiki konfigurasi Nginx untuk development

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fix Nginx Development Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server: ${Username}@${ServerIP}" -ForegroundColor Yellow
Write-Host "Domain: devjargas.ptkiansantang.com" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Lanjutkan fix nginx setup? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Fix dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Checking Nginx status..." -ForegroundColor Green
$checkNginx = @"
ssh ${Username}@${ServerIP} '
    echo "=== Nginx Status ==="
    systemctl status nginx --no-pager -l || echo "Nginx not running"
    echo ""
    echo "=== Nginx Process ==="
    ps aux | grep nginx | grep -v grep || echo "No nginx process found"
    echo ""
    echo "=== Listening Ports ==="
    ss -lntp | grep -E "(100|463)" || netstat -tulpn | grep -E "(100|463)" || echo "Ports 100 and 463 not listening"
    echo ""
    echo "=== Nginx Config Files ==="
    ls -la /etc/nginx/sites-available/jargas-dev 2>/dev/null || echo "Config file not found in sites-available"
    ls -la /etc/nginx/sites-enabled/jargas-dev 2>/dev/null || echo "Config file not found in sites-enabled"
'
"@

try {
    Invoke-Expression $checkNginx
} catch {
    Write-Host "❌ Error checking nginx status!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Copying nginx config to server..." -ForegroundColor Green
$copyCmd = "scp nginx-host/jargas-dev.conf ${Username}@${ServerIP}:~/jargas-dev.conf"
try {
    Invoke-Expression $copyCmd
    Write-Host "✅ Config file uploaded" -ForegroundColor Green
} catch {
    Write-Host "❌ Upload config failed!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Setting up nginx config on server..." -ForegroundColor Green
$setupCmd = @"
ssh ${Username}@${ServerIP} '
    set -e
    echo "Copying config to sites-available..."
    cp ~/jargas-dev.conf /etc/nginx/sites-available/jargas-dev || {
        echo "Error: Cannot copy config file"
        exit 1
    }
    echo "✅ Config copied to sites-available"
    
    echo "Creating symlink to sites-enabled..."
    ln -sf /etc/nginx/sites-available/jargas-dev /etc/nginx/sites-enabled/jargas-dev || {
        echo "Error: Cannot create symlink"
        exit 1
    }
    echo "✅ Symlink created"
    
    echo "Testing nginx configuration..."
    nginx -t || {
        echo "Error: Nginx configuration test failed"
        exit 1
    }
    echo "✅ Nginx configuration test passed"
    
    echo "Reloading nginx..."
    systemctl reload nginx || {
        echo "Warning: Nginx reload failed, trying restart..."
        systemctl restart nginx || {
            echo "Error: Nginx restart failed"
            exit 1
        }
    }
    echo "✅ Nginx reloaded/restarted"
    
    echo ""
    echo "=== Verification ==="
    systemctl status nginx --no-pager -l | head -10
    echo ""
    echo "=== Listening Ports ==="
    ss -lntp | grep -E "(100|463)" || netstat -tulpn | grep -E "(100|463)"
'
"@

try {
    Invoke-Expression $setupCmd
    Write-Host "✅ Nginx config setup completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Setup nginx config failed!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 4: Checking firewall..." -ForegroundColor Green
$firewallCmd = @"
ssh ${Username}@${ServerIP} '
    echo "=== Firewall Status ==="
    if command -v ufw &> /dev/null; then
        ufw status | grep -E "(100|463)" || echo "Ports 100 and 463 may not be open in UFW"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --list-ports | grep -E "(100|463)" || echo "Ports 100 and 463 may not be open in firewalld"
    else
        echo "No firewall management tool found (ufw/firewalld)"
    fi
    echo ""
    echo "=== iptables rules ==="
    iptables -L -n | grep -E "(100|463)" || echo "No iptables rules found for ports 100 and 463"
'
"@

try {
    Invoke-Expression $firewallCmd
} catch {
    Write-Host "⚠️  Warning: Could not check firewall status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 5: Checking services..." -ForegroundColor Green
$servicesCmd = @"
ssh ${Username}@${ServerIP} '
    echo "=== Backend Status ==="
    if [ -f ~/jargas-wajo-batang-kendal-dev/backend/backend.pid ]; then
        BACKEND_PID=\$(cat ~/jargas-wajo-batang-kendal-dev/backend/backend.pid)
        if ps -p \$BACKEND_PID > /dev/null 2>&1; then
            echo "✅ Backend is running (PID: \$BACKEND_PID)"
            curl -f -s http://localhost:8000/health && echo "✅ Backend health check passed" || echo "⚠️  Backend health check failed"
        else
            echo "❌ Backend process not found"
        fi
    else
        echo "⚠️  Backend PID file not found"
    fi
    
    echo ""
    echo "=== Frontend Container Status ==="
    if docker ps | grep -q jargas_frontend; then
        echo "✅ Frontend container is running"
        docker ps | grep jargas_frontend
        CONTAINER_PORT=\$(docker port jargas_frontend 2>/dev/null | grep -oP "0.0.0.0:\K[0-9]+" | head -1 || echo "")
        if [ -n "\$CONTAINER_PORT" ]; then
            echo "   Frontend accessible on port: \$CONTAINER_PORT"
            curl -f -s http://localhost:\$CONTAINER_PORT > /dev/null 2>&1 && echo "✅ Frontend health check passed" || echo "⚠️  Frontend health check failed"
        fi
    else
        echo "❌ Frontend container not found"
        docker ps -a | grep frontend || echo "No frontend containers found"
    fi
'
"@

try {
    Invoke-Expression $servicesCmd
} catch {
    Write-Host "⚠️  Warning: Could not check services status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Fix completed!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test website: https://devjargas.ptkiansantang.com:463" -ForegroundColor White
Write-Host "2. If still not accessible, check firewall:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP}" -ForegroundColor Gray
Write-Host "   sudo ufw allow 100/tcp" -ForegroundColor Gray
Write-Host "   sudo ufw allow 463/tcp" -ForegroundColor Gray
Write-Host "3. Check nginx logs if needed:" -ForegroundColor White
Write-Host "   sudo tail -f /var/log/nginx/jargas_dev_error.log" -ForegroundColor Gray
Write-Host ""

