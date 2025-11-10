# Script untuk memperbaiki database kosong di server
# Script ini akan menjalankan migration dan memastikan semua tabel dibuat

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Perbaiki Database Kosong di Server" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if SSH is available
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "SSH tidak ditemukan!" -ForegroundColor Red
    Write-Host "Install OpenSSH Client dari Settings > Apps > Optional Features" -ForegroundColor Yellow
    exit 1
}

Write-Host "Konfigurasi:" -ForegroundColor Yellow
Write-Host "   Server: ${Username}@${ServerIP}" -ForegroundColor Gray
Write-Host "   Path: $ProjectPath" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Lanjutkan perbaikan database? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Operasi dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1: Cek status containers..." -ForegroundColor Green
$psCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose ps'"
try {
    $status = Invoke-Expression $psCmd
    Write-Host $status -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Tidak bisa cek status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Pastikan semua containers running..." -ForegroundColor Green
$upCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose up -d'"
try {
    Invoke-Expression $upCmd
    Write-Host "✅ Containers started" -ForegroundColor Green
    Write-Host "⏳ Menunggu containers ready (40 detik)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 40
} catch {
    Write-Host "❌ Gagal start containers!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Cek apakah database jargas_apbn ada..." -ForegroundColor Green
$checkDbCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T mysql mysql -u root -padmin123 -e \"SHOW DATABASES;\" 2>/dev/null | grep jargas_apbn'"
try {
    $dbExists = Invoke-Expression $checkDbCmd
    if ($dbExists) {
        Write-Host "✅ Database jargas_apbn ditemukan" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Database jargas_apbn tidak ditemukan, akan dibuat otomatis" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek database" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Cek tabel yang ada saat ini..." -ForegroundColor Green
$checkTablesCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T mysql mysql -u root -padmin123 jargas_apbn -e \"SHOW TABLES;\" 2>/dev/null'"
try {
    $tables = Invoke-Expression $checkTablesCmd
    if ($tables -and $tables -match "Tables_in_jargas_apbn") {
        Write-Host "📋 Tabel yang ada:" -ForegroundColor Cyan
        Write-Host $tables -ForegroundColor Gray
        $tableCount = ($tables -split "`n" | Where-Object { $_ -match "Tables_in_jargas_apbn" -or ($_ -match "^\w" -and $_ -notmatch "Tables_in") }).Count
        if ($tableCount -gt 1) {
            Write-Host "✅ Ada $tableCount tabel di database" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Database masih kosong, akan menjalankan migration" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  Database kosong atau tidak ada tabel" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek tabel (mungkin database baru dibuat)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 5: Cek status migration saat ini..." -ForegroundColor Green
$currentCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T backend alembic current 2>&1'"
try {
    $current = Invoke-Expression $currentCmd
    Write-Host $current -ForegroundColor Gray
    if ($current -match "head" -or $current -match "revision") {
        Write-Host "✅ Migration sudah ada" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Belum ada migration yang dijalankan" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Belum ada migration yang dijalankan atau error" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 6: Jalankan migration ke head..." -ForegroundColor Green
Write-Host "⏳ Ini mungkin memakan waktu beberapa menit..." -ForegroundColor Yellow
$migrateCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T backend alembic upgrade head 2>&1'"
try {
    $result = Invoke-Expression $migrateCmd
    Write-Host $result -ForegroundColor Gray
    
    # Cek apakah berhasil
    if ($LASTEXITCODE -eq 0 -or $result -match "INFO.*Running upgrade" -or $result -match "INFO.*upgrade complete") {
        Write-Host "✅ Migration berhasil dijalankan" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Cek output di atas untuk detail" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Migration gagal!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Coba jalankan manual di server:" -ForegroundColor Yellow
    Write-Host "   ssh ${Username}@${ServerIP}" -ForegroundColor Gray
    Write-Host "   cd $ProjectPath" -ForegroundColor Gray
    Write-Host "   docker-compose exec backend alembic upgrade head" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "Step 7: Verifikasi migration setelah upgrade..." -ForegroundColor Green
$verifyCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T backend alembic current 2>&1'"
try {
    $verify = Invoke-Expression $verifyCmd
    Write-Host $verify -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Tidak bisa verifikasi" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 8: Verifikasi tabel database setelah migration..." -ForegroundColor Green
$finalTablesCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T mysql mysql -u root -padmin123 jargas_apbn -e \"SHOW TABLES;\" 2>/dev/null'"
try {
    $finalTables = Invoke-Expression $finalTablesCmd
    if ($finalTables) {
        Write-Host "✅ Tabel database setelah migration:" -ForegroundColor Green
        Write-Host $finalTables -ForegroundColor Gray
        
        # Hitung jumlah tabel
        $tableLines = $finalTables -split "`n" | Where-Object { $_ -match "^\w" -and $_ -notmatch "Tables_in" }
        $tableCount = $tableLines.Count
        if ($tableCount -gt 0) {
            Write-Host ""
            Write-Host "✅ Berhasil! Ada $tableCount tabel di database" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "⚠️  Masih belum ada tabel, cek log backend:" -ForegroundColor Yellow
            Write-Host "   docker-compose logs backend | grep -i migration" -ForegroundColor Gray
        }
    } else {
        Write-Host "⚠️  Tidak ada tabel atau database masih kosong" -ForegroundColor Yellow
        Write-Host "   Cek log backend untuk detail error" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Tidak bisa verifikasi tabel" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 9: Cek log backend untuk migration..." -ForegroundColor Green
$logCmd = "ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs backend --tail 50 2>&1 | grep -i migration || docker-compose logs backend --tail 50 2>&1'"
try {
    $logs = Invoke-Expression $logCmd
    if ($logs -match "migration" -or $logs -match "migrate") {
        Write-Host "📋 Migration logs:" -ForegroundColor Cyan
        Write-Host $logs -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek log" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Proses perbaikan selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Verifikasi di Adminer:" -ForegroundColor White
Write-Host "   http://jargas.ptkiansantang.com:8081/?server=mysql&username=root&db=jargas_apbn" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Jika masih kosong, cek log backend:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs backend --tail 100'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Restart backend jika perlu:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose restart backend'" -ForegroundColor Gray
Write-Host ""

