from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import date
from app.models.inventory.surat_jalan import SuratJalan
from app.repositories.base import BaseRepository


class SuratJalanRepository(BaseRepository[SuratJalan]):
    """Repository untuk SuratJalan model"""

    def __init__(self, db: Session):
        super().__init__(SuratJalan, db)

    def get_next_number_for_project_code(self, project_code: str, tanggal: date) -> int:
        """Get next sequence number untuk project code (nomor terus berlanjut tanpa reset per hari)
        
        Format: SJ-{PROJECT_CODE}-{YYYYMMDD}-{XXXX}
        Nomor urut (XXXX) terus berlanjut tanpa reset per hari
        """
        try:
            date_str = tanggal.strftime("%Y%m%d")
            prefix = f"SJ-{project_code}-"
            
            # Get all nomor yang match prefix untuk project code ini (tidak peduli tanggal)
            # Tidak filter is_deleted karena unique constraint berlaku untuk semua record
            self.db.expire_all()
            query = self.db.query(self.model.nomor_form).filter(
                self.model.nomor_form.like(f"{prefix}%")
            )
            
            results = query.all()
            
            if not results:
                return 1
            
            # Extract numbers dan cari yang terbesar
            max_num = 0
            for result in results:
                try:
                    if isinstance(result, tuple):
                        nomor = result[0]
                    elif hasattr(result, '__getitem__'):
                        nomor = result[0] if len(result) > 0 else str(result)
                    else:
                        nomor = str(result)
                    
                    if not isinstance(nomor, str):
                        nomor = str(nomor)
                    
                    # Format: SJ-{PROJECT_CODE}-{YYYYMMDD}-{XXXX}
                    # Extract XXXX (4 digit terakhir setelah -)
                    parts = nomor.split("-")
                    if len(parts) == 4:
                        num = int(parts[-1])
                        if num > max_num:
                            max_num = num
                except (ValueError, IndexError, AttributeError, TypeError):
                    continue
            
            return max_num + 1
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error getting next number for project code {project_code}: {str(e)}", exc_info=True)
            return 1

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[SuratJalan]:
        """Get all surat jalan dengan sorting berdasarkan created_at DESC (terbaru dulu)"""
        try:
            query = self.db.query(self.model)
            
            # Auto-filter by project_id if model has project_id column and project_id is provided
            if project_id is not None and hasattr(self.model, 'project_id'):
                query = query.filter(self.model.project_id == project_id)
            
            # Auto-filter by user hierarchy if model has created_by column and user_id is provided
            if user_id is not None and hasattr(self.model, 'created_by'):
                from app.utils.user_hierarchy import filter_by_user_hierarchy
                query = filter_by_user_hierarchy(query, self.db, user_id, self.model.created_by)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            # Sort berdasarkan created_at DESC (terbaru dulu)
            return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_nomor_form(self, nomor_form: str, project_id: Optional[int] = None) -> Optional[SuratJalan]:
        """Get surat jalan by nomor form"""
        try:
            query = self.db.query(self.model).filter(self.model.nomor_form == nomor_form)
            
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.first()
        except Exception:
            return None

    def search_by_nomor_or_kepada(self, search: str, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List[SuratJalan]:
        """Search surat jalan by nomor form atau kepada"""
        try:
            from sqlalchemy import or_
            query = self.db.query(self.model).filter(
                or_(
                    self.model.nomor_form.like(f"%{search}%"),
                    self.model.kepada.like(f"%{search}%")
                )
            ).filter(self.model.is_deleted == 0)
            
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_date_range(self, start_date: date, end_date: date, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List[SuratJalan]:
        """Get surat jalan by date range"""
        try:
            query = self.db.query(self.model).filter(
                self.model.tanggal_pengiriman >= start_date,
                self.model.tanggal_pengiriman <= end_date,
                self.model.is_deleted == 0
            )
            
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
        except Exception:
            return []

    def soft_delete(self, id: int, deleted_by: int) -> Optional[SuratJalan]:
        """Soft delete surat jalan"""
        return self.update(id, {"is_deleted": 1, "deleted_by": deleted_by})

    def is_nomor_barang_keluar_used(self, nomor_barang_keluar: str, exclude_id: Optional[int] = None, project_id: Optional[int] = None) -> bool:
        """Cek apakah nomor barang keluar sudah pernah digunakan untuk surat jalan lain
        
        Best practice: Satu nomor barang keluar hanya bisa digunakan untuk satu surat jalan
        untuk memastikan traceability dan menghindari duplikasi.
        
        Args:
            nomor_barang_keluar: Nomor barang keluar yang akan dicek
            exclude_id: ID surat jalan yang akan di-exclude dari pengecekan (untuk update)
            project_id: Optional project_id untuk filter
            
        Returns:
            True jika nomor sudah digunakan, False jika belum
        """
        try:
            query = self.db.query(self.model).filter(
                self.model.nomor_barang_keluar == nomor_barang_keluar,
                self.model.is_deleted == 0
            )
            
            # Exclude current record jika sedang update
            if exclude_id is not None:
                query = query.filter(self.model.id != exclude_id)
            
            # Filter by project jika diperlukan
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            existing = query.first()
            return existing is not None
        except Exception:
            # Jika error, assume belum digunakan untuk safety
            return False

