from fastapi import APIRouter, Depends, Query, status, Response
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.services.user.role_service import RoleService
from app.schemas.user.role_request import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RolePatchRequest,
    AssignPermissionsRequest,
    AssignRolePermissionsCRUDRequest
)
from app.core.security import get_current_user
from app.models.user.user import User
from app.utils.response import success_response, paginated_response
from app.core.exceptions import ForbiddenError
from app.api.v1.deps import check_superuser

router = APIRouter()


@router.get(
    "",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get all roles",
    description="Mendapatkan daftar semua roles dengan pagination"
)
async def get_roles(
    page: int = Query(1, ge=1, description="Halaman"),
    limit: int = Query(100, ge=1, le=100, description="Jumlah data per halaman"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles dengan pagination"""
    check_superuser(current_user)
    
    skip = (page - 1) * limit
    role_service = RoleService(db)
    roles, total = role_service.get_all(skip=skip, limit=limit)
    
    return paginated_response(
        data=[role.model_dump() for role in roles],
        total=total,
        page=page,
        limit=limit,
        message="Daftar roles berhasil diambil"
    )


@router.get(
    "/{role_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get role by ID",
    description="Mendapatkan detail role berdasarkan ID"
)
async def get_role(
    role_id: int,
    include_permissions: bool = Query(False, description="Include permissions"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get role by ID"""
    check_superuser(current_user)
    
    role_service = RoleService(db)
    role = role_service.get_by_id(role_id, include_permissions=include_permissions)
    
    return success_response(
        data=role.model_dump(),
        message="Data role berhasil diambil"
    )


@router.post(
    "",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create new role",
    description="Membuat role baru"
)
async def create_role(
    role_data: RoleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new role"""
    check_superuser(current_user)
    
    role_service = RoleService(db)
    role = role_service.create(role_data)
    
    return success_response(
        data=role.model_dump(),
        message="Role berhasil dibuat",
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    "/{role_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update role (full update)",
    description="Update semua field role"
)
async def update_role(
    role_id: int,
    role_data: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update role (full update)"""
    check_superuser(current_user)
    
    role_service = RoleService(db)
    role = role_service.update(role_id, role_data)
    
    return success_response(
        data=role.model_dump(),
        message="Role berhasil diupdate"
    )


@router.patch(
    "/{role_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update role (partial update)",
    description="Update sebagian field role"
)
async def patch_role(
    role_id: int,
    role_data: RolePatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Partial update role"""
    check_superuser(current_user)
    
    role_service = RoleService(db)
    role = role_service.patch(role_id, role_data)
    
    return success_response(
        data=role.model_dump(),
        message="Role berhasil diupdate"
    )


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete role",
    description="Menghapus role"
)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    response: Response = None
):
    """Delete role"""
    check_superuser(current_user)
    
    role_service = RoleService(db)
    role_service.delete(role_id)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{role_id}/permissions",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Assign permissions to role",
    description="Assign permissions ke role"
)
async def assign_role_permissions(
    role_id: int,
    permissions_data: AssignPermissionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign permissions to role"""
    check_superuser(current_user)
    
    role_service = RoleService(db)
    role = role_service.assign_permissions(role_id, permissions_data)
    
    return success_response(
        data=role.model_dump(),
        message="Permissions berhasil di-assign ke role"
    )


@router.put(
    "/{role_id}/permissions-crud",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Assign CRUD permissions per page to role",
    description="Assign CRUD permissions per halaman ke role. Setiap halaman bisa diatur CRUD (Create, Read, Update, Delete) secara individual."
)
async def assign_role_permissions_crud(
    role_id: int,
    crud_data: AssignRolePermissionsCRUDRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign CRUD permissions per page ke role"""
    check_superuser(current_user)
    
    try:
        role_service = RoleService(db)
        role = role_service.assign_permissions_crud(role_id, crud_data)
        
        return success_response(
            data=role.model_dump(),
            message="CRUD permissions berhasil di-assign ke role"
        )
    except ValidationError as e:
        # ValidationError sudah di-handle oleh exception handler di main.py
        raise
    except Exception as e:
        # Catch any other exceptions
        from app.utils.response import error_response
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in assign_role_permissions_crud: {str(e)}", exc_info=True)
        return error_response(
            message=f"Gagal menyimpan permissions: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST
        )

