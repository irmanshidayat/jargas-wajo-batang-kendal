# Script untuk memperbaiki kolom yang missing di database VPS
# Script ini akan menambahkan kolom-kolom yang diperlukan untuk DELETE user
# Usage: .\fix-missing-columns-vps.ps1

param(
    [string]$DbHost = "localhost",
    [string]$DbUser = "root",
    [string]$DbPassword = "",
    [string]$DbName = "jargas_apbn",
    [int]$DbPort = 3306
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Missing Columns di Database VPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cek apakah file SQL ada
$sqlFile = Join-Path $PSScriptRoot "fix_missing_columns_vps.sql"
if (-not (Test-Path $sqlFile)) {
    Write-Host "❌ File SQL tidak ditemukan: $sqlFile" -ForegroundColor Red
    exit 1
}

Write-Host "📄 File SQL ditemukan: $sqlFile" -ForegroundColor Green
Write-Host ""

# Build MySQL command
$mysqlCmd = "mysql"
$mysqlArgs = @(
    "-h", $DbHost,
    "-P", $DbPort,
    "-u", $DbUser
)

if ($DbPassword) {
    $mysqlArgs += "-p$DbPassword"
}

$mysqlArgs += $DbName

Write-Host "🔧 Menjalankan script SQL..." -ForegroundColor Yellow
Write-Host "   Host: $DbHost" -ForegroundColor Gray
Write-Host "   Port: $DbPort" -ForegroundColor Gray
Write-Host "   Database: $DbName" -ForegroundColor Gray
Write-Host ""

try {
    # Read SQL file and execute
    $sqlContent = Get-Content $sqlFile -Raw -Encoding UTF8
    $sqlContent | & $mysqlCmd $mysqlArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Script berhasil dijalankan!" -ForegroundColor Green
        Write-Host "   Kolom-kolom yang diperlukan sudah ditambahkan ke database." -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Kolom yang ditambahkan:" -ForegroundColor Cyan
        Write-Host "   - surat_permintaans.status" -ForegroundColor White
        Write-Host "   - surat_jalans.nomor_surat_permintaan" -ForegroundColor White
        Write-Host "   - surat_jalans.nomor_barang_keluar" -ForegroundColor White
        Write-Host "   - surat_jalans.stock_out_id" -ForegroundColor White
        Write-Host ""
        Write-Host "🎉 Sekarang fitur DELETE user seharusnya sudah berfungsi!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Error saat menjalankan script SQL" -ForegroundColor Red
        Write-Host "   Exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

