from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.base import BaseModel
import logging

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository class dengan CRUD operations"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
        self.logger = logging.getLogger(__name__)

    def get(self, id: int, project_id: Optional[int] = None) -> Optional[ModelType]:
        """Get single record by ID"""
        try:
            query = self.db.query(self.model).filter(self.model.id == id)
            
            # Auto-filter by project_id if model has project_id column and project_id is provided
            if project_id is not None and hasattr(self.model, 'project_id'):
                query = query.filter(self.model.project_id == project_id)
            
            return query.first()
        except SQLAlchemyError:
            return None

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        project_id: Optional[int] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filters"""
        try:
            query = self.db.query(self.model)
            
            # Auto-filter by project_id if model has project_id column and project_id is provided
            if project_id is not None and hasattr(self.model, 'project_id'):
                query = query.filter(self.model.project_id == project_id)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError:
            return []

    def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get single record by field(s)"""
        try:
            return self.db.query(self.model).filter_by(**kwargs).first()
        except SQLAlchemyError:
            return None

    def create(self, obj_data: Dict[str, Any]) -> Optional[ModelType]:
        """Create new record"""
        try:
            self.logger.debug(f"Creating {self.model.__name__} with data keys: {list(obj_data.keys())}")
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            # Refresh bisa gagal bila skema DB belum sepenuhnya sinkron.
            # Jangan gagalkan operasi create jika refresh gagal.
            try:
                self.db.refresh(db_obj)
            except SQLAlchemyError:
                pass
            self.logger.debug(f"Successfully created {self.model.__name__} with ID: {getattr(db_obj, 'id', 'N/A')}")
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            self.logger.error(
                f"Integrity error creating {self.model.__name__}: {str(e)}. "
                f"Data keys: {list(obj_data.keys())}",
                exc_info=True
            )
            # Re-raise with original error for upstream handlers to process
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"SQLAlchemy error creating {self.model.__name__}: {str(e)}", exc_info=True)
            raise e

    def update(self, id: int, obj_data: Dict[str, Any]) -> Optional[ModelType]:
        """Update existing record"""
        try:
            db_obj = self.get(id)
            if not db_obj:
                return None
            
            for key, value in obj_data.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete(self, id: int) -> bool:
        """Delete record by ID"""
        try:
            db_obj = self.get(id)
            if not db_obj:
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def count(self, filters: Optional[Dict[str, Any]] = None, project_id: Optional[int] = None) -> int:
        """Count records with optional filters"""
        try:
            query = self.db.query(self.model)
            
            # Auto-filter by project_id if model has project_id column and project_id is provided
            if project_id is not None and hasattr(self.model, 'project_id'):
                query = query.filter(self.model.project_id == project_id)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            return query.count()
        except SQLAlchemyError:
            return 0

    def get_active(
        self,
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get all active records (is_active == 1 or None)
        Best practice: centralized method untuk get active records
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            project_id: Optional project ID untuk filtering
            filters: Additional filters dictionary
            
        Returns:
            List of active records
        """
        try:
            from sqlalchemy import or_
            
            query = self.db.query(self.model)
            
            # Filter by is_active (handle both int 1 and boolean True)
            if hasattr(self.model, 'is_active'):
                # Check column type - boolean or integer
                is_active_col = getattr(self.model.__table__.columns, 'is_active', None)
                if is_active_col is not None and hasattr(is_active_col.type, 'python_type'):
                    # If boolean type, use True (but convert to proper SQLAlchemy boolean)
                    if is_active_col.type.python_type == bool:
                        # Use is_(True) instead of == True for proper SQLAlchemy boolean handling
                        query = query.filter(or_(self.model.is_active.is_(True), self.model.is_active.is_(None)))
                    else:
                        # Integer type, use 1
                        query = query.filter(or_(self.model.is_active == 1, self.model.is_active.is_(None)))
                else:
                    # Fallback: use 1 for integer type (MySQL typically uses INT)
                    query = query.filter(or_(
                        self.model.is_active == 1,
                        self.model.is_active.is_(None)
                    ))
            
            # Auto-filter by project_id if model has project_id column and project_id is provided
            if project_id is not None and hasattr(self.model, 'project_id'):
                query = query.filter(self.model.project_id == project_id)
            
            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        # Support for LIKE operator (e.g., "nama__like")
                        if key.endswith('__like'):
                            field_name = key[:-6]
                            if hasattr(self.model, field_name):
                                query = query.filter(getattr(self.model, field_name).like(f"%{value}%"))
                        else:
                            query = query.filter(getattr(self.model, key) == value)
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError:
            return []

    def count_active(
        self,
        project_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count active records (is_active == 1 or None)
        Best practice: centralized method untuk count active records
        
        Args:
            project_id: Optional project ID untuk filtering
            filters: Additional filters dictionary
            
        Returns:
            Count of active records
        """
        try:
            from sqlalchemy import or_
            
            query = self.db.query(self.model)
            
            # Filter by is_active (handle both int 1 and boolean True)
            if hasattr(self.model, 'is_active'):
                # Check column type - boolean or integer
                is_active_col = getattr(self.model.__table__.columns, 'is_active', None)
                if is_active_col is not None and hasattr(is_active_col.type, 'python_type'):
                    # If boolean type, use True (but convert to proper SQLAlchemy boolean)
                    if is_active_col.type.python_type == bool:
                        # Use is_(True) instead of == True for proper SQLAlchemy boolean handling
                        query = query.filter(or_(self.model.is_active.is_(True), self.model.is_active.is_(None)))
                    else:
                        # Integer type, use 1
                        query = query.filter(or_(self.model.is_active == 1, self.model.is_active.is_(None)))
                else:
                    # Fallback: use 1 for integer type (MySQL typically uses INT)
                    query = query.filter(or_(
                        self.model.is_active == 1,
                        self.model.is_active.is_(None)
                    ))
            
            # Auto-filter by project_id if model has project_id column and project_id is provided
            if project_id is not None and hasattr(self.model, 'project_id'):
                query = query.filter(self.model.project_id == project_id)
            
            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        # Support for LIKE operator (e.g., "nama__like")
                        if key.endswith('__like'):
                            field_name = key[:-6]
                            if hasattr(self.model, field_name):
                                query = query.filter(getattr(self.model, field_name).like(f"%{value}%"))
                        else:
                            query = query.filter(getattr(self.model, key) == value)
            
            return query.count()
        except SQLAlchemyError:
            return 0