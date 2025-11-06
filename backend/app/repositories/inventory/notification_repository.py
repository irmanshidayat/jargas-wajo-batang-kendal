from sqlalchemy.orm import Session
from typing import List
from app.models.inventory.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository untuk Notification model"""

    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def get_unread(self, skip: int = 0, limit: int = 100) -> List[Notification]:
        """Get all unread notifications"""
        return self.get_all(skip=skip, limit=limit, filters={"is_read": False})

    def mark_as_read(self, id: int) -> bool:
        """Mark notification as read"""
        updated = self.update(id, {"is_read": True})
        return updated is not None

    def mark_all_as_read(self) -> int:
        """Mark all notifications as read"""
        try:
            count = self.db.query(self.model).filter(
                self.model.is_read == False
            ).update({"is_read": True})
            self.db.commit()
            return count
        except Exception:
            self.db.rollback()
            return 0

