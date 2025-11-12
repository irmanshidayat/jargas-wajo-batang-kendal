from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_
from datetime import date
from decimal import Decimal
from app.models.inventory.installed import Installed
from app.repositories.base import BaseRepository


class InstalledRepository(BaseRepository[Installed]):
    """Repository untuk Installed model"""

    def __init__(self, db: Session):
        super().__init__(Installed, db)

    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        skip: int = 0, 
        limit: int = 100,
        project_id: Optional[int] = None
    ) -> List[Installed]:
        """Get installed items by date range, optionally filtered by project_id through material"""
        try:
            from app.models.inventory.material import Material
            
            from sqlalchemy import or_
            query = self.db.query(self.model).join(Material).filter(
                and_(
                    self.model.tanggal_pasang >= start_date,
                    self.model.tanggal_pasang <= end_date,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            )
            
            # Filter by project_id through material if provided
            if project_id is not None:
                query = query.filter(Material.project_id == project_id)
            
            return query.offset(skip).limit(limit).all()
        except Exception:
            return []
    
    def get_all_by_project(
        self,
        skip: int = 0,
        limit: int = 10000,
        project_id: Optional[int] = None
    ) -> List[Installed]:
        """Get all installed items, optionally filtered by project_id through material"""
        try:
            from app.models.inventory.material import Material
            
            from sqlalchemy import or_
            query = self.db.query(self.model).join(Material).filter(
                or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
            )
            
            # Filter by project_id through material if provided
            if project_id is not None:
                query = query.filter(Material.project_id == project_id)
            
            return query.offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_mandor_and_material(
        self, 
        mandor_id: int, 
        material_id: int,
        project_id: Optional[int] = None
    ) -> List[Installed]:
        """Get installed items by mandor and material, optionally filtered by project_id through material"""
        try:
            from app.models.inventory.material import Material
            
            from sqlalchemy import or_
            query = self.db.query(self.model).join(Material).filter(
                and_(
                    self.model.mandor_id == mandor_id,
                    self.model.material_id == material_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            )
            
            # Filter by project_id through material if provided
            if project_id is not None:
                query = query.filter(Material.project_id == project_id)
            
            return query.all()
        except Exception:
            return []

    def get_total_quantity_by_stock_out(self, stock_out_id: int) -> Decimal:
        """Get total quantity installed untuk stock_out_id tertentu (tidak termasuk yang deleted)"""
        try:
            from sqlalchemy import func, or_
            result = self.db.query(func.sum(self.model.quantity)).filter(
                and_(
                    self.model.stock_out_id == stock_out_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            ).scalar()
            # Konversi ke Decimal untuk konsistensi tipe data
            return Decimal(str(result)) if result is not None else Decimal('0')
        except Exception:
            return Decimal('0')

    def soft_delete(self, id: int, deleted_by: int) -> Optional[Installed]:
        """Soft delete installed item"""
        return self.update(id, {"is_deleted": 1, "deleted_by": deleted_by})

