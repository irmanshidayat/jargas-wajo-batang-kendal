# PowerShell Script untuk Setup Domain jargas.ptkiansantang.com
# Script ini akan setup domain di server VPS via SSH

param(
    [Parameter(Mandatory=$false)]
    [string]$ServerIP = "72.61.142.109",
    
    [Parameter(Mandatory=$false)]
    [string]$Username = "root",
    
    [string]$SSHKey = "",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal",
    [string]$Domain = "jargas.ptkiansantang.com"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🌐 Setup Domain untuk Jargas APBN" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Domain: $Domain" -ForegroundColor Yellow
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

Write-Host "📋 Langkah-langkah:" -ForegroundColor Yellow
Write-Host "1. Update konfigurasi nginx dengan domain" -ForegroundColor Gray
Write-Host "2. Test konfigurasi nginx" -ForegroundColor Gray
Write-Host "3. Reload nginx" -ForegroundColor Gray
Write-Host "4. Test akses domain" -ForegroundColor Gray
Write-Host "5. Setup SSL (optional)" -ForegroundColor Gray
Write-Host ""

Write-Host "🚀 Menjalankan setup domain di server..." -ForegroundColor Green
Write-Host ""

# Execute commands - using bash script on server
# Use single quotes to prevent PowerShell parsing
$bashScript = 'cd ~/jargas-wajo-batang-kendal; if [ ! -f nginx-host/jargas.conf ]; then echo "File tidak ditemukan"; exit 1; fi; sudo cp nginx-host/jargas.conf /etc/nginx/sites-available/jargas; sudo nginx -t; sudo systemctl reload nginx; sleep 2; curl -s -H "Host: jargas.ptkiansantang.com" http://localhost/health || echo "Health check gagal"; sudo systemctl status nginx --no-pager -l | head -5'

$fullCommand = "$sshCmd `"$bashScript`""
Invoke-Expression $fullCommand

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Domain Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Setup DNS Record di penyedia hosting domain:" -ForegroundColor White
Write-Host "   Type: A" -ForegroundColor Gray
Write-Host "   Name: jargas" -ForegroundColor Gray
Write-Host "   Value: $ServerIP" -ForegroundColor Gray
Write-Host "   TTL: 3600" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Tunggu DNS propagation (5-15 menit, maksimal 48 jam)" -ForegroundColor White
Write-Host ""
Write-Host "3. Test DNS dari lokal:" -ForegroundColor White
Write-Host "   nslookup $Domain" -ForegroundColor Gray
Write-Host "   ping $Domain" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Setup SSL dengan Let's Encrypt (setelah DNS ready):" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'sudo apt install certbot python3-certbot-nginx -y'" -ForegroundColor Gray
Write-Host "   ssh ${Username}@${ServerIP} 'sudo certbot --nginx -d $Domain'" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Test akses domain:" -ForegroundColor White
Write-Host "   http://$Domain" -ForegroundColor Gray
Write-Host "   http://$Domain/health" -ForegroundColor Gray
Write-Host ""
