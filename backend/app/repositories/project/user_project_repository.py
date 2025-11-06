from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import and_
from app.models.project.user_project import UserProject
from app.repositories.base import BaseRepository


class UserProjectRepository(BaseRepository[UserProject]):
    """Repository untuk UserProject model"""

    def __init__(self, db: Session):
        super().__init__(UserProject, db)

    def get_by_user_and_project(self, user_id: int, project_id: int) -> Optional[UserProject]:
        """Get UserProject by user_id dan project_id"""
        try:
            return self.db.query(self.model).filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.project_id == project_id
                )
            ).first()
        except Exception:
            return None

    def get_user_projects(self, user_id: int) -> List[UserProject]:
        """Get all UserProject untuk user tertentu"""
        try:
            return self.db.query(self.model).filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.is_active == True
                )
            ).all()
        except Exception:
            return []

    def get_project_users(self, project_id: int) -> List[UserProject]:
        """Get all UserProject untuk project tertentu"""
        try:
            return self.db.query(self.model).filter(
                and_(
                    self.model.project_id == project_id,
                    self.model.is_active == True
                )
            ).all()
        except Exception:
            return []

    def user_has_access(self, user_id: int, project_id: int) -> bool:
        """Check apakah user punya akses ke project"""
        user_project = self.get_by_user_and_project(user_id, project_id)
        if not user_project:
            return False
        return user_project.is_active

    def user_is_owner(self, user_id: int, project_id: int) -> bool:
        """Check apakah user adalah owner project"""
        user_project = self.get_by_user_and_project(user_id, project_id)
        if not user_project:
            return False
        return user_project.is_active and user_project.is_owner

