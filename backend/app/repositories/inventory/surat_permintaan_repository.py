from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import date
from app.models.inventory.surat_permintaan import SuratPermintaan
from app.repositories.base import BaseRepository


class SuratPermintaanRepository(BaseRepository[SuratPermintaan]):
    """Repository untuk SuratPermintaan model"""

    def __init__(self, db: Session):
        super().__init__(SuratPermintaan, db)

    def get_next_number_for_project_code(self, project_code: str, tanggal: date) -> int:
        """Get next sequence number untuk project code (nomor terus berlanjut tanpa reset per hari)
        
        Format: JRGS-{PROJECT_CODE}-{YYYYMMDD}-{XXXX}
        Nomor urut (XXXX) terus berlanjut tanpa reset per hari
        """
        try:
            date_str = tanggal.strftime("%Y%m%d")
            prefix = f"JRGS-{project_code}-"
            
            # Get all nomor yang match prefix untuk project code ini (tidak peduli tanggal)
            # Tidak filter is_deleted karena unique constraint berlaku untuk semua record
            self.db.expire_all()
            query = self.db.query(self.model.nomor_surat).filter(
                self.model.nomor_surat.like(f"{prefix}%")
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
                    
                    # Format: JRGS-{PROJECT_CODE}-{YYYYMMDD}-{XXXX}
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
        project_id: Optional[int] = None
    ) -> List[SuratPermintaan]:
        """Get all surat permintaan dengan sorting berdasarkan created_at DESC (terbaru dulu)"""
        try:
            query = self.db.query(self.model)
            
            # Auto-filter by project_id if model has project_id column and project_id is provided
            if project_id is not None and hasattr(self.model, 'project_id'):
                query = query.filter(self.model.project_id == project_id)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            # Sort berdasarkan created_at DESC (terbaru dulu)
            return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_nomor_surat(self, nomor_surat: str, project_id: Optional[int] = None) -> Optional[SuratPermintaan]:
        """Get surat permintaan by nomor surat"""
        try:
            query = self.db.query(self.model).filter(self.model.nomor_surat == nomor_surat)
            
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.first()
        except Exception:
            return None

    def search_by_nomor_or_date(self, search: str, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List[SuratPermintaan]:
        """Search surat permintaan by nomor surat atau tanggal"""
        try:
            from sqlalchemy import or_
            query = self.db.query(self.model).filter(
                or_(
                    self.model.nomor_surat.like(f"%{search}%"),
                    self.model.tanggal.like(f"%{search}%")
                )
            ).filter(self.model.is_deleted == 0)
            
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_date_range(self, start_date: date, end_date: date, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List[SuratPermintaan]:
        """Get surat permintaan by date range"""
        try:
            query = self.db.query(self.model).filter(
                self.model.tanggal >= start_date,
                self.model.tanggal <= end_date,
                self.model.is_deleted == 0
            )
            
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()
        except Exception:
            return []

    def soft_delete(self, id: int, deleted_by: int) -> Optional[SuratPermintaan]:
        """Soft delete surat permintaan"""
        return self.update(id, {"is_deleted": 1, "deleted_by": deleted_by})

