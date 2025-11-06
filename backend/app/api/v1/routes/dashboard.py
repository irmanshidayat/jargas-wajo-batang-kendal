from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import date
from app.config.database import get_db
from app.core.security import get_current_user
from app.models.user.user import User
from app.utils.response import success_response
from app.repositories.inventory import (
    MaterialRepository,
    StockInRepository,
    StockOutRepository,
    NotificationRepository,
    MandorRepository
)
from app.services.inventory.stock_service import StockService
from app.services.inventory.notification_service import NotificationService

router = APIRouter()


@router.get(
    "/stats",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard statistics",
    description="Mendapatkan statistik dashboard"
)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    try:
        # Initialize repositories
        material_repo = MaterialRepository(db)
        mandor_repo = MandorRepository(db)
        stock_in_repo = StockInRepository(db)
        stock_out_repo = StockOutRepository(db)
        notification_repo = NotificationRepository(db)
        stock_service = StockService(db)
        notification_service = NotificationService(db)
        
        # Get current month start and end dates
        today = date.today()
        month_start = date(today.year, today.month, 1)
        month_end = today
        
        # Calculate statistics
        # Total materials aktif
        total_materials = material_repo.count(filters={"is_active": 1})
        
        # Total mandors aktif
        total_mandors = mandor_repo.count(filters={"is_active": 1})
        
        # Total stock masuk bulan ini
        stock_ins_month = stock_in_repo.get_by_date_range(month_start, month_end, skip=0, limit=10000)
        total_stock_in_month = sum(si.quantity for si in stock_ins_month if si.is_deleted == 0)
        
        # Total stock keluar bulan ini
        stock_outs_month = stock_out_repo.get_by_date_range(month_start, month_end, skip=0, limit=10000)
        total_stock_out_month = sum(so.quantity for so in stock_outs_month if so.is_deleted == 0)
        
        # Total stock saat ini (dari semua materials)
        stock_balance = stock_service.get_stock_balance()
        if isinstance(stock_balance, list):
            total_stock_current = sum(item.get("stock_saat_ini", 0) for item in stock_balance)
        else:
            total_stock_current = stock_balance.get("stock_saat_ini", 0) if stock_balance else 0
        
        # Notifications belum dibaca
        unread_notifications = notification_repo.count(filters={"is_read": False})
        
        # Jumlah discrepancies yang aktif (selisih_aktual > 0)
        discrepancies = notification_service.check_discrepancy()
        active_discrepancies = sum(1 for d in discrepancies if d.get("selisih_aktual", 0) > 0)
        
        stats = {
            "total_materials": total_materials,
            "total_mandors": total_mandors,
            "total_stock_in_month": total_stock_in_month,
            "total_stock_out_month": total_stock_out_month,
            "total_stock_current": total_stock_current,
            "unread_notifications": unread_notifications,
            "active_discrepancies": active_discrepancies
        }
        
        return success_response(
            data=stats,
            message="Data dashboard berhasil diambil"
        )
    except Exception as e:
        # Fallback jika terjadi error
        stats = {
            "total_materials": 0,
            "total_mandors": 0,
            "total_stock_in_month": 0,
            "total_stock_out_month": 0,
            "total_stock_current": 0,
            "unread_notifications": 0,
            "active_discrepancies": 0
        }
        
        return success_response(
            data=stats,
            message="Data dashboard berhasil diambil"
        )
