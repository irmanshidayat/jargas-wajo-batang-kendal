from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.inventory.mandor import Mandor
from app.repositories.base import BaseRepository


class MandorRepository(BaseRepository[Mandor]):
    """Repository untuk Mandor model"""

    def __init__(self, db: Session):
        super().__init__(Mandor, db)

    def get_active_mandors(self, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List[Mandor]:
        """Get all active mandors - menggunakan get_active() dari base"""
        return self.get_active(skip=skip, limit=limit, project_id=project_id)

    def search_by_name(self, nama: str, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List[Mandor]:
        """Search mandors by name"""
        try:
            from sqlalchemy import and_
            query = self.db.query(self.model).filter(
                and_(
                    self.model.nama.like(f"%{nama}%"),
                    self.model.is_active == 1
                )
            )
            
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.offset(skip).limit(limit).all()
        except Exception:
            return []

