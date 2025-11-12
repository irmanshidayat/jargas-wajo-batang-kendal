# 🚀 Tutorial Deployment ke Server VPS - Jargas APBN

Tutorial ringkas untuk deployment ke VPS dengan 2 subdomain (Production & Development).

## 📋 Prasyarat

- SSH access: `ssh root@72.61.142.109`
- Docker & Docker Compose terinstall
- Git repository sudah setup

---

## 🌿 Overview: 2 Environment

| Aspek | Production | Development |
|-------|-----------|-------------|
| **Branch** | `main` | `dev` |
| **Domain** | `jargas.ptkiansantang.com` | `devjargas.ptkiansantang.com` |
| **Path Server** | `~/jargas-wajo-batang-kendal` | `~/jargas-wajo-batang-kendal-dev` |
| **Docker Compose** | `docker-compose.yml` | `docker-compose.dev.yml` |
| **Environment** | `.env` | `.env.dev` |
| **Database** | `jargas_apbn` | `jargas_apbn_dev` |
| **Port** | 8080, 8001, 3308, 8081 | 8082, 8002, 3309, 8083 |

---

## 🚀 Deployment Cepat

### Via GitHub Actions (Recommended - Auto Deploy)

**Production:**
```powershell
git checkout main
git add . && git commit -m "Update" && git push origin main
# Auto-deploy via GitHub Actions → https://jargas.ptkiansantang.com
```

**Development:**
```powershell
git checkout dev
git add . && git commit -m "Update" && git push origin dev
# Auto-deploy via GitHub Actions → https://devjargas.ptkiansantang.com
```

test

### Manual Deploy (Jika GitHub Actions Tidak Aktif)

**Production:**
```bash
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal
git pull origin main
docker-compose --env-file .env build --no-cache && docker-compose --env-file .env up -d
```

**Development:**
```bash
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal-dev
git pull origin dev
docker-compose -f docker-compose.dev.yml --env-file .env.dev build --no-cache && docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d
```

### Script PowerShell

```powershell
# Production
.\scripts\active\deploy-production.ps1

# Development
.\scripts\active\deploy-dev.ps1
```

---

## 🔨 Rebuild Docker

**Production:**
```bash
cd ~/jargas-wajo-batang-kendal
docker-compose --env-file .env build --no-cache
docker-compose --env-file .env up -d
```

**Development:**
```bash
cd ~/jargas-wajo-batang-kendal-dev
docker-compose -f docker-compose.dev.yml --env-file .env.dev build --no-cache
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d
```

**Catatan:** Migration otomatis berjalan saat backend start (`AUTO_MIGRATE=True`).

---

## ✅ Verifikasi

**Cek Container:**
```bash
# Production
docker-compose --env-file .env ps

# Development
docker-compose -f docker-compose.dev.yml --env-file .env.dev ps
```

**Health Check:**
```bash
# Production
curl https://jargas.ptkiansantang.com/api/v1/health

# Development
curl https://devjargas.ptkiansantang.com/api/v1/health
```

**Log Migration:**
```bash
# Production
docker-compose --env-file .env logs backend | grep -i migration

# Development
docker-compose -f docker-compose.dev.yml --env-file .env.dev logs backend | grep -i migration
```

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
docker system prune -a
```

### Migration tidak jalan
```bash
# Cek log
docker-compose logs backend | grep -i migration

# Manual migration
docker-compose exec backend alembic upgrade head
```

---

## 🤖 GitHub Actions Setup

### Setup Awal (Hanya Sekali)

1. **Generate SSH Key:**
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
```

2. **Copy Public Key ke Server:**
```bash
ssh-copy-id -i ~/.ssh/github_actions.pub root@72.61.142.109
```

3. **Tambah Private Key ke GitHub Secrets:**
   - Buka repository di GitHub
   - Klik **Settings** → **Secrets and variables** → **Actions**
   - Klik **New repository secret**
   - **Name**: `SSH_PRIVATE_KEY` (harus sama persis, case-sensitive)
   - **Value**: Copy seluruh isi dari file `~/.ssh/github_actions` (termasuk `-----BEGIN OPENSSH PRIVATE KEY-----` dan `-----END OPENSSH PRIVATE KEY-----`)
   - Klik **Add secret**
   .
   **Cara copy private key di Windows PowerShell:**
   ```powershell
   Get-Content "$env:USERPROFILE\.ssh\github_actions" | Set-Clipboard
   ```
   Lalu paste ke GitHub Secret value.

### Cara Kerja

- **Push ke `main`** → Auto-deploy Production
- **Push ke `dev`** → Auto-deploy Development
- **Manual trigger:** GitHub → Actions → Run workflow

### Monitoring

- Repository → Actions → Lihat workflow run
- Cek log step-by-step
- Verifikasi deployment summary

### Troubleshooting GitHub Actions

**Error: "The ssh-private-key argument is empty"**
- ❌ **Penyebab**: GitHub Secret `SSH_PRIVATE_KEY` belum dikonfigurasi atau nama secret salah
- ✅ **Solusi**:
  1. Buka GitHub Repository → Settings → Secrets and variables → Actions
  2. Pastikan ada secret dengan nama **`SSH_PRIVATE_KEY`** (case-sensitive, tanpa spasi)
  3. Jika belum ada, tambahkan dengan cara di atas
  4. Jika sudah ada, cek apakah value-nya benar (harus termasuk BEGIN dan END lines)
  5. Setelah update secret, jalankan ulang workflow: Actions → Deploy Development → Run workflow

**Error: "Permission denied"**
- Verifikasi SSH key sudah di-copy ke server dengan: `ssh-copy-id -i ~/.ssh/github_actions.pub root@72.61.142.109`
- Cek GitHub Secret `SSH_PRIVATE_KEY` sudah benar
- Test SSH connection: `ssh -i ~/.ssh/github_actions root@72.61.142.109`

**Error: ".env files not found"**
- Pastikan file `.env.dev` dan `backend/.env.dev` ada di server di path `~/jargas-wajo-batang-kendal-dev`
- Jika belum ada, copy dari local atau buat manual di server

**Error: "Health check failed"**
- Tunggu lebih lama (migration mungkin masih berjalan, bisa sampai 2-3 menit)
- Cek container logs: `docker-compose -f docker-compose.dev.yml --env-file .env.dev logs backend`
- Pastikan backend container sudah running: `docker-compose -f docker-compose.dev.yml --env-file .env.dev ps`

---

## 📝 Workflow Git

### Update ke Dev (Development)

```powershell
git checkout dev
git pull origin dev
git add .
git commit -m "feat: Deskripsi perubahan"
git push origin dev  # Auto-deploy ke devjargas.ptkiansantang.com
```

### Update ke Main (Production)

**⚠️ PENTING: Selalu test di dev terlebih dahulu!**

```powershell
git checkout main
git pull origin main
git merge dev
git push origin main  # Auto-deploy ke jargas.ptkiansantang.com
```

### Workflow Lengkap

```powershell
# 1. Develop di dev
git checkout dev
git pull origin dev
# ... edit code ...
git add . && git commit -m "feat: Fitur baru" && git push origin dev

# 2. Test di devjargas.ptkiansantang.com

# 3. Merge ke main untuk production
git checkout main
git pull origin main
git merge dev
git push origin main
```

---

## 💡 Best Practices

1. **Selalu test di dev sebelum merge ke main**
2. **Monitor deployment logs di GitHub Actions**
3. **Backup database sebelum deploy production:**
   ```bash
   docker-compose exec mysql mysqldump -u root -padmin123 jargas_apbn > backup_$(date +%Y%m%d).sql
   ```
4. **Gunakan commit message yang jelas:** `feat:`, `fix:`, `refactor:`
5. **Jangan push langsung ke main** - selalu lewat dev dulu

---

## 📝 Checklist Deployment

- [ ] Kode sudah di-test di lokal
- [ ] Git commit & push ke branch yang benar (`dev` atau `main`)
- [ ] Cek GitHub Actions untuk deployment status
- [ ] Health check berhasil
- [ ] Migration berjalan (cek log)
- [ ] Verifikasi aplikasi bisa diakses

---

**Terakhir diupdate:** 2025-01-27
