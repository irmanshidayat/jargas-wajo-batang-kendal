from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.repositories.inventory.surat_jalan_repository import SuratJalanRepository
from app.repositories.project.project_repository import ProjectRepository
from app.models.inventory.surat_jalan_item import SuratJalanItem
from app.models.inventory.surat_jalan import SuratJalan
from app.core.exceptions import NotFoundError, ValidationError
import logging


class SuratJalanService:
    """Service untuk handle business logic Surat Jalan operations"""

    def __init__(self, db: Session):
        self.surat_jalan_repo = SuratJalanRepository(db)
        self.project_repo = ProjectRepository(db)
        self.db = db
        self.logger = logging.getLogger(__name__)
        # Late import to avoid circulars
        from app.services.inventory.surat_permintaan_service import SuratPermintaanService
        self.surat_permintaan_service = SuratPermintaanService(db)

    def generate_nomor_form(self, project_code: str, tanggal: date) -> str:
        """Generate nomor form dengan format: SJ-{PROJECT_CODE}-{YYYYMMDD}-{XXXX}
        
        Nomor urut (XXXX) terus berlanjut tanpa reset per hari
        """
        if not project_code:
            raise ValidationError("Kode project tidak boleh kosong")
        
        next_num = self.surat_jalan_repo.get_next_number_for_project_code(project_code, tanggal)
        date_str = tanggal.strftime("%Y%m%d")
        nomor_form = f"SJ-{project_code}-{date_str}-{next_num:04d}"
        
        return nomor_form

    def _update_surat_permintaan_status_by_nomor(
        self, 
        nomor_form: str, 
        nomor_barang_keluar: Optional[str], 
        nomor_surat_permintaan: Optional[str],
        project_id: int
    ):
        """Update status surat permintaan menjadi 'Selesai' jika nomor cocok
        
        Logika:
        1. Jika nomor_surat_permintaan diisi, langsung update dengan nomor tersebut
        2. Jika tidak, cek apakah nomor_form atau nomor_barang_keluar cocok dengan nomor_surat surat permintaan
        3. Jika cocok, update status menjadi 'Selesai'
        """
        from app.repositories.inventory.surat_permintaan_repository import SuratPermintaanRepository
        surat_permintaan_repo = SuratPermintaanRepository(self.db)
        
        # Jika nomor_surat_permintaan sudah diisi, langsung update
        if nomor_surat_permintaan:
            try:
                self.surat_permintaan_service.update_status(
                    nomor_surat=nomor_surat_permintaan,
                    status="Selesai",
                    project_id=project_id
                )
                self.logger.info(f"Status surat permintaan {nomor_surat_permintaan} diupdate menjadi Selesai")
            except Exception as e:
                self.logger.warning(f"Gagal update status surat permintaan {nomor_surat_permintaan}: {str(e)}")
            return
        
        # Jika nomor_surat_permintaan tidak diisi, cek apakah nomor_form atau nomor_barang_keluar cocok
        nomor_to_check = nomor_barang_keluar if nomor_barang_keluar else nomor_form
        
        if nomor_to_check:
            try:
                # Cek apakah nomor tersebut adalah nomor surat permintaan
                surat_permintaan = surat_permintaan_repo.get_by_nomor_surat(nomor_to_check, project_id=project_id)
                
                if surat_permintaan and surat_permintaan.is_deleted == 0:
                    # Nomor cocok dengan surat permintaan, update status
                    self.surat_permintaan_service.update_status(
                        nomor_surat=nomor_to_check,
                        status="Selesai",
                        project_id=project_id
                    )
                    self.logger.info(f"Status surat permintaan {nomor_to_check} diupdate menjadi Selesai (dari nomor_form/nomor_barang_keluar)")
            except Exception as e:
                self.logger.warning(f"Gagal update status surat permintaan dengan nomor {nomor_to_check}: {str(e)}")

    def create(
        self,
        kepada: str,
        tanggal_pengiriman: date,
        items: List[Dict[str, Any]],
        nama_pemberi: Optional[str] = None,
        nama_penerima: Optional[str] = None,
        tanggal_diterima: Optional[date] = None,
        created_by: int = None,
        project_id: int = None,
        nomor_surat_permintaan: Optional[str] = None,
        nomor_barang_keluar: Optional[str] = None
    ):
        """Create surat jalan record dengan auto-numbering atau menggunakan nomor barang keluar
        
        Best practice:
        - Jika nomor_barang_keluar diisi, gunakan sebagai nomor_form
        - Validasi bahwa nomor barang keluar belum pernah digunakan untuk surat jalan lain
        - Validasi bahwa nomor barang keluar ada di database
        - Simpan stock_out_id untuk referential integrity
        """
        # Validate project exists
        project = self.project_repo.get(project_id)
        if not project:
            raise NotFoundError(f"Project dengan ID {project_id} tidak ditemukan")
        
        if not project.code:
            raise ValidationError("Project tidak memiliki kode, tidak dapat membuat surat jalan")
        
        if not items or len(items) == 0:
            raise ValidationError("Minimal harus ada 1 item barang")
        
        if not kepada or not kepada.strip():
            raise ValidationError("Kepada tidak boleh kosong")
        
        # Handle nomor barang keluar jika diisi
        stock_out_id = None
        if nomor_barang_keluar:
            nomor_barang_keluar = nomor_barang_keluar.strip()
            
            # Validasi: Cek apakah nomor barang keluar sudah pernah digunakan untuk surat jalan lain
            if self.surat_jalan_repo.is_nomor_barang_keluar_used(nomor_barang_keluar, project_id=project_id):
                raise ValidationError(f"Nomor barang keluar {nomor_barang_keluar} sudah pernah digunakan untuk surat jalan lain")
            
            # Validasi: Cek apakah nomor barang keluar ada di database
            from app.repositories.inventory.stock_out_repository import StockOutRepository
            stock_out_repo = StockOutRepository(self.db)
            stock_out = stock_out_repo.get_by_nomor(nomor_barang_keluar)
            
            if not stock_out:
                raise NotFoundError(f"Nomor barang keluar {nomor_barang_keluar} tidak ditemukan di database")
            
            if stock_out.is_deleted == 1:
                raise ValidationError(f"Nomor barang keluar {nomor_barang_keluar} sudah dihapus")
            
            # Validasi: Pastikan stock_out milik project yang sama
            if stock_out.project_id and stock_out.project_id != project_id:
                raise ValidationError(f"Nomor barang keluar {nomor_barang_keluar} bukan milik project ini")
            
            # Gunakan nomor barang keluar sebagai nomor_form
            nomor_form = nomor_barang_keluar
            stock_out_id = stock_out.id
        else:
            # Generate nomor form otomatis jika nomor_barang_keluar tidak diisi
            nomor_form = self.generate_nomor_form(project.code, tanggal_pengiriman)
        
        # Validate nomor_surat_permintaan jika diisi
        if nomor_surat_permintaan:
            from app.repositories.inventory.surat_permintaan_repository import SuratPermintaanRepository
            surat_permintaan_repo = SuratPermintaanRepository(self.db)
            surat_permintaan = surat_permintaan_repo.get_by_nomor_surat(nomor_surat_permintaan, project_id=project_id)
            if not surat_permintaan:
                raise NotFoundError(f"Surat permintaan dengan nomor {nomor_surat_permintaan} tidak ditemukan")
            if surat_permintaan.is_deleted == 1:
                raise ValidationError(f"Surat permintaan dengan nomor {nomor_surat_permintaan} sudah dihapus")
        
        # Create surat jalan with retry mechanism
        surat_jalan_data = {
            "nomor_form": nomor_form,
            "kepada": kepada.strip(),
            "tanggal_pengiriman": tanggal_pengiriman,
            "nama_pemberi": nama_pemberi.strip() if nama_pemberi else None,
            "nama_penerima": nama_penerima.strip() if nama_penerima else None,
            "tanggal_diterima": tanggal_diterima,
            "nomor_surat_permintaan": nomor_surat_permintaan,
            "nomor_barang_keluar": nomor_barang_keluar,
            "stock_out_id": stock_out_id,
            "project_id": project_id,
            "created_by": created_by,
            "is_deleted": 0
        }
        
        try:
            # Create surat jalan
            surat_jalan = self.surat_jalan_repo.create(surat_jalan_data)
            if not surat_jalan:
                raise ValidationError("Gagal membuat surat jalan")
            
            # Create items
            for item in items:
                if not item.get('nama_barang') or not item['nama_barang'].strip():
                    raise ValidationError("Nama barang tidak boleh kosong")
                
                item_data = {
                    "surat_jalan_id": surat_jalan.id,
                    "nama_barang": item['nama_barang'].strip(),
                    "qty": item.get('qty', 0),
                    "keterangan": item.get('keterangan', '').strip() if item.get('keterangan') else None
                }
                
                item_obj = SuratJalanItem(**item_data)
                self.db.add(item_obj)
            
            self.db.commit()
            self.db.refresh(surat_jalan)
            
            # Update status surat permintaan jika nomor cocok
            self._update_surat_permintaan_status_by_nomor(
                nomor_form=nomor_form,
                nomor_barang_keluar=nomor_barang_keluar,
                nomor_surat_permintaan=nomor_surat_permintaan,
                project_id=project_id
            )
            
            return surat_jalan
        except IntegrityError as e:
            self.db.rollback()
            # Retry jika nomor form duplicate (very unlikely)
            if "nomor_form" in str(e).lower() or "uq_surat_jalan_number" in str(e).lower():
                # Retry dengan nomor baru (hanya jika bukan dari nomor_barang_keluar)
                if not nomor_barang_keluar:
                    nomor_form = self.generate_nomor_form(project.code, tanggal_pengiriman)
                    surat_jalan_data["nomor_form"] = nomor_form
                    surat_jalan = self.surat_jalan_repo.create(surat_jalan_data)
                    if not surat_jalan:
                        raise ValidationError("Gagal membuat surat jalan setelah retry")
                    
                    # Recreate items
                    for item in items:
                        item_data = {
                            "surat_jalan_id": surat_jalan.id,
                            "nama_barang": item['nama_barang'].strip(),
                            "qty": item.get('qty', 0),
                            "keterangan": item.get('keterangan', '').strip() if item.get('keterangan') else None
                        }
                        
                        item_obj = SuratJalanItem(**item_data)
                        self.db.add(item_obj)
                    
                    self.db.commit()
                    self.db.refresh(surat_jalan)
                    
                    # Update status surat permintaan jika nomor cocok
                    self._update_surat_permintaan_status_by_nomor(
                        nomor_form=nomor_form,
                        nomor_barang_keluar=nomor_barang_keluar,
                        nomor_surat_permintaan=nomor_surat_permintaan,
                        project_id=project_id
                    )
                    
                    return surat_jalan
                else:
                    # Jika menggunakan nomor_barang_keluar dan duplicate, berarti ada masalah
                    raise ValidationError(f"Nomor form {nomor_form} sudah digunakan. Silakan cek kembali.")
            else:
                raise ValidationError(f"Gagal membuat surat jalan: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"SQLAlchemy error creating surat jalan: {str(e)}", exc_info=True)
            raise ValidationError(f"Gagal membuat surat jalan: {str(e)}")

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        project_id: Optional[int] = None
    ) -> tuple[List, int]:
        """Get all surat jalan dengan pagination"""
        try:
            if search:
                items = self.surat_jalan_repo.search_by_nomor_or_kepada(search, skip, limit, project_id)
                total = len(self.surat_jalan_repo.search_by_nomor_or_kepada(search, 0, 10000, project_id))
            elif start_date and end_date:
                items = self.surat_jalan_repo.get_by_date_range(start_date, end_date, skip, limit, project_id)
                total = len(self.surat_jalan_repo.get_by_date_range(start_date, end_date, 0, 10000, project_id))
            else:
                filters = {"is_deleted": 0}
                items = self.surat_jalan_repo.get_all(skip=skip, limit=limit, filters=filters, project_id=project_id)
                total = self.surat_jalan_repo.count(filters=filters, project_id=project_id)
            
            return items, total
        except Exception as e:
            self.logger.error(f"Error getting all surat jalan: {str(e)}", exc_info=True)
            return [], 0

    def get_by_id(self, id: int, project_id: Optional[int] = None) -> Optional[SuratJalan]:
        """Get surat jalan by ID"""
        try:
            surat_jalan = self.surat_jalan_repo.get(id, project_id=project_id)
            if not surat_jalan or surat_jalan.is_deleted == 1:
                return None
            
            # Load items
            from sqlalchemy.orm import joinedload
            surat_jalan = self.db.query(SuratJalan).options(
                joinedload(SuratJalan.items)
            ).filter(SuratJalan.id == id).first()
            
            return surat_jalan
        except Exception as e:
            self.logger.error(f"Error getting surat jalan by ID: {str(e)}", exc_info=True)
            return None

    def get_by_nomor_form(self, nomor_form: str, project_id: Optional[int] = None) -> Optional[SuratJalan]:
        """Get surat jalan by nomor form"""
        try:
            surat_jalan = self.surat_jalan_repo.get_by_nomor_form(nomor_form, project_id=project_id)
            if not surat_jalan or surat_jalan.is_deleted == 1:
                return None
            
            # Load items
            from sqlalchemy.orm import joinedload
            query = self.db.query(SuratJalan).options(
                joinedload(SuratJalan.items)
            ).filter(SuratJalan.nomor_form == nomor_form)
            
            if project_id:
                query = query.filter(SuratJalan.project_id == project_id)
            
            surat_jalan = query.first()
            
            return surat_jalan
        except Exception as e:
            self.logger.error(f"Error getting surat jalan by nomor form: {str(e)}", exc_info=True)
            return None

    def update(
        self,
        id: int,
        kepada: Optional[str] = None,
        tanggal_pengiriman: Optional[date] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        nama_pemberi: Optional[str] = None,
        nama_penerima: Optional[str] = None,
        tanggal_diterima: Optional[date] = None,
        updated_by: int = None,
        project_id: Optional[int] = None
    ) -> Optional[SuratJalan]:
        """Update surat jalan"""
        try:
            surat_jalan = self.get_by_id(id, project_id=project_id)
            if not surat_jalan:
                raise NotFoundError(f"Surat jalan dengan ID {id} tidak ditemukan")
            
            # Update main fields
            update_data = {}
            if kepada is not None:
                if not kepada.strip():
                    raise ValidationError("Kepada tidak boleh kosong")
                update_data["kepada"] = kepada.strip()
            if tanggal_pengiriman is not None:
                update_data["tanggal_pengiriman"] = tanggal_pengiriman
            if nama_pemberi is not None:
                update_data["nama_pemberi"] = nama_pemberi.strip() if nama_pemberi else None
            if nama_penerima is not None:
                update_data["nama_penerima"] = nama_penerima.strip() if nama_penerima else None
            if tanggal_diterima is not None:
                update_data["tanggal_diterima"] = tanggal_diterima
            if updated_by is not None:
                update_data["updated_by"] = updated_by
            
            if update_data:
                surat_jalan = self.surat_jalan_repo.update(id, update_data)
            
            # Update items if provided
            if items is not None:
                # Delete existing items
                self.db.query(SuratJalanItem).filter(SuratJalanItem.surat_jalan_id == id).delete()
                
                # Create new items
                for item in items:
                    if not item.get('nama_barang') or not item['nama_barang'].strip():
                        raise ValidationError("Nama barang tidak boleh kosong")
                    
                    item_data = {
                        "surat_jalan_id": id,
                        "nama_barang": item['nama_barang'].strip(),
                        "qty": item.get('qty', 0),
                        "keterangan": item.get('keterangan', '').strip() if item.get('keterangan') else None
                    }
                    
                    item_obj = SuratJalanItem(**item_data)
                    self.db.add(item_obj)
            
            self.db.commit()
            self.db.refresh(surat_jalan)
            
            return surat_jalan
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating surat jalan: {str(e)}", exc_info=True)
            raise

    def soft_delete(self, id: int, deleted_by: int, project_id: Optional[int] = None) -> bool:
        """Soft delete surat jalan"""
        try:
            surat_jalan = self.get_by_id(id, project_id=project_id)
            if not surat_jalan:
                raise NotFoundError(f"Surat jalan dengan ID {id} tidak ditemukan")
            
            self.surat_jalan_repo.soft_delete(id, deleted_by)
            return True
        except Exception as e:
            self.logger.error(f"Error soft deleting surat jalan: {str(e)}", exc_info=True)
            raise

