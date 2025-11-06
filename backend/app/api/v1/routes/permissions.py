from fastapi import APIRouter, Depends, Query, status, Response
from sqlalchemy.orm import Session
from typing import Optional
import logging
from app.config.database import get_db
from app.services.user.permission_service import PageService, PermissionService
from app.services.user.user_menu_preference_service import UserMenuPreferenceService
from app.schemas.user.permission_request import (
    PageCreateRequest,
    PageUpdateRequest,
    PermissionCreateRequest,
    PermissionUpdateRequest,
    AssignUserPermissionsRequest
)
from app.schemas.user.user_menu_preference_request import (
    UserMenuPreferenceCreateRequest,
    UserMenuPreferenceUpdateRequest,
    UserMenuPreferenceBulkRequest
)
from app.core.security import get_current_user
from app.models.user.user import User
from app.utils.response import success_response, paginated_response, error_response
from app.core.exceptions import ForbiddenError
from app.api.v1.deps import check_superuser

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== PAGE ENDPOINTS ==========

@router.get(
    "/pages",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get all pages",
    description="Mendapatkan daftar semua pages"
)
async def get_pages(
    page: int = Query(1, ge=1, description="Halaman"),
    limit: int = Query(100, ge=1, le=100, description="Jumlah data per halaman"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pages dengan pagination"""
    check_superuser(current_user)
    
    skip = (page - 1) * limit
    page_service = PageService(db)
    pages, total = page_service.get_all(skip=skip, limit=limit)
    
    return paginated_response(
        data=[p.model_dump() for p in pages],
        total=total,
        page=page,
        limit=limit,
        message="Daftar pages berhasil diambil"
    )


@router.get(
    "/pages/{page_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get page by ID",
    description="Mendapatkan detail page berdasarkan ID"
)
async def get_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get page by ID"""
    check_superuser(current_user)
    
    page_service = PageService(db)
    page = page_service.get_by_id(page_id)
    
    return success_response(
        data=page.model_dump(),
        message="Data page berhasil diambil"
    )


@router.post(
    "/pages",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create new page",
    description="Membuat page baru"
)
async def create_page(
    page_data: PageCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new page"""
    check_superuser(current_user)
    
    page_service = PageService(db)
    page = page_service.create(page_data)
    
    return success_response(
        data=page.model_dump(),
        message="Page berhasil dibuat",
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    "/pages/{page_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update page",
    description="Update page"
)
async def update_page(
    page_id: int,
    page_data: PageUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update page"""
    check_superuser(current_user)
    
    page_service = PageService(db)
    page = page_service.update(page_id, page_data)
    
    return success_response(
        data=page.model_dump(),
        message="Page berhasil diupdate"
    )


@router.delete(
    "/pages/{page_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete page",
    description="Menghapus page"
)
async def delete_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    response: Response = None
):
    """Delete page"""
    check_superuser(current_user)
    
    page_service = PageService(db)
    page_service.delete(page_id)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ========== PERMISSION ENDPOINTS ==========

@router.get(
    "",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get all permissions",
    description="Mendapatkan daftar semua permissions"
)
async def get_permissions(
    page: int = Query(1, ge=1, description="Halaman"),
    limit: int = Query(100, ge=1, le=100, description="Jumlah data per halaman"),
    page_id: Optional[int] = Query(None, description="Filter by page ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all permissions dengan pagination"""
    check_superuser(current_user)
    
    skip = (page - 1) * limit
    permission_service = PermissionService(db)
    
    if page_id:
        permissions = permission_service.get_by_page_id(page_id)
        return success_response(
            data=[p.model_dump() for p in permissions],
            message="Daftar permissions berhasil diambil"
        )
    else:
        permissions, total = permission_service.get_all(skip=skip, limit=limit)
        return paginated_response(
            data=[p.model_dump() for p in permissions],
            total=total,
            page=page,
            limit=limit,
            message="Daftar permissions berhasil diambil"
        )


@router.get(
    "/{permission_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get permission by ID",
    description="Mendapatkan detail permission berdasarkan ID"
)
async def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get permission by ID"""
    check_superuser(current_user)
    
    permission_service = PermissionService(db)
    permission = permission_service.get_by_id(permission_id)
    
    return success_response(
        data=permission.model_dump(),
        message="Data permission berhasil diambil"
    )


@router.post(
    "",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create new permission",
    description="Membuat permission baru"
)
async def create_permission(
    permission_data: PermissionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new permission"""
    check_superuser(current_user)
    
    permission_service = PermissionService(db)
    permission = permission_service.create(permission_data)
    
    return success_response(
        data=permission.model_dump(),
        message="Permission berhasil dibuat",
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    "/{permission_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update permission",
    description="Update permission"
)
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update permission"""
    check_superuser(current_user)
    
    permission_service = PermissionService(db)
    permission = permission_service.update(permission_id, permission_data)
    
    return success_response(
        data=permission.model_dump(),
        message="Permission berhasil diupdate"
    )


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete permission",
    description="Menghapus permission"
)
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    response: Response = None
):
    """Delete permission"""
    check_superuser(current_user)
    
    permission_service = PermissionService(db)
    permission_service.delete(permission_id)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/user/{user_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get user permissions",
    description="Mendapatkan semua permissions untuk user (role + override)"
)
async def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user permissions"""
    check_superuser(current_user)
    
    permission_service = PermissionService(db)
    permissions = permission_service.get_user_permissions(user_id)
    
    return success_response(
        data=[p.model_dump() for p in permissions],
        message="Daftar permissions user berhasil diambil"
    )


@router.post(
    "/user/{user_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Assign permissions to user",
    description="Assign permissions ke user (override)"
)
async def assign_user_permissions(
    user_id: int,
    permissions_data: AssignUserPermissionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign permissions to user"""
    check_superuser(current_user)
    
    permission_service = PermissionService(db)
    permission_service.assign_user_permissions(user_id, permissions_data)
    
    return success_response(
        message="Permissions berhasil di-assign ke user"
    )


@router.post(
    "/generate-pages",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Generate pages and permissions",
    description="Manual trigger untuk generate pages dan permissions dari configuration (hanya superuser)"
)
async def generate_pages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manual trigger untuk generate pages dan permissions"""
    check_superuser(current_user)
    
    try:
        from app.config.pages_config import PAGES_CONFIG
        from app.services.user.page_generator_service import PageGeneratorService
        
        generator = PageGeneratorService(db)
        stats = generator.generate_pages_from_config(PAGES_CONFIG)
        
        return success_response(
            data={
                "created": stats['created'],
                "updated": stats['updated'],
                "skipped": stats['skipped'],
                "total": stats['created'] + stats['updated'] + stats['skipped']
            },
            message=f"Pages generation completed: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped"
        )
    except Exception as e:
        logger.error(f"Error generating pages: {str(e)}", exc_info=True)
        return error_response(
            message=f"Error generating pages: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========== USER MENU PREFERENCES ENDPOINTS ==========

@router.get(
    "/user/{user_id}/menu-preferences",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get user menu preferences",
    description="Mendapatkan semua menu preferences untuk user"
)
async def get_user_menu_preferences(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user menu preferences"""
    # User hanya bisa akses preferences sendiri, atau superuser bisa akses semua
    if not current_user.is_superuser and current_user.id != user_id:
        raise ForbiddenError("Anda tidak memiliki akses untuk melihat preferences user ini")
    
    preference_service = UserMenuPreferenceService(db)
    preferences = preference_service.get_user_preferences(user_id)
    
    return success_response(
        data=[p.model_dump() for p in preferences],
        message="Daftar menu preferences berhasil diambil"
    )


@router.get(
    "/user/{user_id}/menu-preferences/{page_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get user menu preference for specific page",
    description="Mendapatkan menu preference untuk user dan page tertentu"
)
async def get_user_menu_preference(
    user_id: int,
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user menu preference for specific page"""
    # User hanya bisa akses preferences sendiri, atau superuser bisa akses semua
    if not current_user.is_superuser and current_user.id != user_id:
        raise ForbiddenError("Anda tidak memiliki akses untuk melihat preferences user ini")
    
    preference_service = UserMenuPreferenceService(db)
    preference = preference_service.get_user_preference(user_id, page_id)
    
    return success_response(
        data=preference.model_dump(),
        message="Menu preference berhasil diambil"
    )


@router.post(
    "/user/{user_id}/menu-preferences",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Create or update user menu preference",
    description="Membuat atau mengupdate menu preference untuk user"
)
async def create_or_update_user_menu_preference(
    user_id: int,
    preference_data: UserMenuPreferenceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update user menu preference"""
    # User hanya bisa update preferences sendiri, atau superuser bisa update semua
    if not current_user.is_superuser and current_user.id != user_id:
        raise ForbiddenError("Anda tidak memiliki akses untuk mengupdate preferences user ini")
    
    preference_service = UserMenuPreferenceService(db)
    preference = preference_service.create_or_update_preference(user_id, preference_data)
    
    return success_response(
        data=preference.model_dump(),
        message="Menu preference berhasil disimpan"
    )


@router.put(
    "/user/{user_id}/menu-preferences/bulk",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Bulk update user menu preferences",
    description="Bulk update menu preferences untuk user"
)
async def bulk_update_user_menu_preferences(
    user_id: int,
    bulk_data: UserMenuPreferenceBulkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update user menu preferences"""
    # User hanya bisa update preferences sendiri, atau superuser bisa update semua
    if not current_user.is_superuser and current_user.id != user_id:
        raise ForbiddenError("Anda tidak memiliki akses untuk mengupdate preferences user ini")
    
    preference_service = UserMenuPreferenceService(db)
    preferences = preference_service.bulk_update_preferences(user_id, bulk_data)
    
    return success_response(
        data=[p.model_dump() for p in preferences],
        message="Menu preferences berhasil diupdate"
    )


@router.delete(
    "/user/{user_id}/menu-preferences/{page_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user menu preference",
    description="Menghapus menu preference untuk user dan page tertentu"
)
async def delete_user_menu_preference(
    user_id: int,
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    response: Response = None
):
    """Delete user menu preference"""
    # User hanya bisa delete preferences sendiri, atau superuser bisa delete semua
    if not current_user.is_superuser and current_user.id != user_id:
        raise ForbiddenError("Anda tidak memiliki akses untuk menghapus preferences user ini")
    
    preference_service = UserMenuPreferenceService(db)
    preference_service.delete_preference(user_id, page_id)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

