# Script untuk memperbaiki error login: Unknown column 'users.created_by'
# Script ini akan menambahkan kolom created_by ke tabel users
# Usage: .\fix-created-by-users.ps1

param(
    [string]$DbHost = "localhost",
    [string]$DbUser = "root",
    [string]$DbPassword = "",
    [string]$DbName = "jargas_apbn",
    [int]$DbPort = 3306
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Error Login: created_by Column" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cek apakah file SQL ada
$sqlFile = Join-Path $PSScriptRoot "fix_created_by_users.sql"
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

Write-Host "🔧 Menjalankan script SQL untuk menambahkan kolom created_by..." -ForegroundColor Yellow
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
        Write-Host "   Kolom created_by sudah ditambahkan ke tabel users." -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 Error login seharusnya sudah teratasi!" -ForegroundColor Green
        Write-Host "   Silakan coba login lagi sebagai admin." -ForegroundColor Green
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

