# Dokumentasi Docker Setup - Jargas APBN

> **Catatan:** Dokumentasi ini menggunakan struktur environment terpisah untuk Production dan Development. Pastikan menggunakan `--env-file` yang sesuai.

## Quick Reference

### Production
```bash
# Rebuild container backend
docker-compose --env-file .env build backend
docker-compose --env-file .env up -d backend

# Restart backend container
docker-compose --env-file .env restart backend
# Atau restart semua services
docker-compose --env-file .env restart

# Verifikasi migration
docker-compose --env-file .env logs backend | grep -i migration

# Verifikasi tabel database
docker-compose --env-file .env exec mysql mysql -u root -padmin123 jargas_apbn -e "SHOW TABLES;"
```

### Development
```bash
# Rebuild container backend
docker-compose -f docker-compose.dev.yml --env-file .env.dev build backend
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d backend

# Restart backend container
docker-compose -f docker-compose.dev.yml --env-file .env.dev restart backend
# Atau restart semua services
docker-compose -f docker-compose.dev.yml --env-file .env.dev restart

# Verifikasi migration
docker-compose -f docker-compose.dev.yml --env-file .env.dev logs backend | grep -i migration

# Verifikasi tabel database
docker-compose -f docker-compose.dev.yml --env-file .env.dev exec mysql mysql -u root -padmin123 jargas_apbn_dev -e "SHOW TABLES;"
```

Dokumentasi lengkap untuk setup dan menjalankan aplikasi Jargas APBN menggunakan Docker.

## 📝 Migration Manual (Jika Auto-Migrate Tidak Berjalan)

### Production

**Langkah 1: Cek Status Migration**
```bash
docker-compose --env-file .env exec backend python scripts/check_migration_status.py
# Atau cek dengan alembic:
docker-compose --env-file .env exec backend alembic current
```

**Langkah 2: Jalankan Migration**
```bash
docker-compose --env-file .env exec backend alembic upgrade head
# Atau gunakan script Python:
docker-compose --env-file .env exec backend python scripts/run_migrations.py
```

**Langkah 3: Cek Log**
```bash
# Di Linux/Mac
docker-compose --env-file .env logs backend | grep -i migration

# Di PowerShell (Windows)
docker-compose --env-file .env logs backend | Select-String -Pattern "migration" -CaseSensitive:$false

# Atau lihat log lengkap:
docker-compose --env-file .env logs backend --tail 100
```

**Langkah 4: Verifikasi Tabel**
```bash
docker-compose --env-file .env exec mysql mysql -u root -padmin123 jargas_apbn -e "SHOW TABLES;"
```

### Development

**Langkah 1: Cek Status Migration**
```bash
docker-compose -f docker-compose.dev.yml --env-file .env.dev exec backend python scripts/check_migration_status.py
# Atau cek dengan alembic:
docker-compose -f docker-compose.dev.yml --env-file .env.dev exec backend alembic current
```

**Langkah 2: Jalankan Migration**
```bash
docker-compose -f docker-compose.dev.yml --env-file .env.dev exec backend alembic upgrade head
# Atau gunakan script Python:
docker-compose -f docker-compose.dev.yml --env-file .env.dev exec backend python scripts/run_migrations.py
```

**Langkah 3: Cek Log**
```bash
# Di Linux/Mac
docker-compose -f docker-compose.dev.yml --env-file .env.dev logs backend | grep -i migration

# Di PowerShell (Windows)
docker-compose -f docker-compose.dev.yml --env-file .env.dev logs backend | Select-String -Pattern "migration" -CaseSensitive:$false
```

**Langkah 4: Verifikasi Tabel**
```bash
docker-compose -f docker-compose.dev.yml --env-file .env.dev exec mysql mysql -u root -padmin123 jargas_apbn_dev -e "SHOW TABLES;"
```

## ⚙️ Auto-Migrate Configuration

Migration otomatis berjalan saat backend start jika `AUTO_MIGRATE=True` di file environment.

**Production:**
- Edit `backend/.env`, set `AUTO_MIGRATE=True`
- Restart: `docker-compose --env-file .env restart backend`

**Development:**
- Edit `backend/.env.dev`, set `AUTO_MIGRATE=True`
- Restart: `docker-compose -f docker-compose.dev.yml --env-file .env.dev restart backend`


## 📋 Daftar Isi

- [Prasyarat](#prasyarat)
- [Struktur Docker](#struktur-docker)
- [Setup Awal](#setup-awal)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [Mengelola Services](#mengelola-services)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## 🛠️ Prasyarat

Sebelum memulai, pastikan Anda sudah menginstall:

1. **Docker** (versi 20.10 atau lebih baru)
   - Download: https://www.docker.com/get-started
   - Verifikasi: `docker --version`

2. **Docker Compose** (versi 2.0 atau lebih baru)
   - Biasanya sudah termasuk dengan Docker Desktop
   - Verifikasi: `docker-compose --version`

3. **Git** (opsional, untuk clone repository)

## 📦 Struktur Docker

Aplikasi ini menggunakan Docker Compose dengan 3 services utama:

### Services

1. **MySQL** (`jargas_mysql`)
   - Database server untuk aplikasi
   - Port: `3307` (host) → `3306` (container)
   - Volume: `jargas_mysql_data` untuk persistence

2. **Backend** (`jargas_backend`)
   - FastAPI application
   - Port: `8001` (host) → `8000` (container)
   - Volume: `jargas_backend_uploads` untuk file uploads

3. **Frontend** (`jargas_frontend`)
   - React application dengan Nginx
   - Port: `8080` (host) → `80` (container)
   - Proxy API requests ke backend

### Port Configuration

| Service | Host Port | Container Port | Keterangan |
|---------|-----------|----------------|------------|
| MySQL | 3307 | 3306 | Menghindari konflik dengan XAMPP |
| Backend | 8001 | 8000 | Menghindari konflik aplikasi lain |
| Frontend | 8080 | 80 | Menghindari konflik web server |

## 🚀 Setup Awal

### 1. Clone Repository (jika belum)

```bash
git clone <repository-url>
cd "Jargas APBN"
```

### 2. Setup Environment Variables

Proyek ini menggunakan **environment terpisah** untuk Production dan Development. Setiap environment memiliki file `.env` sendiri.

#### 🏭 Production Environment

**Langkah 1**: Jalankan script setup production

```powershell
# Dari Windows
.\scripts\setup\setup-env-production.ps1
```

Atau manual:

```bash
# Copy template
cp .env.example .env
cp backend/env.example backend/.env
```

**Langkah 2**: Edit file `.env` dan `backend/.env`, sesuaikan nilai-nilainya:

```bash
# Menggunakan editor favorit Anda
nano .env
nano backend/.env
```

**Langkah 3**: Pastikan untuk mengubah nilai-nilai penting:

```env
# Di root .env
SECRET_KEY=your-production-secret-key-here
DB_NAME=jargas_apbn
DEBUG=False
CORS_ORIGINS=https://jargas.ptkiansantang.com

# Di backend/.env
DB_HOST=mysql
DB_PASSWORD=your_secure_password_here
SECRET_KEY=your-production-secret-key-here  # Harus sama dengan root .env
DEBUG=False
CORS_ORIGINS=https://jargas.ptkiansantang.com
```

#### 🧪 Development Environment

**Langkah 1**: Jalankan script setup development

```powershell
# Dari Windows
.\scripts\setup\setup-env-development.ps1
```

Atau manual:

```bash
# Copy template
cp .env.dev.example .env.dev
cp backend/.env.dev.example backend/.env.dev
```

**Langkah 2**: Edit file `.env.dev` dan `backend/.env.dev`, sesuaikan nilai-nilainya:

```env
# Di root .env.dev
SECRET_KEY=your-development-secret-key-here  # Berbeda dari production!
DB_NAME=jargas_apbn_dev
DEBUG=True
CORS_ORIGINS=https://devjargas.ptkiansantang.com,http://localhost:8082

# Di backend/.env.dev
DB_HOST=mysql
DB_PASSWORD=admin123
SECRET_KEY=your-development-secret-key-here  # Harus sama dengan root .env.dev
DEBUG=True
CORS_ORIGINS=https://devjargas.ptkiansantang.com,http://localhost:8082
```

#### 🔑 Generate Secret Key

Generate Secret Key yang unik untuk setiap environment:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Atau online: https://generate-secret.vercel.app/32

**⚠️ PENTING:**
- Secret Key untuk Production dan Development **HARUS BERBEDA**
- Secret Key di root `.env` dan `backend/.env` **HARUS SAMA** untuk environment yang sama
- Jangan commit file `.env` atau `.env.dev` ke repository (sudah di-ignore)

### 3. Verifikasi Docker

Pastikan Docker berjalan:

```bash
docker ps
```

Jika ada error, start Docker Desktop terlebih dahulu.

## ▶️ Menjalankan Aplikasi

### Quick Start

#### 🏭 Production

```bash
# Build dan start semua services (production)
docker-compose --env-file .env up -d --build

# Melihat logs
docker-compose --env-file .env logs -f
```

#### 🧪 Development

```bash
# Build dan start semua services (development)
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d --build

# Melihat logs
docker-compose -f docker-compose.dev.yml --env-file .env.dev logs -f
```

### Langkah-langkah Detail

**1. Build Images**

**Production:**
```bash
# Build semua images
docker-compose --env-file .env build

# Build service tertentu
docker-compose --env-file .env build backend
docker-compose --env-file .env build frontend
docker-compose --env-file .env build mysql
```

**Development:**
```bash
# Build semua images
docker-compose -f docker-compose.dev.yml --env-file .env.dev build

# Build service tertentu
docker-compose -f docker-compose.dev.yml --env-file .env.dev build backend
docker-compose -f docker-compose.dev.yml --env-file .env.dev build frontend
docker-compose -f docker-compose.dev.yml --env-file .env.dev build mysql
```

**2. Start Services**

**Production:**
```bash
# Start semua services di background
docker-compose --env-file .env up -d

# Start service tertentu
docker-compose --env-file .env up -d mysql
docker-compose --env-file .env up -d backend
docker-compose --env-file .env up -d frontend
```

**Development:**
```bash
# Start semua services di background
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d

# Start service tertentu
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d mysql
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d backend
docker-compose -f docker-compose.dev.yml --env-file .env.dev up -d frontend
```

**3. Check Status**

**Production:**
```bash
# Lihat status semua services
docker-compose --env-file .env ps

# Lihat logs
docker-compose --env-file .env logs -f

# Logs service tertentu
docker-compose --env-file .env logs -f backend
docker-compose --env-file .env logs -f frontend
docker-compose --env-file .env logs -f mysql
```

**Development:**
```bash
# Lihat status semua services
docker-compose -f docker-compose.dev.yml --env-file .env.dev ps

# Lihat logs
docker-compose -f docker-compose.dev.yml --env-file .env.dev logs -f

# Logs service tertentu
docker-compose -f docker-compose.dev.yml --env-file .env.dev logs -f backend
docker-compose -f docker-compose.dev.yml --env-file .env.dev logs -f frontend
docker-compose -f docker-compose.dev.yml --env-file .env.dev logs -f mysql
```

**4. Akses Aplikasi**

Setelah semua services running, akses:

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **MySQL**: `localhost:3307`

## 🔧 Mengelola Services

### Stop Services

```bash
# Stop semua services (tidak hapus data)
docker-compose stop

# Stop service tertentu
docker-compose stop backend
```

### Start Services (setelah stop)

```bash
# Start semua services
docker-compose start

# Start service tertentu
docker-compose start mysql
```

### Restart Services

```bash
# Restart semua services
docker-compose restart

# Restart service tertentu
docker-compose restart backend
```

### Rebuild dan Restart

```bash
# Rebuild dan restart (jika ada perubahan code)
docker-compose up -d --build

# Rebuild service tertentu
docker-compose up -d --build backend
```

### Stop dan Hapus Containers

```bash
# Stop dan hapus containers (data tetap ada)
docker-compose down

# Stop dan hapus containers + volumes (HATI-HATI: hapus data!)
docker-compose down -v
```

### View Logs

```bash
# Semua services
docker-compose logs -f

# Service tertentu
docker-compose logs -f backend

# Logs dengan timestamp
docker-compose logs -f -t

# Last 100 lines
docker-compose logs --tail=100
```

### Execute Commands di Container

```bash
# Masuk ke backend container
docker-compose exec backend bash

# Masuk ke MySQL container
docker-compose exec mysql bash

# Masuk ke frontend container
docker-compose exec frontend sh

# Run command di backend (contoh: migration)
docker-compose exec backend alembic upgrade head

# Run Python script
docker-compose exec backend python scripts/create_admin.py
```

### Database Management

**Akses MySQL via CLI:**

```bash
# Masuk ke MySQL
docker-compose exec mysql mysql -u jargas_user -p jargas_apbn

# Atau dengan root
docker-compose exec mysql mysql -u root -p
```

**Backup Database:**

```bash
# Backup database
docker-compose exec mysql mysqldump -u jargas_user -p jargas_apbn > backup.sql

# Atau dengan root
docker-compose exec mysql mysqldump -u root -p jargas_apbn > backup.sql
```

**Restore Database:**

```bash
# Restore database
docker-compose exec -T mysql mysql -u jargas_user -p jargas_apbn < backup.sql
```

## 🔍 Troubleshooting

### Problem: Port sudah digunakan

**Error**: `Error: bind: address already in use`

**Solusi 1**: Ubah port di `.env`

```env
DB_PORT_MAPPED=3308
BACKEND_PORT_MAPPED=8002
FRONTEND_PORT_MAPPED=8081
```

**Solusi 2**: Stop aplikasi yang menggunakan port tersebut

```bash
# Windows: cek port yang digunakan
netstat -ano | findstr :3307
netstat -ano | findstr :8001
netstat -ano | findstr :8080

# Linux/Mac: cek port yang digunakan
lsof -i :3307
lsof -i :8001
lsof -i :8080
```

### Problem: Container tidak bisa connect ke MySQL

**Error**: `Can't connect to MySQL server`

**Solusi**:

1. Pastikan MySQL sudah healthy:
```bash
docker-compose ps
```

2. Tunggu beberapa detik untuk MySQL siap:
```bash
docker-compose logs mysql
```

3. Check network:
```bash
docker network ls
docker network inspect jargas_network
```

### Problem: Build gagal

**Error**: `Error building image`

**Solusi**:

1. Clear Docker cache:
```bash
docker-compose build --no-cache
```

2. Check Dockerfile:
```bash
# Verifikasi syntax
docker build -t test ./backend
```

3. Check disk space:
```bash
docker system df
docker system prune -a  # Hati-hati: hapus semua unused images
```

### Problem: Permission denied pada uploads

**Solusi**:

```bash
# Fix permission di backend container
docker-compose exec backend chmod -R 755 /app/uploads
```

### Problem: Frontend tidak bisa connect ke backend

**Error**: `Network Error` atau `CORS Error`

**Solusi**:

1. Check CORS_ORIGINS di `.env`:
```env
CORS_ORIGINS=http://localhost:8080,http://localhost:3000,http://localhost:5173
```

2. Restart backend:
```bash
docker-compose restart backend
```

3. Check logs:
```bash
docker-compose logs backend | grep -i cors
```

### Problem: Database migration tidak jalan

**Solusi**:

1. Jalankan migration manual:
```bash
docker-compose exec backend alembic upgrade head
```

2. Check migration status:
```bash
docker-compose exec backend alembic current
docker-compose exec backend alembic history
```

3. Enable auto-migrate di `.env`:
```env
AUTO_MIGRATE=True
AUTO_MIGRATE_ONLY_IF_PENDING=True
```

### Problem: Volume tidak persistent

**Solusi**:

1. Check volume:
```bash
docker volume ls
docker volume inspect jargas_mysql_data
```

2. Recreate volume jika perlu:
```bash
docker-compose down -v
docker-compose up -d
```

## 🚀 Production Deployment

### Checklist Production

- [ ] Ubah `DEBUG=False` di `.env`
- [ ] Generate `SECRET_KEY` yang kuat
- [ ] Ubah `DB_PASSWORD` yang aman
- [ ] Set `AUTO_MIGRATE=False` (migrate manual)
- [ ] Update `CORS_ORIGINS` sesuai domain production
- [ ] Setup SSL/TLS untuk domain
- [ ] Backup database secara berkala
- [ ] Setup monitoring dan logging
- [ ] Setup firewall rules
- [ ] Review security settings

### Environment Variables untuk Production

```env
# Security
DEBUG=False
SECRET_KEY=<strong-secret-key-from-secrets-generator>
DB_PASSWORD=<strong-database-password>

# Database (jika menggunakan external MySQL)
DB_HOST=mysql  # atau IP database server
DB_PORT=3306

# CORS (sesuaikan dengan domain production)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Migration
AUTO_MIGRATE=False  # Manual migration untuk production
AUTO_MIGRATE_ONLY_IF_PENDING=True
```

### Backup Strategy

**1. Backup Database (Otomatis via Cron)**

Buat script `backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T mysql mysqldump -u jargas_user -p${DB_PASSWORD} jargas_apbn > backups/db_${DATE}.sql
```

**2. Backup Uploads**

```bash
# Copy uploads dari volume
docker run --rm -v jargas_backend_uploads:/data -v $(pwd)/backups:/backup alpine tar czf /backup/uploads_$(date +%Y%m%d_%H%M%S).tar.gz /data
```

### Monitoring

**Check Status:**

```bash
# Health check semua services
docker-compose ps

# Resource usage
docker stats

# Logs monitoring
docker-compose logs --tail=100 -f
```

### Scaling (Opsional)

Untuk production dengan traffic tinggi:

```yaml
# Di docker-compose.yml, tambahkan:
backend:
  deploy:
    replicas: 3  # Scale backend ke 3 instances
```

## 📝 Tips dan Best Practices

1. **Selalu backup database** sebelum major changes
2. **Jangan commit** file `.env` ke repository
3. **Gunakan** `.env.example` sebagai template
4. **Monitor logs** secara berkala untuk error
5. **Update images** secara berkala untuk security patches
6. **Gunakan volume** untuk data persistence
7. **Health checks** sudah dikonfigurasi otomatis
8. **Network internal** untuk security antar services

## 🔗 Referensi

- Docker Documentation: https://docs.docker.com/
- Docker Compose Documentation: https://docs.docker.com/compose/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- React Documentation: https://react.dev/
- Nginx Documentation: https://nginx.org/en/docs/

## 📞 Support

Jika mengalami masalah:

1. Check logs: `docker-compose logs -f`
2. Check status: `docker-compose ps`
3. Review dokumentasi troubleshooting di atas
4. Check GitHub issues (jika ada)

---

**Last Updated**: 2025-01-XX  
**Version**: 1.0.0

