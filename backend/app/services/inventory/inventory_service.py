from typing import Optional
from sqlalchemy.orm import Session
from app.services.inventory.material_service import MaterialService
from app.services.inventory.mandor_service import MandorService
from app.services.inventory.stock_service import StockService
from app.services.inventory.notification_service import NotificationService


class InventoryService:
    """Main service untuk handle semua inventory operations"""

    def __init__(self, db: Session):
        self.db = db
        self.material_service = MaterialService(db)
        self.mandor_service = MandorService(db)
        self.stock_service = StockService(db)
        self.notification_service = NotificationService(db)

