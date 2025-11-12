# Script untuk Setup SSH Key GitHub Actions ke Server
# Script ini akan copy public key ke server agar GitHub Actions bisa SSH

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$SSHKeyPath = "$env:USERPROFILE\.ssh\github_actions"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup SSH Key untuk GitHub Actions" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if SSH key exists
if (-not (Test-Path $SSHKeyPath)) {
    Write-Host "❌ SSH key tidak ditemukan: $SSHKeyPath" -ForegroundColor Red
    Write-Host "   Generate SSH key terlebih dahulu:" -ForegroundColor Yellow
    Write-Host "   ssh-keygen -t ed25519 -C `"github-actions`" -f `"$SSHKeyPath`"" -ForegroundColor Gray
    exit 1
}

if (-not (Test-Path "$SSHKeyPath.pub")) {
    Write-Host "❌ Public key tidak ditemukan: $SSHKeyPath.pub" -ForegroundColor Red
    exit 1
}

Write-Host "Konfigurasi:" -ForegroundColor Yellow
Write-Host "   Server: ${Username}@${ServerIP}" -ForegroundColor Gray
Write-Host "   SSH Key: $SSHKeyPath" -ForegroundColor Gray
Write-Host ""

# Read public key
$publicKey = Get-Content "$SSHKeyPath.pub" -Raw
Write-Host "Public Key:" -ForegroundColor Yellow
Write-Host $publicKey.Trim() -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Copy public key ke server? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Setup dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Copy public key ke server..." -ForegroundColor Green

# Try ssh-copy-id first (if available)
$sshCopyIdCmd = "ssh-copy-id -i `"$SSHKeyPath.pub`" ${Username}@${ServerIP}"
try {
    Write-Host "   Mencoba ssh-copy-id..." -ForegroundColor Gray
    Invoke-Expression $sshCopyIdCmd 2>&1 | Out-Null
    Write-Host "✅ Public key berhasil di-copy menggunakan ssh-copy-id" -ForegroundColor Green
} catch {
    Write-Host "   ssh-copy-id tidak tersedia, menggunakan metode manual..." -ForegroundColor Yellow
    
    # Manual method: append to authorized_keys
    $manualCmd = "echo '$($publicKey.Trim())' | ssh ${Username}@${ServerIP} 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'"
    
    try {
        Invoke-Expression $manualCmd
        Write-Host "✅ Public key berhasil di-copy secara manual" -ForegroundColor Green
    } catch {
        Write-Host "❌ Gagal copy public key!" -ForegroundColor Red
        Write-Host "   Error: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 Alternatif: Copy manual" -ForegroundColor Yellow
        Write-Host "   1. Buka: $SSHKeyPath.pub" -ForegroundColor Gray
        Write-Host "   2. Copy isinya" -ForegroundColor Gray
        Write-Host "   3. SSH ke server: ssh ${Username}@${ServerIP}" -ForegroundColor Gray
        Write-Host "   4. Jalankan: echo 'PUBLIC_KEY_CONTENT' >> ~/.ssh/authorized_keys" -ForegroundColor Gray
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Verifikasi SSH connection..." -ForegroundColor Green

# Test SSH connection
$testCmd = "ssh -i `"$SSHKeyPath`" -o StrictHostKeyChecking=no ${Username}@${ServerIP} 'echo `"SSH connection berhasil!`"'"
try {
    $result = Invoke-Expression $testCmd 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSH connection berhasil!" -ForegroundColor Green
        Write-Host $result -ForegroundColor Gray
    } else {
        Write-Host "⚠️  SSH connection test gagal, tapi key mungkin sudah di-copy" -ForegroundColor Yellow
        Write-Host "   Coba test manual: ssh -i `"$SSHKeyPath`" ${Username}@${ServerIP}" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Tidak bisa test SSH connection sekarang" -ForegroundColor Yellow
    Write-Host "   Tapi public key sudah di-copy ke server" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup SSH Key Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Langkah selanjutnya:" -ForegroundColor Yellow
Write-Host "   1. Pastikan GitHub Secret SSH_PRIVATE_KEY sudah ditambahkan" -ForegroundColor White
Write-Host "   2. Test deployment dengan push ke branch dev" -ForegroundColor White
Write-Host ""

