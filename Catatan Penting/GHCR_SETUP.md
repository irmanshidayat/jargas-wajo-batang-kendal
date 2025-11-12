# Tutorial Push Docker Images ke GitHub Container Registry (GHCR) - Jargas APBN

Dokumentasi lengkap untuk memindahkan Docker images aplikasi Jargas APBN ke GitHub Container Registry (GHCR).

## 📋 Daftar Isi

- [Prasyarat](#prasyarat)
- [Pengenalan GHCR](#pengenalan-ghcr)
- [Setup Awal](#setup-awal)
- [Build dan Tag Images](#build-dan-tag-images)
- [Push Images ke GHCR](#push-images-ke-ghcr)
- [Menggunakan Images dari GHCR](#menggunakan-images-dari-ghcr)
- [Otomatisasi dengan GitHub Actions](#otomatisasi-dengan-github-actions)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## 🛠️ Prasyarat

Sebelum memulai, pastikan Anda sudah:

1. **Docker** (versi 20.10 atau lebih baru)
   - Download: https://www.docker.com/get-started
   - Verifikasi: `docker --version`

2. **Akun GitHub**
   - Daftar di: https://github.com/signup
   - Pastikan sudah login

3. **GitHub Repository**
   - Repository sudah dibuat (lihat: `GITHUB_SETUP.md`)
   - Akses write ke repository

4. **GitHub Personal Access Token (PAT)**
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token dengan scope:
     - ✅ `write:packages` (untuk push images)
     - ✅ `read:packages` (untuk pull images)
     - ✅ `delete:packages` (opsional, untuk delete images)
   - Simpan token dengan aman (hanya muncul sekali)

Cara membuat token
Buka GitHub Settings
Login ke GitHub → klik foto profil → Settings
Masuk ke Developer settings
Di sidebar kiri, Developer settings → Personal access tokens → Tokens (classic)
Generate token baru
Klik "Generate new token" → "Generate new token (classic)"
Konfigurasi token
Note: beri nama, misalnya "GHCR Docker Push"
Expiration: pilih durasi (30 hari, 90 hari, atau custom)
Select scopes:
write:packages — untuk push images ke GHCR
read:packages — untuk pull images dari GHCR
delete:packages — untuk menghapus packages (opsional)
Generate dan simpan
Klik "Generate token"
Salin token (hanya muncul sekali) dan simpan dengan aman
Scope yang digunakan
write:packages
Untuk: push Docker images ke GHCR
Contoh: docker push ghcr.io/username/image:tag
read:packages
Untuk: pull Docker images dari GHCR
Contoh: docker pull ghcr.io/username/image:tag
delete:packages
Untuk: menghapus packages/images dari GHCR
Opsional, hanya jika perlu
Contoh penggunaan token
# Ganti dengan token yang Anda buat$GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"$GITHUB_USERNAME = "your-username"# Login ke GHCR menggunakan tokenecho $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

---

## 📚 Pengenalan GHCR

**GitHub Container Registry (GHCR)** adalah layanan Docker registry yang terintegrasi dengan GitHub. Keuntungan menggunakan GHCR:

- ✅ **Gratis** untuk public packages
- ✅ **Terintegrasi** dengan GitHub repository
- ✅ **Keamanan** dengan GitHub authentication
- ✅ **Mudah** diakses dan dikelola
- ✅ **Unlimited** storage untuk public packages

### Format Image Name

Format untuk GHCR:
```
ghcr.io/<username>/<image-name>:<tag>
```

Contoh:
- `ghcr.io/username/jargas-apbn-frontend:latest`
- `ghcr.io/username/jargas-apbn-backend:v1.0.0`

---

## 🚀 Setup Awal

### Langkah 1: Login ke GHCR

```powershell
# Ganti dengan token dan username GitHub Anda
# Pastikan variabel sudah di-set
$GITHUB_USERNAME = "irmanshidayat"
$GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Ganti dengan token Anda

# Login ke GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
```

# Jalankan script
.\scripts\active\push-to-ghcr.ps1 -GitHubUsername $GITHUB_USERNAME -GitHubToken $GITHUB_TOKEN -Version "latest"

# untuk lihat berhasil push atau tidak disini
https://github.com/irmanshidayat?tab=packages

**Catatan Keamanan:**
- Jangan commit token ke repository
- Simpan token di environment variable atau file terpisah
- Gunakan `$env:VARIABLE_NAME` untuk Windows PowerShell

### Langkah 2: Verifikasi Login

```powershell
# Cek apakah sudah login
docker info | Select-String "ghcr.io"

# Atau coba pull image (jika ada)
docker pull ghcr.io/$GITHUB_USERNAME/jargas-apbn-frontend:latest
```

---

## 🏗️ Build dan Tag Images

### Langkah 1: Build Images Lokal

Pastikan images sudah di-build dengan benar:

```powershell
# Build Frontend
docker-compose build frontend

# Build Backend
docker-compose build backend

# Atau build semua sekaligus
docker-compose build
```

### Langkah 2: Tag Images untuk GHCR

```powershell
# Ganti dengan username GitHub Anda
$GITHUB_USERNAME = "your-github-username"
$IMAGE_VERSION = "latest"  # atau "v1.0.0", "main", dll

# Tag Frontend
docker tag jargasapbn-frontend:latest ghcr.io/$GITHUB_USERNAME/jargas-apbn-frontend:$IMAGE_VERSION
docker tag jargasapbn-frontend:latest ghcr.io/$GITHUB_USERNAME/jargas-apbn-frontend:latest

# Tag Backend
docker tag jargasapbn-backend:latest ghcr.io/$GITHUB_USERNAME/jargas-apbn-backend:$IMAGE_VERSION
docker tag jargasapbn-backend:latest ghcr.io/$GITHUB_USERNAME/jargas-apbn-backend:latest

# Verifikasi tags
docker images | Select-String "ghcr.io"
```

**Atau build langsung dengan tag:**

```powershell
$GITHUB_USERNAME = "your-github-username"
$IMAGE_VERSION = "latest"

# Build dan tag Frontend langsung
docker build -t ghcr.io/$GITHUB_USERNAME/jargas-apbn-frontend:$IMAGE_VERSION ./frontend
docker tag ghcr.io/$GITHUB_USERNAME/jargas-apbn-frontend:$IMAGE_VERSION ghcr.io/$GITHUB_USERNAME/jargas-apbn-frontend:latest

# Build dan tag Backend langsung
docker build -t ghcr.io/$GITHUB_USERNAME/jargas-apbn-backend:$IMAGE_VERSION ./backend
docker tag ghcr.io/$GITHUB_USERNAME/jargas-apbn-backend:$IMAGE_VERSION ghcr.io/$GITHUB_USERNAME/jargas-apbn-backend:latest
```

---

## 📤 Push Images ke GHCR

### Langkah 1: Push Images

```powershell
$GITHUB_USERNAME = "your-github-username"
$IMAGE_VERSION = "latest"

# Push Frontend
docker push ghcr.io/$GITHUB_USERNAME/jargas-apbn-frontend:$IMAGE_VERSION
docker push ghcr.io/$GITHUB_USERNAME/jargas-apbn-frontend:latest

# Push Backend
docker push ghcr.io/$GITHUB_USERNAME/jargas-apbn-backend:$IMAGE_VERSION
docker push ghcr.io/$GITHUB_USERNAME/jargas-apbn-backend:latest
```

### Langkah 2: Verifikasi di GitHub

1. Buka repository GitHub Anda
2. Klik tab **Packages** di sidebar kanan
3. Anda akan melihat packages:
   - `jargas-apbn-frontend`
   - `jargas-apbn-backend`

### Langkah 3: Set Package Visibility

Setiap package baru secara default adalah **private**. Untuk mengubah:

1. Buka package di GitHub
2. Klik **Package settings**
3. Scroll ke **Danger Zone**
4. Klik **Change visibility** → Pilih **Public** atau **Private**

---

## 🔄 Menggunakan Images dari GHCR

### Opsi 1: Menggunakan di docker-compose.yml

Edit `docker-compose.yml` untuk menggunakan images dari GHCR:

```yaml
services:
  backend:
    image: ghcr.io/YOUR_GITHUB_USERNAME/jargas-apbn-backend:latest
    # Hapus bagian build:
    # build:
    #   context: ./backend
    #   dockerfile: Dockerfile
    container_name: jargas_backend
    # ... rest of config ...

  frontend:
    image: ghcr.io/YOUR_GITHUB_USERNAME/jargas-apbn-frontend:latest
    # Hapus bagian build:
    # build:
    #   context: ./frontend
    #   dockerfile: Dockerfile
    container_name: jargas_frontend
    # ... rest of config ...
```

### Opsi 2: Pull Images Manual

```powershell
# Login dulu
$GITHUB_TOKEN = "your_token"
$GITHUB_USERNAME = "your_username"
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Pull images
docker pull ghcr.io/$GITHUB_USERNAME/jargas-apbn-frontend:latest
docker pull ghcr.io/$GITHUB_USERNAME/jargas-apbn-backend:latest
```

### Opsi 3: Hybrid (Build Lokal atau Pull dari GHCR)

Gunakan environment variable untuk switch antara build lokal atau pull dari GHCR:

```yaml
services:
  backend:
    # Jika USE_GHCR=true, gunakan image dari GHCR
    # Jika false atau tidak ada, build dari lokal
    ${USE_GHCR:+image}: ghcr.io/YOUR_GITHUB_USERNAME/jargas-apbn-backend:latest
    ${USE_GHCR:-build}:
      context: ./backend
      dockerfile: Dockerfile
    # ... rest of config ...
```

---

## 🤖 Otomatisasi dengan GitHub Actions

Buat file `.github/workflows/docker-publish.yml` untuk otomatisasi build dan push:

```yaml
name: Build and Push Docker Images to GHCR

on:
  push:
    branches:
      - main
      - master
    tags:
      - 'v*'
  pull_request:
    branches:
      - main
      - master

env:
  REGISTRY: ghcr.io
  FRONTEND_IMAGE_NAME: ${{ github.repository }}-frontend
  BACKEND_IMAGE_NAME: ${{ github.repository }}-backend

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (frontend)
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Extract metadata (backend)
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push Backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Penjelasan Workflow:**

- **Trigger**: Build otomatis saat push ke `main`/`master` atau saat membuat tag `v*`
- **Permissions**: Membutuhkan `write:packages` untuk push images
- **Tags**: Otomatis membuat tags berdasarkan branch, semver, atau commit SHA
- **Cache**: Menggunakan GitHub Actions cache untuk mempercepat build

---

## 🔧 Script Otomatisasi (PowerShell)

Buat file `scripts/push-to-ghcr.ps1` untuk memudahkan push:

```powershell
# Script untuk push Docker images ke GHCR
param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [string]$Version = "latest"
)

# Login ke GHCR
Write-Host "Logging in to GHCR..." -ForegroundColor Cyan
echo $GitHubToken | docker login ghcr.io -u $GitHubUsername --password-stdin

if ($LASTEXITCODE -ne 0) {
    Write-Host "Login failed!" -ForegroundColor Red
    exit 1
}

# Build Frontend
Write-Host "Building Frontend..." -ForegroundColor Cyan
docker build -t ghcr.io/$GitHubUsername/jargas-apbn-frontend:$Version ./frontend
docker tag ghcr.io/$GitHubUsername/jargas-apbn-frontend:$Version ghcr.io/$GitHubUsername/jargas-apbn-frontend:latest

# Build Backend
Write-Host "Building Backend..." -ForegroundColor Cyan
docker build -t ghcr.io/$GitHubUsername/jargas-apbn-backend:$Version ./backend
docker tag ghcr.io/$GitHubUsername/jargas-apbn-backend:$Version ghcr.io/$GitHubUsername/jargas-apbn-backend:latest

# Push Frontend
Write-Host "Pushing Frontend..." -ForegroundColor Cyan
docker push ghcr.io/$GitHubUsername/jargas-apbn-frontend:$Version
docker push ghcr.io/$GitHubUsername/jargas-apbn-frontend:latest

# Push Backend
Write-Host "Pushing Backend..." -ForegroundColor Cyan
docker push ghcr.io/$GitHubUsername/jargas-apbn-backend:$Version
docker push ghcr.io/$GitHubUsername/jargas-apbn-backend:latest

Write-Host "Done! Images pushed to GHCR." -ForegroundColor Green
```

**Cara menggunakan:**

```powershell
# Dari root project
.\scripts\active\push-to-ghcr.ps1 -GitHubUsername "your-username" -GitHubToken "your-token" -Version "v1.0.0"
```

---

## 🐛 Troubleshooting

### Masalah 1: Login Gagal

**Error:**
```
Error response from daemon: login attempt to https://ghcr.io/v2/ failed with status: 401 Unauthorized
```

**Solusi:**
1. Pastikan token valid dan belum expired
2. Pastikan token memiliki scope `write:packages`
3. Coba generate token baru

### Masalah 2: Push Gagal - Unauthorized

**Error:**
```
denied: permission_denied: write_package
```

**Solusi:**
1. Pastikan token memiliki permission `write:packages`
2. Pastikan package visibility sudah di-set (Public atau Private dengan akses)
3. Cek apakah package sudah di-link ke repository

### Masalah 3: Image Tidak Ditemukan

**Error:**
```
manifest unknown
```

**Solusi:**
1. Pastikan image sudah di-push
2. Pastikan tag yang digunakan benar
3. Cek di GitHub Packages apakah image sudah ada

### Masalah 4: Pull Image Gagal - Private Package

**Error:**
```
unauthorized: authentication required
```

**Solusi:**
1. Login ke GHCR dulu sebelum pull
2. Pastikan Anda memiliki akses ke package (untuk private package)
3. Gunakan token dengan scope `read:packages`

### Masalah 5: Build Error di GitHub Actions

**Error:**
```
permissions error
```

**Solusi:**
1. Pastikan workflow memiliki permissions:
   ```yaml
   permissions:
     contents: read
     packages: write
   ```
2. Pastikan `GITHUB_TOKEN` tidak perlu di-set manual (otomatis tersedia)

---

## 📝 Best Practices

### 1. Tagging Strategy

Gunakan semantic versioning untuk tags:

```powershell
# Version tags
docker tag image:latest ghcr.io/username/image:v1.0.0
docker tag image:latest ghcr.io/username/image:v1.0
docker tag image:latest ghcr.io/username/image:v1
docker tag image:latest ghcr.io/username/image:latest
```

### 2. Security

- ✅ **Jangan commit token** ke repository
- ✅ Gunakan **GitHub Secrets** untuk token di GitHub Actions
- ✅ Gunakan **environment variables** untuk token lokal
- ✅ Set package **visibility** sesuai kebutuhan
- ✅ **Rotate token** secara berkala

### 3. Image Size

- ✅ Gunakan **multi-stage builds** (sudah diimplementasi)
- ✅ **Optimize** Dockerfile untuk mengurangi ukuran
- ✅ Hapus **unused images** secara berkala

### 4. Versioning

- ✅ Gunakan **semantic versioning** (v1.0.0, v1.0.1, dll)
- ✅ Tag **latest** untuk version terbaru
- ✅ Tag dengan **commit SHA** untuk tracking

### 5. Documentation

- ✅ Dokumentasikan **cara pull** images
- ✅ Buat **README** di package dengan instruksi
- ✅ Update **changelog** untuk setiap release

---

## 📚 Referensi

- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## ✅ Checklist

Sebelum push ke GHCR, pastikan:

- [ ] Docker sudah terinstall dan berjalan
- [ ] GitHub repository sudah dibuat
- [ ] GitHub Personal Access Token sudah dibuat dengan scope yang benar
- [ ] Login ke GHCR berhasil
- [ ] Images sudah di-build dengan benar
- [ ] Images sudah di-tag dengan format yang benar
- [ ] Push images berhasil
- [ ] Package visibility sudah di-set
- [ ] Dokumentasi sudah dibuat

---

**Selamat! Docker images Anda sekarang sudah tersimpan di GitHub Container Registry! 🎉**

