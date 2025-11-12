# 📋 Environment Variables Setup

Dokumentasi environment variables untuk deployment Jargas APBN.

**Struktur: Single Source of Truth** - Semua environment variables hanya di root project, tidak ada duplikasi.

## 🏗️ Struktur Environment Files

### Production Environment
- **Root**: `.env` (semua environment variables untuk docker-compose dan aplikasi)
- **Template**: `.env.example` (contoh konfigurasi)

### Development Environment
- **Root**: `.env.dev` (semua environment variables untuk docker-compose dan aplikasi)
- **Template**: `.env.dev.example` (contoh konfigurasi)

**Note**: Tidak perlu file `.env` di folder `backend/` karena semua variabel di-pass dari docker-compose via environment variables.

## 🔧 Root Environment Variables (.env atau .env.dev)

File ini digunakan oleh:
1. **Docker Compose** - untuk variable substitution (${DB_NAME}, ${SECRET_KEY}, dll)
2. **Backend Application** - semua variabel di-pass ke container via `environment:` section

### Production (.env)

```bash
# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_NAME=jargas_apbn
DB_PASSWORD=admin123                    # Ganti dengan password yang kuat untuk production
DB_PORT_MAPPED=3308

# ============================================
# APPLICATION CONFIGURATION
# ============================================
APP_NAME=Jargas APBN API
APP_VERSION=1.0.0
SECRET_KEY=your-production-secret-key-here    # WAJIB: Generate secret key yang kuat
DEBUG=False                                    # Production: selalu False
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# SERVER CONFIGURATION
# ============================================
HOST=0.0.0.0
PORT=8000

# ============================================
# CORS CONFIGURATION
# ============================================
CORS_ORIGINS=https://jargas.ptkiansantang.com,http://localhost:8080

# ============================================
# FILE UPLOAD CONFIGURATION
# ============================================
UPLOAD_DIR=uploads/evidence
MAX_FILE_SIZE=5242880                         # 5MB
ALLOWED_FILE_TYPES=image/jpeg,image/jpg,image/png,application/pdf

# ============================================
# MIGRATION CONFIGURATION
# ============================================
AUTO_MIGRATE=True
AUTO_MIGRATE_ONLY_IF_PENDING=True
MIGRATION_MODE=sequential
MIGRATION_VALIDATE_BEFORE_UPGRADE=True
MIGRATION_STOP_ON_ERROR=True

# ============================================
# PORT MAPPING (Docker Compose)
# ============================================
BACKEND_PORT_MAPPED=8001
FRONTEND_PORT_MAPPED=8080
ADMINER_PORT_MAPPED=8081
```

### Development (.env.dev)

```bash
# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_NAME=jargas_apbn_dev
DB_PASSWORD=admin123
DB_PORT_MAPPED=3309

# ============================================
# APPLICATION CONFIGURATION
# ============================================
APP_NAME=Jargas APBN API (Dev)
APP_VERSION=1.0.0-dev
SECRET_KEY=your-development-secret-key-here    # WAJIB: Berbeda dari production
DEBUG=True                                       # Development: boleh True
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# SERVER CONFIGURATION
# ============================================
HOST=0.0.0.0
PORT=8000

# ============================================
# CORS CONFIGURATION
# ============================================
CORS_ORIGINS=https://devjargas.ptkiansantang.com,http://localhost:8082,http://localhost:5173

# ============================================
# FILE UPLOAD CONFIGURATION
# ============================================
UPLOAD_DIR=uploads/evidence
MAX_FILE_SIZE=5242880
ALLOWED_FILE_TYPES=image/jpeg,image/jpg,image/png,application/pdf

# ============================================
# MIGRATION CONFIGURATION
# ============================================
AUTO_MIGRATE=True
AUTO_MIGRATE_ONLY_IF_PENDING=True
MIGRATION_MODE=sequential
MIGRATION_VALIDATE_BEFORE_UPGRADE=True
MIGRATION_STOP_ON_ERROR=True

# ============================================
# PORT MAPPING (Docker Compose)
# ============================================
BACKEND_PORT_MAPPED=8002
FRONTEND_PORT_MAPPED=8082
ADMINER_PORT_MAPPED=18083
```

## 📝 Setup Environment Files di Server

### Production Server

```bash
# SSH ke server
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal

# Buat .env di root (copy dari .env.example dan edit)
cp .env.example .env
nano .env

# Atau buat manual
cat > .env << 'EOF'
DB_NAME=jargas_apbn
DB_PASSWORD=your-strong-password-here
DB_PORT_MAPPED=3308
APP_NAME=Jargas APBN API
APP_VERSION=1.0.0
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=https://jargas.ptkiansantang.com,http://localhost:8080
UPLOAD_DIR=uploads/evidence
MAX_FILE_SIZE=5242880
ALLOWED_FILE_TYPES=image/jpeg,image/jpg,image/png,application/pdf
AUTO_MIGRATE=True
AUTO_MIGRATE_ONLY_IF_PENDING=True
MIGRATION_MODE=sequential
MIGRATION_VALIDATE_BEFORE_UPGRADE=True
MIGRATION_STOP_ON_ERROR=True
BACKEND_PORT_MAPPED=8001
FRONTEND_PORT_MAPPED=8080
ADMINER_PORT_MAPPED=8081
EOF
```

### Development Server

```bash
# SSH ke server
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal-dev

# Buat .env.dev di root (copy dari .env.dev.example dan edit)
cp .env.dev.example .env.dev
nano .env.dev

# Atau buat manual
cat > .env.dev << 'EOF'
DB_NAME=jargas_apbn_dev
DB_PASSWORD=admin123
DB_PORT_MAPPED=3309
APP_NAME=Jargas APBN API (Dev)
APP_VERSION=1.0.0-dev
SECRET_KEY=your-development-secret-key-here
DEBUG=True
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=https://devjargas.ptkiansantang.com,http://localhost:8082,http://localhost:5173
UPLOAD_DIR=uploads/evidence
MAX_FILE_SIZE=5242880
ALLOWED_FILE_TYPES=image/jpeg,image/jpg,image/png,application/pdf
AUTO_MIGRATE=True
AUTO_MIGRATE_ONLY_IF_PENDING=True
MIGRATION_MODE=sequential
MIGRATION_VALIDATE_BEFORE_UPGRADE=True
MIGRATION_STOP_ON_ERROR=True
BACKEND_PORT_MAPPED=8002
FRONTEND_PORT_MAPPED=8082
ADMINER_PORT_MAPPED=18083
EOF
```

## 🔄 Cara Kerja

### Di Docker (Production/Development)
1. Docker Compose membaca `.env` atau `.env.dev` dari root project
2. Semua variabel di-pass ke container backend via `environment:` section
3. Backend aplikasi membaca dari environment variables (tidak perlu file `.env` di backend)
4. **Tidak ada duplikasi** - single source of truth

### Development Lokal (Tanpa Docker)
1. Backend aplikasi auto-detect file `.env` atau `.env.dev` di root project
2. Jika tidak ada, menggunakan environment variables atau default values
3. **Tidak perlu file `.env` di folder backend**

## ⚠️ Catatan Penting

1. **SECRET_KEY**: 
   - Wajib diisi dengan secret key yang kuat dan unik
   - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Production dan Development harus berbeda

2. **DB_PASSWORD**: 
   - Ganti password default untuk production
   - Development boleh pakai default `admin123`

3. **CORS_ORIGINS**: 
   - Format: comma-separated tanpa spasi
   - Production: hanya domain production
   - Development: boleh include localhost untuk testing

4. **DEBUG**: 
   - Production: selalu `False`
   - Development: boleh `True` untuk debugging

5. **File .env tidak boleh di-commit ke Git** 
   - Gunakan `.env.example` dan `.env.dev.example` sebagai template
   - File `.env*` sudah di-ignore di `.gitignore`

6. **Tidak perlu file `.env` di folder backend**
   - Semua variabel sudah di root project
   - Docker Compose pass semua variabel ke container

## 🔐 Security Best Practices

1. ✅ Gunakan secret key yang kuat (minimal 32 karakter, random)
2. ✅ Jangan commit file `.env` atau `.env.dev` ke Git
3. ✅ Ganti password default database untuk production
4. ✅ Gunakan HTTPS untuk production (sudah dikonfigurasi di nginx)
5. ✅ Batasi CORS origins hanya ke domain yang diperlukan
6. ✅ Production dan Development harus menggunakan SECRET_KEY yang berbeda
7. ✅ Review semua environment variables sebelum deploy ke production

## 📊 Perbandingan Struktur

### Sebelum (8 file - ada redundancy)
```
Root: .env, .env.dev, .env.example, .env.dev.example
Backend: .env, .env.dev, .env.example, .env.dev.example
```
**Masalah**: SECRET_KEY, DB_NAME, DEBUG, CORS_ORIGINS harus sama di root dan backend (duplikasi)

### Sekarang (4 file - single source of truth)
```
Root: .env, .env.dev, .env.example, .env.dev.example
Backend: (tidak perlu file .env)
```
**Keuntungan**: Tidak ada duplikasi, lebih mudah dirawat, single source of truth

## 🛠️ Troubleshooting

### Backend tidak membaca environment variables
- Pastikan file `.env` atau `.env.dev` ada di root project
- Pastikan docker-compose menggunakan `--env-file .env` atau `--env-file .env.dev`
- Cek log container: `docker-compose logs backend`

### Environment variables tidak ter-update
- Rebuild container: `docker-compose build --no-cache`
- Restart container: `docker-compose restart backend`

### Development lokal tidak membaca .env
- Pastikan file `.env` atau `.env.dev` ada di root project (bukan di backend/)
- Backend akan auto-detect file di root project
