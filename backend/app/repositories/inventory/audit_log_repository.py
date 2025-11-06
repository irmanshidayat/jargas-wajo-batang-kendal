from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_
from datetime import datetime
from app.models.inventory.audit_log import AuditLog, ActionType
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository untuk AuditLog model"""

    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def get_by_user(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by user"""
        return self.get_all(skip=skip, limit=limit, filters={"user_id": user_id})

    def get_by_table(
        self, 
        table_name: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by table name"""
        try:
            return self.db.query(self.model).filter(
                self.model.table_name == table_name
            ).offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_action(
        self, 
        action: ActionType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by action type"""
        try:
            return self.db.query(self.model).filter(
                self.model.action == action
            ).offset(skip).limit(limit).all()
        except Exception:
            return []

