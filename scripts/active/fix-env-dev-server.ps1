# PowerShell Script untuk Fix .env.dev di Server
# Script ini akan memperbaiki format file .env.dev yang corrupt

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fix .env.dev di Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server: ${Username}@${ServerIP}" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Lanjutkan fix .env.dev? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Fix dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Backup .env.dev yang ada..." -ForegroundColor Green
$backupCmd = "ssh ${Username}@${ServerIP} 'cd ~/jargas-wajo-batang-kendal-dev && cp .env.dev .env.dev.backup.$(date +%Y%m%d_%H%M%S) && echo \"✅ Backup created\"'"
try {
    Invoke-Expression $backupCmd
} catch {
    Write-Host "⚠️  Warning: Backup mungkin gagal (non-fatal)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Copy env.dev.example ke server..." -ForegroundColor Green
$copyCmd = "scp env.dev.example ${Username}@${ServerIP}:~/jargas-wajo-batang-kendal-dev/.env.dev.new"
try {
    Invoke-Expression $copyCmd
    Write-Host "✅ Template uploaded" -ForegroundColor Green
} catch {
    Write-Host "❌ Upload template failed!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Merge nilai penting dari .env.dev lama ke yang baru..." -ForegroundColor Green
$mergeCmd = @"
ssh ${Username}@${ServerIP} '
    cd ~/jargas-wajo-batang-kendal-dev
    
    # Backup old file
    if [ -f .env.dev ]; then
        cp .env.dev .env.dev.old
    fi
    
    # Extract important values from old file (if exists)
    if [ -f .env.dev.old ]; then
        SECRET_KEY=\$(grep "^SECRET_KEY=" .env.dev.old | cut -d= -f2- || echo "")
        DB_PASSWORD=\$(grep "^DB_PASSWORD=" .env.dev.old | cut -d= -f2- || echo "")
        DB_NAME=\$(grep "^DB_NAME=" .env.dev.old | cut -d= -f2- || echo "")
        
        # Update new file with old values (if found)
        if [ -n "\$SECRET_KEY" ]; then
            sed -i "s/^SECRET_KEY=.*/SECRET_KEY=\$SECRET_KEY/" .env.dev.new
        fi
        if [ -n "\$DB_PASSWORD" ]; then
            sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=\$DB_PASSWORD/" .env.dev.new
        fi
        if [ -n "\$DB_NAME" ]; then
            sed -i "s/^DB_NAME=.*/DB_NAME=\$DB_NAME/" .env.dev.new
        fi
    fi
    
    # Replace old file with new one
    mv .env.dev.new .env.dev
    
    # Clean up any invalid lines (remove lines with quotes or special chars in variable name)
    sed -i "/^[^#].*[\"'].*=/d" .env.dev
    
    # Ensure correct format for FRONTEND_PORT and PORT
    sed -i "s/FRONTEND_PORT_MAPPED/FRONTEND_PORT/g" .env.dev
    sed -i "s/^FRONTEND_PORT=.*/FRONTEND_PORT=8910/" .env.dev
    sed -i "s/^PORT=8000/PORT=8020/" .env.dev
    
    echo "✅ .env.dev fixed"
    
    # Verify file
    echo ""
    echo "=== Verification ==="
    echo "File lines: \$(wc -l < .env.dev)"
    echo "FRONTEND_PORT: \$(grep FRONTEND_PORT .env.dev | grep -v \"^#\")"
    echo "PORT: \$(grep \"^PORT=\" .env.dev | grep -v \"^#\")"
    
    # Check for invalid lines
    INVALID=\$(grep -n "^[^#].*[\"'].*=" .env.dev || echo "")
    if [ -n "\$INVALID" ]; then
        echo "⚠️  Warning: Found potentially invalid lines:"
        echo "\$INVALID"
    else
        echo "✅ No invalid lines found"
    fi
'
"@

try {
    Invoke-Expression $mergeCmd
    Write-Host "✅ .env.dev fixed" -ForegroundColor Green
} catch {
    Write-Host "❌ Fix failed!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Fix completed!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart frontend container:" -ForegroundColor White
Write-Host "   docker-compose -f docker-compose.frontend.yml --env-file .env.dev down" -ForegroundColor Gray
Write-Host "   docker-compose -f docker-compose.frontend.yml --env-file .env.dev up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Restart backend:" -ForegroundColor White
Write-Host "   pkill -f 'python.*run.py' && cd backend && source venv/bin/activate && nohup python3 run.py > backend.log 2>&1 &" -ForegroundColor Gray
Write-Host ""

