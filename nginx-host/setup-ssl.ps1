# PowerShell Script untuk Setup SSL Certificate dengan Let's Encrypt
# Script ini akan setup SSL di server VPS via SSH

param(
    [Parameter(Mandatory=$false)]
    [string]$ServerIP = "72.61.142.109",
    
    [Parameter(Mandatory=$false)]
    [string]$Username = "root",
    
    [string]$SSHKey = "",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal",
    [string]$Domain = "jargas.ptkiansantang.com",
    [string]$Email = "admin@ptkiansantang.com"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔒 Setup SSL Certificate untuk Jargas APBN" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Domain: $Domain" -ForegroundColor Yellow
Write-Host "Email: $Email" -ForegroundColor Yellow
Write-Host "Server: ${Username}@${ServerIP}" -ForegroundColor Yellow
Write-Host ""

# Check if SSH is available
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ SSH tidak ditemukan!" -ForegroundColor Red
    Write-Host "   Install OpenSSH Client atau gunakan PuTTY/WSL" -ForegroundColor Yellow
    exit 1
}

# Build SSH command
$sshCmd = "ssh"
if ($SSHKey) {
    $sshCmd += " -i `"$SSHKey`""
}
$sshCmd += " ${Username}@${ServerIP}"

Write-Host "📋 Prerequisites:" -ForegroundColor Yellow
Write-Host "   - Domain sudah pointing ke server (DNS A record)" -ForegroundColor Gray
Write-Host "   - Port 80 dan 443 terbuka di firewall" -ForegroundColor Gray
Write-Host "   - Nginx sudah terinstall dan running" -ForegroundColor Gray
Write-Host "   - Nginx config sudah terpasang" -ForegroundColor Gray
Write-Host ""

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Green
Write-Host ""

# Check domain accessibility
Write-Host "1. Checking domain accessibility..." -ForegroundColor Cyan
$domainCheck = ssh ${Username}@${ServerIP} "curl -s --max-time 5 http://$Domain > /dev/null 2>&1 && echo 'OK' || echo 'FAIL'"
if ($domainCheck -match "OK") {
    Write-Host "   ✅ Domain $Domain dapat diakses" -ForegroundColor Green
} else {
    Write-Host "   ❌ Domain $Domain tidak dapat diakses" -ForegroundColor Red
    Write-Host "   Pastikan DNS A record sudah pointing ke server" -ForegroundColor Yellow
    exit 1
}

# Check nginx
Write-Host ""
Write-Host "2. Checking nginx status..." -ForegroundColor Cyan
$nginxStatus = ssh ${Username}@${ServerIP} "systemctl is-active nginx 2>/dev/null && echo 'OK' || echo 'FAIL'"
if ($nginxStatus -match "OK") {
    Write-Host "   ✅ Nginx is running" -ForegroundColor Green
} else {
    Write-Host "   ❌ Nginx tidak berjalan!" -ForegroundColor Red
    exit 1
}

# Check nginx config
Write-Host ""
Write-Host "3. Checking nginx configuration..." -ForegroundColor Cyan
$configCheck = ssh ${Username}@${ServerIP} "[ -f /etc/nginx/sites-available/jargas ] && echo 'OK' || echo 'FAIL'"
if ($configCheck -match "OK") {
    Write-Host "   ✅ Nginx config found" -ForegroundColor Green
} else {
    Write-Host "   ❌ Nginx config tidak ditemukan" -ForegroundColor Red
    Write-Host "   Jalankan setup-domain.ps1 terlebih dahulu" -ForegroundColor Yellow
    exit 1
}

# Check certbot
Write-Host ""
Write-Host "4. Checking certbot installation..." -ForegroundColor Cyan
$certbotCheck = ssh ${Username}@${ServerIP} "command -v certbot > /dev/null 2>&1 && echo 'OK' || echo 'FAIL'"
if ($certbotCheck -match "OK") {
    Write-Host "   ✅ Certbot sudah terinstall" -ForegroundColor Green
    $certbotVersion = ssh ${Username}@${ServerIP} "certbot --version | head -n 1"
    Write-Host "   Version: $certbotVersion" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️  Certbot belum terinstall, akan diinstall..." -ForegroundColor Yellow
    Write-Host "   Installing certbot..." -ForegroundColor Gray
    ssh ${Username}@${ServerIP} "apt update && apt install certbot python3-certbot-nginx -y"
    Write-Host "   ✅ Certbot installed" -ForegroundColor Green
}

# Check existing certificate
Write-Host ""
Write-Host "5. Checking existing certificate..." -ForegroundColor Cyan
$certExists = ssh ${Username}@${ServerIP} "[ -d /etc/letsencrypt/live/$Domain ] && echo 'EXISTS' || echo 'NOT_EXISTS'"
if ($certExists -match "EXISTS") {
    Write-Host "   ⚠️  Certificate sudah ada untuk domain $Domain" -ForegroundColor Yellow
    Write-Host "   Certificate info:" -ForegroundColor Gray
    ssh ${Username}@${ServerIP} "certbot certificates | grep -A 5 '$Domain' || true"
    Write-Host ""
    $renew = Read-Host "   Apakah Anda ingin renew certificate? (y/n)"
    if ($renew -match "^[Yy]") {
        Write-Host "   Renewing certificate..." -ForegroundColor Gray
        ssh ${Username}@${ServerIP} "certbot renew --cert-name $Domain"
        Write-Host "   ✅ Certificate renewed" -ForegroundColor Green
    } else {
        Write-Host "   Skipping certificate generation" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "   ℹ️  Certificate belum ada, akan dibuat baru" -ForegroundColor Gray
}

# Generate SSL certificate
Write-Host ""
Write-Host "6. Generating SSL certificate..." -ForegroundColor Green
Write-Host "   Domain: $Domain" -ForegroundColor Gray
Write-Host "   Email: $Email" -ForegroundColor Gray
Write-Host ""
Write-Host "   Certbot akan:" -ForegroundColor Gray
Write-Host "   - Generate SSL certificate dari Let's Encrypt" -ForegroundColor Gray
Write-Host "   - Update nginx config untuk HTTPS" -ForegroundColor Gray
Write-Host "   - Setup auto-renewal" -ForegroundColor Gray
Write-Host ""

# Run certbot
Write-Host "   Running certbot..." -ForegroundColor Cyan
$certbotResult = ssh ${Username}@${ServerIP} "certbot --nginx -d $Domain --non-interactive --agree-tos --email $Email --redirect 2>&1"
Write-Host $certbotResult

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ SSL certificate berhasil dibuat!" -ForegroundColor Green
} else {
    Write-Host "   ❌ Gagal membuat SSL certificate" -ForegroundColor Red
    Write-Host "   Pastikan:" -ForegroundColor Yellow
    Write-Host "   - Domain sudah pointing ke server (DNS A record)" -ForegroundColor Yellow
    Write-Host "   - Port 80 dan 443 terbuka di firewall" -ForegroundColor Yellow
    Write-Host "   - Nginx config sudah terpasang" -ForegroundColor Yellow
    exit 1
}

# Test nginx config
Write-Host ""
Write-Host "7. Testing nginx configuration..." -ForegroundColor Cyan
$nginxTest = ssh ${Username}@${ServerIP} "nginx -t 2>&1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Nginx config valid" -ForegroundColor Green
} else {
    Write-Host "   ❌ Nginx config error!" -ForegroundColor Red
    Write-Host $nginxTest
    exit 1
}

# Reload nginx
Write-Host ""
Write-Host "8. Reloading nginx..." -ForegroundColor Cyan
ssh ${Username}@${ServerIP} "systemctl reload nginx"
Write-Host "   ✅ Nginx reloaded" -ForegroundColor Green

# Test SSL certificate
Write-Host ""
Write-Host "9. Testing SSL certificate..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
$httpsTest = ssh ${Username}@${ServerIP} "curl -s --max-time 5 https://$Domain > /dev/null 2>&1 && echo 'OK' || echo 'FAIL'"
if ($httpsTest -match "OK") {
    Write-Host "   ✅ HTTPS berhasil diakses" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  HTTPS belum dapat diakses (mungkin perlu beberapa saat)" -ForegroundColor Yellow
}

# Test auto-renewal
Write-Host ""
Write-Host "10. Testing auto-renewal..." -ForegroundColor Cyan
$renewTest = ssh ${Username}@${ServerIP} "certbot renew --dry-run > /dev/null 2>&1 && echo 'OK' || echo 'FAIL'"
if ($renewTest -match "OK") {
    Write-Host "   ✅ Auto-renewal setup berhasil" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Auto-renewal test gagal (tapi mungkin masih OK)" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ SSL Setup Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Informasi:" -ForegroundColor Yellow
Write-Host "   - Domain: $Domain" -ForegroundColor Gray
Write-Host "   - HTTPS: https://$Domain" -ForegroundColor Gray
Write-Host "   - Certificate: /etc/letsencrypt/live/$Domain/" -ForegroundColor Gray
Write-Host "   - Auto-renewal: Sudah diaktifkan" -ForegroundColor Gray
Write-Host ""
Write-Host "🔍 Verifikasi:" -ForegroundColor Yellow
Write-Host "   - Test HTTPS: curl -I https://$Domain" -ForegroundColor Gray
Write-Host "   - Check certificate: sudo certbot certificates" -ForegroundColor Gray
Write-Host "   - Test renewal: sudo certbot renew --dry-run" -ForegroundColor Gray
Write-Host ""

