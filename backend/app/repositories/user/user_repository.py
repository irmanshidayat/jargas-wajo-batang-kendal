from sqlalchemy.orm import Session
from typing import Optional
from app.models.user.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository untuk User model dengan custom methods"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.get_by(email=email)

    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        user = self.get_by_email(email)
        return user is not None
