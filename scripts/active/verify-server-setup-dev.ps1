# Script untuk Verifikasi Setup Server Development
# Script ini akan mengecek semua requirement untuk deployment development

param(
    [string]$ServerIP = "72.61.142.109",
    [string]$Username = "root",
    [string]$ProjectPath = "~/jargas-wajo-batang-kendal-dev"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Verifikasi Setup Server Development" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()

# Check 1: SSH Connection
Write-Host "1. Testing SSH connection..." -ForegroundColor Yellow
try {
    $test = ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ${Username}@${ServerIP} "echo 'SSH OK'" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ SSH connection successful" -ForegroundColor Green
    } else {
        $errors += "SSH connection failed"
        Write-Host "   ❌ SSH connection failed" -ForegroundColor Red
    }
} catch {
    $errors += "SSH connection error: $_"
    Write-Host "   ❌ SSH connection error" -ForegroundColor Red
}

# Check 2: Project Path Exists
Write-Host ""
Write-Host "2. Checking project path..." -ForegroundColor Yellow
$pathCheck = ssh ${Username}@${ServerIP} "test -d $ProjectPath && echo 'EXISTS' || echo 'NOT_EXISTS'" 2>&1
if ($pathCheck -match "EXISTS") {
    Write-Host "   ✅ Project path exists: $ProjectPath" -ForegroundColor Green
} else {
    $errors += "Project path does not exist: $ProjectPath"
    Write-Host "   ❌ Project path does not exist: $ProjectPath" -ForegroundColor Red
    Write-Host "   💡 Create it with: ssh ${Username}@${ServerIP} 'mkdir -p $ProjectPath'" -ForegroundColor Gray
}

# Check 3: Git Repository
Write-Host ""
Write-Host "3. Checking Git repository..." -ForegroundColor Yellow
$gitCheck = ssh ${Username}@${ServerIP} "cd $ProjectPath 2>/dev/null && git rev-parse --git-dir 2>/dev/null && echo 'GIT_OK' || echo 'NOT_GIT'" 2>&1
if ($gitCheck -match "GIT_OK") {
    Write-Host "   ✅ Git repository found" -ForegroundColor Green
    
    # Check if dev branch exists
    $branchCheck = ssh ${Username}@${ServerIP} "cd $ProjectPath && git branch -r | grep origin/dev && echo 'BRANCH_OK' || echo 'NO_BRANCH'" 2>&1
    if ($branchCheck -match "BRANCH_OK") {
        Write-Host "   ✅ Dev branch exists in remote" -ForegroundColor Green
    } else {
        $warnings += "Dev branch not found in remote"
        Write-Host "   ⚠️  Dev branch not found in remote" -ForegroundColor Yellow
    }
} else {
    $warnings += "Git repository not initialized or path incorrect"
    Write-Host "   ⚠️  Git repository not found" -ForegroundColor Yellow
    Write-Host "   💡 Initialize with: ssh ${Username}@${ServerIP} 'cd $ProjectPath && git init && git remote add origin <repo-url>'" -ForegroundColor Gray
}

# Check 4: Environment Files
Write-Host ""
Write-Host "4. Checking environment files..." -ForegroundColor Yellow
$envRootCheck = ssh ${Username}@${ServerIP} "test -f $ProjectPath/.env.dev && echo 'EXISTS' || echo 'NOT_EXISTS'" 2>&1
if ($envRootCheck -match "EXISTS") {
    Write-Host "   ✅ .env.dev found in root" -ForegroundColor Green
} else {
    $errors += ".env.dev not found in project root"
    Write-Host "   ❌ .env.dev not found in root" -ForegroundColor Red
    Write-Host "   💡 Copy from: env.dev.example or create manually" -ForegroundColor Gray
}

$envBackendCheck = ssh ${Username}@${ServerIP} "test -f $ProjectPath/backend/.env.dev && echo 'EXISTS' || echo 'NOT_EXISTS'" 2>&1
if ($envBackendCheck -match "EXISTS") {
    Write-Host "   ✅ backend/.env.dev found" -ForegroundColor Green
} else {
    $errors += "backend/.env.dev not found"
    Write-Host "   ❌ backend/.env.dev not found" -ForegroundColor Red
    Write-Host "   💡 Copy from: backend/env.dev.example or create manually" -ForegroundColor Gray
}

# Check 5: Docker Compose File
Write-Host ""
Write-Host "5. Checking docker-compose.dev.yml..." -ForegroundColor Yellow
$dockerComposeCheck = ssh ${Username}@${ServerIP} "test -f $ProjectPath/docker-compose.dev.yml && echo 'EXISTS' || echo 'NOT_EXISTS'" 2>&1
if ($dockerComposeCheck -match "EXISTS") {
    Write-Host "   ✅ docker-compose.dev.yml found" -ForegroundColor Green
} else {
    $errors += "docker-compose.dev.yml not found"
    Write-Host "   ❌ docker-compose.dev.yml not found" -ForegroundColor Red
}

# Check 6: Docker Installation
Write-Host ""
Write-Host "6. Checking Docker installation..." -ForegroundColor Yellow
$dockerCheck = ssh ${Username}@${ServerIP} "command -v docker >/dev/null 2>&1 && echo 'INSTALLED' || echo 'NOT_INSTALLED'" 2>&1
if ($dockerCheck -match "INSTALLED") {
    Write-Host "   ✅ Docker is installed" -ForegroundColor Green
    
    # Check Docker service
    $dockerService = ssh ${Username}@${ServerIP} "systemctl is-active docker 2>/dev/null && echo 'ACTIVE' || echo 'INACTIVE'" 2>&1
    if ($dockerService -match "ACTIVE") {
        Write-Host "   ✅ Docker service is running" -ForegroundColor Green
    } else {
        $warnings += "Docker service may not be running"
        Write-Host "   ⚠️  Docker service status unclear" -ForegroundColor Yellow
    }
} else {
    $errors += "Docker is not installed"
    Write-Host "   ❌ Docker is not installed" -ForegroundColor Red
}

# Check 7: Docker Compose Installation
Write-Host ""
Write-Host "7. Checking Docker Compose installation..." -ForegroundColor Yellow
$dockerComposeCmd = ssh ${Username}@${ServerIP} "command -v docker-compose >/dev/null 2>&1 && echo 'INSTALLED' || (docker compose version >/dev/null 2>&1 && echo 'DOCKER_COMPOSE_V2' || echo 'NOT_INSTALLED')" 2>&1
if ($dockerComposeCmd -match "INSTALLED|DOCKER_COMPOSE_V2") {
    Write-Host "   ✅ Docker Compose is available" -ForegroundColor Green
} else {
    $errors += "Docker Compose is not installed"
    Write-Host "   ❌ Docker Compose is not installed" -ForegroundColor Red
}

# Check 8: Current Container Status
Write-Host ""
Write-Host "8. Checking current container status..." -ForegroundColor Yellow
$containerStatus = ssh ${Username}@${ServerIP} "cd $ProjectPath 2>/dev/null && docker-compose -f docker-compose.dev.yml --env-file .env.dev ps 2>/dev/null || echo 'ERROR'" 2>&1
if ($containerStatus -notmatch "ERROR") {
    Write-Host "   Container status:" -ForegroundColor Gray
    $containerStatus | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "   ⚠️  Cannot check container status (may be normal if not deployed yet)" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✅ All checks passed! Server is ready for deployment." -ForegroundColor Green
} elseif ($errors.Count -eq 0) {
    Write-Host "⚠️  Some warnings found, but deployment should work:" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
} else {
    Write-Host "❌ Errors found that need to be fixed:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Host "⚠️  Warnings:" -ForegroundColor Yellow
        $warnings | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
    }
    Write-Host ""
    Write-Host "💡 Fix the errors above before deploying." -ForegroundColor Cyan
    exit 1
}

Write-Host ""

