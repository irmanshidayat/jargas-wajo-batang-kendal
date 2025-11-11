-- Script untuk menambahkan kolom yang missing di database VPS
-- Jalankan script ini di database VPS untuk memperbaiki error DELETE user
-- Usage: mysql -u root -p jargas_apbn < fix_missing_columns_vps.sql

USE jargas_apbn;

-- 1. Tambahkan kolom status ke surat_permintaans (jika belum ada)
SET @col_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'surat_permintaans' 
    AND COLUMN_NAME = 'status'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE surat_permintaans ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT ''Draft''',
    'SELECT ''Kolom status sudah ada di surat_permintaans'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Tambahkan index untuk status (jika belum ada)
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'surat_permintaans' 
    AND INDEX_NAME = 'ix_surat_permintaans_status'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX ix_surat_permintaans_status ON surat_permintaans (status)',
    'SELECT ''Index ix_surat_permintaans_status sudah ada'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. Tambahkan kolom nomor_surat_permintaan ke surat_jalans (jika belum ada)
SET @col_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'surat_jalans' 
    AND COLUMN_NAME = 'nomor_surat_permintaan'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE surat_jalans ADD COLUMN nomor_surat_permintaan VARCHAR(255) NULL',
    'SELECT ''Kolom nomor_surat_permintaan sudah ada di surat_jalans'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Tambahkan index untuk nomor_surat_permintaan (jika belum ada)
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'surat_jalans' 
    AND INDEX_NAME = 'ix_surat_jalans_nomor_surat_permintaan'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX ix_surat_jalans_nomor_surat_permintaan ON surat_jalans (nomor_surat_permintaan)',
    'SELECT ''Index ix_surat_jalans_nomor_surat_permintaan sudah ada'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. Tambahkan kolom nomor_barang_keluar ke surat_jalans (jika belum ada)
SET @col_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'surat_jalans' 
    AND COLUMN_NAME = 'nomor_barang_keluar'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE surat_jalans ADD COLUMN nomor_barang_keluar VARCHAR(255) NULL',
    'SELECT ''Kolom nomor_barang_keluar sudah ada di surat_jalans'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Tambahkan index untuk nomor_barang_keluar (jika belum ada)
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'surat_jalans' 
    AND INDEX_NAME = 'ix_surat_jalans_nomor_barang_keluar'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX ix_surat_jalans_nomor_barang_keluar ON surat_jalans (nomor_barang_keluar)',
    'SELECT ''Index ix_surat_jalans_nomor_barang_keluar sudah ada'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4. Tambahkan kolom stock_out_id ke surat_jalans (jika belum ada)
SET @col_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'surat_jalans' 
    AND COLUMN_NAME = 'stock_out_id'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE surat_jalans ADD COLUMN stock_out_id INT NULL',
    'SELECT ''Kolom stock_out_id sudah ada di surat_jalans'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Tambahkan index untuk stock_out_id (jika belum ada)
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'surat_jalans' 
    AND INDEX_NAME = 'ix_surat_jalans_stock_out_id'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX ix_surat_jalans_stock_out_id ON surat_jalans (stock_out_id)',
    'SELECT ''Index ix_surat_jalans_stock_out_id sudah ada'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Tambahkan foreign key untuk stock_out_id (jika belum ada)
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'surat_jalans' 
    AND CONSTRAINT_NAME = 'fk_surat_jalans_stock_out_id'
);

SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE surat_jalans ADD CONSTRAINT fk_surat_jalans_stock_out_id FOREIGN KEY (stock_out_id) REFERENCES stock_outs(id)',
    'SELECT ''Foreign key fk_surat_jalans_stock_out_id sudah ada'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 5. Tambahkan kolom created_by ke users (jika belum ada) - FIX UNTUK ERROR LOGIN
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

-- 6. Tambahkan kolom harga ke materials (jika belum ada) - FIX UNTUK ERROR TAMBAH BARANG
SET @col_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'materials' 
    AND COLUMN_NAME = 'harga'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE materials ADD COLUMN harga DECIMAL(15,2) NULL',
    'SELECT ''Kolom harga sudah ada di materials'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 'Script selesai! Semua kolom yang diperlukan sudah ditambahkan, termasuk created_by di users untuk fix error login dan harga di materials untuk fix error tambah barang.' AS result;

