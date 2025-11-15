# Setup Scripts - One-Time Setup

Folder ini berisi script-script untuk setup one-time server atau environment.

## 📋 Daftar Script Setup

### Environment Setup

#### `setup-env-production.ps1`
Setup environment variables untuk **PRODUCTION** environment.

**Cara Menggunakan:**
```powershell
# Dari Windows (di local atau server)
.\scripts\setup\setup-env-production.ps1
```

**Fitur:**
- Setup `.env` di root project (production)
- Setup `backend/.env` dari `backend/env.example` (production)
- Konfigurasi untuk Docker production environment
- Generate template jika belum ada

**Catatan:**
- File `.env` dan `backend/.env` akan dibuat dari template
- **WAJIB** edit file `.env` dan `backend/.env` setelah dibuat
- Generate SECRET_KEY yang unik untuk production
- Set DEBUG=False untuk production

---

#### `setup-env-development.ps1`
Setup environment variables untuk **DEVELOPMENT** environment.

**Cara Menggunakan:**
```powershell
# Dari Windows (di local atau server)
.\scripts\setup\setup-env-development.ps1
```

**Fitur:**
- Setup `.env.dev` di root project (development)
- Setup `backend/.env.dev` dari `backend/.env.dev.example` (development)
- Konfigurasi untuk Docker development environment
- Generate template jika belum ada

**Catatan:**
- File `.env.dev` dan `backend/.env.dev` akan dibuat dari template
- **WAJIB** edit file `.env.dev` dan `backend/.env.dev` setelah dibuat
- Generate SECRET_KEY yang berbeda dari production
- DEBUG=True untuk development (boleh)

---

#### `setup-env-dev-server.ps1` / `setup-env-dev-server.sh`
Setup environment variables untuk development server (legacy).

**Cara Menggunakan:**
```powershell
# Dari Windows
.\scripts\setup\setup-env-dev-server.ps1

# Atau upload dan jalankan di server
scp scripts/setup/setup-env-dev-server.sh root@server:~/setup-env-dev-server.sh
ssh root@server "bash ~/setup-env-dev-server.sh"
```

**Fitur:**
- Setup `backend/.env` dari `backend/env.example`
- Setup `.env` di root project
- Konfigurasi untuk Docker environment

**Catatan:**
- Script legacy, gunakan `setup-env-development.ps1` untuk setup yang lebih lengkap

---

### Domain Setup

#### `setup-dev-domain.ps1`
Setup domain development (devjargas.ptkiansantang.com).

**Cara Menggunakan:**
```powershell
.\scripts\setup\setup-dev-domain.ps1
```

**Fitur:**
- Upload nginx config ke server
- Setup nginx configuration
- Setup SSL certificate (Let's Encrypt)

---

---

## ⚠️ Catatan

- Script di folder ini biasanya hanya dijalankan **sekali** saat setup awal server
- Berguna untuk **referensi** saat setup server baru
- Pastikan backup konfigurasi sebelum menjalankan script

---

## 🔄 Kapan Menggunakan

Gunakan script di folder ini ketika:
1. Setup server baru
2. Setup environment development baru
3. Perlu referensi konfigurasi yang sudah pernah digunakan

---

## 📚 Referensi

Untuk dokumentasi lengkap setup, lihat:
- [DEPLOYMENT.md](../../Catatan%20Penting/DEPLOYMENT.md)
- [DOCKER_SETUP.md](../../Catatan%20Penting/DOCKER_SETUP.md)

