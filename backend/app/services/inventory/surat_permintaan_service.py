from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.repositories.inventory.surat_permintaan_repository import SuratPermintaanRepository
from app.repositories.inventory.material_repository import MaterialRepository
from app.repositories.project.project_repository import ProjectRepository
from app.models.inventory.surat_permintaan_item import SuratPermintaanItem
from app.models.inventory.surat_permintaan import SuratPermintaan
from app.core.exceptions import NotFoundError, ValidationError
import json
import logging


class SuratPermintaanService:
    """Service untuk handle business logic Surat Permintaan operations"""

    def __init__(self, db: Session):
        self.surat_permintaan_repo = SuratPermintaanRepository(db)
        self.material_repo = MaterialRepository(db)
        self.project_repo = ProjectRepository(db)
        self.db = db
        self.logger = logging.getLogger(__name__)

    def generate_nomor_surat(self, project_code: str, tanggal: date) -> str:
        """Generate nomor surat dengan format: JRGS-{PROJECT_CODE}-{YYYYMMDD}-{XXXX}
        
        Nomor urut (XXXX) terus berlanjut tanpa reset per hari
        """
        if not project_code:
            raise ValidationError("Kode project tidak boleh kosong")
        
        next_num = self.surat_permintaan_repo.get_next_number_for_project_code(project_code, tanggal)
        date_str = tanggal.strftime("%Y%m%d")
        nomor_surat = f"JRGS-{project_code}-{date_str}-{next_num:04d}"
        
        return nomor_surat

    def create(
        self,
        tanggal: date,
        items: List[Dict[str, Any]],
        signatures: Optional[Dict[str, Any]],
        created_by: int,
        project_id: int
    ):
        """Create surat permintaan record dengan auto-numbering"""
        # Validate project exists
        project = self.project_repo.get(project_id)
        if not project:
            raise NotFoundError(f"Project dengan ID {project_id} tidak ditemukan")
        
        if not project.code:
            raise ValidationError("Project tidak memiliki kode, tidak dapat membuat surat permintaan")
        
        if not items or len(items) == 0:
            raise ValidationError("Minimal harus ada 1 item barang")
        
        # Generate nomor surat
        nomor_surat = self.generate_nomor_surat(project.code, tanggal)
        
        # Validate materials jika material_id ada
        for item in items:
            if item.get('material_id'):
                material = self.material_repo.get(item['material_id'], project_id=project_id)
                if not material:
                    raise NotFoundError(f"Material dengan ID {item['material_id']} tidak ditemukan")
        
        # Prepare signatures JSON
        signatures_json = None
        if signatures:
            try:
                signatures_json = json.dumps(signatures)
            except Exception as e:
                self.logger.warning(f"Error serializing signatures: {str(e)}")
        
        # Create surat permintaan with retry mechanism
        surat_permintaan_data = {
            "nomor_surat": nomor_surat,
            "tanggal": tanggal,
            "project_id": project_id,
            "signatures": signatures_json,
            "created_by": created_by,
            "is_deleted": 0
        }
        
        try:
            # Create surat permintaan
            surat_permintaan = self.surat_permintaan_repo.create(surat_permintaan_data)
            if not surat_permintaan:
                raise ValidationError("Gagal membuat surat permintaan")
            
            # Create items
            for item in items:
                # Prepare sumber_barang JSON
                sumber_barang_json = None
                if item.get('sumber_barang'):
                    try:
                        sumber_barang_json = json.dumps(item['sumber_barang'])
                    except Exception:
                        pass
                
                # Prepare peruntukan JSON
                peruntukan_json = None
                if item.get('peruntukan'):
                    try:
                        peruntukan_json = json.dumps(item['peruntukan'])
                    except Exception:
                        pass
                
                item_data = {
                    "surat_permintaan_id": surat_permintaan.id,
                    "material_id": item.get('material_id'),
                    "kode_barang": item.get('kode_barang'),
                    "nama_barang": item['nama_barang'],
                    "qty": item['qty'],
                    "satuan": item['satuan'],
                    "sumber_barang": sumber_barang_json,
                    "peruntukan": peruntukan_json
                }
                
                item_obj = SuratPermintaanItem(**item_data)
                self.db.add(item_obj)
            
            self.db.commit()
            self.db.refresh(surat_permintaan)
            
            return surat_permintaan
        except IntegrityError as e:
            self.db.rollback()
            # Retry jika nomor surat duplicate (very unlikely)
            if "nomor_surat" in str(e).lower() or "uq_surat_permintaan_number" in str(e).lower():
                # Retry dengan nomor baru
                nomor_surat = self.generate_nomor_surat(project.code, tanggal)
                surat_permintaan_data["nomor_surat"] = nomor_surat
                surat_permintaan = self.surat_permintaan_repo.create(surat_permintaan_data)
                if not surat_permintaan:
                    raise ValidationError("Gagal membuat surat permintaan setelah retry")
                
                # Recreate items
                for item in items:
                    sumber_barang_json = None
                    if item.get('sumber_barang'):
                        try:
                            sumber_barang_json = json.dumps(item['sumber_barang'])
                        except Exception:
                            pass
                    
                    peruntukan_json = None
                    if item.get('peruntukan'):
                        try:
                            peruntukan_json = json.dumps(item['peruntukan'])
                        except Exception:
                            pass
                    
                    item_data = {
                        "surat_permintaan_id": surat_permintaan.id,
                        "material_id": item.get('material_id'),
                        "kode_barang": item.get('kode_barang'),
                        "nama_barang": item['nama_barang'],
                        "qty": item['qty'],
                        "satuan": item['satuan'],
                        "sumber_barang": sumber_barang_json,
                        "peruntukan": peruntukan_json
                    }
                    
                    item_obj = SuratPermintaanItem(**item_data)
                    self.db.add(item_obj)
                
                self.db.commit()
                self.db.refresh(surat_permintaan)
                return surat_permintaan
            else:
                raise ValidationError(f"Gagal membuat surat permintaan: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"SQLAlchemy error creating surat permintaan: {str(e)}", exc_info=True)
            raise ValidationError(f"Gagal membuat surat permintaan: {str(e)}")

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        project_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> tuple[List, int]:
        """Get all surat permintaan dengan pagination"""
        try:
            if search:
                items = self.surat_permintaan_repo.search_by_nomor_or_date(search, skip, limit, project_id)
                total = len(self.surat_permintaan_repo.search_by_nomor_or_date(search, 0, 10000, project_id))
            elif start_date and end_date:
                items = self.surat_permintaan_repo.get_by_date_range(start_date, end_date, skip, limit, project_id)
                total = len(self.surat_permintaan_repo.get_by_date_range(start_date, end_date, 0, 10000, project_id))
            else:
                filters = {"is_deleted": 0}
                items = self.surat_permintaan_repo.get_all(skip=skip, limit=limit, filters=filters, project_id=project_id, user_id=user_id)
                total = self.surat_permintaan_repo.count(filters=filters, project_id=project_id)
            
            return items, total
        except Exception as e:
            self.logger.error(f"Error getting all surat permintaan: {str(e)}", exc_info=True)
            return [], 0

    def get_by_id(self, id: int, project_id: Optional[int] = None) -> Optional:
        """Get surat permintaan by ID"""
        try:
            surat_permintaan = self.surat_permintaan_repo.get(id, project_id=project_id)
            if not surat_permintaan or surat_permintaan.is_deleted == 1:
                return None
            
            # Load items
            from sqlalchemy.orm import joinedload
            surat_permintaan = self.db.query(SuratPermintaan).options(
                joinedload(SuratPermintaan.items)
            ).filter(SuratPermintaan.id == id).first()
            
            return surat_permintaan
        except Exception as e:
            self.logger.error(f"Error getting surat permintaan by ID: {str(e)}", exc_info=True)
            return None

    def get_by_nomor_surat(self, nomor_surat: str, project_id: Optional[int] = None) -> Optional:
        """Get surat permintaan by nomor surat"""
        try:
            surat_permintaan = self.surat_permintaan_repo.get_by_nomor_surat(nomor_surat, project_id=project_id)
            if not surat_permintaan or surat_permintaan.is_deleted == 1:
                return None
            
            # Load items
            from sqlalchemy.orm import joinedload
            query = self.db.query(SuratPermintaan).options(
                joinedload(SuratPermintaan.items)
            ).filter(SuratPermintaan.nomor_surat == nomor_surat)
            
            if project_id:
                query = query.filter(SuratPermintaan.project_id == project_id)
            
            surat_permintaan = query.first()
            
            return surat_permintaan
        except Exception as e:
            self.logger.error(f"Error getting surat permintaan by nomor surat: {str(e)}", exc_info=True)
            return None

    def update_status(self, nomor_surat: str, status: str, project_id: Optional[int] = None) -> bool:
        """Update status surat permintaan by nomor surat"""
        try:
            surat_permintaan = self.get_by_nomor_surat(nomor_surat, project_id=project_id)
            if not surat_permintaan:
                self.logger.warning(f"Surat permintaan dengan nomor {nomor_surat} tidak ditemukan untuk update status")
                return False
            
            surat_permintaan.status = status
            self.db.commit()
            self.db.refresh(surat_permintaan)
            self.logger.info(f"Status surat permintaan {nomor_surat} berhasil diupdate menjadi {status}")
            return True
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating status surat permintaan: {str(e)}", exc_info=True)
            return False

