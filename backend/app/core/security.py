from jose import JWTError, jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import bcrypt
from app.config.database import get_db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True
)


def get_password_hash(password: str) -> str:
    """Hash password menggunakan bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password dengan hash"""
    try:
        # Cek jika hash adalah bcrypt format
        if hashed_password.startswith('$2'):
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        # Fallback untuk hash lama (jika ada)
        return False
    except Exception:
        return False


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Dependency untuk get current authenticated user"""
    # Lazy import untuk menghindari circular import
    from app.services.auth.auth_service import AuthService
    auth_service = AuthService(db)
    return auth_service.get_current_user(token)
