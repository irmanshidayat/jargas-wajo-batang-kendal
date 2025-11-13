# Script untuk reload nginx di server setelah update konfigurasi
# Test konfigurasi dan reload nginx via SSH

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔄 Reload Nginx di Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Konfigurasi:" -ForegroundColor Yellow
Write-Host "   Server: ${Username}@${ServerIP}" -ForegroundColor Gray
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
        Write-Host "   Script dihentikan. Perbaiki error nginx terlebih dahulu." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ Error saat test konfigurasi: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Reload nginx
Write-Host "Step 2: Reload Nginx..." -ForegroundColor Green
$reloadCmd = "ssh ${Username}@${ServerIP} 'sudo systemctl reload nginx 2>&1'"
try {
    $reloadResult = Invoke-Expression $reloadCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Nginx berhasil di-reload" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Reload nginx gagal: $reloadResult" -ForegroundColor Yellow
        Write-Host "   💡 Coba restart nginx: sudo systemctl restart nginx" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Error saat reload: $_" -ForegroundColor Yellow
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
    }
} catch {
    Write-Host "   ⚠️  Tidak bisa cek status: $_" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Test akses adminer via HTTPS
Write-Host "Step 4: Test Akses Adminer via HTTPS..." -ForegroundColor Green
Start-Sleep -Seconds 2
$testAccessCmd = "ssh ${Username}@${ServerIP} 'curl -s -o /dev/null -w `"HTTP Code: %{http_code}\n`" -k -H `"Host: jargas.ptkiansantang.com`" https://localhost/adminer 2>&1'"
try {
    $accessResponse = Invoke-Expression $testAccessCmd
    Write-Host $accessResponse -ForegroundColor Gray
    
    if ($accessResponse -match "HTTP Code: 200") {
        Write-Host "   ✅ Adminer bisa diakses via HTTPS (HTTP 200)" -ForegroundColor Green
        Write-Host ""
        Write-Host "   🌐 URL: https://jargas.ptkiansantang.com/adminer" -ForegroundColor Cyan
    } elseif ($accessResponse -match "HTTP Code: 30[12]") {
        Write-Host "   ⚠️  Adminer redirect (HTTP 301/302)" -ForegroundColor Yellow
    } elseif ($accessResponse -match "HTTP Code: 404") {
        Write-Host "   ❌ Adminer tidak ditemukan (HTTP 404)" -ForegroundColor Red
        Write-Host "   💡 Cek konfigurasi location /adminer di nginx" -ForegroundColor Yellow
    } elseif ($accessResponse -match "HTTP Code: 502|503|504") {
        Write-Host "   ❌ Gateway error (HTTP $($matches[0]))" -ForegroundColor Red
        Write-Host "   💡 Cek apakah container adminer berjalan" -ForegroundColor Yellow
    } else {
        Write-Host "   ⚠️  Response: $accessResponse" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Tidak bisa test akses: $_" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Proses Selesai" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test akses dari browser:" -ForegroundColor Yellow
Write-Host "   https://jargas.ptkiansantang.com/adminer" -ForegroundColor Cyan
Write-Host ""

