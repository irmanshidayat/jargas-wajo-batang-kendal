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
| **Port** | 8080, 8001, 3308, 8081 | 8082, 8012, 3309, 8083 |

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
```powershell.
git checkout dev
git add . && git commit -m "Update" && git push origin dev
# Auto-deploy via GitHub Actions → https://devjargas.ptkiansantang.com
```

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
curl https://jargas.ptkiansantang.com/health

# Development
curl https://devjargas.ptkiansantang.com/health
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

**Opsi 1: Menggunakan Script PowerShell (Recommended):**
```powershell
.\scripts\active\setup-github-actions-ssh.ps1
```

**Opsi 2: Manual dengan ssh-copy-id:**
```bash
ssh-copy-id -i ~/.ssh/github_actions.pub root@72.61.142.109
```

**Opsi 3: Manual copy via SSH dengan password:**
```powershell
# Di Windows PowerShell (akan minta password sekali)
$publicKey = Get-Content "$env:USERPROFILE\.ssh\github_actions.pub" -Raw
echo $publicKey.Trim() | ssh root@72.61.142.109 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

**Opsi 4: Copy manual (jika semua opsi di atas gagal):**
1. Buka file: `$env:USERPROFILE\.ssh\github_actions.pub`
2. Copy seluruh isinya (contoh: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC1EpYbTekG20g8y8Vo6wjLyy3AgCAEKdVYfoXKL3zb4 github-actions`)
3. SSH ke server: `ssh root@72.61.142.109`
4. Jalankan perintah di server:
   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC1EpYbTekG20g8y8Vo6wjLyy3AgCAEKdVYfoXKL3zb4 github-actions" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```
   (Ganti dengan public key Anda yang sebenarnya)

**Verifikasi:**
```bash
ssh root@72.61.142.109 "cat ~/.ssh/authorized_keys | grep github-actions"
```

3. **Tambah Private Key ke GitHub Secrets:**
   - Buka repository di GitHub
   - Klik **Settings** → **Secrets and variables** → **Actions**
   - Klik **New repository secret**
   - **Name**: `SSH_PRIVATE_KEY` (harus sama persis, case-sensitive)
   - **Value**: Copy seluruh isi dari file `~/.ssh/github_actions` (termasuk `-----BEGIN OPENSSH PRIVATE KEY-----` dan `-----END OPENSSH PRIVATE KEY-----`)
   - Klik **Add secret**
   ..
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

**Error: "Process completed with exit code 255"**
- ❌ **Penyebab**: SSH connection gagal, biasanya karena public key belum di-copy ke server
- ✅ **Solusi**:
  1. Jalankan script setup SSH: `.\scripts\active\setup-github-actions-ssh.ps1`
  2. Atau manual copy public key ke server:
     ```powershell
     # Di Windows PowerShell
     Get-Content "$env:USERPROFILE\.ssh\github_actions.pub" | ssh root@72.61.142.109 "cat >> ~/.ssh/authorized_keys"
     ```
  3. Verifikasi public key sudah ada di server:
     ```bash
     ssh root@72.61.142.109 "cat ~/.ssh/authorized_keys | grep github-actions"
     ```
  4. Test SSH connection:
     ```powershell
     ssh -i "$env:USERPROFILE\.ssh\github_actions" root@72.61.142.109 "echo 'SSH OK'"
     ```

**Error: "Permission denied"**
- Verifikasi SSH key sudah di-copy ke server dengan: `ssh-copy-id -i ~/.ssh/github_actions.pub root@72.61.142.109`
- Atau gunakan script: `.\scripts\active\setup-github-actions-ssh.ps1`
- Cek GitHub Secret `SSH_PRIVATE_KEY` sudah benar
- Test SSH connection: `ssh -i ~/.ssh/github_actions root@72.61.142.109`

**Error: "Process completed with exit code 1"**
- ❌ **Penyebab**: Ada command yang gagal dalam proses deployment
- ✅ **Solusi**:
  1. Cek log detail di GitHub Actions untuk melihat step mana yang gagal
  2. Kemungkinan penyebab:
     - **Project path tidak ada**: Pastikan folder `~/jargas-wajo-batang-kendal-dev` sudah dibuat di server
     - **Git branch tidak ada**: Pastikan branch `dev` sudah di-push ke remote
     - **File .env.dev tidak ada**: Pastikan file `.env.dev` dan `backend/.env.dev` ada di server
     - **Docker build gagal**: Cek log Docker untuk error detail
     - **Docker-compose gagal**: Cek apakah Docker dan Docker Compose sudah terinstall di server
  3. Verifikasi manual di server:
     ```bash
     ssh root@72.61.142.109
     cd ~/jargas-wajo-batang-kendal-dev
     ls -la .env.dev backend/.env.dev
     docker-compose -f docker-compose.dev.yml --env-file .env.dev ps
     ```

**Error: ".env files not found"**
- Pastikan file `.env.dev` dan `backend/.env.dev` ada di server di path `~/jargas-wajo-batang-kendal-dev`
- Jika belum ada, copy dari local atau buat manual di server
- Verifikasi dengan: `ssh root@72.61.142.109 "ls -la ~/jargas-wajo-batang-kendal-dev/.env.dev"`

**Error: "Health check failed"**
- Tunggu lebih lama (migration mungkin masih berjalan, bisa sampai 2-3 menit)
- Cek container logs: `docker-compose -f docker-compose.dev.yml --env-file .env.dev logs backend`
- Pastikan backend container sudah running: `docker-compose -f docker-compose.dev.yml --env-file .env.dev ps`

**Error: "Bind for 0.0.0.0:8002 failed: port is already allocated"**
- ❌ **Penyebab**: Port backend development (8002) sudah digunakan oleh proses atau container lain
- ✅ **Solusi**:
  1. **Cek proses yang menggunakan port:**
     ```bash
     ssh root@72.61.142.109
     ss -lntp | grep 8002 || netstat -tulpn | grep 8002
     docker ps --format 'table {{.ID}}\t{{.Names}}\t{{.Ports}}' | grep 8002
     ```
  2. **Opsi 1 - Hentikan container yang bentrok (jika ada):**
     ```bash
     docker stop <CONTAINER_NAME_OR_ID>
     docker rm <CONTAINER_NAME_OR_ID>
     ```
  3. **Opsi 2 - Ganti port backend di `.env.dev` (jika port memang diperlukan aplikasi lain):**
     ```bash
     cd ~/jargas-wajo-batang-kendal-dev
     # Edit .env.dev, tambahkan/ubah:
     BACKEND_PORT_MAPPED=8012
     # Lalu rebuild dan restart:
     docker-compose -f docker-compose.dev.yml --env-file .env.dev build --no-cache
     docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d
     ```
  4. **Verifikasi port sudah berubah:**
     ```bash
     docker-compose -f docker-compose.dev.yml --env-file .env.dev ps
     # Pastikan backend menggunakan port baru (contoh: 0.0.0.0:8012->8000/tcp)
     ```
  5. **Update nginx config di server VPS (PENTING!):**
     ```bash
     ssh root@72.61.142.109
     # Update upstream backend port di nginx config
     sed -i 's/127.0.0.1:8002/127.0.0.1:8012/g' /etc/nginx/sites-available/jargas-dev
     # Test konfigurasi
     nginx -t
     # Reload nginx
     systemctl reload nginx
     # Verifikasi
     grep -A 3 "backend_container_dev" /etc/nginx/sites-available/jargas-dev
     ```

**Error: "404 Not Found" pada endpoint `/api/v1/auth/profile` setelah perubahan port**
- ❌ **Penyebab**: Nginx host di server VPS masih menggunakan port lama (8002) untuk upstream backend
- ✅ **Solusi**:
  1. **Update nginx config di server:**
     ```bash
     ssh root@72.61.142.109
     sed -i 's/127.0.0.1:8002/127.0.0.1:8012/g' /etc/nginx/sites-available/jargas-dev
     nginx -t
     systemctl reload nginx
     ```
  2. **Verifikasi backend bisa diakses langsung:**
     ```bash
     curl http://localhost:8012/health
     # Endpoint /api/v1/health tidak ada, gunakan /health saja
     ```
  3. **Test melalui nginx:**
     ```bash
     curl -k https://devjargas.ptkiansantang.com/health
     ```
  4. **Cek nginx error log jika masih error:**
     ```bash
     tail -f /var/log/nginx/jargas_dev_error.log
     ```

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

**Terakhir diupdate:** 2025-11-15
