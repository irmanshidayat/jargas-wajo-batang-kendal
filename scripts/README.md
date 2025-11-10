# Scripts - Jargas APBN

Folder ini berisi script-script utilitas untuk memudahkan operasi Docker dan deployment.

## 📋 Daftar Scripts

### `push-to-ghcr.ps1`

Script PowerShell untuk build dan push Docker images ke GitHub Container Registry (GHCR).

**Syarat:**
- Docker Desktop sudah berjalan
- GitHub Personal Access Token dengan scope `write:packages`
- PowerShell (Windows)

**Cara Menggunakan:**

```powershell
# Dari root project
.\scripts\push-to-ghcr.ps1 -GitHubUsername "your-username" -GitHubToken "ghp_your_token" -Version "v1.0.0"
```

**Parameter:**
- `-GitHubUsername` (Required): Username GitHub Anda
- `-GitHubToken` (Required): GitHub Personal Access Token
- `-Version` (Optional): Version tag untuk images (default: "latest")
- `-SkipBuild` (Optional): Skip build, hanya push images yang sudah ada
- `-BuildOnly` (Optional): Hanya build, tidak push ke GHCR

**Contoh:**

```powershell
# Build dan push dengan version v1.0.0
.\scripts\push-to-ghcr.ps1 -GitHubUsername "johndoe" -GitHubToken "ghp_xxxxxxxxxxxx" -Version "v1.0.0"

# Build dan push dengan latest
.\scripts\push-to-ghcr.ps1 -GitHubUsername "johndoe" -GitHubToken "ghp_xxxxxxxxxxxx"

# Hanya build, tidak push
.\scripts\push-to-ghcr.ps1 -GitHubUsername "johndoe" -GitHubToken "ghp_xxxxxxxxxxxx" -BuildOnly

# Skip build, hanya push images yang sudah ada
.\scripts\push-to-ghcr.ps1 -GitHubUsername "johndoe" -GitHubToken "ghp_xxxxxxxxxxxx" -SkipBuild
```

**Keamanan:**
- Jangan commit token ke repository
- Simpan token di environment variable atau file terpisah
- Gunakan GitHub Secrets untuk otomatisasi

**Contoh dengan Environment Variable:**

```powershell
# Set environment variable
$env:GITHUB_TOKEN = "ghp_your_token"
$env:GITHUB_USERNAME = "your-username"

# Gunakan dalam script
.\scripts\push-to-ghcr.ps1 -GitHubUsername $env:GITHUB_USERNAME -GitHubToken $env:GITHUB_TOKEN -Version "v1.0.0"
```

---

### `deploy-with-migration.ps1`

Script PowerShell untuk deployment lengkap dengan auto-migration ke server VPS.

**Fitur:**
- Pull kode terbaru dari Git
- Rebuild Docker containers
- Start containers (migration otomatis berjalan)
- Verifikasi migration dan tabel database
- Health check endpoint

**Syarat:**
- SSH access ke server
- OpenSSH Client terinstall di Windows
- Project sudah ada di server

**Cara Menggunakan:**

```powershell
# Dengan default settings (72.61.142.109, root, ~/jargas-wajo-batang-kendal)
.\scripts\deploy-with-migration.ps1

# Dengan custom settings
.\scripts\deploy-with-migration.ps1 -ServerIP "192.168.1.100" -Username "admin" -ProjectPath "~/my-project"
```

**Parameter:**
- `-ServerIP` (Optional): IP atau domain server (default: "72.61.142.109")
- `-Username` (Optional): Username SSH (default: "root")
- `-ProjectPath` (Optional): Path project di server (default: "~/jargas-wajo-batang-kendal")

---

### `run-migration-server.ps1`

Script PowerShell untuk menjalankan migration manual di server (jika auto-migrate tidak berjalan).

**Cara Menggunakan:**

```powershell
# Dengan default settings
.\scripts\run-migration-server.ps1

# Dengan custom settings
.\scripts\run-migration-server.ps1 -ServerIP "192.168.1.100" -Username "admin" -ProjectPath "~/my-project"
```

**Parameter:**
- `-ServerIP` (Optional): IP atau domain server (default: "72.61.142.109")
- `-Username` (Optional): Username SSH (default: "root")
- `-ProjectPath` (Optional): Path project di server (default: "~/jargas-wajo-batang-kendal")

---

### `run-migration-server.sh`

Script Bash untuk menjalankan migration manual di server (untuk dijalankan langsung di server via SSH).

**Cara Menggunakan:**

```bash
# Di server SSH
cd ~/jargas-wajo-batang-kendal
bash scripts/run-migration-server.sh

# Atau dengan custom path
bash scripts/run-migration-server.sh ~/custom-path
```

**Catatan:** Script ini akan:
1. Cek status migration saat ini
2. Jalankan migration ke head
3. Verifikasi migration berhasil
4. Verifikasi tabel database sudah dibuat

---

### `fix-missing-columns-vps.ps1` / `fix-missing-columns-vps.sh`

Script untuk memperbaiki kolom yang missing di database VPS. Script ini menambahkan kolom-kolom yang diperlukan agar fitur DELETE user berfungsi dengan baik.

**Masalah yang diperbaiki:**
- Error: `Unknown column 'surat_permintaans.status' in 'field list'`
- Error: `Unknown column 'surat_jalans.nomor_surat_permintaan' in 'field list'`
- Error: `Unknown column 'surat_jalans.nomor_barang_keluar' in 'field list'`
- Error: `Unknown column 'surat_jalans.stock_out_id' in 'field list'`

**Kolom yang ditambahkan:**
- `surat_permintaans.status` (VARCHAR(50), NOT NULL, DEFAULT 'Draft') dengan index
- `surat_jalans.nomor_surat_permintaan` (VARCHAR(255), NULL) dengan index
- `surat_jalans.nomor_barang_keluar` (VARCHAR(255), NULL) dengan index
- `surat_jalans.stock_out_id` (INT, NULL) dengan index dan foreign key

**Cara Menggunakan (PowerShell - Windows):**

```powershell
# Dari root project
.\scripts\fix-missing-columns-vps.ps1

# Dengan custom database settings
.\scripts\fix-missing-columns-vps.ps1 -DbHost "localhost" -DbUser "root" -DbPassword "password" -DbName "jargas_apbn" -DbPort 3306
```

**Cara Menggunakan (Bash - Linux VPS):**

```bash
# Di server VPS via SSH
cd ~/jargas-wajo-batang-kendal
chmod +x scripts/fix-missing-columns-vps.sh
./scripts/fix-missing-columns-vps.sh

# Atau dengan environment variables
export DB_HOST="localhost"
export DB_USER="root"
export DB_PASSWORD="password"
export DB_NAME="jargas_apbn"
export DB_PORT="3306"
./scripts/fix-missing-columns-vps.sh
```

**Atau langsung jalankan SQL file via Docker (jika MySQL client tidak terinstall):**

```bash
# Di server VPS (via Docker container)
docker exec -i jargas_mysql mysql -uroot -padmin123 jargas_apbn < scripts/fix_missing_columns_vps.sql

# Atau gunakan script khusus Docker
chmod +x scripts/fix-missing-columns-vps-docker.sh
./scripts/fix-missing-columns-vps-docker.sh
```

**Parameter (PowerShell):**
- `-DbHost` (Optional): Database host (default: "localhost")
- `-DbUser` (Optional): Database user (default: "root")
- `-DbPassword` (Optional): Database password (default: "")
- `-DbName` (Optional): Database name (default: "jargas_apbn")
- `-DbPort` (Optional): Database port (default: 3306)

**Catatan:**
- Script ini aman dijalankan berkali-kali (idempotent) - akan mengecek apakah kolom sudah ada sebelum menambahkan
- Tidak akan menghapus data yang sudah ada
- Pastikan backup database sebelum menjalankan script (best practice)

---

## 📚 Dokumentasi Lengkap

Untuk dokumentasi lengkap, lihat:
- [DEPLOYMENT.md](../Catatan%20Penting/DEPLOYMENT.md) - Deployment guide
- [DOCKER_SETUP.md](../Catatan%20Penting/DOCKER_SETUP.md) - Docker setup
- [GHCR_SETUP.md](../Catatan%20Penting/GHCR_SETUP.md) - GHCR setup

---

## ⚠️ Catatan Penting

1. **Token Security**: Jangan pernah commit token ke repository
2. **Docker Running**: Pastikan Docker Desktop berjalan sebelum menjalankan script
3. **Network**: Pastikan koneksi internet stabil untuk push images
4. **Permissions**: Pastikan token memiliki permission yang diperlukan
5. **Auto-Migration**: Migration otomatis berjalan saat backend start (AUTO_MIGRATE=True di docker-compose.yml)
6. **SSH Access**: Pastikan SSH key sudah di-setup atau password sudah benar

