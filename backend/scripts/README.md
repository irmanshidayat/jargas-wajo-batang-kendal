# Scripts Directory - Jargas APBN

Direktori ini berisi script-script utility untuk maintenance, migration, dan development.

## 📁 Struktur Folder

```
scripts/
├── dev/              # Script development & debugging
├── archive/          # Script one-time migration yang sudah tidak diperlukan
└── [active scripts]  # Script yang masih aktif digunakan
```

## 🚀 Script Aktif (Masih Digunakan)

### Migration Scripts
- **`smart_migrate.py`** - Script migration utama dengan best practice
  - Usage: `python -m scripts.smart_migrate [--mode sequential|head|auto]`
  - Features: Auto-fix cycles, validation, sequential migration
  
- **`run_migrations.py`** - Alternatif script migration
  - Usage: `python -m scripts.run_migrations [--revision <rev>]`
  
- **`migrate_cli.py`** - CLI sederhana untuk migration
  - Usage: `python -m scripts.migrate_cli upgrade|downgrade|current|history`
  
- **`check_migration_status.py`** - Cek status migration
  - Usage: `python -m scripts.check_migration_status`

### Setup & Utility Scripts
- **`auto_generate_pages.py`** - Auto-generate pages & permissions (dipanggil otomatis di startup)
  - Usage: `python -m scripts.auto_generate_pages`
  - Dipanggil otomatis di `app/main.py` saat startup
  
- **`create_admin.py`** - Membuat akun admin
  - Usage: `python -m scripts.create_admin`
  
- **`check_quantity_column_types.py`** - Cek tipe kolom quantity
  - Usage: `python -m scripts.check_quantity_column_types`

### Data Migration Scripts
- **`migrate_data_xampp_to_docker.py`** - Migrasi data dari XAMPP ke Docker
  - Usage: `python -m scripts.migrate_data_xampp_to_docker [--auto]`
  - Menggunakan: `export_data_from_xampp.py` dan `import_data_to_docker.py`

- **`export_data_from_xampp.py`** - Export data dari MySQL XAMPP
  - Usage: `python -m scripts.export_data_from_xampp [--output backup.sql]`
  
- **`import_data_to_docker.py`** - Import data ke MySQL Docker
  - Usage: `python -m scripts.import_data_to_docker backup.sql`

### Verification Scripts
- **`verify_one_time_scripts.py`** - Verifikasi apakah script one-time masih diperlukan
  - Usage: `python -m scripts.verify_one_time_scripts`
  - Mengecek apakah kolom/tabel dari script one-time sudah ada di database

## 🔧 Script Development (Folder `dev/`)

Script untuk development dan debugging:
- `debug_surat_permintaan.py` - Debug surat permintaan
- `inspect_returns.py` - Inspect data returns
- `delete_materials_data.py` - Hapus data materials (HATI-HATI!)

**Catatan:** Script di folder `dev/` tidak digunakan di production.

## 📦 Script Archive (Folder `archive/`)

Script one-time migration yang sudah tidak diperlukan lagi karena:
- Kolom/tabel yang ditambahkan sudah ada di migration Alembic
- Database production sudah memiliki kolom/tabel tersebut
- Tidak ada rencana setup database baru dari awal

**Catatan:** Script di folder `archive/` TIDAK PERLU dijalankan lagi. Di-archive untuk referensi historis.

## 📋 Best Practices

1. **Migration**: Gunakan `smart_migrate.py` untuk migration utama
2. **Verification**: Jalankan `verify_one_time_scripts.py` sebelum menghapus script
3. **Development**: Script debugging dipindahkan ke folder `dev/`
4. **Archive**: Script one-time yang sudah tidak diperlukan dipindahkan ke folder `archive/`

## ⚠️ Catatan Penting

- Jangan hapus script di folder `archive/` tanpa verifikasi terlebih dahulu
- Script di folder `dev/` hanya untuk development, jangan digunakan di production
- Pastikan backup database sebelum menjalankan script yang mengubah data

