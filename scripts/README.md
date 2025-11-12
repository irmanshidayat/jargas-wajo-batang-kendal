# Scripts - Jargas APBN

Folder ini berisi script-script utilitas untuk memudahkan operasi Docker dan deployment.

## 📁 Struktur Folder

```
scripts/
├── active/          # Script yang masih aktif digunakan (rutin)
├── setup/           # Script setup one-time (untuk referensi setup server baru)
└── archive/         # Script one-time fix yang sudah tidak diperlukan (referensi historis)
```

---

## 🚀 Script Aktif (Folder `active/`)

Script yang masih digunakan secara rutin untuk operasi sehari-hari.

### Deployment & Git

#### `deploy-production.ps1`
Script PowerShell untuk deployment **PRODUCTION** lengkap dengan auto-migration ke server VPS.

**Fitur:**
- Verifikasi file `.env` production
- Pull kode terbaru dari Git (branch main)
- Rebuild Docker containers dengan `--env-file .env`
- Start containers (migration otomatis berjalan)
- Verifikasi migration dan tabel database
- Health check endpoint

**Cara Menggunakan:**
```powershell
# Dengan default settings (72.61.142.109, root, ~/jargas-wajo-batang-kendal)
.\scripts\active\deploy-production.ps1

# Dengan custom settings
.\scripts\active\deploy-production.ps1 -ServerIP "192.168.1.100" -Username "admin" -ProjectPath "~/my-project"
```

**Parameter:**
- `-ServerIP` (Optional): IP atau domain server (default: "72.61.142.109")
- `-Username` (Optional): Username SSH (default: "root")
- `-ProjectPath` (Optional): Path project di server (default: "~/jargas-wajo-batang-kendal")

**Catatan:**
- Script ini menggunakan `docker-compose --env-file .env` untuk production
- Pastikan file `.env` dan `backend/.env` sudah dibuat (gunakan `scripts/setup/setup-env-production.ps1`)

---

#### `deploy-with-migration.ps1` (Legacy)
Script PowerShell untuk deployment production (legacy, gunakan `deploy-production.ps1`).

**Catatan:** Script ini sudah di-update untuk menggunakan `--env-file .env`, tapi disarankan menggunakan `deploy-production.ps1` yang lebih lengkap.

---

#### `deploy-dev.ps1`
Script PowerShell untuk deployment **DEVELOPMENT** dengan auto-migration.

**Fitur:**
- Verifikasi file `.env.dev` development
- Pull kode terbaru dari Git (branch dev)
- Rebuild Docker containers dengan `docker-compose.dev.yml --env-file .env.dev`
- Start containers (migration otomatis berjalan)
- Verifikasi migration dan tabel database
- Health check endpoint

**Cara Menggunakan:**
```powershell
# Dengan default settings (72.61.142.109, root, ~/jargas-wajo-batang-kendal-dev)
.\scripts\active\deploy-dev.ps1

# Dengan custom settings
.\scripts\active\deploy-dev.ps1 -ServerIP "192.168.1.100" -Username "admin" -ProjectPath "~/my-project-dev"
```

**Parameter:**
- `-ServerIP` (Optional): IP atau domain server (default: "72.61.142.109")
- `-Username` (Optional): Username SSH (default: "root")
- `-ProjectPath` (Optional): Path project di server (default: "~/jargas-wajo-batang-kendal-dev")

**Catatan:**
- Script ini menggunakan `docker-compose -f docker-compose.dev.yml --env-file .env.dev` untuk development
- Pastikan file `.env.dev` dan `backend/.env.dev` sudah dibuat (gunakan `scripts/setup/setup-env-development.ps1`)

---

#### `push-to-dev.ps1`
Script untuk push perubahan ke branch dev.

**Cara Menggunakan:**
```powershell
.\scripts\active\push-to-dev.ps1 -Message "Update development"
```

---

#### `push-to-ghcr.ps1`
Script PowerShell untuk build dan push Docker images ke GitHub Container Registry (GHCR).

**Syarat:**
- Docker Desktop sudah berjalan
- GitHub Personal Access Token dengan scope `write:packages`
- PowerShell (Windows)

**Cara Menggunakan:**
```powershell
.\scripts\active\push-to-ghcr.ps1 -GitHubUsername "your-username" -GitHubToken "ghp_your_token" -Version "v1.0.0"
```

**Parameter:**
- `-GitHubUsername` (Required): Username GitHub Anda
- `-GitHubToken` (Required): GitHub Personal Access Token
- `-Version` (Optional): Version tag untuk images (default: "latest")
- `-SkipBuild` (Optional): Skip build, hanya push images yang sudah ada
- `-BuildOnly` (Optional): Hanya build, tidak push ke GHCR

---

### Monitoring & Debugging

#### `check-container-status-server.ps1`
Script untuk cek status container di server.

**Cara Menggunakan:**
```powershell
.\scripts\active\check-container-status-server.ps1
```

**Fitur:**
- Menampilkan status semua container
- Cek restart count
- Cek health status
- Menampilkan log terakhir

---

#### `check-docker-logs-server.ps1`
Script untuk cek log docker di server.

**Cara Menggunakan:**
```powershell
# Log terakhir 200 baris
.\scripts\active\check-docker-logs-server.ps1

# Log real-time
.\scripts\active\check-docker-logs-server.ps1 -Follow

# Hanya error
.\scripts\active\check-docker-logs-server.ps1 -ErrorsOnly

# Custom jumlah baris
.\scripts\active\check-docker-logs-server.ps1 -Lines 500
```

**Parameter:**
- `-Lines` (Optional): Jumlah baris log (default: 200)
- `-Follow` (Optional): Follow log real-time
- `-ErrorsOnly` (Optional): Hanya tampilkan error

---

### Database Operations

#### `clear-database-vps.ps1`
Script untuk menghapus semua data database di VPS (kecuali users, roles, pages, permissions).

**⚠️ PERINGATAN:** Script ini akan menghapus SEMUA DATA dari database!

**Cara Menggunakan:**
```powershell
.\scripts\active\clear-database-vps.ps1
```

**Catatan:** Script akan meminta konfirmasi dua kali untuk keamanan.

---

#### `run-migration-server.ps1` / `run-migration-server.sh`
Script untuk menjalankan migration manual di server (jika auto-migrate tidak berjalan).

**Cara Menggunakan (PowerShell):**
```powershell
.\scripts\active\run-migration-server.ps1
```

**Cara Menggunakan (Bash - di server):**
```bash
cd ~/jargas-wajo-batang-kendal
bash scripts/active/run-migration-server.sh
```

---

## 🔧 Script Setup (Folder `setup/`)

Script untuk setup one-time. Berguna untuk setup server baru atau referensi konfigurasi.

### `setup-env-dev-server.ps1` / `setup-env-dev-server.sh`
Setup environment variables untuk development server.

### `setup-dev-domain.ps1`
Setup domain development (devjargas.ptkiansantang.com).

### `setup-port-8083-ssl.ps1` / `setup-port-8083-ssl.sh`
Setup port 8083 dan SSL certificate untuk Adminer.

**Catatan:** Script di folder `setup/` biasanya hanya dijalankan sekali saat setup awal server.

---

## 📦 Script Archive (Folder `archive/`)

Script one-time fix yang sudah tidak diperlukan lagi karena:
- Masalah sudah diperbaiki dan sudah ada di migration Alembic
- Database production sudah memiliki kolom/tabel tersebut
- Tidak ada rencana setup database baru dari awal

### Script yang Di-archive:

1. **Fix created_by column:**
   - `fix-created-by-users.sh`
   - `fix-created-by-users.ps1`
   - `fix-created-by-vps-auto.ps1`
   - `fix-created-by-vps-server.sh`
   - `run-fix-created-by-on-vps.sh`
   - `fix_created_by_users.sql`

2. **Fix harga materials:**
   - `fix-harga-materials.sh`
   - `fix-harga-materials.ps1`
   - `fix-harga-materials-docker.sh`
   - `fix_harga_materials.sql`

3. **Fix missing columns:**
   - `fix-missing-columns-vps.sh`
   - `fix-missing-columns-vps.ps1`
   - `fix-missing-columns-vps-docker.sh`
   - `fix_missing_columns_vps.sql`

4. **Fix lainnya:**
   - `fix-database-empty.ps1` (sudah ada auto-migration)
   - `fix-dev-domain.ps1` (setup one-time)
   - `debug-nginx-adminer.sh` (debug one-time)
   - `update-nginx-adminer-dev.sh` (update one-time)

**⚠️ Catatan Penting:**
- Script di folder `archive/` TIDAK PERLU dijalankan lagi
- Di-archive untuk referensi historis saja
- Jangan hapus script di folder `archive/` tanpa verifikasi terlebih dahulu

---

## 📚 Dokumentasi Lengkap

Untuk dokumentasi lengkap, lihat:
- [DEPLOYMENT.md](../Catatan%20Penting/DEPLOYMENT.md) - Deployment guide
- [DOCKER_SETUP.md](../Catatan%20Penting/DOCKER_SETUP.md) - Docker setup
- [GHCR_SETUP.md](../Catatan%20Penting/GHCR_SETUP.md) - GHCR setup
- [DELETE_DATABASE.md](../Catatan%20Penting/DELETE_DATABASE.md) - Database operations

---

## ⚠️ Catatan Penting

1. **Token Security**: Jangan pernah commit token ke repository
2. **Docker Running**: Pastikan Docker Desktop berjalan sebelum menjalankan script
3. **Network**: Pastikan koneksi internet stabil untuk push images
4. **Permissions**: Pastikan token memiliki permission yang diperlukan
5. **Auto-Migration**: Migration otomatis berjalan saat backend start (AUTO_MIGRATE=True di docker-compose.yml)
6. **SSH Access**: Pastikan SSH key sudah di-setup atau password sudah benar
7. **Path Update**: Setelah reorganisasi, pastikan path script di dokumentasi lain sudah di-update

---

## 🔄 Migrasi Path Script

Jika Anda menggunakan script dari dokumentasi lama, update path-nya:

**Sebelum:**
```powershell
.\scripts\deploy-with-migration.ps1
```

**Sesudah:**
```powershell
.\scripts\active\deploy-with-migration.ps1
```

**Atau buat symlink/alias untuk kemudahan:**
```powershell
# Di PowerShell profile
function Deploy-Production {
    .\scripts\active\deploy-with-migration.ps1 @args
}

function Deploy-Dev {
    .\scripts\active\deploy-dev.ps1 @args
}
```
