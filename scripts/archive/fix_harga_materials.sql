-- Script untuk menambahkan kolom harga ke tabel materials di database VPS
-- FIX UNTUK ERROR: Unknown column 'materials.harga' in 'field list'
-- Usage: 
--   - Via MySQL CLI: mysql -u root -p jargas_apbn < fix_harga_materials.sql
--   - Via Docker: docker-compose exec mysql mysql -u root -padmin123 jargas_apbn < fix_harga_materials.sql

USE jargas_apbn;

-- Tambahkan kolom harga ke materials (jika belum ada)
SET @col_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'jargas_apbn' 
    AND TABLE_NAME = 'materials' 
    AND COLUMN_NAME = 'harga'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE materials ADD COLUMN harga DECIMAL(15,2) NULL',
    'SELECT ''Kolom harga sudah ada di materials, tidak perlu ditambahkan lagi'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 
    IF(@col_exists = 0, 
        '✅ Kolom harga berhasil ditambahkan ke tabel materials!', 
        'ℹ️  Kolom harga sudah ada di tabel materials, tidak ada perubahan.'
    ) AS result;

