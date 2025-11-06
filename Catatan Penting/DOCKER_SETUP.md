# Dokumentasi Docker Setup - Jargas APBN

Dokumentasi lengkap untuk setup dan menjalankan aplikasi Jargas APBN menggunakan Docker.

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

**Langkah 1**: Copy file `.env.example` ke `.env`

```bash
cp .env.example .env
```

**Langkah 2**: Edit file `.env` dan sesuaikan nilai-nilainya:

```bash
# Menggunakan editor favorit Anda
nano .env
# atau
notepad .env
# atau
code .env
```

**Langkah 3**: Pastikan untuk mengubah nilai-nilai penting:

```env
# Database Password (WAJIB diubah!)
DB_PASSWORD=your_secure_password_here

# Secret Key untuk JWT (WAJIB diubah!)
# Generate dengan: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_generated_secret_key_here

# Debug mode (False untuk production)
DEBUG=False
```

**Langkah 4**: Generate Secret Key (opsional tapi direkomendasikan)

Jika menggunakan Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Atau online: https://generate-secret.vercel.app/32

### 3. Verifikasi Docker

Pastikan Docker berjalan:

```bash
docker ps
```

Jika ada error, start Docker Desktop terlebih dahulu.

## ▶️ Menjalankan Aplikasi

### Quick Start (Development)

```bash
# Build dan start semua services
docker-compose up -d --build

# Melihat logs
docker-compose logs -f
```

### Langkah-langkah Detail

**1. Build Images**

```bash
# Build semua images
docker-compose build

# Build service tertentu
docker-compose build backend
docker-compose build frontend
docker-compose build mysql
```

**2. Start Services**

```bash
# Start semua services di background
docker-compose up -d

# Start service tertentu
docker-compose up -d mysql
docker-compose up -d backend
docker-compose up -d frontend
```

**3. Check Status**

```bash
# Lihat status semua services
docker-compose ps

# Lihat logs
docker-compose logs -f

# Logs service tertentu
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
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

