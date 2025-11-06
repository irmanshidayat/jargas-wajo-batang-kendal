from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_
from datetime import date
from app.models.inventory.stock_in import StockIn
from app.repositories.base import BaseRepository


class StockInRepository(BaseRepository[StockIn]):
    """Repository untuk StockIn model"""

    def __init__(self, db: Session):
        super().__init__(StockIn, db)

    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[StockIn]:
        """Get stock ins by date range"""
        try:
            from sqlalchemy import or_
            return self.db.query(self.model).filter(
                and_(
                    self.model.tanggal_masuk >= start_date,
                    self.model.tanggal_masuk <= end_date,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            ).offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_material(
        self, 
        material_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[StockIn]:
        """Get stock ins by material"""
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

    def soft_delete(self, id: int, deleted_by: int) -> Optional[StockIn]:
        """Soft delete stock in"""
        return self.update(id, {"is_deleted": 1, "deleted_by": deleted_by})

