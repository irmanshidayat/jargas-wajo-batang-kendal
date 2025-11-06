from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from app.config.settings import settings
from app.repositories.user.user_repository import UserRepository
from app.services.user.permission_service import PermissionService
from app.schemas.auth.request import LoginRequest
from app.schemas.auth.response import LoginResponse, UserResponse, RoleInfo, PermissionInfo
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import verify_password


class AuthService:
    """Service untuk authentication logic"""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def authenticate_user(self, login_data: LoginRequest) -> LoginResponse:
        """Authenticate user dan return token"""
        from sqlalchemy.orm import joinedload
        from app.models.user.user import User
        
        user = self.db.query(User).options(
            joinedload(User.role_obj)
        ).filter(User.email == login_data.email).first()
        
        if not user:
            raise UnauthorizedError("Email atau password salah")
        
        if not user.is_active:
            raise ForbiddenError("User tidak aktif")
        
        if not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedError("Email atau password salah")
        
        # Create token
        access_token = self.create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Get user permissions
        permission_service = PermissionService(self.db)
        try:
            permissions = permission_service.get_user_permissions(user.id)
            permission_infos = [
                PermissionInfo(
                    id=p.id,
                    page_id=p.page_id,
                    page_name=p.page_name,
                    page_path=p.page_path,
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
        
        return LoginResponse(
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

    def get_current_user(self, token: str):
        """Get current user from token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if email is None or user_id is None:
                raise UnauthorizedError("Token tidak valid")
        except JWTError:
            raise UnauthorizedError("Token tidak valid")
        
        user = self.user_repo.get(user_id)
        if user is None:
            raise UnauthorizedError("User tidak ditemukan")
        
        return user

    def get_user_profile(self, user_id: int) -> UserResponse:
        """Get user profile with permissions (untuk refresh permissions)"""
        from sqlalchemy.orm import joinedload
        from app.models.user.user import User
        
        user = self.db.query(User).options(
            joinedload(User.role_obj)
        ).filter(User.id == user_id).first()
        
        if not user:
            raise UnauthorizedError("User tidak ditemukan")
        
        if not user.is_active:
            raise ForbiddenError("User tidak aktif")
        
        # Get user permissions
        permission_service = PermissionService(self.db)
        try:
            permissions = permission_service.get_user_permissions(user.id)
            permission_infos = [
                PermissionInfo(
                    id=p.id,
                    page_id=p.page_id,
                    page_name=p.page_name,
                    page_path=p.page_path,
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
        
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            role=role_info,
            permissions=permission_infos
        )