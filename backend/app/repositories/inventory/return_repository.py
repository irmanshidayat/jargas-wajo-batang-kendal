from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_, func
from datetime import date
from app.models.inventory.return_model import Return
from app.repositories.base import BaseRepository


class ReturnRepository(BaseRepository[Return]):
    """Repository untuk Return model"""

    def __init__(self, db: Session):
        super().__init__(Return, db)

    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        skip: int = 0, 
        limit: int = 100,
        project_id: Optional[int] = None
    ) -> List[Return]:
        """Get returns by date range, optionally filtered by project_id"""
        try:
            from sqlalchemy import or_
            query = self.db.query(self.model).filter(
                and_(
                    self.model.tanggal_kembali >= start_date,
                    self.model.tanggal_kembali <= end_date,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            )
            
            # Filter by project_id if provided
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_mandor_and_material(
        self, 
        mandor_id: int, 
        material_id: int,
        project_id: Optional[int] = None
    ) -> List[Return]:
        """Get returns by mandor and material, optionally filtered by project_id"""
        try:
            from sqlalchemy import or_
            query = self.db.query(self.model).filter(
                and_(
                    self.model.mandor_id == mandor_id,
                    self.model.material_id == material_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            )
            
            # Filter by project_id if provided
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.all()
        except Exception:
            return []

    def get_total_quantity_by_stock_out(self, stock_out_id: int) -> int:
        """Get total quantity_kembali untuk stock_out_id tertentu (tidak termasuk yang deleted)"""
        try:
            from sqlalchemy import or_
            result = self.db.query(func.sum(self.model.quantity_kembali)).filter(
                and_(
                    self.model.stock_out_id == stock_out_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            ).scalar()
            return result if result is not None else 0
        except Exception:
            return 0

    def get_total_reject_by_stock_out(self, stock_out_id: int) -> int:
        """Get total quantity_kondisi_reject untuk stock_out_id tertentu (tidak termasuk yang deleted)"""
        try:
            from sqlalchemy import or_
            result = self.db.query(func.sum(self.model.quantity_kondisi_reject)).filter(
                and_(
                    self.model.stock_out_id == stock_out_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            ).scalar()
            return result if result is not None else 0
        except Exception:
            return 0

    def get_by_stock_out(self, stock_out_id: int) -> List[Return]:
        """Get all returns by stock_out_id (tidak termasuk yang deleted)"""
        try:
            from sqlalchemy import or_
            return self.db.query(self.model).filter(
                and_(
                    self.model.stock_out_id == stock_out_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            ).all()
        except Exception:
            return []

    def get_all_by_material(self, material_id: int, skip: int = 0, limit: int = 10000) -> List[Return]:
        """Get all returns by material_id, tanpa filter project_id (untuk backward compatibility)"""
        try:
            from sqlalchemy import or_
            return self.db.query(self.model).filter(
                and_(
                    self.model.material_id == material_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            ).offset(skip).limit(limit).all()
        except Exception:
            return []

    def soft_delete(self, id: int, deleted_by: int) -> Optional[Return]:
        """Soft delete return"""
        return self.update(id, {"is_deleted": 1, "deleted_by": deleted_by})

