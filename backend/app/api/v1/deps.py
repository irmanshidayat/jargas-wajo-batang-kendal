"""
Common dependencies untuk API routes
"""
from fastapi import Depends
from app.core.security import get_current_user
from app.models.user.user import User
from app.core.exceptions import ForbiddenError


def check_superuser(current_user: User) -> None:
    """
    Helper function untuk check apakah current user adalah superuser
    Raises ForbiddenError jika bukan superuser
    
    Usage:
        current_user: User = Depends(get_current_user)
        check_superuser(current_user)
    """
    if not current_user.is_superuser:
        raise ForbiddenError("Hanya superuser yang dapat mengakses endpoint ini")


def check_superuser_depends(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency untuk check apakah current user adalah superuser
    Raises ForbiddenError jika bukan superuser
    
    Usage:
        current_user: User = Depends(check_superuser_depends)
    """
    if not current_user.is_superuser:
        raise ForbiddenError("Hanya superuser yang dapat mengakses endpoint ini")
    return current_user

