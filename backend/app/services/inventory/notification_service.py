from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.repositories.inventory import (
    NotificationRepository,
    StockOutRepository,
    InstalledRepository,
    ReturnRepository,
    MandorRepository,
    MaterialRepository,
)
from app.models.inventory.notification import Notification


class NotificationService:
    """Service untuk handle business logic Notifications dan Discrepancy Check"""

    def __init__(self, db: Session):
        self.notification_repo = NotificationRepository(db)
        self.stock_out_repo = StockOutRepository(db)
        self.installed_repo = InstalledRepository(db)
        self.return_repo = ReturnRepository(db)
        self.mandor_repo = MandorRepository(db)
        self.material_repo = MaterialRepository(db)
        self.db = db

    def check_discrepancy(self, project_id: Optional[int] = None) -> List[Dict]:
        """
        Check selisih antara barang keluar dan barang terpasang
        Formula: Barang Keluar - Barang Terpasang = Barang Pengembalian yang seharusnya
        Jika ada selisih, create notification
        Filter berdasarkan project_id jika provided
        """
        discrepancies = []
        
        # Get all active mandors, filter by project_id if provided
        mandors = self.mandor_repo.get_active_mandors(skip=0, limit=10000, project_id=project_id)
        
        # Get all active materials, filter by project_id if provided
        materials = self.material_repo.get_active_materials(skip=0, limit=10000, project_id=project_id)
        
        # Kumpulkan stock_out_id yang berasal dari rilis retur (harus dikecualikan dari perhitungan barang keluar)
        try:
            from app.models.inventory.return_model import Return as ReturnModel
            from sqlalchemy import or_, and_
            query = self.db.query(ReturnModel.stock_out_id).filter(
                and_(
                    ReturnModel.is_released == 1,
                    ReturnModel.stock_out_id.isnot(None),
                    or_(ReturnModel.is_deleted == 0, ReturnModel.is_deleted.is_(None))
                )
            )
            
            # Filter by project_id if provided
            if project_id is not None:
                query = query.filter(ReturnModel.project_id == project_id)
            
            released_so_ids = set(
                so_id for (so_id,) in query.all()
            )
        except Exception:
            released_so_ids = set()

        for mandor in mandors:
            for material in materials:
                # Get total barang keluar untuk mandor + material ini, filter by project_id if provided
                stock_outs = self.stock_out_repo.get_by_mandor_and_material(
                    mandor.id, material.id, project_id=project_id
                )
                # Exclude stock-out yang merupakan hasil rilis retur
                total_keluar = sum(
                    so.quantity for so in stock_outs 
                    if so.is_deleted == 0 and so.id not in released_so_ids
                )
                
                # Get total barang terpasang untuk mandor + material ini, filter by project_id if provided
                installed_items = self.installed_repo.get_by_mandor_and_material(
                    mandor.id, material.id, project_id=project_id
                )
                total_terpasang = sum(i.quantity for i in installed_items if i.is_deleted == 0)
                
                # Get total barang kembali yang sudah dicatat, filter by project_id if provided
                # PENTING: Exclude return yang sudah di-release (is_released = 1) karena 
                # return tersebut sudah dikeluarkan lagi sebagai stock out baru
                returns = self.return_repo.get_by_mandor_and_material(
                    mandor.id, material.id, project_id=project_id
                )
                total_kembali_dicatat = sum(
                    r.quantity_kembali for r in returns 
                    if r.is_deleted == 0 and getattr(r, 'is_released', 0) == 0
                )
                
                # Calculate selisih yang seharusnya
                selisih_seharusnya = total_keluar - total_terpasang
                selisih_aktual = selisih_seharusnya - total_kembali_dicatat
                
                # Jika ada selisih (barang keluar > barang terpasang)
                if selisih_seharusnya > 0:
                    discrepancies.append({
                        "mandor_id": mandor.id,
                        "mandor_nama": mandor.nama,
                        "material_id": material.id,
                        "material_kode": material.kode_barang,
                        "material_nama": material.nama_barang,
                        "barang_keluar": total_keluar,
                        "barang_terpasang": total_terpasang,
                        "barang_kembali_dicatat": total_kembali_dicatat,
                        "selisih_seharusnya": selisih_seharusnya,
                        "selisih_aktual": selisih_aktual,  # Selisih yang belum dicatat
                        "status": "warning" if selisih_aktual > 0 else "info"
                    })
                    
                    # Create or update notification jika ada selisih yang belum dicatat
                    if selisih_aktual > 0:
                        self._create_or_update_notification(
                            mandor.id,
                            material.id,
                            total_keluar,
                            total_terpasang,
                            selisih_aktual
                        )
                    else:
                        # Jika selisih sudah 0 atau negatif, hapus notifikasi yang ada (jika ada)
                        self._delete_notification_if_exists(mandor.id, material.id)
                else:
                    # Jika tidak ada selisih sama sekali (selisih_seharusnya <= 0),
                    # hapus notifikasi yang ada (jika ada) karena sudah tidak relevan
                    self._delete_notification_if_exists(mandor.id, material.id)
        
        return discrepancies

    def _create_or_update_notification(
        self,
        mandor_id: int,
        material_id: int,
        barang_keluar: int,
        barang_terpasang: int,
        selisih: int
    ):
        """Create or update notification for discrepancy"""
        # Check if notification already exists (baik yang sudah dibaca maupun belum)
        existing = self.notification_repo.get_by(
            mandor_id=mandor_id,
            material_id=material_id
        )
        
        material = self.material_repo.get(material_id)
        mandor = self.mandor_repo.get(mandor_id)
        
        notification_data = {
            "mandor_id": mandor_id,
            "material_id": material_id,
            "title": f"Selisih Barang Pengembalian - {mandor.nama if mandor else ''}",
            "message": f"Ada selisih {selisih} unit {material.nama_barang if material else ''} "
                      f"yang belum dicatat sebagai barang pengembalian untuk mandor {mandor.nama if mandor else ''}",
            "barang_keluar": barang_keluar,
            "barang_terpasang": barang_terpasang,
            "selisih": selisih,
            "status": "warning"
        }
        
        if existing:
            # Update existing notification
            self.notification_repo.update(existing.id, notification_data)
        else:
            # Create new notification
            self.notification_repo.create(notification_data)
    
    def _delete_notification_if_exists(
        self,
        mandor_id: int,
        material_id: int
    ):
        """Delete notification if exists (untuk case ketika selisih sudah 0 atau negatif)"""
        try:
            existing = self.notification_repo.get_by(
                mandor_id=mandor_id,
                material_id=material_id
            )
            
            if existing:
                # Hapus notifikasi yang ada
                self.notification_repo.delete(existing.id)
        except Exception:
            # Jika ada error, skip saja (tidak critical)
            pass

    def get_notifications(self, is_read: bool = None, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> tuple[List[Notification], int]:
        """Get notifications, optionally filtered by project_id through material"""
        from app.models.inventory.material import Material
        
        # Base query
        query = self.db.query(self.notification_repo.model)
        
        # Filter by project_id through material if provided
        if project_id is not None:
            query = query.join(Material).filter(
                Material.project_id == project_id
            )
        
        # Apply is_read filter if specified
        if is_read is not None:
            query = query.filter(self.notification_repo.model.is_read == is_read)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and get results
        notifications = query.offset(skip).limit(limit).all()
        
        return notifications, total

    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        return self.notification_repo.mark_as_read(notification_id)

    def mark_all_as_read(self) -> int:
        """Mark all notifications as read"""
        return self.notification_repo.mark_all_as_read()

