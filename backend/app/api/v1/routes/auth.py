from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.auth.auth_service import AuthService
from app.services.user.user_service import UserService
from app.repositories.user.user_repository import UserRepository
from app.repositories.user.role_repository import RoleRepository
from app.schemas.auth.request import LoginRequest, RegisterAdminRequest
from app.schemas.auth.response import LoginResponse, UserResponse, RoleInfo, PermissionInfo
from app.core.security import get_current_user, get_password_hash
from app.models.user.user import User, UserRole
from app.utils.response import success_response
from app.core.exceptions import ValidationError

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


@router.post(
    "/register-admin",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Register admin",
    description="Mendaftarkan akun admin baru (public endpoint, tidak perlu authentication)"
)
async def register_admin(
    register_data: RegisterAdminRequest,
    db: Session = Depends(get_db)
):
    """Register admin endpoint - create admin user dan return token untuk auto-login"""
    from sqlalchemy.orm import joinedload
    from app.services.user.permission_service import PermissionService
    
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    auth_service = AuthService(db)
    
    # Validasi email unik
    if user_repo.email_exists(register_data.email):
        raise ValidationError(f"Email {register_data.email} sudah terdaftar")
    
    # Cari role admin dari database (jika ada)
    admin_role = role_repo.get_by_name("admin")
    role_id = admin_role.id if admin_role else None
    
    # Hash password
    password_hash = get_password_hash(register_data.password)
    
    # Create user data dict
    user_dict = {
        "email": register_data.email,
        "name": register_data.name,
        "password_hash": password_hash,
        "role": UserRole.ADMIN,
        "role_id": role_id,
        "is_active": True,
        "is_superuser": True,
        "created_by": None,  # Admin pertama tidak punya created_by
    }
    
    # Create user
    user = user_repo.create(user_dict)
    if not user:
        raise ValidationError("Gagal membuat akun admin")
    
    # Reload user dengan role_obj untuk mendapatkan role info
    user = db.query(User).options(joinedload(User.role_obj)).filter(User.id == user.id).first()
    
    # Generate token
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # Get user permissions
    permission_service = PermissionService(db)
    try:
        permissions = permission_service.get_user_permissions(user.id)
        permission_infos = [
            PermissionInfo(
                id=p.id,
                page_id=p.page_id,
                page_name=p.page_name,
                page_path=p.page_path,
                display_name=p.display_name,
                can_create=p.can_create,
                can_read=p.can_read,
                can_update=p.can_update,
                can_delete=p.can_delete,
            )
            for p in permissions
        ]
    except Exception:
        permission_infos = []
    
    # Build role info
    role_info = None
    if user.role_obj:
        role_info = RoleInfo(
            id=user.role_obj.id,
            name=user.role_obj.name,
            description=user.role_obj.description
        )
    
    # Build LoginResponse
    login_response = LoginResponse(
        token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            role=role_info,
            permissions=permission_infos
        )
    )
    
    return success_response(
        data={
            "token": login_response.token,
            "user": login_response.user.model_dump()
        },
        message="Akun admin berhasil dibuat",
        status_code=status.HTTP_201_CREATED
    )