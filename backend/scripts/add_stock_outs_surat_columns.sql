-- SQL Migration untuk menambahkan kolom surat_permohonan_paths dan surat_serah_terima_paths ke tabel stock_outs
-- Database: jargas_apbn
-- Jalankan script ini di MySQL/XAMPP

USE jargas_apbn;

-- Check dan tambahkan kolom surat_permohonan_paths jika belum ada
SET @dbname = DATABASE();
SET @tablename = "stock_outs";
SET @columnname = "surat_permohonan_paths";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  "SELECT 'Column surat_permohonan_paths already exists.' AS message",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " TEXT NULL")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- Check dan tambahkan kolom surat_serah_terima_paths jika belum ada
SET @columnname = "surat_serah_terima_paths";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = @columnname)
  ) > 0,
  "SELECT 'Column surat_serah_terima_paths already exists.' AS message",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " TEXT NULL")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SELECT 'Migration completed successfully!' AS result;
