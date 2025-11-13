# Script untuk test dan restart nginx setelah fix

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔧 Fix dan Restart Nginx" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Test konfigurasi nginx
Write-Host "Step 1: Test Konfigurasi Nginx..." -ForegroundColor Green
$testCmd = "ssh ${Username}@${ServerIP} 'sudo nginx -t 2>&1'"
try {
    $testResult = Invoke-Expression $testCmd
    Write-Host $testResult -ForegroundColor Gray
    
    if ($testResult -match "successful") {
        Write-Host "   ✅ Konfigurasi nginx VALID" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Konfigurasi nginx ERROR!" -ForegroundColor Red
        Write-Host ""
        Write-Host "   Script dihentikan. Perbaiki error terlebih dahulu." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Restart nginx
Write-Host "Step 2: Restart Nginx..." -ForegroundColor Green
$restartCmd = "ssh ${Username}@${ServerIP} 'sudo systemctl restart nginx 2>&1'"
try {
    $restartResult = Invoke-Expression $restartCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Nginx berhasil di-restart" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } else {
        Write-Host "   ❌ Restart gagal: $restartResult" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Cek status nginx
Write-Host "Step 3: Cek Status Nginx..." -ForegroundColor Green
$statusCmd = "ssh ${Username}@${ServerIP} 'systemctl is-active nginx 2>&1'"
try {
    $status = Invoke-Expression $statusCmd
    if ($status -eq "active") {
        Write-Host "   ✅ Nginx BERJALAN" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Nginx TIDAK BERJALAN (status: $status)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ⚠️  Error: $_" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Test akses adminer
Write-Host "Step 4: Test Akses Adminer..." -ForegroundColor Green
Start-Sleep -Seconds 2
$testAccessCmd = "ssh ${Username}@${ServerIP} 'curl -s -k -H `"Host: jargas.ptkiansantang.com`" https://localhost/adminer | head -30'"
try {
    $accessResponse = Invoke-Expression $testAccessCmd
    Write-Host $accessResponse -ForegroundColor Gray
    
    if ($accessResponse -match "Adminer|adminer|Login.*database|Database|System:|Server:") {
        Write-Host "   ✅ Adminer bisa diakses!" -ForegroundColor Green
        Write-Host ""
        Write-Host "   🌐 URL: https://jargas.ptkiansantang.com/adminer" -ForegroundColor Cyan
    } elseif ($accessResponse -match "Jargas APBN|vite\.svg|index\.html") {
        Write-Host "   ❌ Masih mengembalikan frontend!" -ForegroundColor Red
        Write-Host "   💡 Location /adminer mungkin tidak match" -ForegroundColor Yellow
    } else {
        Write-Host "   ⚠️  Response tidak jelas" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Error: $_" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Proses Selesai" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

