# PowerShell Script untuk Setup Domain Development - devjargas.ptkiansantang.com
# Script ini akan setup nginx configuration untuk domain development

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$Domain = "devjargas.ptkiansantang.com"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Domain Development" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Domain: $Domain" -ForegroundColor Yellow
Write-Host "Server: ${Username}@${ServerIP}" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Lanjutkan setup domain development? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Setup dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Copy nginx config ke server..." -ForegroundColor Green
$copyCmd = "scp nginx-host/jargas-dev.conf ${Username}@${ServerIP}:~/jargas-dev.conf"
try {
    Invoke-Expression $copyCmd
    Write-Host "✅ Config file ter-upload" -ForegroundColor Green
} catch {
    Write-Host "❌ Upload config gagal!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Setup nginx config di server..." -ForegroundColor Green
$setupCmd = @"
ssh ${Username}@${ServerIP} '
    sudo cp ~/jargas-dev.conf /etc/nginx/sites-available/jargas-dev &&
    sudo ln -sf /etc/nginx/sites-available/jargas-dev /etc/nginx/sites-enabled/jargas-dev &&
    sudo nginx -t &&
    sudo systemctl reload nginx
'
"@
try {
    Invoke-Expression $setupCmd
    Write-Host "✅ Nginx config berhasil di-setup" -ForegroundColor Green
} catch {
    Write-Host "❌ Setup nginx config gagal!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Setup SSL Certificate (Let's Encrypt)..." -ForegroundColor Green
Write-Host "⚠️  Pastikan DNS A record sudah pointing ke server!" -ForegroundColor Yellow
Write-Host "   Domain: $Domain → IP: $ServerIP" -ForegroundColor Gray
Write-Host ""

$sslConfirm = Read-Host "Setup SSL certificate sekarang? (y/n)"
if ($sslConfirm -eq "y" -or $sslConfirm -eq "Y") {
    $sslCmd = "ssh ${Username}@${ServerIP} 'sudo certbot --nginx -d $Domain'"
    try {
        Invoke-Expression $sslCmd
        Write-Host "✅ SSL certificate berhasil di-setup" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  SSL setup mungkin perlu dijalankan manual:" -ForegroundColor Yellow
        Write-Host "   ssh ${Username}@${ServerIP} 'sudo certbot --nginx -d $Domain'" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  SSL akan di-setup manual nanti" -ForegroundColor Yellow
    Write-Host "   Jalankan: ssh ${Username}@${ServerIP} 'sudo certbot --nginx -d $Domain'" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Domain Development Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Pastikan DNS A record sudah pointing:" -ForegroundColor White
Write-Host "   Type: A" -ForegroundColor Gray
Write-Host "   Name: devjargas" -ForegroundColor Gray
Write-Host "   Value: $ServerIP" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Verifikasi domain:" -ForegroundColor White
Write-Host "   curl -H 'Host: $Domain' http://$ServerIP/health" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Setelah SSL terpasang, akses:" -ForegroundColor White
Write-Host "   https://$Domain" -ForegroundColor Gray
Write-Host ""

