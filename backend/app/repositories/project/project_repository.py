from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import and_
from app.models.project.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository untuk Project model"""

    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_by_code(self, code: str) -> Optional[Project]:
        """Get project by code"""
        return self.get_by(code=code)

    def get_active_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all active projects - menggunakan get_active() dari base"""
        # Note: Project menggunakan is_active=True (boolean), tapi get_active() di base handle is_active==1 atau None
        # Untuk kompatibilitas, kita tetap gunakan get_active() tapi dengan filter khusus
        return self.get_active(skip=skip, limit=limit)

    def get_projects_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects untuk user tertentu"""
        try:
            from app.models.project.user_project import UserProject
            
            return self.db.query(Project).join(
                UserProject, Project.id == UserProject.project_id
            ).filter(
                and_(
                    UserProject.user_id == user_id,
                    UserProject.is_active == True,
                    Project.is_active == True
                )
            ).offset(skip).limit(limit).all()
        except Exception:
            return []

