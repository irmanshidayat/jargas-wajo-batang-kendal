# 🚀 Tutorial Deployment ke Server VPS - Jargas APBN

docker-compose logs -f backend | grep -i migration

Tutorial ringkas untuk deployment ke VPS.

## 📋 Prasyarat

- SSH access: `ssh root@72.61.142.109`
- Project path: `~/jargas-wajo-batang-kendal`
- Docker & Docker Compose terinstall

---

## 🚀 Deployment Cepat

### Metode 1: Via GitHub (Recommended)

**Lokal:**
```powershell
cd "C:\Irman\Coding Jargas APBN\Jargas APBN"
git add . && git commit -m "Update" && git push origin main
```

**Server:**
```bash
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal
git pull origin main
docker-compose build --no-cache && docker-compose up -d
```

### Metode 2: Via SCP (Cepat)

```powershell
# Upload files
scp -r .\backend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/backend
scp -r .\frontend\ root@72.61.142.109:~/jargas-wajo-batang-kendal/frontend

# Rebuild di server
ssh root@72.61.142.109 "cd ~/jargas-wajo-batang-kendal && docker-compose build --no-cache && docker-compose up -d"
```

### Script Otomatis

```powershell
# Dari Windows
.\scripts\deploy-with-migration.ps1
```

---

## 🔨 Rebuild Docker

```bash
# Di server
cd ~/jargas-wajo-batang-kendal
docker-compose build --no-cache
docker-compose up -d

# Rebuild service tertentu
docker-compose build --no-cache backend
docker-compose up -d backend
```

**Catatan:** Migration otomatis berjalan saat backend start (`AUTO_MIGRATE=True`).

### Fitur Auto-Migration

- ✅ **Deteksi database kosong** - Auto force migration untuk initial setup
- ✅ **Retry logic** - Otomatis retry 3x (delay 5 detik) jika error koneksi
- ✅ **Smart error handling** - Deteksi error dan retry otomatis

---

## ✅ Verifikasi

```bash
# Status container
docker-compose ps

# Log migration
docker-compose logs backend | grep -i migration

# Cek tabel database
docker-compose exec mysql mysql -u root -padmin123 jargas_apbn -e "SHOW TABLES;"

# Health check
curl http://localhost/health
```

**Akses:**
- Frontend: `http://jargas.ptkiansantang.com` atau `http://72.61.142.109:8080`
- Backend: `http://jargas.ptkiansantang.com/api/v1/health`
- Adminer: `http://72.61.142.109:8081`

---

## 🔧 Troubleshooting

### Container tidak start
```bash
docker-compose logs backend
docker-compose restart
```

### Build gagal
```bash
docker-compose build --no-cache 2>&1 | tee build.log
docker system prune -a  # Clean up
```

### Database migration tidak jalan

**Auto-migrate sudah aktif** dengan fitur:
- Auto-detect database kosong → Force migration
- Retry 3x jika error koneksi

**Cek log:**
```bash
docker-compose logs backend | grep -i migration
docker-compose logs backend --tail 100
```

**Manual migration (jika perlu):**
```bash
docker-compose exec backend alembic upgrade head
# Atau dari Windows
.\scripts\run-migration-server.ps1
```

**Verifikasi:**
```bash
docker-compose exec backend alembic current
docker-compose exec mysql mysql -u root -padmin123 jargas_apbn -e "SHOW TABLES;"
```

---

## 🌐 Setup Domain (Opsional)

### 1. DNS Record
Tambahkan A Record di panel DNS:
```
Type: A
Name: jargas
Value: 72.61.142.109
```

### 2. Setup di Server
```powershell
# Dari Windows
.\nginx-host\setup-domain.ps1
```

Atau di server:
```bash
bash nginx-host/setup-domain.sh
```

### 3. SSL (Opsional)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d jargas.ptkiansantang.com
```

---

## 💡 Best Practices

1. **Backup sebelum update:**
   ```bash
   docker-compose exec mysql mysqldump -u root -padmin123 jargas_apbn > backup_$(date +%Y%m%d).sql
   ```

2. **Monitor setelah deployment:**
   ```bash
   docker-compose logs -f
   docker stats
   ```

3. **Gunakan Git untuk production** - Selalu commit & push sebelum deploy

---

## 📝 Checklist

- [ ] Kode sudah di-test di lokal
- [ ] Git commit & push (jika pakai Git)
- [ ] Container sudah di-rebuild
- [ ] Health check berhasil
- [ ] Migration berjalan (cek log)

---

## 🔄 Auto-Migration Features

### Fitur Utama

1. **Auto-Detection Database Kosong**
   - Deteksi otomatis jika database kosong
   - Force migration meskipun `AUTO_MIGRATE_ONLY_IF_PENDING=True`
   - Tidak perlu manual migration untuk initial setup

2. **Retry Logic**
   - Retry 3x dengan delay 5 detik
   - Deteksi error: `connection`, `timeout`, `refused`, `unreachable`
   - Aplikasi tetap berjalan meskipun migration gagal

3. **Logging Detail**
   - `🔍 Database kosong terdeteksi` → Initial migration
   - `⚠️ Database belum ready (attempt 1/3)` → Retry
   - `✅ Initial migration berhasil` → Success

### Cara Kerja

```
Startup → Cek AUTO_MIGRATE
→ Cek database kosong
→ Jika kosong → Force migration
→ Jika error koneksi → Retry 3x (delay 5 detik)
→ Log semua proses
```

### Konfigurasi

```yaml
# docker-compose.yml
AUTO_MIGRATE: ${AUTO_MIGRATE:-True}
AUTO_MIGRATE_ONLY_IF_PENDING: ${AUTO_MIGRATE_ONLY_IF_PENDING:-True}
MIGRATION_MODE: sequential
```

**Catatan:** Semua fitur sudah terintegrasi, tidak perlu setup manual.

---

**Terakhir diupdate:** 2025-01-27
