from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.models.inventory.material import Material
from app.repositories.base import BaseRepository


class MaterialRepository(BaseRepository[Material]):
    """Repository untuk Material model"""

    def __init__(self, db: Session):
        super().__init__(Material, db)

    def get_by_kode(self, kode_barang: str, project_id: Optional[int] = None) -> Optional[Material]:
        """Get material by kode barang, filter by project_id if provided"""
        query = self.db.query(self.model).filter(self.model.kode_barang == kode_barang)
        
        if project_id is not None:
            query = query.filter(self.model.project_id == project_id)
        
        return query.first()

    def get_active_materials(self, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List[Material]:
        """Get all active materials - menggunakan get_active() dari base"""
        return self.get_active(skip=skip, limit=limit, project_id=project_id)

    def count_active_materials(self, project_id: Optional[int] = None) -> int:
        """Hitung jumlah material aktif + NULL - menggunakan count_active() dari base"""
        return self.count_active(project_id=project_id)

    def search_by_name(self, nama: str, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List[Material]:
        """Search materials by name"""
        try:
            from sqlalchemy import and_
            query = self.db.query(self.model).filter(
                and_(
                    self.model.nama_barang.like(f"%{nama}%"),
                    or_(self.model.is_active == 1, self.model.is_active.is_(None))
                )
            )
            
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.offset(skip).limit(limit).all()
        except Exception:
            return []

    def search_by_name_or_code(self, search_term: str, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List[Material]:
        """Search materials by name or code"""
        try:
            from sqlalchemy import and_
            query = self.db.query(self.model).filter(
                and_(
                    or_(
                        self.model.nama_barang.like(f"%{search_term}%"),
                        self.model.kode_barang.like(f"%{search_term}%")
                    ),
                    or_(self.model.is_active == 1, self.model.is_active.is_(None))
                )
            )
            
            if project_id is not None:
                query = query.filter(self.model.project_id == project_id)
            
            return query.offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_unique_satuans(self) -> List[str]:
        """Get unique satuan values from active materials"""
        try:
            from sqlalchemy import distinct, and_
            results = self.db.query(distinct(self.model.satuan)).filter(
                and_(
                    or_(self.model.is_active == 1, self.model.is_active.is_(None)),
                    self.model.satuan.isnot(None),
                    self.model.satuan != ''
                )
            ).order_by(self.model.satuan).all()
            return [result[0] for result in results if result[0]]
        except Exception:
            return []

    def get_unique_kategoris(self) -> List[str]:
        """Get unique kategori values from active materials"""
        try:
            from sqlalchemy import distinct, and_
            results = self.db.query(distinct(self.model.kategori)).filter(
                and_(
                    or_(self.model.is_active == 1, self.model.is_active.is_(None)),
                    self.model.kategori.isnot(None),
                    self.model.kategori != ''
                )
            ).order_by(self.model.kategori).all()
            return [result[0] for result in results if result[0]]
        except Exception:
            return []

