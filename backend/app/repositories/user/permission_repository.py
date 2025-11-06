from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user.permission import Page, Permission
from app.repositories.base import BaseRepository


class PageRepository(BaseRepository[Page]):
    """Repository untuk Page model"""

    def __init__(self, db: Session):
        super().__init__(Page, db)

    def get_by_name(self, name: str) -> Optional[Page]:
        """Get page by name"""
        return self.get_by(name=name)

    def get_by_path(self, path: str) -> Optional[Page]:
        """Get page by path"""
        return self.get_by(path=path)

    def name_exists(self, name: str) -> bool:
        """Check if page name already exists"""
        page = self.get_by_name(name)
        return page is not None

    def get_all_ordered(self, skip: int = 0, limit: int = 100) -> List[Page]:
        """Get all pages ordered by order field"""
        return self.db.query(Page).order_by(Page.order.asc()).offset(skip).limit(limit).all()


class PermissionRepository(BaseRepository[Permission]):
    """Repository untuk Permission model"""

    def __init__(self, db: Session):
        super().__init__(Permission, db)

    def get_by_page_id(self, page_id: int) -> List[Permission]:
        """Get all permissions for a page"""
        return self.db.query(Permission).filter(Permission.page_id == page_id).all()

    def get_with_page(self, permission_id: int) -> Optional[Permission]:
        """Get permission with page loaded"""
        from sqlalchemy.orm import joinedload
        return self.db.query(Permission).options(
            joinedload(Permission.page)
        ).filter(Permission.id == permission_id).first()

    def get_permission_by_page_and_crud(
        self,
        page_id: int,
        can_create: bool,
        can_read: bool,
        can_update: bool,
        can_delete: bool
    ) -> Optional[Permission]:
        """Get permission by page and CRUD flags"""
        return self.db.query(Permission).filter(
            Permission.page_id == page_id,
            Permission.can_create == can_create,
            Permission.can_read == can_read,
            Permission.can_update == can_update,
            Permission.can_delete == can_delete
        ).first()

