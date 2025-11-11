# 🚀 Tutorial Deployment ke Server VPS - Jargas APBN

docker-compose logs -f backend | grep -i migration

Tutorial ringkas untuk deployment ke VPS.

## 📋 Prasyarat

- SSH access: `ssh root@72.61.142.109`
- Project path: `~/jargas-wajo-batang-kendal`
- Docker & Docker Compose terinstall

---

## 🚀 Deployment Cepat

### Metode 1: Via GitHub (Recommended)

**Lokal:**
```powershell
cd "C:\Irman\Coding Jargas APBN\Jargas APBN"
git add . && git commit -m "Update" && git push origin main
```

**Server:**
```bash
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal
git pull origin main
docker-compose build --no-cache && docker-compose up -d
```

### Metode 2: Via SCP (Cepat)

```powershell
# Upload files
scp -r .\backend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/backend
scp -r .\frontend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/frontend

# Rebuild di server
ssh root@72.61.142.109 "cd ~/jargas-wajo-batang-kendal && docker-compose build --no-cache && docker-compose up -d"
```

### Script Otomatis

```powershell
# Dari Windows
.\scripts\deploy-with-migration.ps1
```

---

## 🔨 Rebuild Docker

```bash
# Di server
cd ~/jargas-wajo-batang-kendal
docker-compose build --no-cache
docker-compose up -d

# Rebuild service tertentu
docker-compose build --no-cache backend
docker-compose up -d backend
```

**Catatan:** Migration otomatis berjalan saat backend start (`AUTO_MIGRATE=True`).

### Fitur Auto-Migration

- ✅ **Deteksi database kosong** - Auto force migration untuk initial setup
- ✅ **Retry logic** - Otomatis retry 3x (delay 5 detik) jika error koneksi
- ✅ **Smart error handling** - Deteksi error dan retry otomatis

---

## ✅ Verifikasi

```bash
# Status container
docker-compose ps

# Log migration
docker-compose logs backend | grep -i migration

# Cek tabel database
docker-compose exec mysql mysql -u root -padmin123 jargas_apbn -e "SHOW TABLES;"

# Health check
curl http://localhost/health
```

**Akses:**
- Frontend: `https://jargas.ptkiansantang.com` (HTTPS) atau `http://72.61.142.109:8080` (HTTP)
- Backend: `https://jargas.ptkiansantang.com/api/v1/health` (HTTPS)
- Adminer: `http://72.61.142.109:8081` (HTTP, internal)

---

## 🔧 Troubleshooting

### Container tidak start
```bash
docker-compose logs backend
docker-compose restart
```

### Build gagal
```bash
docker-compose build --no-cache 2>&1 | tee build.log
docker system prune -a  # Clean up
```

### Database migration tidak jalan

**Auto-migrate sudah aktif** dengan fitur:
- Auto-detect database kosong → Force migration
- Retry 3x jika error koneksi

**Cek log:**
```bash
docker-compose logs backend | grep -i migration
docker-compose logs backend --tail 100
```

**Manual migration (jika perlu):**
```bash
docker-compose exec backend alembic upgrade head
# Atau dari Windows
.\scripts\run-migration-server.ps1
```

**Verifikasi:**
```bash
docker-compose exec backend alembic current
docker-compose exec mysql mysql -u root -padmin123 jargas_apbn -e "SHOW TABLES;"
```

---

## 🌐 Setup Domain (Opsional)

### 1. DNS Record
Tambahkan A Record di panel DNS:
```
Type: A
Name: jargas
Value: 72.61.142.109
```

### 2. Setup di Server
```powershell
# Dari Windows
.\nginx-host\setup-domain.ps1
```

Atau di server:
```bash
bash nginx-host/setup-domain.sh
```

### 3. Setup SSL/HTTPS (Let's Encrypt)

**Prasyarat:**
- Domain sudah pointing ke server (DNS A record)
- Domain bisa diakses via HTTP
- Port 80 dan 443 terbuka di firewall
- Nginx host sudah terinstall dan running

**Proses Setup:**

1. **Install Certbot:**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

2. **Generate SSL Certificate:**
```bash
sudo certbot --nginx -d jargas.ptkiansantang.com
```

Certbot akan:
- Generate certificate otomatis
- Update nginx config untuk HTTPS
- Setup auto-renewal

3. **Verifikasi SSL:**
```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Cek status certificate
sudo certbot certificates
```

4. **Update Nginx Config (jika perlu):**
Setelah SSL terpasang, uncomment bagian HTTPS di `/etc/nginx/sites-available/jargas`:
```bash
sudo nano /etc/nginx/sites-available/jargas
# Uncomment bagian HTTPS (baris 114-184)
# Uncomment redirect HTTP → HTTPS (baris 22-30)
sudo nginx -t
sudo systemctl reload nginx
```

**Hasil:**
- ✅ Domain bisa diakses via HTTPS: `https://jargas.ptkiansantang.com`
- ✅ HTTP otomatis redirect ke HTTPS
- ✅ Certificate auto-renewal setiap 90 hari

**Troubleshooting:**
```bash
# Cek nginx config
sudo nginx -t

# Cek certificate
sudo certbot certificates

# Manual renew (jika perlu)
sudo certbot renew

# Cek log
sudo tail -f /var/log/nginx/jargas_error.log
```

---

## 💡 Best Practices

1. **Backup sebelum update:**
   ```bash
   docker-compose exec mysql mysqldump -u root -padmin123 jargas_apbn > backup_$(date +%Y%m%d).sql
   ```

2. **Monitor setelah deployment:**
   ```bash
   docker-compose logs -f
   docker stats
   ```

3. **Gunakan Git untuk production** - Selalu commit & push sebelum deploy

---

## 📝 Checklist

- [ ] Kode sudah di-test di lokal
- [ ] Git commit & push (jika pakai Git)
- [ ] Container sudah di-rebuild
- [ ] Health check berhasil
- [ ] Migration berjalan (cek log)
- [ ] Domain sudah setup (DNS A record)
- [ ] Nginx host sudah dikonfigurasi
- [ ] SSL/HTTPS sudah terpasang (jika production)

---

## 🔄 Auto-Migration Features

### Fitur Utama

1. **Auto-Detection Database Kosong**
   - Deteksi otomatis jika database kosong
   - Force migration meskipun `AUTO_MIGRATE_ONLY_IF_PENDING=True`
   - Tidak perlu manual migration untuk initial setup

2. **Retry Logic**
   - Retry 3x dengan delay 5 detik
   - Deteksi error: `connection`, `timeout`, `refused`, `unreachable`
   - Aplikasi tetap berjalan meskipun migration gagal

3. **Logging Detail**
   - `🔍 Database kosong terdeteksi` → Initial migration
   - `⚠️ Database belum ready (attempt 1/3)` → Retry
   - `✅ Initial migration berhasil` → Success

### Cara Kerja

```
Startup → Cek AUTO_MIGRATE
→ Cek database kosong
→ Jika kosong → Force migration
→ Jika error koneksi → Retry 3x (delay 5 detik)
→ Log semua proses
```

### Konfigurasi

```yaml
# docker-compose.yml
AUTO_MIGRATE: ${AUTO_MIGRATE:-True}
AUTO_MIGRATE_ONLY_IF_PENDING: ${AUTO_MIGRATE_ONLY_IF_PENDING:-True}
MIGRATION_MODE: sequential
```

**Catatan:** Semua fitur sudah terintegrasi, tidak perlu setup manual.

---

## 🌿 Branch Strategy & Multi-Environment Deployment

### Overview

Project ini menggunakan 2 branch utama:
- **`main`** → Production → `https://jargas.ptkiansantang.com/`
- **`dev`** → Development → `https://devjargas.ptkiansantang.com/`

### Struktur Folder di Server

```
~/jargas-wajo-batang-kendal/          # Production
  ├── docker-compose.yml
  └── ...

~/jargas-wajo-batang-kendal-dev/      # Development
  ├── docker-compose.dev.yml
  └── ...
```

### Port Configuration

**Production:**
- Frontend: `8080`
- Backend: `8001`
- MySQL: `3308`
- Adminer: `8081`

**Development:**
- Frontend: `8082`
- Backend: `8002`
- MySQL: `3309`
- Adminer: `8083`

### Database

- **Production**: `jargas_apbn`
- **Development**: `jargas_apbn_dev` (terpisah)

### Deployment Production

**Lokal - Cara Update ke Branch Main (Setelah Testing di Dev):**

**⚠️ PENTING: Selalu test di dev terlebih dahulu sebelum push ke main!**

```powershell
# 1. Pastikan semua perubahan sudah di-test di dev
# 2. Pindah ke branch main
git checkout main

# 3. Pull update terbaru dari main
git pull origin main

# 4. Merge dev ke main
git merge dev

# 5. Resolve conflict jika ada (jika tidak ada conflict, skip langkah ini)
# Edit file yang conflict, lalu:
git add .
git commit -m "merge: Merge dev ke main"

# 6. Push ke main (akan deploy ke production)
git push origin main
```

**Atau dengan Rebase (untuk history yang lebih bersih):**
```powershell
git checkout main
git pull origin main
git rebase dev
git push origin main
```

**Server (Otomatis via GitHub Actions):**
- Auto-deploy saat push ke `main`
- Atau manual: `ssh root@72.61.142.109 'cd ~/jargas-wajo-batang-kendal && git pull origin main && docker-compose build --no-cache && docker-compose up -d'`

**Script Manual:**
```powershell
# Dari Windows
.\scripts\deploy-with-migration.ps1
```

**Verifikasi Setelah Push ke Main:**
1. Cek GitHub Actions: Repository → Actions → "Deploy Production"
2. Tunggu deployment selesai (biasanya 5-10 menit)
3. Akses: `https://jargas.ptkiansantang.com/`
4. Cek health: `https://jargas.ptkiansantang.com/api/v1/health`

### Deployment Development

**Lokal - Cara Update ke Branch Dev (Tidak Langsung ke Main):**

**Metode 1: Langsung Push ke Branch Dev (Recommended)**
```powershell
# 1. Pastikan Anda di branch dev
git checkout dev

# 2. Pull update terbaru dari dev (jika ada)
git pull origin dev

# 3. Cek status perubahan
git status

# 4. Tambahkan file yang diubah
git add .

# 5. Commit perubahan
git commit -m "feat: Deskripsi perubahan"

# 6. Push ke branch dev
git push origin dev
```

**Metode 2: Jika Lupa dan Sudah Commit di Branch Lain**
```powershell
# Jika sudah commit di branch lain, pindahkan ke dev
git checkout dev
git cherry-pick <commit-hash>
git push origin dev

# Atau merge branch lain ke dev
git checkout dev
git merge <nama-branch-lain>
git push origin dev
```

**Metode 3: Set Upstream (Hanya Sekali)**
```powershell
# Set upstream untuk branch dev (hanya sekali)
git checkout dev
git push -u origin dev

# Setelah ini, cukup ketik: git push
```

**Cek Branch Aktif:**
```powershell
# Cek branch yang sedang aktif
git branch

# Atau dengan status
git status

# Cek semua branch (lokal dan remote)
git branch -a
```

**Server (Otomatis via GitHub Actions):**
- Auto-deploy saat push ke `dev`
- Atau manual: `ssh root@72.61.142.109 'cd ~/jargas-wajo-batang-kendal-dev && git pull origin dev && docker-compose -f docker-compose.dev.yml build --no-cache && docker-compose -f docker-compose.dev.yml up -d'`

**Script Manual:**
```powershell
# Dari Windows
.\scripts\deploy-dev.ps1
```

**Verifikasi Setelah Push ke Dev:**
1. Cek GitHub Actions: Repository → Actions → "Deploy Development"
2. Tunggu deployment selesai (biasanya 5-10 menit)
3. Akses: `https://devjargas.ptkiansantang.com/`
4. Cek health: `https://devjargas.ptkiansantang.com/api/v1/health`

### Setup Awal Development Environment

1. **Clone repository ke folder dev:**
```bash
ssh root@72.61.142.109
cd ~
git clone <repository-url> jargas-wajo-batang-kendal-dev
cd jargas-wajo-batang-kendal-dev
git checkout dev
```

2. **Setup domain:**
```powershell
# Dari Windows
.\scripts\setup-dev-domain.ps1
```

3. **Setup SSL:**
```bash
# Di server
sudo certbot --nginx -d devjargas.ptkiansantang.com
```

4. **Deploy pertama kali:**
```powershell
# Dari Windows
.\scripts\deploy-dev.ps1
```

### GitHub Actions Setup

1. **Buat SSH Key Pair:**
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
```

2. **Copy public key ke server:**
```bash
ssh-copy-id -i ~/.ssh/github_actions.pub root@72.61.142.109
```

3. **Tambah SSH Private Key ke GitHub Secrets:**
   - GitHub Repository → Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `SSH_PRIVATE_KEY`
   - Value: Isi dari `~/.ssh/github_actions` (private key)

4. **Test Deployment:**
   - Push ke branch `main` → Auto-deploy production
   - Push ke branch `dev` → Auto-deploy development

### Perbedaan Update ke Dev vs Main

| Aspek | Branch Dev | Branch Main |
|-------|------------|------------|
| **Tujuan** | Testing & Development | Production |
| **Domain** | devjargas.ptkiansantang.com | jargas.ptkiansantang.com |
| **Database** | jargas_apbn_dev | jargas_apbn |
| **Port** | 8082, 8002, 3309, 8083 | 8080, 8001, 3308, 8081 |
| **Auto-Deploy** | ✅ Ya (via GitHub Actions) | ✅ Ya (via GitHub Actions) |
| **Kapan Update** | Setiap perubahan kode | Setelah testing di dev |
| **Risiko** | Rendah (tidak mempengaruhi production) | Tinggi (langsung ke production) |

### Best Practices

1. **Selalu test di dev sebelum merge ke main**
2. **Gunakan commit message yang jelas** (contoh: `feat:`, `fix:`, `refactor:`)
3. **Monitor deployment logs di GitHub Actions**
4. **Backup database sebelum deploy production**
5. **Gunakan feature branch untuk fitur besar**
6. **Jangan langsung push ke main** - selalu lewat dev dulu
7. **Cek branch aktif sebelum commit** - gunakan `git branch` atau `git status`

### Workflow Development

**Workflow Lengkap dari Development ke Production:**

```powershell
# 1. Buat feature branch dari dev
git checkout dev
git pull origin dev
git checkout -b feature/nama-fitur

# 2. Develop dan commit
git add .
git commit -m "feat: Tambah fitur baru"

# 3. Push ke feature branch
git push origin feature/nama-fitur

# 4. Test di development server (setelah merge ke dev)
git checkout dev
git merge feature/nama-fitur
git push origin dev  # Auto-deploy ke devjargas.ptkiansantang.com

# 5. Test di devjargas.ptkiansantang.com
# - Cek semua fitur berjalan dengan baik
# - Test edge cases
# - Verifikasi tidak ada bug

# 6. Setelah testing selesai, merge ke main untuk production
git checkout main
git pull origin main
git merge dev
git push origin main  # Auto-deploy ke jargas.ptkiansantang.com
```

**Workflow Cepat (Tanpa Feature Branch):**

```powershell
# Untuk perubahan kecil, bisa langsung ke dev
git checkout dev
git pull origin dev
git add .
git commit -m "fix: Perbaikan bug kecil"
git push origin dev  # Auto-deploy ke devjargas.ptkiansantang.com

# Setelah testing, merge ke main
git checkout main
git pull origin main
git merge dev
git push origin main  # Auto-deploy ke jargas.ptkiansantang.com
```

### Troubleshooting Multi-Environment

**Problem: Lupa Branch dan Sudah Commit di Branch Salah**

```powershell
# Cek di branch mana
git branch

# Jika sudah commit di branch salah, pindahkan ke dev
git checkout dev
git cherry-pick <commit-hash>
git push origin dev

# Atau reset commit (jika belum push)
git reset HEAD~1  # Hapus commit terakhir, tetap simpan perubahan
git checkout dev
git add .
git commit -m "feat: Perubahan"
git push origin dev
```

**Problem: Conflict Saat Merge Dev ke Main**

```powershell
git checkout main
git merge dev

# Jika ada conflict:
# 1. Edit file yang conflict
# 2. Resolve conflict (pilih perubahan yang benar)
# 3. git add .
# 4. git commit -m "merge: Resolve conflict dev ke main"
# 5. git push origin main
```

**Problem: Push ke Branch Salah**

```powershell
# Jika sudah push ke main padahal seharusnya dev
# 1. Revert commit di main
git checkout main
git revert <commit-hash>
git push origin main

# 2. Push ke dev
git checkout dev
git cherry-pick <commit-hash>
git push origin dev
```

**Problem: Branch Dev Tidak Update**

```powershell
# Pastikan branch dev sudah di-push
git checkout dev
git push origin dev

# Cek apakah branch dev ada di remote
git branch -r

# Jika belum ada, push dengan upstream
git push -u origin dev
```

**Problem: Deployment Dev Tidak Jalan**

1. **Cek GitHub Actions:**
   - Repository → Actions → "Deploy Development"
   - Lihat log error jika ada

2. **Cek Server:**
   ```bash
   ssh root@72.61.142.109
   cd ~/jargas-wajo-batang-kendal-dev
   git pull origin dev
   docker-compose -f docker-compose.dev.yml ps
   docker-compose -f docker-compose.dev.yml logs
   ```

3. **Manual Deploy:**
   ```powershell
   .\scripts\deploy-dev.ps1
   ```

---

### Script PowerShell untuk Push ke Branch Dev

Buat file `scripts/push-to-dev.ps1` untuk memudahkan push ke dev:

```powershell
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
```

**Cara menggunakan:**
```powershell
# Dengan default message
.\scripts\push-to-dev.ps1

# Dengan custom message
.\scripts\push-to-dev.ps1 -Message "feat: Tambah fitur export Excel"
```

---

**Terakhir diupdate:** 2025-01-27 (ditambahkan: Multi-Environment Deployment, Workflow Git Lengkap)
