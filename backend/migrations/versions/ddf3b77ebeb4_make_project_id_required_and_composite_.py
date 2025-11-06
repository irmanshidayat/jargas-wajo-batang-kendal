"""make_project_id_required_and_composite_unique_kode_barang

Revision ID: ddf3b77ebeb4
Revises: 82b36e17b6fd
Create Date: 2025-11-03 09:32:40.561899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddf3b77ebeb4'
down_revision: Union[str, None] = '82b36e17b6fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    1. Assign data existing yang project_id=NULL ke default project
    2. Ubah project_id menjadi NOT NULL untuk semua tabel inventory
    3. Ubah unique constraint kode_barang menjadi composite unique (project_id, kode_barang)
    """
    
    # Step 1: Buat atau dapatkan default project
    connection = op.get_bind()
    
    # Cek apakah default project sudah ada
    result = connection.execute(sa.text("SELECT id FROM projects WHERE code = 'DEFAULT' LIMIT 1"))
    default_project = result.fetchone()
    
    if not default_project:
        # Buat default project
        connection.execute(sa.text("""
            INSERT INTO projects (name, code, description, is_active, created_at, updated_at)
            VALUES ('Default Project', 'DEFAULT', 'Project default untuk data existing', 1, NOW(), NOW())
        """))
        result = connection.execute(sa.text("SELECT id FROM projects WHERE code = 'DEFAULT' LIMIT 1"))
        default_project = result.fetchone()
    
    default_project_id = default_project[0]
    
    # Step 2: Assign data existing ke default project
    tables_with_project_id = [
        'materials',
        'mandors',
        'stock_ins',
        'stock_outs',
        'installed',
        'returns',
        'audit_logs'
    ]
    
    for table in tables_with_project_id:
        connection.execute(sa.text(f"""
            UPDATE {table} 
            SET project_id = :project_id 
            WHERE project_id IS NULL
        """), {"project_id": default_project_id})
    
    # Assign semua user ke default project (jika belum ada)
    connection.execute(sa.text("""
        INSERT IGNORE INTO user_projects (user_id, project_id, is_active, is_owner, created_at, updated_at)
        SELECT u.id, :project_id, 1, 1, NOW(), NOW()
        FROM users u
        WHERE NOT EXISTS (
            SELECT 1 FROM user_projects up 
            WHERE up.user_id = u.id AND up.project_id = :project_id
        )
    """), {"project_id": default_project_id})
    
    connection.commit()
    
    # Step 3: Hapus unique constraint dan index pada kode_barang di materials
    # MySQL: Unique constraint biasanya dibuat sebagai index, jadi kita drop index-nya
    try:
        # Coba drop index dengan nama umum
        op.drop_index('ix_materials_kode_barang', table_name='materials')
    except Exception:
        try:
            # Coba dengan nama constraint
            op.drop_index('uq_materials_kode_barang', table_name='materials')
        except Exception:
            try:
                # Coba dengan nama lain
                op.drop_index('materials_kode_barang_key', table_name='materials')
            except Exception:
                # Jika semua gagal, coba drop constraint langsung (jika bukan index)
                try:
                    op.drop_constraint('uq_materials_kode_barang', 'materials', type_='unique')
                except Exception:
                    try:
                        op.drop_constraint('materials_kode_barang_key', 'materials', type_='unique')
                    except Exception:
                        pass  # Constraint/index mungkin tidak ada
    
    # Step 4: Buat composite unique constraint untuk (project_id, kode_barang)
    op.create_unique_constraint(
        'uq_material_project_kode',
        'materials',
        ['project_id', 'kode_barang']
    )
    
    # Step 5: Ubah project_id menjadi NOT NULL untuk semua tabel
    for table in tables_with_project_id:
        op.alter_column(
            table,
            'project_id',
            existing_type=sa.Integer(),
            nullable=False
        )


def downgrade() -> None:
    """Rollback perubahan"""
    
    # Step 1: Ubah project_id kembali menjadi nullable
    tables_with_project_id = [
        'materials',
        'mandors',
        'stock_ins',
        'stock_outs',
        'installed',
        'returns',
        'audit_logs'
    ]
    
    for table in tables_with_project_id:
        op.alter_column(
            table,
            'project_id',
            existing_type=sa.Integer(),
            nullable=True
        )
    
    # Step 2: Drop composite unique constraint
    op.drop_constraint('uq_material_project_kode', 'materials', type_='unique')
    
    # Step 3: Kembalikan unique constraint pada kode_barang
    op.create_unique_constraint(
        'uq_materials_kode_barang',
        'materials',
        ['kode_barang']
    )
