from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_, func
from datetime import date
from app.models.inventory.stock_out import StockOut
from app.repositories.base import BaseRepository


class StockOutRepository(BaseRepository[StockOut]):
    """Repository untuk StockOut model"""

    def __init__(self, db: Session):
        super().__init__(StockOut, db)

    def get_by_nomor(self, nomor_barang_keluar: str) -> Optional[StockOut]:
        """Get stock out by nomor barang keluar (tidak termasuk yang deleted)"""
        try:
            return self.db.query(self.model).filter(
                and_(
                    self.model.nomor_barang_keluar == nomor_barang_keluar,
                    self.model.is_deleted == 0
                )
            ).first()
        except Exception:
            return None

    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[StockOut]:
        """Get stock outs by date range"""
        try:
            from sqlalchemy import or_
            return self.db.query(self.model).filter(
                and_(
                    self.model.tanggal_keluar >= start_date,
                    self.model.tanggal_keluar <= end_date,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            ).offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_mandor(
        self, 
        mandor_id: int, 
        skip: int = 0, 
        limit: int = 100,
        project_id: Optional[int] = None
    ) -> List[StockOut]:
        """Get stock outs by mandor dengan eager load material dan mandor.

        Catatan penting filter project:
        - Banyak data lama memiliki StockOut.project_id = NULL.
        - Halaman list stock-out memfilter berdasarkan Material.project_id (bukan StockOut.project_id)
          agar data lama tetap muncul sesuai project material-nya.
        - Ikuti pola yang sama di sini agar konsisten dengan halaman list dan tidak menghilangkan data.
        """
        try:
            from sqlalchemy.orm import joinedload
            from sqlalchemy import or_, and_
            from app.models.inventory.material import Material

            query = self.db.query(self.model).options(
                joinedload(self.model.material),
                joinedload(self.model.mandor)
            )

            # Base filter: mandor dan tidak deleted (akomodir NULL sebagai tidak terhapus)
            query = query.filter(
                and_(
                    self.model.mandor_id == mandor_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            )

            # Project filter: gunakan Material.project_id seperti pada list endpoint
            if project_id is not None:
                query = query.join(Material, self.model.material_id == Material.id).filter(Material.project_id == project_id)

            return query.order_by(self.model.id.desc()).offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_by_mandor_and_material(
        self, 
        mandor_id: int, 
        material_id: int,
        project_id: Optional[int] = None
    ) -> List[StockOut]:
        """Get stock outs by mandor and material, optionally filtered by project_id"""
        try:
            from sqlalchemy import or_
            query = self.db.query(self.model).filter(
                and_(
                    self.model.mandor_id == mandor_id,
                    self.model.material_id == material_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            )
            
            # Penting: JANGAN filter project_id di sini karena nomor harus unik secara global
            
            return query.all()
        except Exception:
            return []
    
    def get_all_by_material(self, material_id: int, skip: int = 0, limit: int = 10000) -> List[StockOut]:
        """Get all stock outs by material_id, tanpa filter project_id (untuk backward compatibility)"""
        try:
            from sqlalchemy import or_
            return self.db.query(self.model).filter(
                and_(
                    self.model.material_id == material_id,
                    or_(self.model.is_deleted == 0, self.model.is_deleted.is_(None))
                )
            ).offset(skip).limit(limit).all()
        except Exception:
            return []

    def get_next_number_for_date(self, tanggal: date, project_id: Optional[int] = None) -> int:
        """Get next sequence number for given date (untuk auto-numbering)
        
        Catatan: Query ini tidak memfilter is_deleted karena unique constraint 
        berlaku untuk semua record (termasuk yang sudah dihapus).
        Kita perlu memeriksa semua record untuk memastikan nomor yang dihasilkan benar-benar unik.
        """
        try:
            date_str = tanggal.strftime("%Y%m%d")
            prefix = f"JRGS-KDL-{date_str}-"
            
            # Get all nomor yang match prefix untuk tanggal ini
            # Tidak filter is_deleted karena unique constraint berlaku untuk semua record
            # Jadi kita perlu memeriksa semua nomor yang sudah ada (termasuk yang dihapus)
            # Expire semua object untuk memastikan query fresh (tidak dari cache)
            self.db.expire_all()
            # Query langsung ke database untuk mendapatkan data terbaru
            query = self.db.query(self.model.nomor_barang_keluar).filter(
                self.model.nomor_barang_keluar.like(f"{prefix}%")
            )
            
            # Jangan filter project_id di sini agar nomor unik secara global lintas project
            
            results = query.all()
            
            if not results:
                return 1
            
            # Extract numbers dan cari yang terbesar
            max_num = 0
            for result in results:
                # Handle different result types from SQLAlchemy
                # Could be tuple, Row, or direct string
                try:
                    if isinstance(result, tuple):
                        nomor = result[0]
                    elif hasattr(result, '__getitem__'):
                        nomor = result[0] if len(result) > 0 else str(result)
                    else:
                        nomor = str(result)
                    
                    # Ensure nomor is string
                    if not isinstance(nomor, str):
                        nomor = str(nomor)
                    
                    # Format: JRGS-KDL-YYYYMMDD-XXXX
                    # Extract XXXX (4 digit terakhir setelah -)
                    parts = nomor.split("-")
                    if len(parts) == 4:
                        num = int(parts[-1])
                        if num > max_num:
                            max_num = num
                except (ValueError, IndexError, AttributeError, TypeError) as e:
                    # Skip invalid entries
                    continue
            
            return max_num + 1
        except Exception as e:
            # Log error for debugging but return safe default
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error getting next number for date {tanggal}: {str(e)}", exc_info=True)
            return 1

    def soft_delete(self, id: int, deleted_by: int) -> Optional[StockOut]:
        """Soft delete stock out"""
        return self.update(id, {"is_deleted": 1, "deleted_by": deleted_by})

