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

## 📚 Dokumentasi Lengkap

Untuk dokumentasi lengkap tentang GHCR, lihat:
- [GHCR_SETUP.md](../Catatan%20Penting/GHCR_SETUP.md)

---

## ⚠️ Catatan Penting

1. **Token Security**: Jangan pernah commit token ke repository
2. **Docker Running**: Pastikan Docker Desktop berjalan sebelum menjalankan script
3. **Network**: Pastikan koneksi internet stabil untuk push images
4. **Permissions**: Pastikan token memiliki permission yang diperlukan

