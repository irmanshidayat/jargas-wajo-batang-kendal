# PowerShell Script untuk Setup Nginx Host dari Windows
# Script ini akan membantu setup nginx di server Linux via SSH

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerIP,
    
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [string]$SSHKey = "",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Setup Nginx Host untuk Jargas APBN" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
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

Write-Host "📋 Konfigurasi:" -ForegroundColor Yellow
Write-Host "   Server: ${Username}@${ServerIP}" -ForegroundColor Gray
Write-Host "   Project Path: $ProjectPath" -ForegroundColor Gray
Write-Host ""

# Commands to run on server
$setupCommands = @"
cd $ProjectPath && \
if [ ! -f nginx-host/jargas.conf ]; then
    echo '❌ File konfigurasi tidak ditemukan!'
    exit 1
fi && \
echo '📝 Copy konfigurasi...' && \
sudo cp nginx-host/jargas.conf /etc/nginx/sites-available/jargas && \
echo '🔗 Buat symbolic link...' && \
sudo ln -sf /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas && \
echo '📦 Hapus default config...' && \
sudo rm -f /etc/nginx/sites-enabled/default && \
echo '🧪 Test konfigurasi nginx...' && \
sudo nginx -t && \
echo '🔄 Reload nginx...' && \
sudo systemctl reload nginx && \
echo '' && \
echo '✅ Setup selesai!' && \
echo '' && \
echo '📊 Status:' && \
sudo systemctl status nginx --no-pager -l | head -5 && \
echo '' && \
echo '🏥 Test health check:' && \
curl -s http://localhost/health || echo '⚠️  Health check gagal (container mungkin belum ready)'
"@

Write-Host "🚀 Menjalankan setup di server..." -ForegroundColor Green
Write-Host ""

# Execute commands
$fullCommand = "$sshCmd `"$setupCommands`""
Invoke-Expression $fullCommand

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📋 Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Rebuild container frontend:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose build frontend && docker-compose up -d frontend'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test akses:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'curl http://localhost/health'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Edit domain (jika ada):" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'sudo nano /etc/nginx/sites-available/jargas'" -ForegroundColor Gray
Write-Host "   (ubah server_name _; menjadi domain Anda)" -ForegroundColor Gray
Write-Host ""

