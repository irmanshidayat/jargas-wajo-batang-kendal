from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.inventory import MaterialRepository
from app.services.base import BaseService
from app.core.exceptions import NotFoundError, ValidationError


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

    def delete(self, material_id: int, project_id: int = None) -> bool:
        """Soft delete material - menggunakan BaseService.delete()"""
        return super().delete(material_id, project_id=project_id, soft_delete=True)

    def bulk_create(self, materials_data: List[Dict[str, Any]], project_id: int) -> Dict[str, Any]:
        """
        Bulk create materials dari list of dictionaries
        
        Args:
            materials_data: List of dictionaries dengan keys: nama_barang, kode_barang, satuan, kategori
        
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
                    errors.append(f"Row {row_num}: Project ID harus disertakan")
                    continue
                
                material_data['project_id'] = project_id
                
                # Kode barang (optional, bisa null)
                kode_barang = row.get('kode_barang', '').strip()
                if kode_barang:
                    material_data['kode_barang'] = kode_barang
                    
                    # Check duplicate dalam file yang sama (dalam batch yang sama)
                    if kode_barang in processed_kodes:
                        failed_count += 1
                        errors.append(f"Row {row_num}: Kode barang '{kode_barang}' duplikat dalam file")
                        continue
                    
                    # Check duplicate di database (per project)
                    if project_id is None:
                        failed_count += 1
                        errors.append(f"Row {row_num}: Project ID harus disertakan")
                        continue
                    
                    existing = self.repository.get_by_kode(kode_barang, project_id=project_id)
                    if existing:
                        failed_count += 1
                        errors.append(f"Row {row_num}: Kode barang '{kode_barang}' sudah terdaftar di project ini")
                        continue
                    
                    processed_kodes.add(kode_barang)
                else:
                    # Jika kode_barang kosong, biarkan null (sesuai requirement)
                    material_data['kode_barang'] = None
                
                # Kategori (optional, tapi harus valid jika ada)
                kategori = row.get('kategori', '').strip()
                if kategori:
                    # Validate kategori dari list valid
                    kategori_upper = kategori.upper()
                    if kategori_upper not in VALID_KATEGORIS:
                        failed_count += 1
                        errors.append(
                            f"Row {row_num}: Kategori '{kategori}' tidak valid. "
                            f"Kategori yang valid: {', '.join(VALID_KATEGORIS)}"
                        )
                        continue
                    material_data['kategori'] = kategori_upper
                else:
                    material_data['kategori'] = None
                
                # Create material
                try:
                    material = self.repository.create(material_data)
                    if material:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"Row {row_num}: Gagal membuat material '{material_data['nama_barang']}'")
                except IntegrityError as ie:
                    # Handle duplicate entry error
                    failed_count += 1
                    error_msg = str(ie.orig) if hasattr(ie, 'orig') else str(ie)
                    
                    if "Duplicate entry" in error_msg or "uq_material_project_kode" in error_msg:
                        kode = material_data.get('kode_barang', '')
                        errors.append(f"Row {row_num}: Kode barang '{kode}' sudah terdaftar di project ini")
                    else:
                        errors.append(f"Row {row_num}: Error - {error_msg}")
                    
            except Exception as e:
                failed_count += 1
                error_msg = str(e)
                if "kode_barang" in error_msg.lower() and "sudah terdaftar" in error_msg.lower():
                    errors.append(f"Row {row_num}: {error_msg}")
                else:
                    errors.append(f"Row {row_num}: Error - {error_msg}")
        
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

