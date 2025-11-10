# Script Setup Otomatis Nginx Host - JALANKAN DI WINDOWS
# Script ini akan melakukan setup nginx di server via SSH

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Nginx Host untuk Jargas APBN" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if SSH is available
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "SSH tidak ditemukan!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install OpenSSH Client:" -ForegroundColor Yellow
    Write-Host "1. Buka Settings > Apps > Optional Features" -ForegroundColor Gray
    Write-Host "2. Add a feature > OpenSSH Client" -ForegroundColor Gray
    Write-Host ""
    Write-Host "ATAU gunakan WSL/PuTTY" -ForegroundColor Yellow
    exit 1
}

# Get server information
Write-Host "Masukkan informasi server:" -ForegroundColor Yellow
Write-Host ""

$ServerIP = Read-Host "IP Server (contoh: 192.168.1.100 atau domain.com)"
$Username = Read-Host "Username SSH (contoh: root)"
$ProjectPath = Read-Host "Path project di server (tekan Enter untuk default: ~/jargas-wajo-batang-kendal)"

if ([string]::IsNullOrWhiteSpace($ProjectPath)) {
    $ProjectPath = "~/jargas-wajo-batang-kendal"
}

Write-Host ""
Write-Host "Konfigurasi:" -ForegroundColor Yellow
$serverInfo = "$Username@$ServerIP"
Write-Host "   Server: $serverInfo" -ForegroundColor Gray
Write-Host "   Path: $ProjectPath" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Lanjutkan setup? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Setup dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Menjalankan setup di server..." -ForegroundColor Green
Write-Host ""

# Check if config file exists locally
$localConfigFile = "nginx-host\jargas.conf"
if (-not (Test-Path $localConfigFile)) {
    Write-Host "File konfigurasi tidak ditemukan di lokal: $localConfigFile" -ForegroundColor Red
    Write-Host "Pastikan file ada sebelum menjalankan setup!" -ForegroundColor Yellow
    exit 1
}

Write-Host "Mengupload file konfigurasi ke server..." -ForegroundColor Gray
# Upload config file using SCP
$scpCommand = "scp `"$localConfigFile`" ${Username}@${ServerIP}:${ProjectPath}/nginx-host/jargas.conf"
try {
    Invoke-Expression $scpCommand
    Write-Host "File berhasil diupload" -ForegroundColor Green
} catch {
    Write-Host "Warning: Upload file gagal, pastikan file sudah ada di server" -ForegroundColor Yellow
    Write-Host "Atau upload manual dengan: $scpCommand" -ForegroundColor Gray
}

Write-Host ""

# Commands to run on server (using single line to avoid line ending issues)
# Escape variables properly for bash
$setupCommands = "cd $ProjectPath && if [ ! -f nginx-host/jargas.conf ]; then echo 'ERROR: File konfigurasi tidak ditemukan!'; echo 'Pastikan file nginx-host/jargas.conf ada di server'; exit 1; fi && echo 'Step 1: Copy konfigurasi...' && sudo cp nginx-host/jargas.conf /etc/nginx/sites-available/jargas && echo 'Config copied' && echo 'Step 2: Buat symbolic link...' && if [ -L /etc/nginx/sites-enabled/jargas ]; then sudo rm /etc/nginx/sites-enabled/jargas; fi && sudo ln -sf /etc/nginx/sites-available/jargas /etc/nginx/sites-enabled/jargas && echo 'Symlink created' && echo 'Step 3: Hapus default config...' && sudo rm -f /etc/nginx/sites-enabled/default && echo 'Default config removed' && echo 'Step 4: Test konfigurasi nginx...' && if sudo nginx -t; then echo 'Nginx configuration is valid'; else echo 'Nginx configuration error!'; exit 1; fi && echo 'Step 5: Reload nginx...' && sudo systemctl reload nginx && echo 'Nginx reloaded' && echo 'Step 6: Check nginx status...' && if sudo systemctl is-active --quiet nginx; then echo 'Nginx is running' && echo 'Testing health endpoint...' && if curl -s http://localhost/health > /dev/null; then echo 'Health check passed'; else echo 'Health check failed (container mungkin belum ready)'; fi && echo 'Setup selesai!'; else echo 'Nginx tidak berjalan!'; sudo systemctl status nginx --no-pager -l | head -10; exit 1; fi"

# Execute SSH command
try {
    $sshTarget = "$Username@$ServerIP"
    # Use bash -c to avoid line ending issues (CRLF from Windows)
    # Properly escape the command for SSH
    $escapedCommands = $setupCommands -replace "'", "''"
    $sshCommand = "ssh $sshTarget bash -c `"$escapedCommands`""
    Write-Host "Menghubungkan ke server dan menjalankan setup..." -ForegroundColor Gray
    Invoke-Expression $sshCommand
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Setup Selesai!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Rebuild container frontend:" -ForegroundColor White
    $rebuildCmd = "ssh $sshTarget 'cd $ProjectPath && docker-compose build frontend && docker-compose up -d frontend'"
    Write-Host "   $rebuildCmd" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Test akses:" -ForegroundColor White
    $testCmd = "ssh $sshTarget 'curl http://localhost/health'"
    Write-Host "   $testCmd" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Edit domain (jika ada):" -ForegroundColor White
    $editCmd = "ssh $sshTarget 'sudo nano /etc/nginx/sites-available/jargas'"
    Write-Host "   $editCmd" -ForegroundColor Gray
    Write-Host "   (ubah server_name menjadi domain Anda)" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "Error saat menjalankan setup!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Pastikan SSH key sudah di-setup atau password sudah benar" -ForegroundColor Gray
    Write-Host "2. Pastikan file nginx-host/jargas.conf ada di server" -ForegroundColor Gray
    Write-Host "3. Pastikan user memiliki akses sudo" -ForegroundColor Gray
    $sshTestCmd = "ssh $sshTarget"
    Write-Host "4. Cek koneksi: $sshTestCmd" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
