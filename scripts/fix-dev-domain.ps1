# PowerShell Script untuk Fix Domain Development - devjargas.ptkiansantang.com
# Script ini akan diagnose dan fix masalah domain development

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$Domain = "devjargas.ptkiansantang.com"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fix Domain Development" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Domain: $Domain" -ForegroundColor Yellow
Write-Host "Server: ${Username}@${ServerIP}" -ForegroundColor Yellow
Write-Host ""

# Step 1: Diagnose masalah
Write-Host "Step 1: Diagnose masalah..." -ForegroundColor Green
Write-Host ""

# Cek apakah nginx config sudah ada
Write-Host "1.1 Cek nginx config..." -ForegroundColor Cyan
$checkConfig = "ssh ${Username}@${ServerIP} 'test -f /etc/nginx/sites-available/jargas-dev && echo EXISTS || echo NOT_EXISTS'"
$configStatus = Invoke-Expression $checkConfig | Out-String
$configStatus = $configStatus.Trim()

if ($configStatus -eq "EXISTS") {
    Write-Host "   [OK] Nginx config ditemukan" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Nginx config TIDAK ditemukan!" -ForegroundColor Red
    Write-Host "   Akan di-setup sekarang..." -ForegroundColor Yellow
}

# Cek apakah symlink sudah ada
Write-Host ""
Write-Host "1.2 Cek nginx symlink..." -ForegroundColor Cyan
$checkSymlink = "ssh ${Username}@${ServerIP} 'test -L /etc/nginx/sites-enabled/jargas-dev && echo EXISTS || echo NOT_EXISTS'"
$symlinkStatus = Invoke-Expression $checkSymlink | Out-String
$symlinkStatus = $symlinkStatus.Trim()

if ($symlinkStatus -eq "EXISTS") {
    Write-Host "   [OK] Nginx symlink ditemukan" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Nginx symlink TIDAK ditemukan!" -ForegroundColor Red
    Write-Host "   Akan di-setup sekarang..." -ForegroundColor Yellow
}

# Cek container status
Write-Host ""
Write-Host "1.3 Cek container status..." -ForegroundColor Cyan
$checkContainer = "ssh ${Username}@${ServerIP} 'cd ~/jargas-wajo-batang-kendal-dev && docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo NOT_FOUND'"
$containerStatus = Invoke-Expression $checkContainer | Out-String

if ($containerStatus -match "Up") {
    Write-Host "   [OK] Container running" -ForegroundColor Green
    Write-Host "   $containerStatus" -ForegroundColor Gray
} else {
    Write-Host "   [ERROR] Container TIDAK running!" -ForegroundColor Red
    Write-Host "   Akan di-start sekarang..." -ForegroundColor Yellow
}

# Cek port 8082 dan 8002
Write-Host ""
Write-Host "1.4 Cek port 8082 (frontend) dan 8002 (backend)..." -ForegroundColor Cyan
$checkPorts = @"
ssh ${Username}@${ServerIP} 'netstat -tuln | grep -E "8082|8002" || echo NO_PORTS'
"@
$portStatus = Invoke-Expression $checkPorts | Out-String

if ($portStatus -match "8082" -or $portStatus -match "8002") {
    Write-Host "   [OK] Port listening" -ForegroundColor Green
    Write-Host "   $portStatus" -ForegroundColor Gray
} else {
    Write-Host "   [ERROR] Port TIDAK listening!" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 2: Fix masalah..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Fix 1: Upload dan setup nginx config
if ($configStatus -ne "EXISTS" -or $symlinkStatus -ne "EXISTS") {
    Write-Host "2.1 Upload nginx config..." -ForegroundColor Yellow
    
    # Dapatkan path absolut file config
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $projectRoot = Split-Path -Parent $scriptPath
    $configFile = Join-Path $projectRoot "nginx-host\jargas-dev.conf"
    
    # Cek apakah file lokal ada
    if (-not (Test-Path $configFile)) {
        Write-Host "   [ERROR] File config tidak ditemukan: $configFile" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "   Mengupload dari: $configFile" -ForegroundColor Gray
    $copyCmd = "scp `"$configFile`" ${Username}@${ServerIP}:~/jargas-dev.conf"
    try {
        $uploadResult = Invoke-Expression $copyCmd 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "SCP failed with exit code $LASTEXITCODE"
        }
        Write-Host "   [OK] Config file ter-upload" -ForegroundColor Green
    } catch {
        Write-Host "   [ERROR] Upload config gagal!" -ForegroundColor Red
        Write-Host "   Error: $_" -ForegroundColor Red
        Write-Host "   Output: $uploadResult" -ForegroundColor Red
        exit 1
    }

    # Verifikasi file sudah ter-upload
    Write-Host ""
    Write-Host "2.2 Verifikasi file ter-upload..." -ForegroundColor Yellow
    $verifyUpload = "ssh ${Username}@${ServerIP} 'test -f ~/jargas-dev.conf && echo EXISTS || echo NOT_EXISTS'"
    $uploadStatus = Invoke-Expression $verifyUpload | Out-String
    $uploadStatus = $uploadStatus.Trim()
    
    if ($uploadStatus -ne "EXISTS") {
        Write-Host "   [ERROR] File tidak ditemukan di server setelah upload!" -ForegroundColor Red
        exit 1
    }
    Write-Host "   [OK] File terverifikasi di server" -ForegroundColor Green

    Write-Host ""
    Write-Host "2.3 Setup nginx config di server..." -ForegroundColor Yellow
    $setupCmd = @"
ssh ${Username}@${ServerIP} '
    if [ -f ~/jargas-dev.conf ]; then
        # Disable default nginx config jika ada
        if [ -L /etc/nginx/sites-enabled/default ]; then
            sudo rm /etc/nginx/sites-enabled/default
            echo "Default nginx config disabled"
        fi
        
        # Copy dan enable config jargas-dev
        sudo cp ~/jargas-dev.conf /etc/nginx/sites-available/jargas-dev &&
        sudo ln -sf /etc/nginx/sites-available/jargas-dev /etc/nginx/sites-enabled/jargas-dev &&
        sudo nginx -t &&
        sudo systemctl reload nginx &&
        echo "SUCCESS"
    else
        echo "ERROR: File ~/jargas-dev.conf tidak ditemukan"
        exit 1
    fi
'
"@
    try {
        $setupResult = Invoke-Expression $setupCmd | Out-String
        if ($setupResult -match "SUCCESS") {
            Write-Host "   [OK] Nginx config berhasil di-setup" -ForegroundColor Green
        } else {
            throw "Setup failed: $setupResult"
        }
    } catch {
        Write-Host "   [ERROR] Setup nginx config gagal!" -ForegroundColor Red
        Write-Host "   Error: $_" -ForegroundColor Red
        Write-Host "   Output: $setupResult" -ForegroundColor Red
        Write-Host ""
        Write-Host "   Coba manual:" -ForegroundColor Yellow
        Write-Host "   ssh ${Username}@${ServerIP}" -ForegroundColor Gray
        Write-Host "   sudo cp ~/jargas-dev.conf /etc/nginx/sites-available/jargas-dev" -ForegroundColor Gray
        Write-Host "   sudo ln -sf /etc/nginx/sites-available/jargas-dev /etc/nginx/sites-enabled/jargas-dev" -ForegroundColor Gray
        Write-Host "   sudo nginx -t" -ForegroundColor Gray
        Write-Host "   sudo systemctl reload nginx" -ForegroundColor Gray
        exit 1
    }
} else {
    Write-Host "2.1 Nginx config sudah ada, skip..." -ForegroundColor Gray
}

# Fix 2: Start container jika belum running
if ($containerStatus -notmatch "Up") {
    Write-Host ""
    Write-Host "2.4 Start container..." -ForegroundColor Yellow
    $startContainer = "ssh ${Username}@${ServerIP} 'cd ~/jargas-wajo-batang-kendal-dev && docker-compose -f docker-compose.dev.yml up -d'"
    try {
        Invoke-Expression $startContainer
        Write-Host "   [OK] Container di-start" -ForegroundColor Green
        Write-Host "   [WAIT] Tunggu 30 detik untuk container ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    } catch {
        Write-Host "   [ERROR] Start container gagal!" -ForegroundColor Red
        Write-Host "   Error: $_" -ForegroundColor Red
        Write-Host "   Coba manual: ssh ${Username}@${ServerIP} 'cd ~/jargas-wajo-batang-kendal-dev && docker-compose -f docker-compose.dev.yml up -d'" -ForegroundColor Yellow
    }
} else {
    Write-Host "2.4 Container sudah running, skip..." -ForegroundColor Gray
}

# Fix 3: Disable default nginx config jika masih ada
Write-Host ""
Write-Host "2.5 Disable default nginx config..." -ForegroundColor Yellow
$disableDefault = @"
ssh ${Username}@${ServerIP} 'if [ -L /etc/nginx/sites-enabled/default ]; then sudo rm /etc/nginx/sites-enabled/default && echo "DISABLED" || echo "NOT_FOUND"; else echo "ALREADY_DISABLED"; fi'
"@
try {
    $disableResult = Invoke-Expression $disableDefault | Out-String
    $disableResult = $disableResult.Trim()
    if ($disableResult -match "DISABLED") {
        Write-Host "   [OK] Default nginx config disabled" -ForegroundColor Green
    } elseif ($disableResult -match "ALREADY_DISABLED") {
        Write-Host "   [OK] Default nginx config sudah disabled" -ForegroundColor Gray
    } else {
        Write-Host "   [INFO] Default nginx config tidak ditemukan" -ForegroundColor Gray
    }
} catch {
    Write-Host "   [WARNING] Tidak bisa disable default config" -ForegroundColor Yellow
}

# Fix 4: Reload nginx untuk memastikan
Write-Host ""
Write-Host "2.6 Reload nginx..." -ForegroundColor Yellow
$reloadNginx = "ssh ${Username}@${ServerIP} 'sudo nginx -t && sudo systemctl reload nginx'"
try {
    Invoke-Expression $reloadNginx
    Write-Host "   [OK] Nginx reloaded" -ForegroundColor Green
} catch {
    Write-Host "   [WARNING] Reload nginx gagal, coba manual" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Step 3: Verifikasi..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verifikasi container
Write-Host "3.1 Verifikasi container..." -ForegroundColor Cyan
$verifyContainer = "ssh ${Username}@${ServerIP} 'cd ~/jargas-wajo-batang-kendal-dev && docker-compose -f docker-compose.dev.yml ps'"
try {
    $containerInfo = Invoke-Expression $verifyContainer
    Write-Host $containerInfo -ForegroundColor Gray
} catch {
    Write-Host "   [WARNING] Tidak bisa cek container status" -ForegroundColor Yellow
}

# Verifikasi nginx config
Write-Host ""
Write-Host "3.2 Verifikasi nginx config..." -ForegroundColor Cyan
$verifyNginx = "ssh ${Username}@${ServerIP} 'sudo nginx -t'"
try {
    Invoke-Expression $verifyNginx
    Write-Host "   [OK] Nginx config valid" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Nginx config error!" -ForegroundColor Red
}

# Verifikasi enabled sites
Write-Host ""
Write-Host "3.2.1 Verifikasi enabled nginx sites..." -ForegroundColor Cyan
$checkEnabled = @"
ssh ${Username}@${ServerIP} 'ls -la /etc/nginx/sites-enabled/ | grep -E "jargas-dev|default"'
"@
try {
    $enabledSites = Invoke-Expression $checkEnabled | Out-String
    if ($enabledSites -match "jargas-dev") {
        Write-Host "   [OK] jargas-dev config enabled" -ForegroundColor Green
    } else {
        Write-Host "   [ERROR] jargas-dev config TIDAK enabled!" -ForegroundColor Red
    }
    if ($enabledSites -match "default") {
        Write-Host "   [WARNING] Default nginx config masih enabled!" -ForegroundColor Yellow
    } else {
        Write-Host "   [OK] Default nginx config disabled" -ForegroundColor Green
    }
    Write-Host "   Enabled sites:" -ForegroundColor Gray
    Write-Host $enabledSites -ForegroundColor Gray
} catch {
    Write-Host "   [WARNING] Tidak bisa cek enabled sites" -ForegroundColor Yellow
}

# Test health endpoint
Write-Host ""
Write-Host "3.3 Test health endpoint..." -ForegroundColor Cyan
$testHealth = "ssh ${Username}@${ServerIP} 'curl -s http://localhost:8002/health || echo FAILED'"
try {
    $healthResponse = Invoke-Expression $testHealth | Out-String
    $healthResponse = $healthResponse.Trim()
    if ($healthResponse -match "healthy" -or $healthResponse -match "ok") {
        Write-Host "   [OK] Health check berhasil" -ForegroundColor Green
    } else {
        Write-Host "   [WARNING] Health check: $healthResponse" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   [WARNING] Health check gagal (container mungkin masih starting)" -ForegroundColor Yellow
}

# Test frontend
Write-Host ""
Write-Host "3.4 Test frontend..." -ForegroundColor Cyan
$testFrontend = "ssh ${Username}@${ServerIP} 'curl -s -I http://localhost:8082/ | head -1 || echo FAILED'"
try {
    $frontendResponse = Invoke-Expression $testFrontend | Out-String
    if ($frontendResponse -match "200" -or $frontendResponse -match "301" -or $frontendResponse -match "302") {
        Write-Host "   [OK] Frontend accessible" -ForegroundColor Green
    } else {
        Write-Host "   [WARNING] Frontend response: $frontendResponse" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   [WARNING] Frontend test gagal" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "[OK] Fix Domain Development Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Tunggu beberapa menit untuk container fully ready" -ForegroundColor White
Write-Host "2. Test akses domain:" -ForegroundColor White
Write-Host "   https://$Domain" -ForegroundColor Gray
Write-Host "   https://$Domain/api/v1/health" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Jika masih ada masalah, cek log:" -ForegroundColor White
Write-Host "   ssh ${Username}@${ServerIP} 'cd ~/jargas-wajo-batang-kendal-dev && docker-compose -f docker-compose.dev.yml logs'" -ForegroundColor Gray
Write-Host "   ssh ${Username}@${ServerIP} 'sudo tail -f /var/log/nginx/jargas_dev_error.log'" -ForegroundColor Gray
Write-Host ""

