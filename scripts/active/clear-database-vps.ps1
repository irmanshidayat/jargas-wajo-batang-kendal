# Script untuk menghapus semua data database di VPS
# Kecuali tabel: users, roles, pages, permissions
# Script ini akan menjalankan script Python via SSH

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal",
    [switch]$Force
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Hapus Data Database VPS (Kecuali Users)" -ForegroundColor Cyan
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

Write-Host "PERINGATAN:" -ForegroundColor Red
Write-Host "   Script ini akan menghapus SEMUA DATA dari database jargas_apbn" -ForegroundColor Yellow
Write-Host "   KECUALI tabel berikut:" -ForegroundColor Yellow
Write-Host "   - users" -ForegroundColor Green
Write-Host "   - roles" -ForegroundColor Green
Write-Host "   - pages" -ForegroundColor Green
Write-Host "   - permissions" -ForegroundColor Green
Write-Host ""
Write-Host "   Operasi ini TIDAK DAPAT DIBATALKAN setelah dikonfirmasi!" -ForegroundColor Red
Write-Host ""

if (-not $Force) {
    $confirm = Read-Host "Lanjutkan? (y/n)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "Operasi dibatalkan." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "Step 1: Cek koneksi ke server..." -ForegroundColor Green
$testConnection = "ssh ${Username}@${ServerIP} `"echo OK`""
try {
    $result = Invoke-Expression $testConnection
    if ($result -eq "OK") {
        Write-Host "✅ Koneksi berhasil" -ForegroundColor Green
    } else {
        Write-Host "❌ Koneksi gagal" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Tidak bisa terhubung ke server: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Cek status container backend..." -ForegroundColor Green
$checkContainer = "ssh ${Username}@${ServerIP} `"cd $ProjectPath && docker-compose ps backend`""
try {
    $containerStatus = Invoke-Expression $checkContainer
    if ($containerStatus -match "Up") {
        Write-Host "✅ Container backend sedang berjalan" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Container backend tidak berjalan" -ForegroundColor Yellow
        Write-Host "   Mencoba start container..." -ForegroundColor Yellow
        $startCmd = "ssh ${Username}@${ServerIP} `"cd $ProjectPath && docker-compose up -d backend`""
        Invoke-Expression $startCmd
        Write-Host "   Menunggu container ready (10 detik)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek status container: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Memastikan script Python ada di server..." -ForegroundColor Green
$scriptPath = "backend/scripts/clear_database_except_users.py"
$checkScriptCmd = "ssh ${Username}@${ServerIP} `"test -f $ProjectPath/$scriptPath && echo 'EXISTS' || echo 'NOT_EXISTS'`""
try {
    $scriptExists = Invoke-Expression $checkScriptCmd
    if ($scriptExists -match "NOT_EXISTS") {
        Write-Host "⚠️  Script Python belum ada di server" -ForegroundColor Yellow
        Write-Host "   Mencoba push ke git atau copy file..." -ForegroundColor Yellow
        
        # Cek apakah ada perubahan yang belum di-push
        $gitStatus = git status --porcelain 2>$null
        if ($gitStatus) {
            Write-Host "   Ada perubahan yang belum di-commit" -ForegroundColor Yellow
            Write-Host "   Silakan commit dan push terlebih dahulu, atau copy file manual" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "   Atau copy file manual dengan:" -ForegroundColor Cyan
            Write-Host "   scp backend\scripts\clear_database_except_users.py ${Username}@${ServerIP}:$ProjectPath/backend/scripts/" -ForegroundColor Gray
            Write-Host ""
            $copyConfirm = Read-Host "Copy file sekarang? (y/n)"
            if ($copyConfirm -eq "y" -or $copyConfirm -eq "Y") {
                Write-Host "   Copying file..." -ForegroundColor Yellow
                $scpCmd = "scp backend\scripts\clear_database_except_users.py ${Username}@${ServerIP}:$ProjectPath/backend/scripts/"
                Invoke-Expression $scpCmd
                Write-Host "   ✅ File berhasil di-copy" -ForegroundColor Green
            } else {
                Write-Host "   Operasi dibatalkan. Silakan copy file manual atau push ke git terlebih dahulu." -ForegroundColor Yellow
                exit 0
            }
        } else {
            Write-Host "   Mencoba pull dari git di server..." -ForegroundColor Yellow
            $gitPullCmd = "ssh ${Username}@${ServerIP} `"cd $ProjectPath && git pull origin main`""
            Invoke-Expression $gitPullCmd
            Write-Host "   ✅ Git pull selesai" -ForegroundColor Green
        }
        
        # Rebuild backend container untuk memastikan file ter-copy
        Write-Host "   Rebuild backend container..." -ForegroundColor Yellow
        $rebuildCmd = "ssh ${Username}@${ServerIP} `"cd $ProjectPath && docker-compose build --no-cache backend && docker-compose up -d backend`""
        Invoke-Expression $rebuildCmd
        Write-Host "   Menunggu container ready (15 detik)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
    } else {
        Write-Host "✅ Script Python sudah ada di server" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Tidak bisa cek script: $_" -ForegroundColor Yellow
    Write-Host "   Lanjutkan dengan asumsi script sudah ada..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Menjalankan script penghapusan data..." -ForegroundColor Green
Write-Host "   (Script akan meminta konfirmasi lagi di server)" -ForegroundColor Gray
Write-Host ""

# Command untuk menjalankan script Python di dalam container backend
# Gunakan double quotes dan escape yang benar untuk PowerShell
$scriptCmd = "ssh ${Username}@${ServerIP} `"cd $ProjectPath && docker-compose exec -T backend python -m scripts.clear_database_except_users`""

try {
    # Jalankan script dan tampilkan output real-time
    Invoke-Expression $scriptCmd
    
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-Host "⚠️  Script mengembalikan exit code: $exitCode" -ForegroundColor Yellow
        Write-Host "   Periksa output di atas untuk detail error" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Proses Selesai!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Verifikasi data yang tersisa:" -ForegroundColor White
    Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose exec -T mysql mysql -u root -padmin123 jargas_apbn -e \"SELECT COUNT(*) as users_count FROM users;\"'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Cek log jika ada masalah:" -ForegroundColor White
    Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs backend --tail 50'" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Error saat menjalankan script!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Cek log untuk detail:" -ForegroundColor Yellow
    Write-Host "   ssh ${Username}@${ServerIP} 'cd $ProjectPath && docker-compose logs backend --tail 100'" -ForegroundColor Gray
    exit 1
}

