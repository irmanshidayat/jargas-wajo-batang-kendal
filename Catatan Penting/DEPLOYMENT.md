# 🚀 Tutorial Deployment ke Server VPS - Jargas APBN

Tutorial sederhana untuk mengupdate kode dari lokal ke server VPS dan rebuild Docker.

## 📋 Daftar Isi

- [Prasyarat](#prasyarat)
- [Setup Domain](#setup-domain)
- [Opsi Deployment](#opsi-deployment)
- [Metode 1: Via GitHub (Recommended)](#metode-1-via-github-recommended)
- [Metode 2: Langsung via SCP/RSYNC](#metode-2-langsung-via-scprsync)
- [Rebuild Docker Container](#rebuild-docker-container)
- [Verifikasi Deployment](#verifikasi-deployment)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## 🛠️ Prasyarat

Sebelum deployment, pastikan:

1. **Akses SSH ke Server**
   - Username SSH: `root` (atau username server Anda)
   - IP Server: `72.61.142.109` (atau IP server Anda)
   - Test koneksi: `ssh root@72.61.142.109`

2. **Project Path di Server**
   - Default: `~/jargas-wajo-batang-kendal`
   - Pastikan project sudah ada di server

3. **Docker & Docker Compose**
   - Sudah terinstall di server
   - Test: `docker --version` dan `docker-compose --version`

---

## 🌐 Setup Domain

Untuk menggunakan domain `jargas.ptkiansantang.com` di VPS, ikuti langkah berikut:

### 1. Setup DNS Record di Penyedia Hosting Domain

Di panel DNS domain `ptkiansantang.com` (di penyedia hosting domain), tambahkan record:

**A Record:**
```
Type: A
Name: jargas
Value: 72.61.142.109  (IP VPS Anda)
TTL: 3600 (atau default)
```

**Catatan:** Gunakan A Record jika IP VPS statis.

### 2. Setup Domain di Server VPS

Ada 2 cara untuk setup domain:

#### Opsi A: Setup dari Windows (PowerShell)

```powershell
# Dari folder project lokal
cd "C:\Irman\Coding Jargas APBN\Jargas APBN"

# Jalankan script setup domain
.\nginx-host\setup-domain.ps1

# Atau dengan parameter custom
.\nginx-host\setup-domain.ps1 -ServerIP "72.61.142.109" -Username "root"
```

#### Opsi B: Setup di Server (SSH)

```bash
# Masuk ke server
ssh root@72.61.142.109

# Masuk ke folder project
cd ~/jargas-wajo-batang-kendal

# Jalankan script setup domain
bash nginx-host/setup-domain.sh
```

### 3. Verifikasi DNS Propagation

Tunggu beberapa menit (biasanya 5-15 menit, maksimal 48 jam) untuk DNS propagation, lalu test:

```bash
# Test dari server VPS
curl -I http://jargas.ptkiansantang.com/health

# Test dari lokal Windows
nslookup jargas.ptkiansantang.com
ping jargas.ptkiansantang.com
```

### 4. Setup SSL dengan Let's Encrypt (Opsional)

Setelah DNS sudah mengarah ke VPS, setup SSL:

```bash
# Di server SSH
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# Setup SSL untuk domain
sudo certbot --nginx -d jargas.ptkiansantang.com

# Auto-renewal (sudah otomatis setup)
sudo certbot renew --dry-run
```

### 5. Test Akses Domain

Setelah setup selesai, test akses:

- Frontend: `http://jargas.ptkiansantang.com` (atau `https://` jika sudah setup SSL)
- Backend API: `http://jargas.ptkiansantang.com/api/v1/health`
- Health Check: `http://jargas.ptkiansantang.com/health`

### Troubleshooting Domain

Jika domain belum bisa diakses:

1. **Cek DNS propagation:**
   ```bash
   nslookup jargas.ptkiansantang.com
   # Harus return IP: 72.61.142.109
   ```

2. **Cek firewall VPS:**
   ```bash
   # Pastikan port 80 dan 443 terbuka
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

3. **Cek log Nginx:**
   ```bash
   sudo tail -f /var/log/nginx/jargas_error.log
   ```

4. **Test dari server langsung:**
   ```bash
   curl -H "Host: jargas.ptkiansantang.com" http://localhost/health
   ```

---

## 🎯 Opsi Deployment

Ada 2 cara utama untuk deployment:

| Metode | Kecepatan | Backup | Version Control | Best For |
|--------|----------|--------|-----------------|----------|
| **Git Push → Pull** | Sedang | ✅ | ✅ | Production |
| **SCP/RSYNC** | Cepat | ❌ | ❌ | Development/Testing |

**Rekomendasi:**
- **Production**: Gunakan Git (aman, ada backup)
- **Development**: Gunakan SCP/RSYNC (lebih cepat)

---

## 📤 Metode 1: Via GitHub (Recommended)

### Keuntungan:
- ✅ Backup otomatis di GitHub
- ✅ Version control dan rollback mudah
- ✅ History perubahan jelas
- ✅ Deployment konsisten

### Langkah-langkah:

#### 1. Push ke GitHub (dari lokal Windows)

```powershell
# Di folder project lokal
cd "C:\Irman\Coding Jargas APBN\Jargas APBN"

# Cek status perubahan
git status

# Tambahkan semua perubahan
git add .

# Commit perubahan
git commit -m "Update: pembaruan kode"

# Push ke GitHub
git push origin main
```

#### 2. Pull di Server (via SSH)

```bash
# Masuk ke server
ssh root@72.61.142.109

# Masuk ke folder project
cd ~/jargas-wajo-batang-kendal

# Pull perubahan terbaru
git pull origin main

# Rebuild container (lihat bagian Rebuild Docker)
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Script Otomatis (Opsional)

Buat file `deploy-git.sh` di server:

```bash
#!/bin/bash
cd ~/jargas-wajo-batang-kendal
git pull origin main
docker-compose build --no-cache
docker-compose up -d
echo "✅ Deployment selesai!"
```

Jalankan dengan:
```bash
bash deploy-git.sh
```

---

## 📤 Metode 2: Langsung via SCP/RSYNC

### Keuntungan:
- ✅ Lebih cepat untuk perubahan kecil
- ✅ Tidak perlu commit/push
- ✅ Cocok untuk testing cepat

### Langkah-langkah:

#### Opsi A: Menggunakan SCP (Simple)

```powershell
# Dari PowerShell di Windows

# Upload backend
scp -r .\backend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/backend

# Upload frontend
scp -r .\frontend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/frontend

# Upload docker-compose.yml (jika ada perubahan)
scp docker-compose.yml root@72.61.142.109:~/jargas-wajo-batang-kendal/
```

#### Opsi B: Menggunakan RSYNC (Lebih Efisien)

**Install RSYNC di Windows:**
- Download: https://github.com/cwrsync/cwrsync/releases
- Atau gunakan WSL: `wsl rsync`

```powershell
# Sync backend (exclude cache dan temp files)
rsync -avz --exclude '__pycache__' --exclude '*.pyc' --exclude '.pytest_cache' `
  .\backend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/backend/

# Sync frontend (exclude node_modules)
rsync -avz --exclude 'node_modules' --exclude 'dist' `
  .\frontend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/frontend/
```

#### Setelah Upload, Rebuild di Server

```bash
# Masuk ke server
ssh root@72.61.142.109

# Masuk ke folder project
cd ~/jargas-wajo-batang-kendal

# Rebuild container (lihat bagian Rebuild Docker)
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔨 Rebuild Docker Container

Setelah kode diupdate, rebuild container:

### Rebuild Semua Services

```bash
# Di server SSH
cd ~/jargas-wajo-batang-kendal

# Stop containers
docker-compose down

# Build tanpa cache
docker-compose build --no-cache

# Start containers
docker-compose up -d
```

### Rebuild Service Tertentu

```bash
# Rebuild backend saja
docker-compose build --no-cache backend
docker-compose up -d backend

# Rebuild frontend saja
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Rebuild dari Windows (via SSH)

```powershell
# Rebuild semua
ssh root@72.61.142.109 "cd ~/jargas-wajo-batang-kendal && docker-compose build --no-cache && docker-compose up -d"

# Rebuild frontend saja
ssh root@72.61.142.109 "cd ~/jargas-wajo-batang-kendal && docker-compose build --no-cache frontend && docker-compose up -d frontend"
```

---

## ✅ Verifikasi Deployment

### 1. Cek Status Container

```bash
# Di server SSH
docker-compose ps

# Atau dari Windows
ssh root@72.61.142.109 "cd ~/jargas-wajo-batang-kendal && docker-compose ps"
```

### 2. Cek Log Container

```bash
# Log backend
docker-compose logs backend --tail 50

# Log frontend
docker-compose logs frontend --tail 50

# Log semua
docker-compose logs --tail 50
```

### 3. Test Health Check

```bash
# Test health endpoint
curl http://localhost/health

# Test frontend
curl http://localhost/

# Test backend API
curl http://localhost/api/v1/health
```

### 4. Cek dari Browser

- Frontend: `http://72.61.142.109:8080` (atau domain Anda)
- Backend API: `http://72.61.142.109:8001/api/v1/health`
- Adminer: `http://72.61.142.109:8081`

---

## 🔧 Troubleshooting

### ❌ Container tidak start

```bash
# Cek log error
docker-compose logs backend
docker-compose logs frontend

# Cek status detail
docker-compose ps -a

# Restart container
docker-compose restart
```

### ❌ Build gagal

```bash
# Cek error detail
docker-compose build --no-cache 2>&1 | tee build.log

# Cek disk space
df -h

# Clean up Docker
docker system prune -a
```

### ❌ File tidak terupdate

```bash
# Pastikan file sudah diupload
ls -la ~/jargas-wajo-batang-kendal/backend/
ls -la ~/jargas-wajo-batang-kendal/frontend/

# Rebuild dengan no cache
docker-compose build --no-cache

# Restart container
docker-compose restart
```

### ❌ Permission denied

```bash
# Pastikan file permission benar
chmod -R 755 ~/jargas-wajo-batang-kendal

# Cek ownership
ls -la ~/jargas-wajo-batang-kendal/
```

### ❌ Git pull gagal

```bash
# Cek koneksi internet
ping github.com

# Cek git remote
git remote -v

# Force pull (hati-hati!)
git fetch origin
git reset --hard origin/main
```

---

## 💡 Best Practices

### 1. Selalu Backup Sebelum Update

```bash
# Backup database
docker-compose exec mysql mysqldump -u root -padmin123 jargas_apbn > backup_$(date +%Y%m%d).sql

# Backup volume
docker run --rm -v jargas_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql_backup_$(date +%Y%m%d).tar.gz /data
```

### 2. Test di Development Dulu

- Test perubahan di lokal dulu
- Pastikan tidak ada error sebelum deploy
- Gunakan `docker-compose build --no-cache` untuk test build

### 3. Monitor Setelah Deployment

```bash
# Monitor log real-time
docker-compose logs -f

# Monitor resource usage
docker stats

# Monitor container health
docker-compose ps
```

### 4. Gunakan Git untuk Production

- Selalu commit perubahan penting
- Push ke GitHub sebelum deploy
- Gunakan tag untuk versioning

### 5. Dokumentasi Perubahan

- Tulis commit message yang jelas
- Dokumentasi breaking changes
- Update changelog jika perlu

---

## 📝 Checklist Deployment

Sebelum deployment, pastikan:

- [ ] Kode sudah di-test di lokal
- [ ] Tidak ada error di log
- [ ] Database backup sudah dibuat
- [ ] Git commit sudah dibuat (jika pakai Git)
- [ ] File sudah diupload (jika pakai SCP/RSYNC)
- [ ] Container sudah di-rebuild
- [ ] Health check berhasil
- [ ] Aplikasi bisa diakses dari browser

---

## 🚀 Quick Reference

### Deployment Cepat (Git)

```bash
# Di lokal
git add . && git commit -m "Update" && git push

# Di server
ssh root@72.61.142.109 "cd ~/jargas-wajo-batang-kendal && git pull && docker-compose build --no-cache && docker-compose up -d"
```

### Deployment Cepat (SCP)

```powershell
# Di Windows PowerShell
scp -r .\backend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/backend
scp -r .\frontend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/frontend
ssh root@72.61.142.109 "cd ~/jargas-wajo-batang-kendal && docker-compose build --no-cache && docker-compose up -d"
```

### Rebuild Cepat

```bash
# Di server
cd ~/jargas-wajo-batang-kendal
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose ps
```

---

## 📞 Butuh Bantuan?

Jika ada masalah:

1. Cek log: `docker-compose logs`
2. Cek status: `docker-compose ps`
3. Cek dokumentasi lain:
   - `DOCKER_SETUP.md` - Setup Docker
   - `GITHUB_SETUP.md` - Setup GitHub

---

**Terakhir diupdate:** 2025-01-27

