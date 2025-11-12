# Script untuk push perubahan ke branch dev
param(
    [string]$Message = "Update development"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Push ke Branch Dev" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Cek branch aktif
$currentBranch = git branch --show-current
Write-Host "Branch aktif: $currentBranch" -ForegroundColor Yellow

if ($currentBranch -ne "dev") {
    Write-Host "⚠️  Anda tidak di branch dev!" -ForegroundColor Yellow
    $switch = Read-Host "Switch ke branch dev? (y/n)"
    if ($switch -eq "y" -or $switch -eq "Y") {
        git checkout dev
        Write-Host "✅ Switched ke branch dev" -ForegroundColor Green
    } else {
        Write-Host "❌ Push dibatalkan" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Step 1: Pull update terbaru..." -ForegroundColor Green
git pull origin dev
Write-Host "✅ Pull berhasil" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Cek status perubahan..." -ForegroundColor Green
git status

Write-Host ""
$confirm = Read-Host "Lanjutkan push ke dev? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Push dibatalkan." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 3: Add perubahan..." -ForegroundColor Green
git add .
Write-Host "✅ Files added" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Commit..." -ForegroundColor Green
git commit -m $Message
Write-Host "✅ Committed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Push ke dev..." -ForegroundColor Green
git push origin dev
Write-Host "✅ Pushed to dev" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Push ke Dev Selesai!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Langkah Selanjutnya:" -ForegroundColor Yellow
Write-Host "1. Cek GitHub Actions untuk deployment" -ForegroundColor White
Write-Host "2. Tunggu deployment selesai (5-10 menit)" -ForegroundColor White
Write-Host "3. Test di: https://devjargas.ptkiansantang.com" -ForegroundColor White
Write-Host ""

