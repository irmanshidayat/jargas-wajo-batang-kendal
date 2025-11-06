from sqlalchemy.orm import Session
from app.config.database import get_db
from app.core.security import get_current_user
from app.models.user.user import User


def get_db_session() -> Session:
    """Dependency untuk database session"""
    return next(get_db())


def get_authenticated_user() -> User:
    """Dependency untuk authenticated user"""
    return get_current_user()
