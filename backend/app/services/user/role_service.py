from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.user.role_repository import RoleRepository
from app.repositories.user.permission_repository import PermissionRepository
from app.models.user.role_permission import RolePermission
from app.schemas.user.role_request import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RolePatchRequest,
    AssignPermissionsRequest,
    AssignRolePermissionsCRUDRequest
)
from app.schemas.user.role_response import RoleResponse, RoleDetailResponse, RoleListResponse
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.helpers import sanitize_dict


class RoleService:
    """Service untuk handle business logic Role"""

    def __init__(self, db: Session):
        self.role_repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[RoleListResponse], int]:
        """Get all roles with pagination"""
        roles = self.role_repo.get_all(skip=skip, limit=limit, filters=filters)
        total = self.role_repo.count(filters=filters)
        
        return [
            RoleListResponse.model_validate(role) for role in roles
        ], total

    def get_by_id(self, role_id: int, include_permissions: bool = False) -> RoleResponse | RoleDetailResponse:
        """Get role by ID"""
        if include_permissions:
            role = self.role_repo.get_with_permissions(role_id)
        else:
            role = self.role_repo.get(role_id)
        
        if not role:
            raise NotFoundError(f"Role dengan ID {role_id} tidak ditemukan")
        
        if include_permissions:
            # Build permission details
            permission_details = []
            for rp in role.role_permissions:
                perm = rp.permission
                page = perm.page
                permission_details.append({
                    "id": perm.id,
                    "page_id": page.id,
                    "page_name": page.name,
                    "page_path": page.path,
                    "can_create": perm.can_create,
                    "can_read": perm.can_read,
                    "can_update": perm.can_update,
                    "can_delete": perm.can_delete,
                })
            
            role_dict = {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": permission_details,
                "created_at": role.created_at,
                "updated_at": role.updated_at,
            }
            return RoleDetailResponse.model_validate(role_dict)
        else:
            return RoleResponse.model_validate(role)

    def create(self, role_data: RoleCreateRequest) -> RoleResponse:
        """Create new role"""
        # Check if name already exists
        if self.role_repo.name_exists(role_data.name):
            raise ValidationError(f"Role dengan nama {role_data.name} sudah ada")
        
        # Create role data dict
        role_dict = {
            "name": role_data.name,
            "description": role_data.description,
        }
        
        role = self.role_repo.create(role_dict)
        if not role:
            raise ValidationError("Gagal membuat role baru")
        
        return RoleResponse.model_validate(role)

    def update(self, role_id: int, role_data: RoleUpdateRequest) -> RoleResponse:
        """Update role (full update)"""
        role = self.role_repo.get(role_id)
        if not role:
            raise NotFoundError(f"Role dengan ID {role_id} tidak ditemukan")
        
        # Check if name changed and already exists
        if role_data.name and role_data.name != role.name:
            if self.role_repo.name_exists(role_data.name):
                raise ValidationError(f"Role dengan nama {role_data.name} sudah ada")
        
        # Prepare update data
        update_data = sanitize_dict(role_data.model_dump(exclude_unset=True))
        
        updated_role = self.role_repo.update(role_id, update_data)
        if not updated_role:
            raise ValidationError("Gagal mengupdate role")
        
        return RoleResponse.model_validate(updated_role)

    def patch(self, role_id: int, role_data: RolePatchRequest) -> RoleResponse:
        """Partial update role"""
        role = self.role_repo.get(role_id)
        if not role:
            raise NotFoundError(f"Role dengan ID {role_id} tidak ditemukan")
        
        # Check if name changed and already exists
        if role_data.name and role_data.name != role.name:
            if self.role_repo.name_exists(role_data.name):
                raise ValidationError(f"Role dengan nama {role_data.name} sudah ada")
        
        # Prepare update data
        update_data = sanitize_dict(role_data.model_dump(exclude_unset=True))
        
        updated_role = self.role_repo.update(role_id, update_data)
        if not updated_role:
            raise ValidationError("Gagal mengupdate role")
        
        return RoleResponse.model_validate(updated_role)

    def delete(self, role_id: int) -> bool:
        """Delete role"""
        role = self.role_repo.get(role_id)
        if not role:
            raise NotFoundError(f"Role dengan ID {role_id} tidak ditemukan")
        
        result = self.role_repo.delete(role_id)
        if not result:
            raise ValidationError("Gagal menghapus role")
        
        return True

    def assign_permissions(self, role_id: int, permissions_data: AssignPermissionsRequest) -> RoleDetailResponse:
        """Assign permissions to role"""
        role = self.role_repo.get(role_id)
        if not role:
            raise NotFoundError(f"Role dengan ID {role_id} tidak ditemukan")
        
        # Delete existing role permissions
        existing_rps = self.db.query(RolePermission).filter(RolePermission.role_id == role_id).all()
        for rp in existing_rps:
            self.db.delete(rp)
        
        # Add new role permissions
        for permission_id in permissions_data.permission_ids:
            # Verify permission exists
            permission = self.permission_repo.get(permission_id)
            if not permission:
                raise NotFoundError(f"Permission dengan ID {permission_id} tidak ditemukan")
            
            # Create role permission
            role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission_id
            )
            self.db.add(role_permission)
        
        self.db.commit()
        
        # Return updated role with permissions
        return self.get_by_id(role_id, include_permissions=True)

    def assign_permissions_crud(self, role_id: int, crud_data: AssignRolePermissionsCRUDRequest) -> RoleDetailResponse:
        """
        Assign CRUD permissions per page ke role.
        Untuk setiap page, buat atau cari permission dengan kombinasi CRUD yang sesuai,
        lalu assign ke role.
        """
        from app.services.user.permission_service import PermissionService
        from sqlalchemy.exc import IntegrityError
        
        role = self.role_repo.get(role_id)
        if not role:
            raise NotFoundError(f"Role dengan ID {role_id} tidak ditemukan")
        
        permission_service = PermissionService(self.db)
        permission_ids = []
        
        # Loop setiap page_permission di crud_data
        for page_perm in crud_data.page_permissions:
            # Cek apakah ada minimal satu CRUD yang enabled
            if not (page_perm.can_create or page_perm.can_read or page_perm.can_update or page_perm.can_delete):
                # Skip jika semua CRUD false (tidak ada akses sama sekali)
                continue
            
            # Get atau create permission dengan kombinasi CRUD yang sesuai
            permission_id = permission_service.get_or_create_permission(
                page_id=page_perm.page_id,
                can_create=page_perm.can_create,
                can_read=page_perm.can_read,
                can_update=page_perm.can_update,
                can_delete=page_perm.can_delete
            )
            permission_ids.append(permission_id)
        
        # Remove duplicates dari permission_ids (preserves order)
        permission_ids = list(dict.fromkeys(permission_ids))
        
        # Delete existing role permissions dengan bulk delete
        self.db.query(RolePermission).filter(RolePermission.role_id == role_id).delete(synchronize_session=False)
        
        # Flush untuk memastikan delete sudah dilakukan sebelum insert
        self.db.flush()
        
        # Add new role permissions (langsung insert karena kita sudah delete semua)
        for permission_id in permission_ids:
            role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission_id
            )
            self.db.add(role_permission)
        
        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            # Jika masih ada duplicate error, berarti ada issue dengan data atau race condition
            raise ValidationError(f"Gagal menyimpan permissions. Pastikan tidak ada duplikasi permission untuk role ini.")
        
        # Return updated role with permissions
        return self.get_by_id(role_id, include_permissions=True)

