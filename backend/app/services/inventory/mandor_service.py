from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.inventory import MandorRepository
from app.services.base import BaseService


class MandorService(BaseService[MandorRepository]):
    """
    Service untuk handle business logic Mandor
    Menggunakan BaseService untuk CRUD operations standar
    """

    def __init__(self, db: Session):
        repository = MandorRepository(db)
        super().__init__(repository, db)

    def search_by_name(self, nama: str, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List:
        """Search mandors by name"""
        return self.repository.search_by_name(nama, skip=skip, limit=limit, project_id=project_id)

    def create(self, mandor_data: dict, project_id: Optional[int] = None):
        """Create new mandor - project_id tidak wajib untuk mandor"""
        return super().create(mandor_data, project_id=project_id, validate_project_id=False)

    def delete(self, mandor_id: int, project_id: Optional[int] = None) -> bool:
        """Soft delete mandor"""
        return super().delete(mandor_id, project_id=project_id, soft_delete=True)

