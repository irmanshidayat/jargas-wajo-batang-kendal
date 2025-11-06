# Tutorial Setup dan Upload ke GitHub - Jargas APBN

Dokumentasi lengkap untuk menyimpan dan mengelola kode proyek Jargas APBN di GitHub.

## 📋 Daftar Isi

- [Prasyarat](#prasyarat)
- [Cara Membuat Repository di GitHub](#cara-membuat-repository-di-github)
- [Setup Git di Local](#setup-git-di-local)
- [Upload Kode ke GitHub](#upload-kode-ke-github)
- [Update Kode ke GitHub](#update-kode-ke-github)
- [Struktur File yang Di-commit](#struktur-file-yang-di-commit)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## 🛠️ Prasyarat

Sebelum memulai, pastikan Anda sudah menginstall:

1. **Git** (versi 2.30 atau lebih baru)
   - Download: https://git-scm.com/download/win
   - Verifikasi: `git --version`
   
2. **Akun GitHub**
   - Daftar di: https://github.com/signup
   - Pastikan sudah login

3. **GitHub Personal Access Token** (untuk push)
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token dengan scope: `repo`
   - Simpan token dengan aman (hanya muncul sekali)

---

## 🆕 Cara Membuat Repository di GitHub

### Langkah 1: Buat Repository Baru

1. Buka https://github.com/new
2. Isi informasi repository:
   - **Repository name**: `jargas-apbn` (atau nama yang diinginkan)
   - **Description**: "Sistem Manajemen Jargas APBN"
   - **Visibility**: 
     - **Public** (semua orang bisa lihat)
     - **Private** (hanya Anda yang bisa akses)
   - **JANGAN** centang "Add a README file"
   - **JANGAN** centang "Add .gitignore"
   - **JANGAN** centang "Choose a license"
3. Klik **"Create repository"**

### Langkah 2: Catat URL Repository

Setelah repository dibuat, Anda akan melihat URL seperti:
- `https://github.com/username/jargas-apbn.git`

**Simpan URL ini** untuk digunakan di langkah selanjutnya.

---

## 💻 Setup Git di Local

### Langkah 1: Buka Terminal di Root Folder Project

1. Buka folder project: `C:\Irman\Coding Jargas APBN\Jargas APBN`
2. Buka terminal di folder tersebut:
   - Klik kanan di folder → **"Open in Terminal"** atau
   - Tekan `Shift + Right Click` → **"Open PowerShell window here"**

### Langkah 2: Konfigurasi Git (Pertama Kali)

Jalankan perintah berikut di terminal:

```bash
# Konfigurasi nama (sesuaikan dengan nama Anda)
git config --global user.name "Irman"

# Konfigurasi email (gunakan email yang sama dengan GitHub)
git config --global user.email "your.email@example.com"

# Konfigurasi line endings untuk Windows (untuk menghindari warning)
git config --global core.autocrlf true

# Verifikasi konfigurasi
git config --list
```

**Catatan**: 
- Jika sudah pernah setup Git sebelumnya, langkah nama dan email bisa dilewati
- Konfigurasi `core.autocrlf true` membantu menghindari warning line endings di Windows

### Langkah 3: Inisialisasi Git Repository

```bash
# Masuk ke root folder project (jika belum)
cd "C:\Irman\Coding Jargas APBN\Jargas APBN"

# Inisialisasi Git
git init
```

Output yang diharapkan:
```
Initialized empty Git repository in C:/Irman/Coding Jargas APBN/Jargas APBN/.git/
```

---

## 📤 Upload Kode ke GitHub

### Langkah 1: Cek Status File

```bash
# Cek file apa saja yang akan di-commit
git status
```

File yang **TIDAK** akan di-commit (karena ada di `.gitignore`):
- `backend/venv/` atau `backend/.venv/` (virtual environment)
- `frontend/node_modules/` (dependencies)
- `backend/uploads/` (file upload)
- `.env` (environment variables)
- `__pycache__/` (Python cache)

**Jika folder `.venv` masih muncul di status:**
```bash
# Hapus dari staging area (jika sudah ter-add)
git rm -r --cached backend/.venv/

# Pastikan .gitignore sudah benar
# File .gitignore di root harus berisi: backend/.venv/
```

### Langkah 2: Tambahkan File ke Staging

```bash
# Tambahkan semua file ke staging area
git add .

# Atau tambahkan file spesifik jika perlu
git add backend/
git add frontend/
git add docker-compose.yml
```

### Langkah 3: Buat Commit Pertama

```bash
# Buat commit dengan pesan
git commit -m "Initial commit: Jargas APBN System"
```

Output yang diharapkan:
```
[main (root-commit) abc1234] Initial commit: Jargas APBN System
 X files changed, Y insertions(+)
```

### Langkah 4: Hubungkan dengan GitHub Repository

```bash
# Tambahkan remote repository (ganti dengan URL repository Anda)
git remote add origin https://github.com/username/jargas-apbn.git

# Verifikasi remote
git remote -v
```

### Langkah 5: Push ke GitHub

```bash
# Ubah branch ke main (jika belum)
git branch -M main

# Push ke GitHub
git push -u origin main
```

**Jika meminta autentikasi:**
- **Username**: Masukkan username GitHub Anda
- **Password**: Masukkan **Personal Access Token** (bukan password GitHub)

Setelah berhasil, buka repository di browser dan cek apakah semua file sudah ter-upload.

---

## 🔄 Update Kode ke GitHub

Setelah melakukan perubahan kode, ikuti langkah berikut:

### Langkah 1: Cek Perubahan

```bash
# Lihat file apa saja yang berubah
git status

# Lihat detail perubahan (opsional)
git diff
```

### Langkah 2: Tambahkan Perubahan

```bash
# Tambahkan semua perubahan
git add .

# Atau tambahkan file spesifik
git add backend/app/main.py
git add frontend/src/App.tsx
```

### Langkah 3: Commit Perubahan

```bash
# Buat commit dengan pesan yang deskriptif
git commit -m "Fix: Perbaikan bug pada fitur inventory"
```

**Tips Pesan Commit:**
- `feat: Tambah fitur export Excel`
- `fix: Perbaikan bug validasi form`
- `refactor: Refactor kode service`
- `docs: Update dokumentasi`
- `style: Perbaikan formatting code`

### Langkah 4: Push ke GitHub

```bash
# Push perubahan ke GitHub
git push
```

**Catatan**: Jika sudah menggunakan `git push -u origin main` sebelumnya, cukup ketik `git push` saja.

---

## 📁 Struktur File yang Di-commit

File dan folder yang **AKAN** di-upload ke GitHub:

```
✅ backend/
   ✅ app/ (semua kode Python)
   ✅ migrations/ (database migrations)
   ✅ scripts/ (utility scripts)
   ✅ Dockerfile
   ✅ requirements.txt
   ✅ env.example (template environment)
   ✅ .gitignore
   ❌ venv/ (TIDAK di-commit)
   ❌ .env (TIDAK di-commit)
   ❌ uploads/ (TIDAK di-commit)

✅ frontend/
   ✅ src/ (semua kode React/TypeScript)
   ✅ public/
   ✅ package.json
   ✅ package-lock.json
   ✅ Dockerfile
   ✅ .gitignore
   ❌ node_modules/ (TIDAK di-commit)
   ❌ dist/ (TIDAK di-commit)

✅ docker-compose.yml
✅ .gitignore (di root)
✅ Catatan Penting/
```

---

## 🔧 Troubleshooting

### Error: "fatal: remote origin already exists"

**Solusi:**
```bash
# Hapus remote yang lama
git remote remove origin

# Tambahkan lagi dengan URL yang benar
git remote add origin https://github.com/username/jargas-apbn.git
```

### Error: "Permission denied" saat push

**Solusi:**
1. Pastikan sudah login GitHub dengan benar
2. Gunakan **Personal Access Token** bukan password
3. Cek apakah repository adalah milik Anda atau punya akses

### Error: "failed to push some refs"

**Solusi:**
```bash
# Pull dulu perubahan dari GitHub (jika ada)
git pull origin main --allow-unrelated-histories

# Push lagi
git push -u origin main
```

### File .env Ter-commit

**Solusi:**
```bash
# Hapus dari Git (tapi tetap ada di local)
git rm --cached backend/.env

# Commit perubahan
git commit -m "Remove .env from Git"

# Push
git push
```

Pastikan `.env` sudah ada di `.gitignore`.

### File `venv/` atau `node_modules/` Ter-commit

**Solusi:**
```bash
# Hapus folder dari Git
git rm -r --cached backend/venv/
git rm -r --cached backend/.venv/
git rm -r --cached frontend/node_modules/

# Commit
git commit -m "Remove venv and node_modules from Git"

# Push
git push
```

Pastikan folder tersebut sudah ada di `.gitignore`.

### Warning: "LF will be replaced by CRLF"

Warning ini muncul karena perbedaan line endings antara Windows (CRLF) dan Linux/Mac (LF). Ini **normal** dan tidak berbahaya.

**Solusi (Opsional):**
```bash
# Konfigurasi Git untuk auto-convert line endings
git config --global core.autocrlf true

# Atau untuk Windows, gunakan input (tidak convert saat commit)
git config --global core.autocrlf input

# Verifikasi
git config --global core.autocrlf
```

**Penjelasan:**
- `true`: Auto-convert CRLF → LF saat commit, LF → CRLF saat checkout (untuk Windows)
- `input`: Auto-convert CRLF → LF saat commit, tidak convert saat checkout (untuk Linux/Mac)
- `false`: Tidak convert sama sekali

**Rekomendasi untuk Windows:**
```bash
git config --global core.autocrlf true
```

Warning ini tidak akan mempengaruhi kode Anda, hanya informasi bahwa Git akan melakukan konversi otomatis.

---

## 💡 Best Practices

### 1. Commit Message yang Baik

**Hindari:**
```
git commit -m "update"
git commit -m "fix"
git commit -m "perbaikan"
```

**Gunakan:**
```
git commit -m "feat: Tambah fitur export data ke Excel"
git commit -m "fix: Perbaikan validasi form input material"
git commit -m "refactor: Optimasi query database di inventory service"
```

### 2. Commit Secara Berkala

- Jangan tunggu terlalu lama untuk commit
- Commit setiap fitur atau perbaikan selesai
- Lebih mudah untuk rollback jika ada masalah

### 3. Jangan Commit File Sensitif

Pastikan file berikut **TIDAK** pernah di-commit:
- `.env` (berisi password, API key, dll)
- File dengan credential
- File upload user (kecuali sampel)

### 4. Gunakan Branch untuk Fitur Besar

```bash
# Buat branch baru untuk fitur
git checkout -b feature/export-excel

# Kerjakan fitur
# ... edit file ...

# Commit
git add .
git commit -m "feat: Tambah fitur export Excel"

# Push branch
git push -u origin feature/export-excel

# Merge ke main (via GitHub Pull Request atau langsung)
git checkout main
git merge feature/export-excel
```

### 5. Pull Sebelum Push

Jika bekerja dengan tim:
```bash
# Selalu pull dulu sebelum push
git pull origin main

# Baru push perubahan Anda
git push
```

---

## 📚 Command Git yang Sering Digunakan

### Cek Status
```bash
git status
```

### Lihat History Commit
```bash
git log
git log --oneline
```

### Lihat Perubahan
```bash
git diff
git diff filename.py
```

### Undo Perubahan (belum di-commit)
```bash
# Batalkan perubahan file tertentu
git checkout -- filename.py

# Batalkan semua perubahan
git checkout .
```

### Undo Commit (belum di-push)
```bash
# Batalkan commit terakhir, tapi tetap simpan perubahan
git reset --soft HEAD~1

# Batalkan commit terakhir, hapus perubahan
git reset --hard HEAD~1
```

### Clone Repository
```bash
# Clone repository dari GitHub
git clone https://github.com/username/jargas-apbn.git
```

---

## 🔐 Keamanan

### Jangan Commit File Sensitif

File yang **HARUS** ada di `.gitignore`:
- `.env`
- `.env.local`
- `backend/uploads/` (file user)
- `*.key`
- `*.pem`
- File dengan credential

### Gunakan GitHub Secrets untuk CI/CD

Jika menggunakan GitHub Actions, simpan secret di:
- Settings → Secrets and variables → Actions

---

## 📞 Bantuan

Jika mengalami masalah:

1. **Cek dokumentasi Git**: https://git-scm.com/doc
2. **Cek dokumentasi GitHub**: https://docs.github.com
3. **Google error message** yang muncul
4. **Stack Overflow**: https://stackoverflow.com

---

## ✅ Checklist Setup GitHub

- [ ] Git sudah terinstall
- [ ] Akun GitHub sudah dibuat
- [ ] Personal Access Token sudah dibuat
- [ ] Repository GitHub sudah dibuat
- [ ] Git sudah dikonfigurasi (nama & email)
- [ ] Git repository sudah diinisialisasi
- [ ] File sudah di-commit
- [ ] Remote sudah ditambahkan
- [ ] Kode sudah di-push ke GitHub
- [ ] File `.gitignore` sudah benar
- [ ] File `.env` tidak ter-commit

---

**Selamat! Proyek Jargas APBN Anda sudah tersimpan di GitHub! 🎉**

Untuk update selanjutnya, cukup jalankan:
```bash
git add .
git commit -m "Deskripsi perubahan"
git push
```

