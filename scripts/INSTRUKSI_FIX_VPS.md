# Instruksi Fix Error Login di VPS

## Error yang Terjadi
```
Unknown column 'users.created_by' in 'field list'
```

## Solusi Cepat - Jalankan di Server VPS

### Opsi 1: Via SSH (Recommended)
Jalankan perintah berikut di terminal Windows (PowerShell):

```powershell
ssh root@72.61.142.109 "docker exec -i jargas_mysql mysql -uroot -padmin123 jargas_apbn < /dev/stdin" < scripts/fix_created_by_users.sql
```

### Opsi 2: Upload File dan Jalankan
1. Upload file SQL ke server:
```powershell
scp scripts/fix_created_by_users.sql root@72.61.142.109:/tmp/
```

2. SSH ke server dan jalankan:
```bash
ssh root@72.61.142.109
cd ~/jargas-wajo-batang-kendal
docker exec -i jargas_mysql mysql -uroot -padmin123 jargas_apbn < /tmp/fix_created_by_users.sql
```

### Opsi 3: Jalankan SQL Langsung (Satu Baris)
Jalankan perintah ini di server VPS:

```bash
docker exec -i jargas_mysql mysql -uroot -padmin123 jargas_apbn << 'EOF'
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'jargas_apbn' AND TABLE_NAME = 'users' AND COLUMN_NAME = 'created_by');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE users ADD COLUMN created_by INT NULL', 'SELECT ''Kolom sudah ada'' AS message');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @idx_exists = (SELECT COUNT(*) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = 'jargas_apbn' AND TABLE_NAME = 'users' AND INDEX_NAME = 'ix_users_created_by');
SET @sql = IF(@idx_exists = 0, 'CREATE INDEX ix_users_created_by ON users (created_by)', 'SELECT ''Index sudah ada'' AS message');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SET @fk_exists = (SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = 'jargas_apbn' AND TABLE_NAME = 'users' AND CONSTRAINT_NAME = 'fk_users_created_by');
SET @sql = IF(@fk_exists = 0, 'ALTER TABLE users ADD CONSTRAINT fk_users_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL', 'SELECT ''FK sudah ada'' AS message');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;
SELECT '✅ Kolom created_by berhasil ditambahkan!' AS result;
EOF
```

### Opsi 4: Via Adminer (Web Interface)
1. Buka http://jargas.ptkiansantang.com:8081
2. Login dengan:
   - System: MySQL
   - Server: mysql
   - Username: root
   - Password: admin123
   - Database: jargas_apbn
3. Pilih tab "SQL command"
4. Copy-paste isi file `scripts/fix_created_by_users.sql`
5. Klik "Execute"

## Verifikasi
Setelah menjalankan script, verifikasi kolom sudah ada:

```bash
docker exec -i jargas_mysql mysql -uroot -padmin123 jargas_apbn -e "DESCRIBE users;" | grep created_by
```

## Restart Backend (Jika Perlu)
Jika masih error setelah menambahkan kolom, restart backend:

```bash
ssh root@72.61.142.109 "cd ~/jargas-wajo-batang-kendal && docker-compose restart backend"
```

## File yang Tersedia
- `scripts/fix_created_by_users.sql` - Script SQL lengkap
- `scripts/fix-created-by-vps-auto.ps1` - Script PowerShell otomatis (perlu SSH key)
- `scripts/fix-created-by-vps-server.sh` - Script bash untuk dijalankan di server

