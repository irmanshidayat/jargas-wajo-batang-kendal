from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.auth.auth_service import AuthService
from app.schemas.auth.request import LoginRequest
from app.schemas.auth.response import LoginResponse, UserResponse
from app.core.security import get_current_user
from app.models.user.user import User
from app.utils.response import success_response

router = APIRouter()


@router.post(
    "/login",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Login user dan mendapatkan access token"
)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login endpoint - authenticate user dan return token"""
    auth_service = AuthService(db)
    result = auth_service.authenticate_user(login_data)
    
    return success_response(
        data={
            "token": result.token,
            "user": result.user.model_dump()
        },
        message="Login berhasil"
    )


@router.post(
    "/logout",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout user (token invalidasi dilakukan di client)"
)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout endpoint"""
    # Note: JWT token biasanya stateless, logout dilakukan di client
    # Jika perlu token blacklist, bisa ditambahkan di sini
    return success_response(
        message="Logout berhasil"
    )


@router.get(
    "/profile",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Mendapatkan profil user yang sedang login dengan permissions lengkap"
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile with permissions"""
    auth_service = AuthService(db)
    user_response = auth_service.get_user_profile(current_user.id)
    
    return success_response(
        data=user_response.model_dump(),
        message="Data profil berhasil diambil"
    )


@router.get(
    "/projects",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get user projects",
    description="Mendapatkan daftar project yang dapat diakses oleh user yang sedang login"
)
async def get_user_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get projects untuk current user (untuk project selection setelah login)"""
    from app.services.project.project_service import ProjectService
    
    project_service = ProjectService(db)
    projects, total = project_service.get_user_projects(current_user.id, skip=0, limit=1000)
    
    return success_response(
        data={
            "projects": [p.model_dump() for p in projects],
            "total": total
        },
        message="Daftar project berhasil diambil"
    )