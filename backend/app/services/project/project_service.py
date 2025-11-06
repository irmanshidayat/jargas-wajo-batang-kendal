from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.project import ProjectRepository, UserProjectRepository
from app.services.base import BaseService
from app.schemas.project.request import ProjectCreateRequest, ProjectUpdateRequest, UserProjectCreateRequest
from app.schemas.project.response import ProjectResponse, ProjectWithUserResponse
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError
from app.utils.helpers import sanitize_dict


class ProjectService(BaseService[ProjectRepository]):
    """
    Service untuk handle business logic Project
    Menggunakan BaseService untuk CRUD operations standar
    Memiliki logika khusus untuk owner validation dan user assignment
    """

    def __init__(self, db: Session):
        repository = ProjectRepository(db)
        super().__init__(repository, db)
        self.user_project_repo = UserProjectRepository(db)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ProjectResponse], int]:
        """Get all projects with pagination - menggunakan BaseService.get_all()"""
        projects, total = super().get_all(skip=skip, limit=limit)
        return [ProjectResponse.model_validate(p) for p in projects], total

    def get_by_id(self, project_id: int) -> ProjectResponse:
        """Get project by ID - menggunakan BaseService.get_by_id()"""
        project = super().get_by_id(project_id)
        return ProjectResponse.model_validate(project)

    def get_user_projects(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ProjectWithUserResponse], int]:
        """Get all projects untuk user tertentu dengan info apakah user adalah owner"""
        projects = self.repository.get_projects_by_user(user_id, skip=skip, limit=limit)
        
        result = []
        for project in projects:
            is_owner = self.user_project_repo.user_is_owner(user_id, project.id)
            project_dict = {
                "id": project.id,
                "name": project.name,
                "code": project.code,
                "description": project.description,
                "is_active": project.is_active,
                "is_owner": is_owner,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
            }
            result.append(ProjectWithUserResponse.model_validate(project_dict))
        
        # Count total
        from app.models.project.user_project import UserProject
        total = self.db.query(UserProject).filter(
            UserProject.user_id == user_id,
            UserProject.is_active == True
        ).count()
        
        return result, total

    def create(self, project_data: ProjectCreateRequest, creator_user_id: int) -> ProjectResponse:
        """Create new project dan assign creator sebagai owner"""
        # Check if code already exists (if provided)
        if project_data.code:
            existing = self.repository.get_by_code(project_data.code)
            if existing:
                raise ValidationError(f"Project dengan kode {project_data.code} sudah ada")
        
        # Create project
        project_dict = {
            "name": project_data.name,
            "code": project_data.code,
            "description": project_data.description,
            "is_active": True,
        }
        
        project = self.repository.create(project_dict)
        if not project:
            raise ValidationError("Gagal membuat project baru")
        
        # Assign creator sebagai owner
        user_project_dict = {
            "user_id": creator_user_id,
            "project_id": project.id,
            "is_active": True,
            "is_owner": True,
        }
        self.user_project_repo.create(user_project_dict)
        
        return self.get_by_id(project.id)

    def update(
        self,
        project_id: int,
        project_data: ProjectUpdateRequest,
        user_id: int
    ) -> ProjectResponse:
        """
        Update project (hanya owner yang bisa)
        Validasi khusus: check owner permission dan duplicate code
        """
        # Check if user is owner
        if not self.user_project_repo.user_is_owner(user_id, project_id):
            raise ForbiddenError("Hanya owner project yang dapat mengupdate project")
        
        # Get existing project untuk check perubahan code
        project = super().get_by_id(project_id)
        
        # Check if code already exists (if changed)
        if project_data.code and project_data.code != project.code:
            existing = self.repository.get_by_code(project_data.code)
            if existing:
                raise ValidationError(f"Project dengan kode {project_data.code} sudah ada")
        
        # Prepare update data
        update_data = sanitize_dict(project_data.model_dump(exclude_unset=True))
        
        # Gunakan BaseService.update()
        updated_project = super().update(project_id, update_data)
        return ProjectResponse.model_validate(updated_project)

    def delete(self, project_id: int, user_id: int) -> bool:
        """
        Soft delete project (hanya owner yang bisa)
        Validasi khusus: check owner permission
        """
        # Check if user is owner
        if not self.user_project_repo.user_is_owner(user_id, project_id):
            raise ForbiddenError("Hanya owner project yang dapat menghapus project")
        
        # Soft delete menggunakan BaseService.delete()
        return super().delete(project_id, soft_delete=True)

    def assign_user_to_project(
        self,
        user_project_data: UserProjectCreateRequest,
        assigner_user_id: int
    ) -> bool:
        """Assign user ke project (hanya owner yang bisa)"""
        # Check if project exists
        project = self.repository.get(user_project_data.project_id)
        if not project:
            raise NotFoundError(f"Project dengan ID {user_project_data.project_id} tidak ditemukan")
        
        # Check if assigner is owner
        if not self.user_project_repo.user_is_owner(assigner_user_id, user_project_data.project_id):
            raise ForbiddenError("Hanya owner project yang dapat assign user ke project")
        
        # Check if user already assigned
        existing = self.user_project_repo.get_by_user_and_project(
            user_project_data.user_id,
            user_project_data.project_id
        )
        if existing:
            # Update existing assignment
            self.user_project_repo.update(existing.id, {
                "is_active": True,
                "is_owner": user_project_data.is_owner
            })
        else:
            # Create new assignment
            user_project_dict = {
                "user_id": user_project_data.user_id,
                "project_id": user_project_data.project_id,
                "is_active": True,
                "is_owner": user_project_data.is_owner,
            }
            self.user_project_repo.create(user_project_dict)
        
        return True

    def user_has_access(self, user_id: int, project_id: int) -> bool:
        """Check apakah user punya akses ke project"""
        return self.user_project_repo.user_has_access(user_id, project_id)

    def user_is_owner(self, user_id: int, project_id: int) -> bool:
        """Check apakah user adalah owner project"""
        return self.user_project_repo.user_is_owner(user_id, project_id)

