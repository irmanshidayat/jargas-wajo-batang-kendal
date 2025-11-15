# Backend - Setup Tanpa Docker

Dokumentasi untuk menjalankan backend Jargas APBN tanpa Docker (development lokal).

## 📋 Prasyarat

1. **Python 3.11 atau lebih tinggi**
   - Download dari: https://www.python.org/downloads/
   - Pastikan Python ditambahkan ke PATH saat instalasi

2. **XAMPP (MySQL)**
   - Download dari: https://www.apachefriends.org/
   - Install dan pastikan MySQL service berjalan
   - Default port: 3306
   - Default user: root
   - Default password: (kosong)

3. **Database MySQL**
   - Buat database: `jargas_apbn_dev` atau `jargas_apbn`
   - Bisa dibuat via phpMyAdmin (http://localhost/phpmyadmin)

## 🚀 Quick Start

### 1. Setup Virtual Environment

Jalankan script setup untuk membuat virtual environment dan install dependencies:

```powershell
cd backend
.\setup-venv.ps1
```

Script ini akan:
- ✅ Memeriksa Python version
- ✅ Membuat virtual environment (`venv/`)
- ✅ Install semua dependencies dari `requirements.txt`
- ✅ Verifikasi instalasi

**Catatan:** Jika error tentang execution policy PowerShell, jalankan:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Konfigurasi Environment

Backend akan membaca file `.env` dari root project dengan priority:
1. `.env.dev` di root project (untuk development)
2. `.env` di root project (untuk production/default)

**Opsi 1: Gunakan file .env.dev di root (Recommended)**
- Copy `env.dev.example` ke `.env.dev` di root project
- Edit dan sesuaikan konfigurasi database XAMPP:
  ```env
  DB_HOST=localhost
  DB_PORT=3306
  DB_USER=root
  DB_PASSWORD=          # Kosong jika XAMPP default
  DB_NAME=jargas_apbn_dev
  ```

**Opsi 2: Gunakan file .env.local di backend (Alternatif)**
- Copy `backend/.env.local.example` ke `backend/.env.local`
- Edit konfigurasi sesuai kebutuhan
- Set environment variable: `$env:ENV_FILE="backend/.env.local"`

### 3. Jalankan Backend

Jalankan script untuk menjalankan backend:

```powershell
cd backend
.\run-local.ps1
```

Backend akan berjalan di: **http://localhost:8000**

**Fitur:**
- ✅ Hot-reload otomatis (auto-reload saat file berubah)
- ✅ Auto-migration database (jika `AUTO_MIGRATE=True`)
- ✅ API Documentation: http://localhost:8000/docs
- ✅ Health Check: http://localhost:8000/health

## 📝 Manual Setup (Tanpa Script)

Jika ingin setup manual:

### 1. Buat Virtual Environment

```powershell
cd backend
python -m venv venv
```

### 2. Aktifkan Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Jalankan Backend

```powershell
python run.py
```

## 🔧 Konfigurasi

### Database Configuration (XAMPP)

File `.env.dev` atau `.env` di root project:

```env
# Database XAMPP MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=              # Kosong untuk XAMPP default
DB_NAME=jargas_apbn_dev   # Sesuaikan dengan database yang dibuat
```

### Server Configuration

```env
# Server
HOST=127.0.0.1           # localhost (hanya local)
# atau
HOST=0.0.0.0             # Semua interface (untuk akses dari device lain)

PORT=8000                # Port backend
```

### CORS Configuration

Untuk development lokal dengan frontend:

```env
CORS_ORIGINS=http://localhost:8080,http://localhost:3000,http://localhost:5173
```

### Auto-Migration

```env
# Auto-migrate saat startup
AUTO_MIGRATE=True
AUTO_MIGRATE_ONLY_IF_PENDING=True
MIGRATION_MODE=sequential
```

## 🗄️ Database Migration

### Auto-Migration (Recommended)

Backend akan otomatis migrate saat startup jika `AUTO_MIGRATE=True`.

### Manual Migration

Jika auto-migration tidak aktif atau ingin migrate manual:

```powershell
# Aktifkan virtual environment
.\venv\Scripts\Activate.ps1

# Cek status migration
alembic current

# Upgrade ke latest
alembic upgrade head

# Atau gunakan script smart migrate
python -m scripts.smart_migrate
```

## 🐛 Troubleshooting

### Error: Python tidak ditemukan

**Solusi:**
- Pastikan Python terinstall dan ditambahkan ke PATH
- Restart terminal setelah install Python
- Verifikasi: `python --version`

### Error: Execution Policy

**Error:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solusi:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: Database Connection

**Error:**
```
OperationalError: (2003, "Can't connect to MySQL server")
```

**Solusi:**
- Pastikan XAMPP MySQL service berjalan
- Cek konfigurasi `DB_HOST`, `DB_PORT` di file `.env`
- Verifikasi database sudah dibuat
- Test koneksi: `mysql -u root -h localhost -P 3306`

### Error: Module tidak ditemukan

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solusi:**
- Pastikan virtual environment aktif: `.\venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`
- Verifikasi instalasi: `pip list`

### Error: Port sudah digunakan

**Error:**
```
Address already in use
```

**Solusi:**
- Cek aplikasi lain yang menggunakan port 8000
- Ubah `PORT` di file `.env` ke port lain (misal: 8001)
- Atau stop aplikasi yang menggunakan port tersebut

### Error: Migration Error

**Error:**
```
Alembic migration error
```

**Solusi:**
- Cek status migration: `alembic current`
- Cek log error untuk detail
- Jika perlu, rollback: `alembic downgrade -1`
- Atau gunakan script smart migrate: `python -m scripts.smart_migrate --status`

## 📚 API Documentation

Setelah backend berjalan, akses:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 🔄 Hot Reload

Backend menggunakan uvicorn dengan `reload=True` untuk development, sehingga:
- ✅ Perubahan file Python akan otomatis reload
- ✅ Tidak perlu restart manual
- ✅ Cocok untuk development cepat

## 📁 Struktur File

```
backend/
├── setup-venv.ps1          # Script setup virtual environment
├── run-local.ps1           # Script run backend lokal
├── .env.local.example       # Template environment (opsional)
├── README-LOCAL.md          # Dokumentasi ini
├── run.py                   # Entry point aplikasi
├── requirements.txt         # Dependencies
├── venv/                    # Virtual environment (dibuat oleh setup-venv.ps1)
└── app/                     # Source code aplikasi
```

## 💡 Tips

1. **Gunakan Virtual Environment**
   - Selalu aktifkan virtual environment sebelum menjalankan backend
   - Jangan install dependencies di global Python

2. **File .env**
   - Jangan commit file `.env` ke repository
   - Gunakan `.env.example` sebagai template

3. **Database**
   - Backup database sebelum migration
   - Test migration di development dulu sebelum production

4. **Development**
   - Gunakan `DEBUG=True` untuk development
   - Gunakan `AUTO_MIGRATE=True` untuk auto-migration
   - Monitor log untuk error dan warning

## 🔗 Referensi

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [XAMPP Documentation](https://www.apachefriends.org/docs/)

---

**Selamat Development! 🚀**

