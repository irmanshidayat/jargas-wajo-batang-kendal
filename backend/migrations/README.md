# Migrations Directory - Jargas APBN

Direktori ini berisi migration files untuk database schema management menggunakan Alembic.

## 📁 Struktur Folder

```
migrations/
├── env.py                    # Konfigurasi Alembic (menggunakan app.config.settings)
├── script.py.mako            # Template untuk generate migration file (standar Alembic)
├── TEMPLATE_migration.py     # Template migration dengan best practice ⭐
├── utils.py                  # Helper functions untuk migration (reusable) ⭐
├── versions/                 # Folder migration files
│   ├── 2bcb46d867a0_*.py    # Base migration
│   ├── 80cb2c36260b_*.py    # Create users table
│   └── ...                   # Migration files lainnya
└── README.md                 # Dokumentasi ini
```

## 🚀 Cara Menggunakan

### Generate Migration Baru

```bash
# Generate migration baru
alembic revision -m "deskripsi_migration"

# Atau gunakan template
cp migrations/TEMPLATE_migration.py migrations/versions/YYYYMMDD_deskripsi.py
```

### Jalankan Migration

```bash
# Upgrade ke head
alembic upgrade head

# Atau gunakan script
python -m scripts.smart_migrate
python -m scripts.run_migrations
```

### Cek Status Migration

```bash
# Cek current version
alembic current

# Atau gunakan script
python -m scripts.check_migration_status
```

## 📋 Best Practices

### 1. Gunakan `utils.py` untuk Helper Functions

**✅ BENAR** - Menggunakan utils:
```python
from migrations.utils import table_exists, column_exists, safe_add_column
from sqlalchemy import inspect

def upgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)
    
    if table_exists(inspector, 'materials'):
        safe_add_column(
            inspector,
            'materials',
            'harga',
            sa.Numeric(precision=15, scale=2),
            nullable=True
        )
```

**❌ SALAH** - Duplicate code:
```python
def upgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    
    if 'materials' in existing_tables:
        existing_columns = [col['name'] for col in inspector.get_columns('materials')]
        if 'harga' not in existing_columns:
            op.add_column('materials', sa.Column('harga', sa.Numeric(15, 2)))
```

### 2. Selalu Gunakan Safety Checks (Idempotent)

**✅ BENAR** - Idempotent:
```python
from migrations.utils import safe_add_column

def upgrade() -> None:
    # safe_add_column sudah idempotent (cek apakah kolom sudah ada)
    safe_add_column(inspector, 'materials', 'harga', sa.Numeric(15, 2))
```

**❌ SALAH** - Tidak idempotent:
```python
def upgrade() -> None:
    # Akan error jika kolom sudah ada
    op.add_column('materials', sa.Column('harga', sa.Numeric(15, 2)))
```

### 3. Gunakan Logging

**✅ BENAR** - Dengan logging:
```python
import logging
logger = logging.getLogger(__name__)

def upgrade() -> None:
    logger.info("Starting migration: add_harga_to_materials")
    # ... migration code ...
    logger.info("✅ Migration completed successfully")
```

### 4. Naming Convention

**✅ BENAR** - Menggunakan hash untuk revision ID:
```python
revision: str = '2bcb46d867a0'  # Hash dari Alembic
```

**❌ SALAH** - Menggunakan string:
```python
revision: str = 'add_harga_materials'  # Tidak konsisten
```

## 🔧 Helper Functions di `utils.py`

### Available Functions:

1. **Existence Checks**:
   - `table_exists(inspector, table_name)` - Cek apakah tabel ada
   - `column_exists(inspector, table_name, column_name)` - Cek apakah kolom ada
   - `index_exists(inspector, table_name, index_name)` - Cek apakah index ada
   - `foreign_key_exists(inspector, table_name, fk_name)` - Cek apakah FK ada

2. **Safe Operations** (Idempotent):
   - `safe_add_column(inspector, table, column, type, nullable=True)` - Add column dengan safety check
   - `safe_drop_column(inspector, table, column)` - Drop column dengan safety check
   - `safe_create_index(inspector, table, index, columns, unique=False)` - Create index dengan safety check
   - `safe_drop_index(inspector, table, index)` - Drop index dengan safety check

3. **Information**:
   - `get_table_columns(inspector, table_name)` - Get list kolom
   - `get_table_indexes(inspector, table_name)` - Get list index

4. **Validation**:
   - `validate_migration_prerequisites(inspector, required_tables, required_columns)` - Validasi prerequisites

## ⚠️ Catatan Penting

1. **Jangan Ubah Migration yang Sudah di Production**
   - Jika migration sudah dijalankan di production, jangan ubah revision ID
   - Hanya update untuk menggunakan `utils.py` jika tidak mengubah behavior

2. **Test Migration Sebelum Deploy**
   - Selalu test migration di development/staging dulu
   - Pastikan downgrade juga berfungsi

3. **Backup Database**
   - Selalu backup database sebelum menjalankan migration
   - Khususnya untuk data migration

4. **Template File**
   - `TEMPLATE_migration.py` adalah template, jangan di-copy ke `versions/` tanpa di-rename
   - Gunakan sebagai reference saat membuat migration baru

## 📊 Migration History

Lihat file `ANALYSIS_AND_RECOMMENDATIONS.md` untuk:
- Analisis lengkap migration files
- Masalah yang ditemukan
- Rekomendasi perbaikan
- Action items

## 🔗 Related Files

- `alembic.ini` - Konfigurasi Alembic
- `scripts/smart_migrate.py` - Script migration utama
- `scripts/run_migrations.py` - Alternatif script migration
- `app/utils/migration.py` - Migration utilities untuk auto-migrate

