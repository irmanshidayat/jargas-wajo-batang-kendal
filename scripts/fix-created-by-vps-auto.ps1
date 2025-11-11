# Script untuk memperbaiki error login: Unknown column 'users.created_by'
# Script ini akan menambahkan kolom created_by ke tabel users di VPS secara otomatis
# Usage: .\fix-created-by-vps-auto.ps1

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal",
    [string]$DbPassword = "admin123",
    [string]$DbName = "jargas_apbn",
    [string]$ContainerName = "jargas_mysql"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Error Login: created_by Column (VPS)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if SSH is available
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ SSH tidak ditemukan!" -ForegroundColor Red
    Write-Host "   Install OpenSSH Client dari Settings > Apps > Optional Features" -ForegroundColor Yellow
    exit 1
}

Write-Host "Konfigurasi:" -ForegroundColor Yellow
Write-Host "   Server: ${Username}@${ServerIP}" -ForegroundColor Gray
Write-Host "   Project Path: $ProjectPath" -ForegroundColor Gray
Write-Host "   Container: $ContainerName" -ForegroundColor Gray
Write-Host "   Database: $DbName" -ForegroundColor Gray
Write-Host ""

# Step 1: Upload SQL file ke server
Write-Host "Step 1: Upload script SQL ke server..." -ForegroundColor Green
$sqlFile = Join-Path $PSScriptRoot "fix_created_by_users.sql"
if (-not (Test-Path $sqlFile)) {
    Write-Host "❌ File SQL tidak ditemukan: $sqlFile" -ForegroundColor Red
    exit 1
}

$remoteSqlPath = "/tmp/fix_created_by_users.sql"
try {
    $scpCmd = "scp `"$sqlFile`" ${Username}@${ServerIP}:${remoteSqlPath}"
    Invoke-Expression $scpCmd
    Write-Host "✅ File SQL berhasil diupload" -ForegroundColor Green
} catch {
    Write-Host "❌ Gagal upload file SQL: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Jalankan SQL script di container MySQL
Write-Host "Step 2: Menjalankan script SQL di container MySQL..." -ForegroundColor Green
$runSqlCmd = "ssh ${Username}@${ServerIP} bash -c `"docker exec -i $ContainerName mysql -u root -p$DbPassword $DbName < $remoteSqlPath`""
try {
    $output = & ssh "${Username}@${ServerIP}" "bash -c `"docker exec -i $ContainerName mysql -u root -p$DbPassword $DbName < $remoteSqlPath`"" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Script SQL berhasil dijalankan" -ForegroundColor Green
        if ($output) {
            Write-Host $output -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠️  Warning: Exit code $LASTEXITCODE" -ForegroundColor Yellow
        if ($output) {
            Write-Host $output -ForegroundColor Gray
        }
        # Coba metode alternatif
        Write-Host "   Mencoba metode alternatif..." -ForegroundColor Yellow
        $altOutput = & ssh "${Username}@${ServerIP}" "cat $remoteSqlPath | docker exec -i $ContainerName mysql -u root -p$DbPassword $DbName" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Script SQL berhasil dijalankan (metode alternatif)" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "⚠️  Warning: $_" -ForegroundColor Yellow
    Write-Host "   Mencoba metode alternatif..." -ForegroundColor Yellow
    try {
        $altOutput = & ssh "${Username}@${ServerIP}" "cat $remoteSqlPath | docker exec -i $ContainerName mysql -u root -p$DbPassword $DbName" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Script SQL berhasil dijalankan (metode alternatif)" -ForegroundColor Green
        } else {
            Write-Host "❌ Gagal menjalankan script SQL" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Gagal menjalankan script SQL: $_" -ForegroundColor Red
    }
}

Write-Host ""

# Step 3: Verifikasi kolom created_by sudah ada
Write-Host "Step 3: Verifikasi kolom created_by..." -ForegroundColor Green
try {
    $verifyResult = & ssh "${Username}@${ServerIP}" "docker exec -i $ContainerName mysql -u root -p$DbPassword $DbName -e 'DESCRIBE users;' 2>/dev/null | grep created_by" 2>&1
    if ($verifyResult -and $verifyResult -match "created_by") {
        Write-Host "✅ Kolom created_by berhasil ditambahkan!" -ForegroundColor Green
        Write-Host "   $verifyResult" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Kolom created_by belum terdeteksi (mungkin perlu waktu)" -ForegroundColor Yellow
        Write-Host "   Coba verifikasi manual dengan:" -ForegroundColor Yellow
        Write-Host "   ssh ${Username}@${ServerIP} 'docker exec -i $ContainerName mysql -u root -p$DbPassword $DbName -e \"DESCRIBE users;\"'" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Tidak bisa verifikasi (mungkin kolom sudah ada atau ada error)" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Cleanup - Hapus file SQL dari server
Write-Host "Step 4: Cleanup file temporary..." -ForegroundColor Green
try {
    & ssh "${Username}@${ServerIP}" "rm -f $remoteSqlPath" | Out-Null
    Write-Host "✅ File temporary dihapus" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Gagal hapus file temporary (tidak masalah)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Proses Selesai!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 Kolom created_by sudah ditambahkan ke tabel users" -ForegroundColor Green
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Coba login lagi sebagai admin di:" -ForegroundColor White
Write-Host "   http://jargas.ptkiansantang.com" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Jika masih error, restart backend container:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose restart backend'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Cek log backend untuk memastikan tidak ada error:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs backend --tail 50'" -ForegroundColor Gray
Write-Host ""

