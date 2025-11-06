from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository untuk Role model dengan custom methods"""

    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.get_by(name=name)

    def name_exists(self, name: str) -> bool:
        """Check if role name already exists"""
        role = self.get_by_name(name)
        return role is not None

    def get_with_permissions(self, role_id: int) -> Optional[Role]:
        """Get role with its permissions loaded"""
        from sqlalchemy.orm import joinedload
        from app.models.user.role_permission import RolePermission
        from app.models.user.permission import Permission, Page
        
        return self.db.query(Role).options(
            joinedload(Role.role_permissions).joinedload(RolePermission.permission).joinedload(Permission.page)
        ).filter(Role.id == role_id).first()

    def get_all_with_permissions(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get all roles with permissions loaded"""
        from sqlalchemy.orm import joinedload
        from app.models.user.role_permission import RolePermission
        from app.models.user.permission import Permission, Page
        
        return self.db.query(Role).options(
            joinedload(Role.role_permissions).joinedload(RolePermission.permission).joinedload(Permission.page)
        ).offset(skip).limit(limit).all()

