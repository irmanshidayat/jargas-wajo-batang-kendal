#!/bin/bash
# Script ini dijalankan DI SERVER VPS
# Copy-paste perintah di bawah ini ke terminal VPS

# Atau jalankan: bash <(curl -s https://raw.githubusercontent.com/.../fix_created_by_users.sql)
# Atau upload file fix_created_by_users.sql ke server, lalu jalankan:

docker exec -i jargas_mysql mysql -uroot -padmin123 jargas_apbn << 'EOF'
-- Tambahkan kolom created_by ke users (jika belum ada)
SET @col_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'users' 
    AND COLUMN_NAME = 'created_by'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE users ADD COLUMN created_by INT NULL',
    'SELECT ''Kolom created_by sudah ada di users'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Tambahkan index untuk created_by (jika belum ada)
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'users' 
    AND INDEX_NAME = 'ix_users_created_by'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX ix_users_created_by ON users (created_by)',
    'SELECT ''Index ix_users_created_by sudah ada'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Tambahkan foreign key untuk created_by (jika belum ada)
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'users' 
    AND CONSTRAINT_NAME = 'fk_users_created_by'
);

SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE users ADD CONSTRAINT fk_users_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL',
    'SELECT ''Foreign key fk_users_created_by sudah ada'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT '✅ Kolom created_by berhasil ditambahkan ke tabel users. Error login seharusnya sudah teratasi!' AS result;
EOF

echo ""
echo "✅ Script selesai dijalankan!"
echo "Silakan coba login lagi sebagai admin."

