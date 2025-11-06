from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.inventory import AuditLogRepository
from app.models.inventory.audit_log import AuditLog, ActionType
from datetime import datetime


class AuditLogService:
    """Service untuk handle business logic Audit Log"""

    def __init__(self, db: Session):
        self.repository = AuditLogRepository(db)
        self.db = db

    def create_log(
        self,
        user_id: int,
        action: ActionType,
        table_name: str,
        record_id: Optional[int] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """Create audit log entry"""
        import json
        
        log_data = {
            "user_id": user_id,
            "action": action,
            "table_name": table_name,
            "record_id": record_id,
            "old_values": json.dumps(old_values, ensure_ascii=False, default=str) if old_values else None,
            "new_values": json.dumps(new_values, ensure_ascii=False, default=str) if new_values else None,
            "description": description,
            "ip_address": ip_address
        }
        
        return self.repository.create(log_data)

    def get_logs(
        self,
        user_id: Optional[int] = None,
        table_name: Optional[str] = None,
        action: Optional[ActionType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[AuditLog], int]:
        """Get audit logs with filters"""
        if user_id:
            logs = self.repository.get_by_user(user_id, skip=skip, limit=limit)
            total = len(logs)
        elif table_name:
            logs = self.repository.get_by_table(table_name, skip=skip, limit=limit)
            total = len(logs)
        elif action:
            logs = self.repository.get_by_action(action, skip=skip, limit=limit)
            total = len(logs)
        else:
            logs = self.repository.get_all(skip=skip, limit=limit)
            total = self.repository.count()
        
        return logs, total

