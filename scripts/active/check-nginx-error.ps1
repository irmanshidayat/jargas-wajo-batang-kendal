# Script untuk cek error nginx dan perbaiki

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔍 Cek Error Nginx" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Cek status nginx
Write-Host "Step 1: Cek Status Nginx..." -ForegroundColor Green
$statusCmd = "ssh ${Username}@${ServerIP} 'systemctl status nginx.service 2>&1 | head -20'"
try {
    $status = Invoke-Expression $statusCmd
    Write-Host $status -ForegroundColor Gray
} catch {
    Write-Host "   ⚠️  Error: $_" -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Test konfigurasi nginx
Write-Host "Step 2: Test Konfigurasi Nginx..." -ForegroundColor Green
$testCmd = "ssh ${Username}@${ServerIP} 'sudo nginx -t 2>&1'"
try {
    $testResult = Invoke-Expression $testCmd
    Write-Host $testResult -ForegroundColor Gray
    
    if ($testResult -match "successful") {
        Write-Host "   ✅ Konfigurasi nginx VALID" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Konfigurasi nginx ERROR!" -ForegroundColor Red
        Write-Host "   💡 Perbaiki error di atas" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}
Write-Host ""

# Step 3: Cek journal log
Write-Host "Step 3: Cek Journal Log (10 baris terakhir)..." -ForegroundColor Green
$journalCmd = "ssh ${Username}@${ServerIP} 'journalctl -xeu nginx.service --no-pager 2>&1 | tail -20'"
try {
    $journal = Invoke-Expression $journalCmd
    Write-Host $journal -ForegroundColor Gray
} catch {
    Write-Host "   ⚠️  Error: $_" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Cek error log nginx
Write-Host "Step 4: Cek Error Log Nginx (10 baris terakhir)..." -ForegroundColor Green
$errorLogCmd = "ssh ${Username}@${ServerIP} 'sudo tail -10 /var/log/nginx/error.log 2>/dev/null || echo LOG_NOT_FOUND'"
try {
    $errorLog = Invoke-Expression $errorLogCmd
    if ($errorLog -match "LOG_NOT_FOUND") {
        Write-Host "   ⚠️  Error log tidak ditemukan" -ForegroundColor Yellow
    } else {
        Write-Host $errorLog -ForegroundColor Red
    }
} catch {
    Write-Host "   ⚠️  Error: $_" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Cek syntax error di konfigurasi
Write-Host "Step 5: Cek Syntax Error di Konfigurasi..." -ForegroundColor Green
$syntaxCmd = "ssh ${Username}@${ServerIP} 'sudo nginx -T 2>&1 | head -50'"
try {
    $syntax = Invoke-Expression $syntaxCmd
    if ($syntax -match "error|failed|invalid") {
        Write-Host "   ❌ Ada error di konfigurasi:" -ForegroundColor Red
        Write-Host $syntax -ForegroundColor Red
    } else {
        Write-Host "   ✅ Tidak ada syntax error yang jelas" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Error: $_" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📋 Rekomendasi" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Jika ada error, perbaiki sesuai error message di atas" -ForegroundColor Yellow
Write-Host ""

