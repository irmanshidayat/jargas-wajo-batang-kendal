"""
Service untuk handle business logic UserMenuPreference
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.repositories.user.user_menu_preference_repository import UserMenuPreferenceRepository
from app.repositories.user.permission_repository import PageRepository
from app.schemas.user.user_menu_preference_request import (
    UserMenuPreferenceCreateRequest,
    UserMenuPreferenceUpdateRequest,
    UserMenuPreferenceBulkRequest
)
from app.schemas.user.user_menu_preference_response import (
    UserMenuPreferenceResponse,
    UserMenuPreferenceListResponse
)
from app.core.exceptions import NotFoundError, ValidationError


class UserMenuPreferenceService:
    """Service untuk handle business logic UserMenuPreference"""

    def __init__(self, db: Session):
        self.pref_repo = UserMenuPreferenceRepository(db)
        self.page_repo = PageRepository(db)
        self.db = db

    def get_user_preferences(self, user_id: int) -> List[UserMenuPreferenceListResponse]:
        """Get all menu preferences for a user"""
        preferences = self.pref_repo.get_by_user_id(user_id)
        return [UserMenuPreferenceListResponse.model_validate(pref) for pref in preferences]

    def get_user_preference(self, user_id: int, page_id: int) -> UserMenuPreferenceResponse:
        """Get specific preference for user and page"""
        preference = self.pref_repo.get_by_user_and_page(user_id, page_id)
        
        if not preference:
            # Return default (show_in_menu = True) if not found
            return UserMenuPreferenceResponse(
                id=0,
                user_id=user_id,
                page_id=page_id,
                show_in_menu=True,
                created_at=None,
                updated_at=None
            )
        
        return UserMenuPreferenceResponse.model_validate(preference)

    def create_or_update_preference(
        self,
        user_id: int,
        preference_data: UserMenuPreferenceCreateRequest
    ) -> UserMenuPreferenceResponse:
        """Create or update preference"""
        # Validate page exists
        page = self.page_repo.get(preference_data.page_id)
        if not page:
            raise NotFoundError(f"Page dengan ID {preference_data.page_id} tidak ditemukan")
        
        # Upsert preference
        preference = self.pref_repo.upsert(
            user_id=user_id,
            page_id=preference_data.page_id,
            show_in_menu=preference_data.show_in_menu
        )
        
        return UserMenuPreferenceResponse.model_validate(preference)

    def bulk_update_preferences(
        self,
        user_id: int,
        bulk_data: UserMenuPreferenceBulkRequest
    ) -> List[UserMenuPreferenceResponse]:
        """Bulk update preferences for a user"""
        results = []
        
        for pref_data in bulk_data.preferences:
            if not isinstance(pref_data, dict) or 'page_id' not in pref_data:
                continue
            
            page_id = pref_data['page_id']
            show_in_menu = pref_data.get('show_in_menu', True)
            
            # Validate page exists
            page = self.page_repo.get(page_id)
            if not page:
                continue
            
            # Upsert preference
            preference = self.pref_repo.upsert(
                user_id=user_id,
                page_id=page_id,
                show_in_menu=show_in_menu
            )
            
            results.append(UserMenuPreferenceResponse.model_validate(preference))
        
        self.db.commit()
        return results

    def delete_preference(self, user_id: int, page_id: int) -> bool:
        """Delete preference"""
        preference = self.pref_repo.get_by_user_and_page(user_id, page_id)
        if not preference:
            return False
        
        result = self.pref_repo.delete(preference.id)
        return result

    def get_user_preferences_map(self, user_id: int) -> Dict[int, bool]:
        """Get user preferences as a map of page_id -> show_in_menu"""
        preferences = self.pref_repo.get_by_user_id(user_id)
        return {pref.page_id: pref.show_in_menu for pref in preferences}

