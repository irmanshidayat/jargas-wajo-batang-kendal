from typing import Optional
from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.core.security import get_current_user
from app.models.user.user import User
from app.services.project.project_service import ProjectService
from app.core.exceptions import ForbiddenError


def get_project_id(
    x_project_id: Optional[int] = Header(None, alias="X-Project-ID")
) -> Optional[int]:
    """Dependency untuk mendapatkan project_id dari header"""
    return x_project_id


def get_current_project(
    project_id: Optional[int] = Depends(get_project_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> int:
    """
    Dependency untuk mendapatkan current project yang valid untuk user.
    Project ID sekarang WAJIB untuk semua operasi.
    Raises HTTPException jika project_id tidak ada atau invalid.
    """
    if project_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID harus disertakan dalam header X-Project-ID"
        )
    
    # Verify user has access to this project
    project_service = ProjectService(db)
    if not project_service.user_has_access(current_user.id, project_id):
        raise ForbiddenError(f"User tidak memiliki akses ke project ID {project_id}")
    
    return project_id


def require_project(
    project_id: Optional[int] = Depends(get_current_project)
) -> int:
    """
    Dependency yang require project_id (untuk endpoints yang wajib punya project).
    Raises HTTPException jika project_id tidak ada.
    """
    if project_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID harus disertakan dalam header X-Project-ID"
        )
    return project_id

