# Instruksi Fix Kolom harga di Tabel materials

## Masalah
Error saat menambahkan barang di server VPS:
```
Unknown column 'materials.harga' in 'field list'
```

## Penyebab
Kolom `harga` belum ada di tabel `materials` di database VPS, padahal model SQLAlchemy sudah menggunakan kolom ini.

## Solusi

### Opsi 1: Menggunakan Script SQL Langsung (Paling Cepat)

#### Via MySQL CLI (Langsung ke Database)
```bash
mysql -u root -p jargas_apbn < scripts/fix_harga_materials.sql
```

#### Via Docker Container
```bash
# Jika menggunakan Docker Compose
docker-compose exec mysql mysql -u root -padmin123 jargas_apbn < scripts/fix_harga_materials.sql

# Atau jika container MySQL sudah berjalan
docker exec -i jargas_mysql mysql -uroot -padmin123 jargas_apbn < scripts/fix_harga_materials.sql
```

### Opsi 2: Menggunakan Script Bash (Linux/Mac)

```bash
# Berikan permission execute
chmod +x scripts/fix-harga-materials.sh

# Jalankan script
./scripts/fix-harga-materials.sh

# Atau dengan custom parameter
DB_HOST=localhost DB_USER=root DB_PASSWORD=yourpass DB_NAME=jargas_apbn ./scripts/fix-harga-materials.sh
```

### Opsi 3: Menggunakan Script Docker (Jika Database di Docker)

```bash
# Berikan permission execute
chmod +x scripts/fix-harga-materials-docker.sh

# Jalankan script
./scripts/fix-harga-materials-docker.sh

# Atau dengan custom parameter
DB_CONTAINER=jargas_mysql DB_USER=root DB_PASSWORD=admin123 DB_NAME=jargas_apbn ./scripts/fix-harga-materials-docker.sh
```

### Opsi 4: Menggunakan Script PowerShell (Windows)

```powershell
# Jalankan script
.\scripts\fix-harga-materials.ps1

# Atau dengan custom parameter
.\scripts\fix-harga-materials.ps1 -DbHost localhost -DbUser root -DbPassword yourpass -DbName jargas_apbn
```

### Opsi 5: Menjalankan Migrasi Alembic (Untuk Konsistensi Jangka Panjang)

```bash
# Masuk ke container backend
docker-compose exec backend bash

# Jalankan migrasi
alembic upgrade head

# Atau langsung dari luar container
docker-compose exec backend alembic upgrade head
```

## Verifikasi

Setelah menjalankan script, verifikasi kolom sudah ditambahkan:

```sql
-- Cek struktur tabel materials
DESCRIBE materials;

-- Atau
SHOW COLUMNS FROM materials LIKE 'harga';

-- Atau via Docker
docker exec -i jargas_mysql mysql -uroot -padmin123 jargas_apbn -e "DESCRIBE materials;"
```

Kolom `harga` seharusnya muncul dengan tipe `DECIMAL(15,2)` dan nullable.

## Catatan

- Script SQL sudah idempotent (aman dijalankan berulang kali)
- Jika kolom sudah ada, script akan skip dan tidak error
- Kolom `harga` dibuat sebagai `DECIMAL(15,2) NULL` sesuai dengan model SQLAlchemy

## Troubleshooting

### Error: Access denied
- Pastikan username dan password database benar
- Pastikan user memiliki privilege ALTER TABLE

### Error: Container tidak ditemukan
- Cek nama container dengan: `docker ps -a`
- Sesuaikan nama container di script atau parameter

### Error: Database tidak ditemukan
- Pastikan database `jargas_apbn` sudah dibuat
- Cek nama database di parameter script

