"""
Base Service Class
Menyediakan CRUD operations standar untuk mengurangi duplikasi code
"""
from typing import Optional, List, Dict, Any, Generic, TypeVar
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.core.exceptions import NotFoundError, ValidationError

# Type variable for Repository
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[RepositoryType]):
    """
    Base Service class dengan CRUD operations standar
    Mengurangi duplikasi code di service layer
    """

    def __init__(self, repository: RepositoryType, db: Session):
        """
        Initialize base service dengan repository
        
        Args:
            repository: Repository instance untuk entity ini
            db: Database session
        """
        self.repository = repository
        self.db = db
        self.entity_name = self._get_entity_name()

    def _get_entity_name(self) -> str:
        """Get entity name dari model class untuk error messages"""
        model_name = self.repository.model.__name__ if hasattr(self.repository, 'model') else 'Entity'
        # Remove 'Model' suffix jika ada
        if model_name.endswith('Model'):
            model_name = model_name[:-5]
        return model_name

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List, int]:
        """
        Get all active records dengan pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            project_id: Optional project ID untuk filtering
            filters: Additional filters dictionary
            
        Returns:
            Tuple of (list of records, total count)
        """
        # Gunakan get_active jika repository mendukung
        if hasattr(self.repository, 'get_active'):
            items = self.repository.get_active(skip=skip, limit=limit, project_id=project_id, filters=filters)
            total = self.repository.count_active(project_id=project_id, filters=filters) if hasattr(self.repository, 'count_active') else len(items)
        else:
            # Fallback ke get_all dengan filter is_active
            active_filters = filters or {}
            active_filters['is_active'] = 1
            items = self.repository.get_all(skip=skip, limit=limit, project_id=project_id, filters=active_filters)
            total = self.repository.count(project_id=project_id, filters=active_filters)
        
        return items, total

    def get_by_id(self, entity_id: int, project_id: Optional[int] = None):
        """
        Get single record by ID
        
        Args:
            entity_id: ID of the entity
            project_id: Optional project ID untuk filtering
            
        Returns:
            Entity instance
            
        Raises:
            NotFoundError: Jika entity tidak ditemukan
        """
        entity = self.repository.get(entity_id, project_id=project_id)
        if not entity:
            raise NotFoundError(f"{self.entity_name} dengan ID {entity_id} tidak ditemukan")
        return entity

    def create(
        self,
        entity_data: dict,
        project_id: Optional[int] = None,
        validate_project_id: bool = False
    ):
        """
        Create new record
        
        Args:
            entity_data: Dictionary dengan data untuk entity baru
            project_id: Optional project ID
            validate_project_id: Jika True, project_id wajib diisi
            
        Returns:
            Created entity instance
            
        Raises:
            ValidationError: Jika validasi gagal atau create gagal
        """
        if validate_project_id and project_id is None:
            raise ValidationError("Project ID harus disertakan")
        
        if project_id is not None:
            entity_data['project_id'] = project_id
        
        entity = self.repository.create(entity_data)
        if not entity:
            raise ValidationError(f"Gagal membuat {self.entity_name} baru")
        return entity

    def update(
        self,
        entity_id: int,
        entity_data: dict,
        project_id: Optional[int] = None
    ):
        """
        Update existing record
        
        Args:
            entity_id: ID of the entity to update
            entity_data: Dictionary dengan data yang akan diupdate
            project_id: Optional project ID untuk filtering
            
        Returns:
            Updated entity instance
            
        Raises:
            NotFoundError: Jika entity tidak ditemukan
            ValidationError: Jika update gagal
        """
        entity = self.get_by_id(entity_id, project_id=project_id)
        
        updated = self.repository.update(entity_id, entity_data)
        if not updated:
            raise ValidationError(f"Gagal mengupdate {self.entity_name}")
        return updated

    def delete(self, entity_id: int, project_id: Optional[int] = None, soft_delete: bool = True) -> bool:
        """
        Delete record (soft delete by default)
        
        Args:
            entity_id: ID of the entity to delete
            project_id: Optional project ID untuk filtering
            soft_delete: Jika True, set is_active=0, jika False hard delete
            
        Returns:
            True jika berhasil, False jika gagal
            
        Raises:
            NotFoundError: Jika entity tidak ditemukan
        """
        entity = self.get_by_id(entity_id, project_id=project_id)
        
        if soft_delete:
            # Soft delete by setting is_active = 0
            updated = self.repository.update(entity_id, {"is_active": 0})
            return updated is not None
        else:
            # Hard delete
            return self.repository.delete(entity_id)

    def search_by_name(
        self,
        name: str,
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[int] = None,
        name_field: str = "nama"
    ) -> List:
        """
        Search records by name field
        
        Args:
            name: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return
            project_id: Optional project ID untuk filtering
            name_field: Nama field untuk search (default: "nama")
            
        Returns:
            List of matching records
        """
        if hasattr(self.repository, 'search_by_name'):
            return self.repository.search_by_name(name, skip=skip, limit=limit, project_id=project_id)
        else:
            # Fallback: use get_all dengan filter
            filters = {f"{name_field}__like": f"%{name}%"}
            return self.repository.get_all(skip=skip, limit=limit, project_id=project_id, filters=filters)

