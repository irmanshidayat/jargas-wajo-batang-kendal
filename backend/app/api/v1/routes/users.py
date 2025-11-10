from fastapi import APIRouter, Depends, Query, status, Response
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Optional
from app.config.database import get_db
from app.services.user.user_service import UserService
from app.schemas.user.request import (
    UserCreateRequest,
    UserUpdateRequest,
    UserPatchRequest,
    UserPasswordUpdateRequest
)
from app.schemas.user.response import UserResponse, UserListResponse
from app.core.security import get_current_user
from app.models.user.user import User
from app.utils.response import success_response, paginated_response, error_response
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.api.v1.deps import check_superuser

router = APIRouter()


@router.get(
    "",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    description="Mendapatkan daftar semua users dengan pagination"
)
async def get_users(
    page: int = Query(1, ge=1, description="Halaman"),
    limit: int = Query(100, ge=1, le=100, description="Jumlah data per halaman"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users dengan pagination"""
    check_superuser(current_user)
    
    skip = (page - 1) * limit
    filters = {}
    if is_active is not None:
        filters["is_active"] = is_active
    
    user_service = UserService(db)
    users, total = user_service.get_all(skip=skip, limit=limit, filters=filters)
    
    return paginated_response(
        data=[user.model_dump() for user in users],
        total=total,
        page=page,
        limit=limit,
        message="Daftar users berhasil diambil"
    )


@router.get(
    "/{user_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Mendapatkan detail user berdasarkan ID"
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    # Users can view their own profile, superusers can view any profile
    if not current_user.is_superuser and current_user.id != user_id:
        raise ForbiddenError("Anda hanya dapat melihat profil sendiri")
    
    user_service = UserService(db)
    user = user_service.get_by_id(user_id)
    
    return success_response(
        data=user.model_dump(),
        message="Data user berhasil diambil"
    )


@router.post(
    "",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Membuat user baru"
)
async def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new user"""
    check_superuser(current_user)
    
    user_service = UserService(db)
    user = user_service.create(user_data)
    
    return success_response(
        data=user.model_dump(),
        message="User berhasil dibuat",
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    "/{user_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update user (full update)",
    description="Update semua field user"
)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user (full update)"""
    # Users can update their own profile (except superuser status), superusers can update any profile
    if not current_user.is_superuser and current_user.id != user_id:
        raise ForbiddenError("Anda hanya dapat mengupdate profil sendiri")
    
    # Non-superusers cannot change superuser status
    if not current_user.is_superuser and user_data.is_superuser is not None:
        raise ForbiddenError("Tidak dapat mengubah status superuser")
    
    user_service = UserService(db)
    user = user_service.update(user_id, user_data)
    
    return success_response(
        data=user.model_dump(),
        message="User berhasil diupdate"
    )


@router.patch(
    "/{user_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update user (partial update)",
    description="Update sebagian field user"
)
async def patch_user(
    user_id: int,
    user_data: UserPatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Partial update user"""
    # Users can update their own profile (except superuser status), superusers can update any profile
    if not current_user.is_superuser and current_user.id != user_id:
        raise ForbiddenError("Anda hanya dapat mengupdate profil sendiri")
    
    # Non-superusers cannot change superuser status
    if not current_user.is_superuser and user_data.is_superuser is not None:
        raise ForbiddenError("Tidak dapat mengubah status superuser")
    
    user_service = UserService(db)
    user = user_service.patch(user_id, user_data)
    
    return success_response(
        data=user.model_dump(),
        message="User berhasil diupdate"
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Menghapus user"
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    response: Response = None
):
    """Delete user"""
    logger = logging.getLogger(__name__)
    
    try:
        check_superuser(current_user)
        
        # Prevent self-deletion
        if current_user.id == user_id:
            raise ForbiddenError("Tidak dapat menghapus akun sendiri")
        
        user_service = UserService(db)
        user_service.delete(user_id)
        
        # Return 204 No Content
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except (ForbiddenError, NotFoundError, ValidationError) as e:
        # Re-raise custom exceptions untuk ditangani oleh exception handler
        raise
    except IntegrityError as e:
        logger.error(f"Integrity error saat menghapus user ID {user_id}: {str(e)}", exc_info=True)
        db.rollback()
        return error_response(
            message=f"Gagal menghapus user: terdapat constraint database yang dilanggar",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error saat menghapus user ID {user_id}: {str(e)}", exc_info=True)
        db.rollback()
        return error_response(
            message="Terjadi kesalahan pada database saat menghapus user",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Unexpected error saat menghapus user ID {user_id}: {str(e)}", exc_info=True)
        db.rollback()
        return error_response(
            message=f"Gagal menghapus user: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.patch(
    "/{user_id}/password",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update user password",
    description="Mengupdate password user"
)
async def update_user_password(
    user_id: int,
    password_data: UserPasswordUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user password"""
    # Users can only update their own password
    if not current_user.is_superuser and current_user.id != user_id:
        raise ForbiddenError("Anda hanya dapat mengupdate password sendiri")
    
    user_service = UserService(db)
    user_service.update_password(user_id, password_data)
    
    return success_response(
        message="Password berhasil diupdate"
    )

