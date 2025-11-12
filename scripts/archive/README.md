# Archive - Script One-Time Fix

Folder ini berisi script-script one-time fix yang sudah **TIDAK PERLU** dijalankan lagi.

## ⚠️ Catatan Penting

**JANGAN JALANKAN SCRIPT DI FOLDER INI!**

Script di folder ini sudah di-archive karena:
- ✅ Masalah sudah diperbaiki dan sudah ada di migration Alembic
- ✅ Database production sudah memiliki kolom/tabel tersebut
- ✅ Tidak ada rencana setup database baru dari awal

Script di-archive untuk **referensi historis** saja.

---

## 📋 Daftar Script Archive

### Fix created_by Column
Script untuk memperbaiki error: `Unknown column 'users.created_by'`

**Script:**
- `fix-created-by-users.sh`
- `fix-created-by-users.ps1`
- `fix-created-by-vps-auto.ps1`
- `fix-created-by-vps-server.sh`
- `run-fix-created-by-on-vps.sh`
- `fix_created_by_users.sql`

**Status:** ✅ Sudah diperbaiki di migration Alembic

---

### Fix harga Materials
Script untuk memperbaiki error: `Unknown column 'materials.harga'`

**Script:**
- `fix-harga-materials.sh`
- `fix-harga-materials.ps1`
- `fix-harga-materials-docker.sh`
- `fix_harga_materials.sql`

**Status:** ✅ Sudah diperbaiki di migration Alembic

---

### Fix Missing Columns
Script untuk memperbaiki kolom yang missing di database.

**Script:**
- `fix-missing-columns-vps.sh`
- `fix-missing-columns-vps.ps1`
- `fix-missing-columns-vps-docker.sh`
- `fix_missing_columns_vps.sql`

**Status:** ✅ Sudah diperbaiki di migration Alembic

---

### Setup Environment (Legacy)
Script setup environment development yang sudah digantikan dengan script baru.

**Script:**
- `setup-env-dev-server.sh` - Legacy script untuk setup development environment
- `setup-env-dev-server.ps1` - Legacy script untuk setup development environment (PowerShell)

**Status:** ✅ Digantikan dengan `scripts/setup/setup-env-development.ps1` yang lebih lengkap

**Catatan:** Script baru menggunakan struktur environment terpisah (`.env.dev` dan `backend/.env.dev`) yang lebih sesuai dengan best practice.

---

### Fix Lainnya
- `fix-database-empty.ps1` - Sudah ada auto-migration
- `fix-dev-domain.ps1` - Setup one-time
- `debug-nginx-adminer.sh` - Debug one-time
- `update-nginx-adminer-dev.sh` - Update one-time

---

## 🔍 Verifikasi

Jika Anda ingin memverifikasi apakah script ini masih diperlukan, gunakan:

```bash
# Di backend container
python -m scripts.verify_one_time_scripts
```

Script ini akan mengecek apakah kolom/tabel dari script one-time sudah ada di database.

---

## 📚 Referensi

Untuk migration yang aktif, lihat:
- `backend/alembic/versions/` - Migration files
- `backend/scripts/smart_migrate.py` - Migration script aktif

