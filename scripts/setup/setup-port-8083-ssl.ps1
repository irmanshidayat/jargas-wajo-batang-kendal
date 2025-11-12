# PowerShell Script untuk Setup Port 8083 dan SSL - Development Environment
# Script ini akan setup firewall dan verifikasi SSL certificate untuk port 8083
# Domain: devjargas.ptkiansantang.com

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$Domain = "devjargas.ptkiansantang.com",
    [string]$Port = "8083"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔒 Setup Port 8083 dan SSL Certificate" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Domain: $Domain" -ForegroundColor Yellow
Write-Host "Port: $Port" -ForegroundColor Yellow
Write-Host "Server: ${Username}@${ServerIP}" -ForegroundColor Yellow
Write-Host ""

# Step 1: Upload script bash ke server
Write-Host "📤 Step 1: Upload script setup ke server..." -ForegroundColor Green
Write-Host ""

$scriptPath = Join-Path $PSScriptRoot "setup-port-8083-ssl.sh"
if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ Script bash tidak ditemukan: $scriptPath" -ForegroundColor Red
    Write-Host "   Pastikan file scripts/setup-port-8083-ssl.sh ada" -ForegroundColor Yellow
    exit 1
}

# Upload script
$remoteScriptPath = "~/setup-port-8083-ssl.sh"
try {
    scp $scriptPath "${Username}@${ServerIP}:${remoteScriptPath}"
    Write-Host "   ✅ Script berhasil di-upload" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Gagal upload script: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Make script executable and run
Write-Host ""
Write-Host "🚀 Step 2: Menjalankan script di server..." -ForegroundColor Green
Write-Host ""

$runScript = "ssh ${Username}@${ServerIP} 'chmod +x ${remoteScriptPath} && sudo bash ${remoteScriptPath}'"

try {
    Invoke-Expression $runScript
    Write-Host ""
    Write-Host "✅ Setup selesai!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "⚠️  Ada error saat menjalankan script" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Alternatif: Jalankan manual di server:" -ForegroundColor Yellow
    Write-Host "   ssh ${Username}@${ServerIP}" -ForegroundColor Gray
    Write-Host "   sudo bash ${remoteScriptPath}" -ForegroundColor Gray
    exit 1
}

# Step 3: Verify setup
Write-Host ""
Write-Host "🔍 Step 3: Verifikasi setup..." -ForegroundColor Green
Write-Host ""

# Check firewall
Write-Host "   Memeriksa firewall..." -ForegroundColor Cyan
$firewallCheck = "ssh ${Username}@${ServerIP} 'sudo ufw status | grep $Port'"
try {
    $firewallResult = Invoke-Expression $firewallCheck 2>&1
    if ($firewallResult -match $Port) {
        Write-Host "   ✅ Port $Port sudah diizinkan di firewall" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Port $Port mungkin belum diizinkan" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Tidak bisa memeriksa firewall" -ForegroundColor Yellow
}

# Check SSL certificate
Write-Host ""
Write-Host "   Memeriksa SSL certificate..." -ForegroundColor Cyan
$certCheck = "ssh ${Username}@${ServerIP} 'sudo test -f /etc/letsencrypt/live/$Domain/fullchain.pem && echo EXISTS || echo NOT_EXISTS'"
try {
    $certResult = Invoke-Expression $certCheck 2>&1 | Out-String
    $certResult = $certResult.Trim()
    if ($certResult -eq "EXISTS") {
        Write-Host "   ✅ SSL certificate ditemukan" -ForegroundColor Green
    } else {
        Write-Host "   ❌ SSL certificate tidak ditemukan" -ForegroundColor Red
        Write-Host "   💡 Jalankan: ssh ${Username}@${ServerIP} 'sudo certbot --nginx -d $Domain'" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Tidak bisa memeriksa certificate" -ForegroundColor Yellow
}

# Check nginx config
Write-Host ""
Write-Host "   Memeriksa konfigurasi nginx..." -ForegroundColor Cyan
$nginxCheck = "ssh ${Username}@${ServerIP} 'sudo nginx -t 2>&1'"
try {
    $nginxResult = Invoke-Expression $nginxCheck 2>&1 | Out-String
    if ($nginxResult -match "successful") {
        Write-Host "   ✅ Konfigurasi nginx valid" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Konfigurasi nginx ada masalah" -ForegroundColor Yellow
        Write-Host "   $nginxResult" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  Tidak bisa memeriksa nginx" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Verifikasi Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Akses Adminer:" -ForegroundColor Yellow
Write-Host "   https://${Domain}:${Port}/" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Test akses dari server:" -ForegroundColor Yellow
Write-Host "   curl -k https://${Domain}:${Port}/" -ForegroundColor Gray
Write-Host ""
Write-Host "📝 Catatan:" -ForegroundColor Yellow
Write-Host "   - Pastikan docker container adminer sudah running" -ForegroundColor Gray
Write-Host "   - Pastikan port mapping di docker-compose.dev.yml sudah benar (18083:8080)" -ForegroundColor Gray
Write-Host "   - Jika ada masalah, cek log nginx:" -ForegroundColor Gray
Write-Host "     ssh ${Username}@${ServerIP} 'sudo tail -f /var/log/nginx/jargas_dev_adminer_error.log'" -ForegroundColor Gray
Write-Host ""

