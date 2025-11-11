from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.inventory import MaterialRepository
from app.services.base import BaseService
from app.core.exceptions import NotFoundError, ValidationError
import logging


# Valid kategori untuk material (berdasarkan image description)
VALID_KATEGORIS = [
    "PIPA DITRIBUSI",
    "BUNGAN RUMAH",
    "BUNGAN KOMPOR"
]


class MaterialService(BaseService[MaterialRepository]):
    """
    Service untuk handle business logic Material
    Menggunakan BaseService untuk CRUD operations standar
    Memiliki logika khusus untuk validasi kode_barang dan bulk operations
    """

    def __init__(self, db: Session):
        repository = MaterialRepository(db)
        super().__init__(repository, db)
        self.logger = logging.getLogger(__name__)

    def get_all(self, skip: int = 0, limit: int = 100, project_id: int = None) -> tuple[List, int]:
        """
        Get all active materials
        Menggunakan count_active_materials untuk konsistensi dengan filter aktif + NULL
        """
        materials = self.repository.get_active_materials(skip=skip, limit=limit, project_id=project_id)
        # Total harus konsisten dengan filter aktif + NULL
        if hasattr(self.repository, "count_active_materials"):
            total = self.repository.count_active_materials(project_id=project_id)
        else:
            total = self.repository.count_active(project_id=project_id)
        return materials, total

    def get_by_kode(self, kode_barang: str, project_id: int):
        """Get material by kode barang, required project_id"""
        if project_id is None:
            raise ValidationError("Project ID harus disertakan")
        material = self.repository.get_by_kode(kode_barang, project_id=project_id)
        if not material:
            raise NotFoundError(f"Material dengan kode {kode_barang} tidak ditemukan")
        return material

    def search_by_name(self, nama: str, skip: int = 0, limit: int = 100, project_id: Optional[int] = None) -> List:
        """Search materials by name"""
        return self.repository.search_by_name(nama, skip=skip, limit=limit, project_id=project_id)

    def create(self, material_data: dict, project_id: int):
        """
        Create new material, required project_id
        Validasi khusus: check duplicate kode_barang per project
        """
        if project_id is None:
            raise ValidationError("Project ID harus disertakan")
        
        # Check if kode_barang already exists in this project (only when provided)
        if "kode_barang" in material_data and material_data["kode_barang"]:
            existing = self.repository.get_by_kode(material_data["kode_barang"], project_id=project_id)
            if existing:
                raise ValidationError(f"Kode barang {material_data['kode_barang']} sudah terdaftar di project ini")
        
        # Gunakan BaseService.create() dengan validate_project_id=True
        return super().create(material_data, project_id=project_id, validate_project_id=True)

    def update(self, material_id: int, material_data: dict, project_id: int):
        """
        Update material, required project_id
        Validasi khusus: check duplicate kode_barang per project jika berubah
        """
        if project_id is None:
            raise ValidationError("Project ID harus disertakan")
        
        # Get existing material untuk check perubahan kode_barang
        material = super().get_by_id(material_id, project_id=project_id)
        
        # Check if kode_barang changed and already exists in this project
        if "kode_barang" in material_data and material_data["kode_barang"] != material.kode_barang:
            existing = self.repository.get_by_kode(material_data["kode_barang"], project_id=project_id)
            if existing:
                raise ValidationError(f"Kode barang {material_data['kode_barang']} sudah terdaftar di project ini")
        
        # Gunakan BaseService.update()
        return super().update(material_id, material_data, project_id=project_id)

    def _check_material_usage(self, material_id: int) -> None:
        """
        Cek apakah material masih digunakan di tabel lain
        Raise ValidationError jika masih digunakan
        """
        from app.models.inventory.stock_in import StockIn
        from app.models.inventory.stock_out import StockOut
        from app.models.inventory.installed import Installed
        from app.models.inventory.return_model import Return
        from app.models.inventory.surat_permintaan_item import SuratPermintaanItem
        
        usage_details = []
        
        # Cek stock_ins (yang belum dihapus)
        stock_ins_count = self.db.query(StockIn).filter(
            StockIn.material_id == material_id,
            StockIn.is_deleted == 0
        ).count()
        if stock_ins_count > 0:
            usage_details.append(f"{stock_ins_count} data stock in")
        
        # Cek stock_outs (yang belum dihapus)
        stock_outs_count = self.db.query(StockOut).filter(
            StockOut.material_id == material_id,
            StockOut.is_deleted == 0
        ).count()
        if stock_outs_count > 0:
            usage_details.append(f"{stock_outs_count} data stock out")
        
        # Cek installed (yang belum dihapus)
        installed_count = self.db.query(Installed).filter(
            Installed.material_id == material_id,
            Installed.is_deleted == 0
        ).count()
        if installed_count > 0:
            usage_details.append(f"{installed_count} data installed")
        
        # Cek returns (yang belum dihapus)
        returns_count = self.db.query(Return).filter(
            Return.material_id == material_id,
            Return.is_deleted == 0
        ).count()
        if returns_count > 0:
            usage_details.append(f"{returns_count} data return")
        
        # Cek surat_permintaan_items (hanya yang memiliki material_id)
        surat_permintaan_count = self.db.query(SuratPermintaanItem).filter(
            SuratPermintaanItem.material_id == material_id,
            SuratPermintaanItem.material_id.isnot(None)
        ).count()
        if surat_permintaan_count > 0:
            usage_details.append(f"{surat_permintaan_count} data surat permintaan")
        
        # Jika masih digunakan, raise ValidationError
        if usage_details:
            usage_text = ", ".join(usage_details)
            raise ValidationError(
                f"Material tidak dapat dihapus karena masih digunakan di: {usage_text}. "
                f"Hapus data terkait terlebih dahulu."
            )

    def delete(self, material_id: int, project_id: int = None) -> bool:
        """
        Hard delete material - benar-benar menghapus dari database
        Validasi terlebih dahulu apakah material masih digunakan
        """
        # Validasi: cek apakah material masih digunakan
        self._check_material_usage(material_id)
        
        # Jika validasi berhasil, lanjutkan delete
        return super().delete(material_id, project_id=project_id, soft_delete=False)

    def bulk_create(self, materials_data: List[Dict[str, Any]], project_id: int) -> Dict[str, Any]:
        """
        Bulk create materials dari list of dictionaries
        
        Args:
            materials_data: List of dictionaries dengan keys: nama_barang, kode_barang, satuan, kategori, harga
        
        Returns:
            Dictionary dengan keys: success_count, failed_count, errors (list of error messages)
        """
        success_count = 0
        failed_count = 0
        errors = []
        
        # Track kode_barang yang sudah diproses untuk duplicate detection
        processed_kodes = set()
        
        for row in materials_data:
            row_num = row.get('_row_number', '?')
            
            try:
                # Prepare material data
                material_data = {
                    'nama_barang': row.get('nama_barang', '').strip(),
                    'satuan': row.get('satuan', '').strip(),
                    'is_active': 1
                }
                
                # Add project_id (required)
                if project_id is None:
                    failed_count += 1
                    error_msg = f"Row {row_num}: Project ID harus disertakan"
                    errors.append(error_msg)
                    self.logger.warning(error_msg)
                    continue
                
                material_data['project_id'] = project_id
                
                # Kode barang (optional, bisa null)
                kode_barang = row.get('kode_barang', '').strip()
                if kode_barang:
                    material_data['kode_barang'] = kode_barang
                    
                    # Check duplicate dalam file yang sama (dalam batch yang sama)
                    if kode_barang in processed_kodes:
                        failed_count += 1
                        error_msg = f"Row {row_num}: Kode barang '{kode_barang}' duplikat dalam file"
                        errors.append(error_msg)
                        self.logger.warning(error_msg)
                        continue
                    
                    # Check duplicate di database (per project)
                    existing = self.repository.get_by_kode(kode_barang, project_id=project_id)
                    if existing:
                        failed_count += 1
                        error_msg = f"Row {row_num}: Kode barang '{kode_barang}' sudah terdaftar di project ini"
                        errors.append(error_msg)
                        self.logger.warning(f"Row {row_num}: Kode barang '{kode_barang}' sudah ada di database (id: {existing.id})")
                        continue
                    
                    processed_kodes.add(kode_barang)
                else:
                    # Jika kode_barang kosong, biarkan null (sesuai requirement)
                    material_data['kode_barang'] = None
                
                # Kategori (optional, bisa null atau harus valid jika ada)
                kategori = row.get('kategori', '').strip()
                if kategori:
                    # Validate kategori dari list valid (case insensitive)
                    kategori_upper = kategori.upper().strip()
                    valid_upper = [k.upper() for k in VALID_KATEGORIS]
                    if kategori_upper in valid_upper:
                        # Find exact match dari VALID_KATEGORIS
                        for valid_kategori in VALID_KATEGORIS:
                            if valid_kategori.upper() == kategori_upper:
                                material_data['kategori'] = valid_kategori
                                break
                    else:
                        # Jika kategori tidak valid, set ke None (kategori optional)
                        # Kategori optional, jadi tidak perlu error, hanya set ke None
                        material_data['kategori'] = None
                else:
                    material_data['kategori'] = None
                
                # Harga (optional, tapi kalau ada harus numerik dan >= 0)
                harga_str = row.get('harga', '').strip()
                if harga_str:
                    try:
                        from decimal import Decimal
                        harga_value = Decimal(str(harga_str))
                        if harga_value < 0:
                            failed_count += 1
                            errors.append(f"Row {row_num}: Harga tidak boleh negatif")
                            continue
                        material_data['harga'] = harga_value
                    except (ValueError, TypeError, Exception) as e:
                        failed_count += 1
                        errors.append(f"Row {row_num}: Harga harus berupa angka (contoh: 150000 atau 150000.50)")
                        continue
                else:
                    material_data['harga'] = None
                
                # Create material
                try:
                    # Validasi nama_barang dan satuan tidak boleh kosong
                    if not material_data.get('nama_barang'):
                        failed_count += 1
                        error_msg = f"Row {row_num}: Nama Barang wajib diisi"
                        errors.append(error_msg)
                        self.logger.warning(error_msg)
                        continue
                    
                    if not material_data.get('satuan'):
                        failed_count += 1
                        error_msg = f"Row {row_num}: Satuan wajib diisi"
                        errors.append(error_msg)
                        self.logger.warning(error_msg)
                        continue
                    
                    self.logger.info(f"Row {row_num}: Mencoba membuat material: {material_data}")
                    material = self.repository.create(material_data)
                    if material:
                        success_count += 1
                        self.logger.info(f"Row {row_num}: Berhasil membuat material dengan id: {material.id}")
                    else:
                        failed_count += 1
                        error_msg = f"Row {row_num}: Gagal membuat material '{material_data['nama_barang']}'"
                        errors.append(error_msg)
                        self.logger.error(error_msg)
                except IntegrityError as ie:
                    # Handle duplicate entry error
                    failed_count += 1
                    error_msg = str(ie.orig) if hasattr(ie, 'orig') else str(ie)
                    self.logger.error(f"Row {row_num}: IntegrityError - {error_msg}")
                    
                    if "Duplicate entry" in error_msg or "uq_material_project_kode" in error_msg:
                        kode = material_data.get('kode_barang', '')
                        error_msg = f"Row {row_num}: Kode barang '{kode}' sudah terdaftar di project ini"
                        errors.append(error_msg)
                    else:
                        error_msg = f"Row {row_num}: Error database - {error_msg}"
                        errors.append(error_msg)
                except Exception as db_error:
                    # Handle other database errors
                    failed_count += 1
                    error_msg = f"Row {row_num}: Error membuat material - {str(db_error)}"
                    errors.append(error_msg)
                    self.logger.error(f"Row {row_num}: Database error - {str(db_error)}", exc_info=True)
                    
            except Exception as e:
                failed_count += 1
                error_msg = f"Row {row_num}: Error memproses data - {str(e)}"
                errors.append(error_msg)
                self.logger.error(f"Row {row_num}: Exception - {str(e)}", exc_info=True)
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors
        }

    @staticmethod
    def get_valid_kategoris() -> List[str]:
        """Get list of valid kategori"""
        return VALID_KATEGORIS.copy()

    def get_unique_satuans(self) -> List[str]:
        """Get unique satuan values from database"""
        return self.repository.get_unique_satuans()

    def get_unique_kategoris(self) -> List[str]:
        """Get unique kategori values from database"""
        return self.repository.get_unique_kategoris()

