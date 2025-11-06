from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.core.security import get_current_user
from app.models.user.user import User
from app.services.project.project_service import ProjectService
from app.schemas.project.request import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    UserProjectCreateRequest,
    ProjectSelectRequest
)
from app.schemas.project.response import ProjectResponse, ProjectWithUserResponse
from app.utils.response import success_response, paginated_response
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError

router = APIRouter()


@router.post(
    "/projects",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    description="Membuat project baru (user yang membuat akan menjadi owner)"
)
async def create_project(
    project_data: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new project"""
    project_service = ProjectService(db)
    project = project_service.create(project_data, current_user.id)
    
    return success_response(
        data=project.model_dump(),
        message="Project berhasil dibuat"
    )


@router.get(
    "/projects",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get all projects",
    description="Mendapatkan daftar semua project aktif"
)
async def get_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all projects with pagination"""
    project_service = ProjectService(db)
    skip = (page - 1) * limit
    projects, total = project_service.get_all(skip=skip, limit=limit)
    
    return paginated_response(
        data=[p.model_dump() for p in projects],
        total=total,
        page=page,
        limit=limit,
        message="Daftar project berhasil diambil"
    )


@router.get(
    "/projects/my-projects",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get my projects",
    description="Mendapatkan daftar project yang dimiliki user yang sedang login"
)
async def get_my_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get projects untuk current user"""
    project_service = ProjectService(db)
    skip = (page - 1) * limit
    projects, total = project_service.get_user_projects(current_user.id, skip=skip, limit=limit)
    
    return paginated_response(
        data=[p.model_dump() for p in projects],
        total=total,
        page=page,
        limit=limit,
        message="Daftar project berhasil diambil"
    )


@router.get(
    "/projects/{project_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get project by ID",
    description="Mendapatkan detail project berdasarkan ID"
)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project by ID"""
    project_service = ProjectService(db)
    
    # Check if user has access
    if not project_service.user_has_access(current_user.id, project_id):
        raise ForbiddenError("Anda tidak memiliki akses ke project ini")
    
    project = project_service.get_by_id(project_id)
    
    return success_response(
        data=project.model_dump(),
        message="Detail project berhasil diambil"
    )


@router.put(
    "/projects/{project_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Update project",
    description="Update project (hanya owner yang bisa)"
)
async def update_project(
    project_id: int,
    project_data: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update project"""
    project_service = ProjectService(db)
    project = project_service.update(project_id, project_data, current_user.id)
    
    return success_response(
        data=project.model_dump(),
        message="Project berhasil diupdate"
    )


@router.delete(
    "/projects/{project_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Delete project",
    description="Soft delete project (hanya owner yang bisa)"
)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete project"""
    project_service = ProjectService(db)
    project_service.delete(project_id, current_user.id)
    
    return success_response(
        message="Project berhasil dihapus"
    )


@router.post(
    "/projects/{project_id}/assign-user",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Assign user to project",
    description="Assign user ke project (hanya owner yang bisa)"
)
async def assign_user_to_project(
    project_id: int,
    user_project_data: UserProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign user to project"""
    # Ensure project_id from path matches request body
    if user_project_data.project_id != project_id:
        raise ValidationError("Project ID tidak sesuai")
    
    project_service = ProjectService(db)
    project_service.assign_user_to_project(user_project_data, current_user.id)
    
    return success_response(
        message="User berhasil ditambahkan ke project"
    )

