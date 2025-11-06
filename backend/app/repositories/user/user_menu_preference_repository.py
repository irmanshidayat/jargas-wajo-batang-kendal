from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user.user_menu_preference import UserMenuPreference
from app.repositories.base import BaseRepository


class UserMenuPreferenceRepository(BaseRepository[UserMenuPreference]):
    """Repository untuk UserMenuPreference model"""

    def __init__(self, db: Session):
        super().__init__(UserMenuPreference, db)

    def get_by_user_and_page(self, user_id: int, page_id: int) -> Optional[UserMenuPreference]:
        """Get preference by user_id and page_id"""
        return self.get_by(user_id=user_id, page_id=page_id)

    def get_by_user_id(self, user_id: int) -> List[UserMenuPreference]:
        """Get all preferences for a user"""
        return self.get_all(filters={'user_id': user_id}, limit=1000)

    def upsert(self, user_id: int, page_id: int, show_in_menu: bool) -> UserMenuPreference:
        """Upsert preference (create if not exists, update if exists)"""
        existing = self.get_by_user_and_page(user_id, page_id)
        
        if existing:
            # Update existing
            return self.update(existing.id, {'show_in_menu': show_in_menu})
        else:
            # Create new
            return self.create({
                'user_id': user_id,
                'page_id': page_id,
                'show_in_menu': show_in_menu
            })

