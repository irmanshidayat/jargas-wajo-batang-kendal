from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.user.permission_repository import PageRepository, PermissionRepository
from app.schemas.user.permission_request import (
    PageCreateRequest,
    PageUpdateRequest,
    PermissionCreateRequest,
    PermissionUpdateRequest,
    AssignUserPermissionsRequest
)
from app.schemas.user.permission_response import (
    PageResponse,
    PageListResponse,
    PermissionResponse,
    PermissionDetailResponse
)
from app.models.user.user_permission import UserPermission
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.helpers import sanitize_dict


class PageService:
    """Service untuk handle business logic Page"""

    def __init__(self, db: Session):
        self.page_repo = PageRepository(db)
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[PageListResponse], int]:
        """Get all pages with pagination"""
        pages = self.page_repo.get_all_ordered(skip=skip, limit=limit)
        total = self.page_repo.count(filters=filters)
        
        return [
            PageListResponse.model_validate(page) for page in pages
        ], total

    def get_by_id(self, page_id: int) -> PageResponse:
        """Get page by ID"""
        page = self.page_repo.get(page_id)
        if not page:
            raise NotFoundError(f"Page dengan ID {page_id} tidak ditemukan")
        
        return PageResponse.model_validate(page)

    def create(self, page_data: PageCreateRequest) -> PageResponse:
        """Create new page"""
        # Check if name already exists
        if self.page_repo.name_exists(page_data.name):
            raise ValidationError(f"Page dengan nama {page_data.name} sudah ada")
        
        # Check if path already exists
        if self.page_repo.get_by_path(page_data.path):
            raise ValidationError(f"Page dengan path {page_data.path} sudah ada")
        
        page_dict = {
            "name": page_data.name,
            "path": page_data.path,
            "icon": page_data.icon,
            "display_name": page_data.display_name,
            "order": page_data.order or 0,
        }
        
        page = self.page_repo.create(page_dict)
        if not page:
            raise ValidationError("Gagal membuat page baru")
        
        return PageResponse.model_validate(page)

    def update(self, page_id: int, page_data: PageUpdateRequest) -> PageResponse:
        """Update page"""
        page = self.page_repo.get(page_id)
        if not page:
            raise NotFoundError(f"Page dengan ID {page_id} tidak ditemukan")
        
        # Check if name changed and already exists
        if page_data.name and page_data.name != page.name:
            if self.page_repo.name_exists(page_data.name):
                raise ValidationError(f"Page dengan nama {page_data.name} sudah ada")
        
        # Check if path changed and already exists
        if page_data.path and page_data.path != page.path:
            if self.page_repo.get_by_path(page_data.path):
                raise ValidationError(f"Page dengan path {page_data.path} sudah ada")
        
        update_data = sanitize_dict(page_data.model_dump(exclude_unset=True))
        
        updated_page = self.page_repo.update(page_id, update_data)
        if not updated_page:
            raise ValidationError("Gagal mengupdate page")
        
        return PageResponse.model_validate(updated_page)

    def delete(self, page_id: int) -> bool:
        """Delete page"""
        page = self.page_repo.get(page_id)
        if not page:
            raise NotFoundError(f"Page dengan ID {page_id} tidak ditemukan")
        
        result = self.page_repo.delete(page_id)
        if not result:
            raise ValidationError("Gagal menghapus page")
        
        return True


class PermissionService:
    """Service untuk handle business logic Permission"""

    def __init__(self, db: Session):
        self.permission_repo = PermissionRepository(db)
        self.page_repo = PageRepository(db)
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[PermissionResponse], int]:
        """Get all permissions with pagination"""
        permissions = self.permission_repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.permission_repo.count(filters=filters)
        
        result = []
        for perm in permissions:
            perm_dict = {
                "id": perm.id,
                "page_id": perm.page_id,
                "page_name": perm.page.name if perm.page else None,
                "page_path": perm.page.path if perm.page else None,
                "can_create": perm.can_create,
                "can_read": perm.can_read,
                "can_update": perm.can_update,
                "can_delete": perm.can_delete,
                "created_at": perm.created_at,
                "updated_at": perm.updated_at,
            }
            result.append(PermissionResponse.model_validate(perm_dict))
        
        return result, total

    def get_by_id(self, permission_id: int) -> PermissionDetailResponse:
        """Get permission by ID"""
        permission = self.permission_repo.get_with_page(permission_id)
        if not permission:
            raise NotFoundError(f"Permission dengan ID {permission_id} tidak ditemukan")
        
        return PermissionDetailResponse.model_validate(permission)

    def get_by_page_id(self, page_id: int) -> List[PermissionResponse]:
        """Get all permissions for a page"""
        permissions = self.permission_repo.get_by_page_id(page_id)
        
        result = []
        for perm in permissions:
            perm_dict = {
                "id": perm.id,
                "page_id": perm.page_id,
                "page_name": perm.page.name if perm.page else None,
                "page_path": perm.page.path if perm.page else None,
                "can_create": perm.can_create,
                "can_read": perm.can_read,
                "can_update": perm.can_update,
                "can_delete": perm.can_delete,
                "created_at": perm.created_at,
                "updated_at": perm.updated_at,
            }
            result.append(PermissionResponse.model_validate(perm_dict))
        
        return result

    def create(self, permission_data: PermissionCreateRequest) -> PermissionDetailResponse:
        """Create new permission"""
        # Verify page exists
        page = self.page_repo.get(permission_data.page_id)
        if not page:
            raise NotFoundError(f"Page dengan ID {permission_data.page_id} tidak ditemukan")
        
        # Check if permission with same CRUD flags already exists
        existing = self.permission_repo.get_permission_by_page_and_crud(
            permission_data.page_id,
            permission_data.can_create,
            permission_data.can_read,
            permission_data.can_update,
            permission_data.can_delete
        )
        if existing:
            raise ValidationError("Permission dengan kombinasi CRUD yang sama sudah ada untuk page ini")
        
        permission_dict = {
            "page_id": permission_data.page_id,
            "can_create": permission_data.can_create,
            "can_read": permission_data.can_read,
            "can_update": permission_data.can_update,
            "can_delete": permission_data.can_delete,
        }
        
        permission = self.permission_repo.create(permission_dict)
        if not permission:
            raise ValidationError("Gagal membuat permission baru")
        
        return self.get_by_id(permission.id)

    def update(self, permission_id: int, permission_data: PermissionUpdateRequest) -> PermissionDetailResponse:
        """Update permission"""
        permission = self.permission_repo.get(permission_id)
        if not permission:
            raise NotFoundError(f"Permission dengan ID {permission_id} tidak ditemukan")
        
        update_data = sanitize_dict(permission_data.model_dump(exclude_unset=True))
        
        updated_permission = self.permission_repo.update(permission_id, update_data)
        if not updated_permission:
            raise ValidationError("Gagal mengupdate permission")
        
        return self.get_by_id(permission_id)

    def delete(self, permission_id: int) -> bool:
        """Delete permission"""
        permission = self.permission_repo.get(permission_id)
        if not permission:
            raise NotFoundError(f"Permission dengan ID {permission_id} tidak ditemukan")
        
        result = self.permission_repo.delete(permission_id)
        if not result:
            raise ValidationError("Gagal menghapus permission")
        
        return True

    def assign_user_permissions(self, user_id: int, permissions_data: AssignUserPermissionsRequest) -> bool:
        """Assign permissions to user (override)"""
        # Verify user exists
        from app.repositories.user.user_repository import UserRepository
        user_repo = UserRepository(self.db)
        user = user_repo.get(user_id)
        if not user:
            raise NotFoundError(f"User dengan ID {user_id} tidak ditemukan")
        
        # Delete existing user permissions
        existing_ups = self.db.query(UserPermission).filter(UserPermission.user_id == user_id).all()
        for up in existing_ups:
            self.db.delete(up)
        
        # Add new user permissions
        for permission_id in permissions_data.permission_ids:
            # Verify permission exists
            permission = self.permission_repo.get(permission_id)
            if not permission:
                raise NotFoundError(f"Permission dengan ID {permission_id} tidak ditemukan")
            
            # Create user permission
            user_permission = UserPermission(
                user_id=user_id,
                permission_id=permission_id
            )
            self.db.add(user_permission)
        
        self.db.commit()
        return True

    def get_or_create_permission(
        self,
        page_id: int,
        can_create: bool,
        can_read: bool,
        can_update: bool,
        can_delete: bool
    ) -> int:
        """
        Get atau create permission dengan kombinasi CRUD tertentu untuk page.
        Return permission ID.
        
        Jika permission dengan kombinasi CRUD yang sama sudah ada untuk page tersebut,
        return ID yang sudah ada. Jika tidak, create permission baru.
        """
        # Cek apakah page exists
        page = self.page_repo.get(page_id)
        if not page:
            raise NotFoundError(f"Page dengan ID {page_id} tidak ditemukan")
        
        # Cari permission dengan kombinasi CRUD yang sama untuk page ini
        existing_permission = self.permission_repo.get_permission_by_page_and_crud(
            page_id=page_id,
            can_create=can_create,
            can_read=can_read,
            can_update=can_update,
            can_delete=can_delete
        )
        
        if existing_permission:
            return existing_permission.id
        
        # Create permission baru
        permission_data = {
            'page_id': page_id,
            'can_create': can_create,
            'can_read': can_read,
            'can_update': can_update,
            'can_delete': can_delete,
        }
        
        new_permission = self.permission_repo.create(permission_data)
        if not new_permission:
            raise ValidationError("Gagal membuat permission baru")
        
        return new_permission.id

    def get_user_permissions(self, user_id: int) -> List[PermissionResponse]:
        """Get all permissions for a user (role permissions + user overrides)"""
        from app.repositories.user.user_repository import UserRepository
        from app.models.user.role_permission import RolePermission
        
        user_repo = UserRepository(self.db)
        user = user_repo.get(user_id)
        if not user:
            raise NotFoundError(f"User dengan ID {user_id} tidak ditemukan")
        
        permission_ids = set()
        
        # Get permissions from role
        if user.role_id:
            role_permissions = self.db.query(RolePermission).filter(
                RolePermission.role_id == user.role_id
            ).all()
            for rp in role_permissions:
                permission_ids.add(rp.permission_id)
        
        # Get user override permissions (will override role permissions)
        user_permissions = self.db.query(UserPermission).filter(
            UserPermission.user_id == user_id
        ).all()
        for up in user_permissions:
            permission_ids.add(up.permission_id)
        
        # Fetch all permissions
        permissions = []
        for perm_id in permission_ids:
            perm = self.permission_repo.get_with_page(perm_id)
            if perm:
                perm_dict = {
                    "id": perm.id,
                    "page_id": perm.page_id,
                    "page_name": perm.page.name if perm.page else None,
                    "page_path": perm.page.path if perm.page else None,
                    "can_create": perm.can_create,
                    "can_read": perm.can_read,
                    "can_update": perm.can_update,
                    "can_delete": perm.can_delete,
                    "created_at": perm.created_at,
                    "updated_at": perm.updated_at,
                }
                permissions.append(PermissionResponse.model_validate(perm_dict))
        
        return permissions

