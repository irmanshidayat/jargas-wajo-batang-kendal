# Script untuk push Docker images ke GitHub Container Registry (GHCR)
# Usage: .\scripts\push-to-ghcr.ps1 -GitHubUsername "username" -GitHubToken "token" -Version "v1.0.0"

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [string]$Version = "latest",
    
    [switch]$SkipBuild = $false,
    
    [switch]$BuildOnly = $false
)

# Set error action
$ErrorActionPreference = "Stop"

# Colors
function Write-Step {
    param([string]$Message)
    Write-Host "`n$Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "$Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "$Message" -ForegroundColor Red
}

# Validate Docker is running
Write-Step "Validating Docker..."
try {
    docker info | Out-Null
    Write-Success "Docker is running"
} catch {
    Write-Error "Docker is not running. Please start Docker Desktop."
    exit 1
}

# Login to GHCR
Write-Step "Logging in to GHCR..."
try {
    echo $GitHubToken | docker login ghcr.io -u $GitHubUsername --password-stdin
    if ($LASTEXITCODE -ne 0) {
        throw "Login failed"
    }
    Write-Success "Successfully logged in to GHCR"
} catch {
    Write-Error "Failed to login to GHCR. Please check your token and username."
    exit 1
}

# Build images (if not skipped)
if (-not $SkipBuild) {
    Write-Step "Building Frontend image..."
    try {
        docker build -t ghcr.io/$GitHubUsername/jargas-apbn-frontend:$Version ./frontend
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend build failed"
        }
        Write-Success "Frontend image built successfully"
    } catch {
        Write-Error "Failed to build Frontend image"
        exit 1
    }

    Write-Step "Building Backend image..."
    try {
        docker build -t ghcr.io/$GitHubUsername/jargas-apbn-backend:$Version ./backend
        if ($LASTEXITCODE -ne 0) {
            throw "Backend build failed"
        }
        Write-Success "Backend image built successfully"
    } catch {
        Write-Error "Failed to build Backend image"
        exit 1
    }
} else {
    Write-Step "Skipping build (using existing images)..."
}

# Tag latest
Write-Step "Tagging images as latest..."
try {
    docker tag ghcr.io/$GitHubUsername/jargas-apbn-frontend:$Version ghcr.io/$GitHubUsername/jargas-apbn-frontend:latest
    docker tag ghcr.io/$GitHubUsername/jargas-apbn-backend:$Version ghcr.io/$GitHubUsername/jargas-apbn-backend:latest
    Write-Success "Images tagged as latest"
} catch {
    Write-Error "Failed to tag images"
    exit 1
}

# Push images (if not build-only)
if (-not $BuildOnly) {
    Write-Step "Pushing Frontend image..."
    try {
        docker push ghcr.io/$GitHubUsername/jargas-apbn-frontend:$Version
        docker push ghcr.io/$GitHubUsername/jargas-apbn-frontend:latest
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend push failed"
        }
        Write-Success "Frontend image pushed successfully"
    } catch {
        Write-Error "Failed to push Frontend image"
        exit 1
    }

    Write-Step "Pushing Backend image..."
    try {
        docker push ghcr.io/$GitHubUsername/jargas-apbn-backend:$Version
        docker push ghcr.io/$GitHubUsername/jargas-apbn-backend:latest
        if ($LASTEXITCODE -ne 0) {
            throw "Backend push failed"
        }
        Write-Success "Backend image pushed successfully"
    } catch {
        Write-Error "Failed to push Backend image"
        exit 1
    }
} else {
    Write-Step "Build-only mode: Skipping push..."
}

# Summary
Write-Host "`n" -NoNewline
Write-Success "=========================================="
Write-Success "Summary"
Write-Success "=========================================="
Write-Success "GitHub Username: $GitHubUsername"
Write-Success "Version: $Version"
Write-Success "Frontend Image: ghcr.io/$GitHubUsername/jargas-apbn-frontend:$Version"
Write-Success "Backend Image: ghcr.io/$GitHubUsername/jargas-apbn-backend:$Version"
Write-Success "=========================================="

if (-not $BuildOnly) {
    Write-Host "`nImages are now available at:" -ForegroundColor Yellow
    Write-Host "  https://github.com/$GitHubUsername?tab=packages" -ForegroundColor Yellow
    Write-Host "`nDon't forget to set package visibility in GitHub!" -ForegroundColor Yellow
}

Write-Host "`nDone! ✅" -ForegroundColor Green

