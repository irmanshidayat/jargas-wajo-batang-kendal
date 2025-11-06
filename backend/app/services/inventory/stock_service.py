from typing import Optional, List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.repositories.inventory import (
    StockInRepository,
    StockOutRepository,
    InstalledRepository,
    ReturnRepository,
    MaterialRepository,
)
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.file_upload import save_evidence_paths_to_db, get_evidence_paths_from_db
import json
import logging
import time


class StockService:
    """Service untuk handle business logic Stock operations"""

    def __init__(self, db: Session):
        self.stock_in_repo = StockInRepository(db)
        self.stock_out_repo = StockOutRepository(db)
        self.installed_repo = InstalledRepository(db)
        self.return_repo = ReturnRepository(db)
        self.material_repo = MaterialRepository(db)
        # Late import to avoid circulars
        from app.repositories.inventory.mandor_repository import MandorRepository
        from app.repositories.inventory.surat_permintaan_repository import SuratPermintaanRepository
        self.mandor_repo = MandorRepository(db)
        self.surat_permintaan_repo = SuratPermintaanRepository(db)
        self.db = db
        self.logger = logging.getLogger(__name__)

    def _filter_not_deleted(self, items: List) -> List:
        """Helper method untuk filter items yang tidak deleted (is_deleted == 0 or None)"""
        return [item for item in items if (getattr(item, 'is_deleted', None) == 0 or getattr(item, 'is_deleted', None) is None)]
    
    def _filter_by_material_and_not_deleted(self, items: List, material_id: int) -> List:
        """Helper method untuk filter items by material_id dan tidak deleted"""
        return [
            item for item in items
            if (getattr(item, 'material_id', None) == material_id and 
                (getattr(item, 'is_deleted', None) == 0 or getattr(item, 'is_deleted', None) is None))
        ]

    def create_stock_in(
        self,
        nomor_invoice: str,
        material_id: int,
        quantity: Decimal,
        tanggal_masuk: date,
        evidence_paths: List[str],
        created_by: int,
        surat_jalan_paths: List[str] = None,
        material_datang_paths: List[str] = None,
        project_id: Optional[int] = None
    ):
        """Create stock in record"""
        # Validate material exists
        material = self.material_repo.get(material_id, project_id=project_id)
        if not material:
            raise NotFoundError(f"Material dengan ID {material_id} tidak ditemukan")
        
        # Normalisasi quantity ke 2 desimal
        quantity = Decimal(str(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if quantity <= 0:
            raise ValidationError("Quantity harus lebih dari 0")
        
        # Create stock in
        stock_in_data = {
            "nomor_invoice": nomor_invoice,
            "material_id": material_id,
            "quantity": quantity,
            "tanggal_masuk": tanggal_masuk,
            "evidence_paths": save_evidence_paths_to_db(evidence_paths),
            "surat_jalan_paths": save_evidence_paths_to_db(surat_jalan_paths) if surat_jalan_paths else None,
            "material_datang_paths": save_evidence_paths_to_db(material_datang_paths) if material_datang_paths else None,
            "created_by": created_by,
            "is_deleted": 0
        }
        
        if project_id is not None:
            stock_in_data["project_id"] = project_id
        
        stock_in = self.stock_in_repo.create(stock_in_data)
        if not stock_in:
            raise ValidationError("Gagal membuat data barang masuk")
        
        return stock_in

    def update_stock_in(
        self,
        stock_in_id: int,
        nomor_invoice: Optional[str] = None,
        material_id: Optional[int] = None,
        quantity: Optional[Decimal] = None,
        tanggal_masuk: Optional[date] = None,
        evidence_paths: Optional[List[str]] = None,
        surat_jalan_paths: Optional[List[str]] = None,
        material_datang_paths: Optional[List[str]] = None,
        updated_by: Optional[int] = None,
        project_id: Optional[int] = None
    ):
        """Update stock in record"""
        # Get existing stock in
        stock_in = self.stock_in_repo.get(stock_in_id)
        if not stock_in:
            raise NotFoundError(f"Stock in dengan ID {stock_in_id} tidak ditemukan")
        
        if stock_in.is_deleted == 1:
            raise NotFoundError(f"Stock in dengan ID {stock_in_id} sudah dihapus")
        
        # Prepare update data
        update_data = {}
        
        # Validate and update material if provided
        if material_id is not None:
            material = self.material_repo.get(material_id, project_id=project_id)
            if not material:
                raise NotFoundError(f"Material dengan ID {material_id} tidak ditemukan")
            update_data["material_id"] = material_id
        
        # Validate and normalize quantity if provided
        if quantity is not None:
            quantity = Decimal(str(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if quantity <= 0:
                raise ValidationError("Quantity harus lebih dari 0")
            update_data["quantity"] = quantity
        
        # Update other fields
        if nomor_invoice is not None:
            update_data["nomor_invoice"] = nomor_invoice
        
        if tanggal_masuk is not None:
            update_data["tanggal_masuk"] = tanggal_masuk
        
        # Handle file paths
        if evidence_paths is not None:
            update_data["evidence_paths"] = save_evidence_paths_to_db(evidence_paths)
        
        if surat_jalan_paths is not None:
            update_data["surat_jalan_paths"] = save_evidence_paths_to_db(surat_jalan_paths)
        
        if material_datang_paths is not None:
            update_data["material_datang_paths"] = save_evidence_paths_to_db(material_datang_paths)
        
        if updated_by is not None:
            update_data["updated_by"] = updated_by
        
        # Update stock in
        updated_stock_in = self.stock_in_repo.update(stock_in_id, update_data)
        if not updated_stock_in:
            raise ValidationError("Gagal mengupdate data barang masuk")
        
        return updated_stock_in

    def create_stock_out(
        self,
        mandor_id: int,
        material_id: int,
        quantity: Decimal,
        tanggal_keluar: date,
        evidence_paths: List[str],
        created_by: int,
        surat_permohonan_paths: List[str] = None,
        surat_serah_terima_paths: List[str] = None,
        project_id: Optional[int] = None,
        nomor_surat_permintaan: Optional[str] = None
    ):
        """Create stock out record dengan auto-numbering atau menggunakan nomor surat permintaan"""
        # Validate material exists
        material = self.material_repo.get(material_id, project_id=project_id)
        if not material:
            raise NotFoundError(f"Material dengan ID {material_id} tidak ditemukan")
        
        # Validate mandor exists
        mandor = self.mandor_repo.get(mandor_id, project_id=project_id)
        if not mandor:
            raise NotFoundError(f"Mandor dengan ID {mandor_id} tidak ditemukan")
        
        # Normalisasi quantity ke 2 desimal
        quantity = Decimal(str(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if quantity <= 0:
            raise ValidationError("Quantity harus lebih dari 0")
        
        # Jika nomor_surat_permintaan diisi, gunakan sebagai nomor_barang_keluar
        if nomor_surat_permintaan:
            # Validasi nomor surat permintaan ada di database
            surat_permintaan = self.surat_permintaan_repo.get_by_nomor_surat(nomor_surat_permintaan, project_id=project_id)
            if not surat_permintaan:
                raise NotFoundError(f"Surat permintaan dengan nomor {nomor_surat_permintaan} tidak ditemukan")
            if surat_permintaan.is_deleted == 1:
                raise ValidationError(f"Surat permintaan dengan nomor {nomor_surat_permintaan} sudah dihapus")
            
            # Cek apakah nomor surat permintaan sudah digunakan untuk stock out lain
            existing_stock_out = self.stock_out_repo.get_by_nomor(nomor_surat_permintaan)
            if existing_stock_out and existing_stock_out.is_deleted == 0:
                raise ValidationError(f"Nomor surat permintaan {nomor_surat_permintaan} sudah digunakan untuk stock out lain")
            
            nomor_barang_keluar = nomor_surat_permintaan
        else:
            # Generate nomor barang keluar otomatis
            next_num = self.stock_out_repo.get_next_number_for_date(tanggal_keluar, project_id=project_id)
            date_str = tanggal_keluar.strftime("%Y%m%d")
            nomor_barang_keluar = f"JRGS-KDL-{date_str}-{next_num:04d}"
        
        # Create stock out with retry mechanism
        stock_out_data = {
            "nomor_barang_keluar": nomor_barang_keluar,
            "mandor_id": mandor_id,
            "material_id": material_id,
            "quantity": quantity,
            "tanggal_keluar": tanggal_keluar,
            "evidence_paths": save_evidence_paths_to_db(evidence_paths),
            "surat_permohonan_paths": save_evidence_paths_to_db(surat_permohonan_paths) if surat_permohonan_paths else None,
            "surat_serah_terima_paths": save_evidence_paths_to_db(surat_serah_terima_paths) if surat_serah_terima_paths else None,
            "created_by": created_by,
            "is_deleted": 0
        }
        
        if project_id is not None:
            stock_out_data["project_id"] = project_id
        
        stock_out = self._create_stock_out_with_retry(stock_out_data, tanggal_keluar)
        return stock_out

    def create_installed(
        self,
        material_id: int,
        quantity: Decimal,
        tanggal_pasang: date,
        mandor_id: int,
        stock_out_id: Optional[int],
        evidence_paths: List[str],
        created_by: int,
        no_register: Optional[str] = None,
        project_id: Optional[int] = None
    ):
        """Create installed record"""
        # Validate material exists
        material = self.material_repo.get(material_id, project_id=project_id)
        if not material:
            raise NotFoundError(f"Material dengan ID {material_id} tidak ditemukan")
        
        # Validate mandor exists
        mandor = self.mandor_repo.get(mandor_id, project_id=project_id)
        if not mandor:
            raise NotFoundError(f"Mandor dengan ID {mandor_id} tidak ditemukan")
        
        # Normalisasi quantity ke 2 desimal
        quantity = Decimal(str(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if quantity <= 0:
            raise ValidationError("Quantity harus lebih dari 0")
        
        # Create installed
        installed_data = {
            "material_id": material_id,
            "quantity": quantity,
            "tanggal_pasang": tanggal_pasang,
            "mandor_id": mandor_id,
            "stock_out_id": stock_out_id,
            "no_register": no_register,
            "evidence_paths": save_evidence_paths_to_db(evidence_paths),
            "created_by": created_by,
            "is_deleted": 0
        }
        
        # Tidak masukkan project_id karena kolom belum ada di database
        # TODO: Uncomment setelah migration project_id selesai dijalankan
        # if project_id is not None:
        #     installed_data["project_id"] = project_id
        
        installed = self.installed_repo.create(installed_data)
        if not installed:
            raise ValidationError("Gagal membuat data barang terpasang")
        
        return installed

    def create_return(
        self,
        mandor_id: int,
        material_id: int,
        quantity_kembali: Decimal,
        stock_out_id: Optional[int],
        tanggal_kembali: date,
        evidence_paths: List[str],
        created_by: int,
        quantity_kondisi_baik: Optional[Decimal] = None,
        quantity_kondisi_reject: Optional[Decimal] = None,
        project_id: Optional[int] = None
    ):
        """Create return record dengan validasi ketat:
        
        - stock_out_id wajib ada
        - stock_out harus ada dan tidak deleted
        - total quantity_kembali (termasuk yang sudah ada) tidak boleh melebihi quantity stock_out
        """
        # Validate material exists
        material = self.material_repo.get(material_id, project_id=project_id)
        if not material:
            raise NotFoundError(f"Material dengan ID {material_id} tidak ditemukan")
        
        # Normalisasi quantity ke 2 desimal
        quantity_kembali = Decimal(str(quantity_kembali)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if quantity_kondisi_baik is not None:
            quantity_kondisi_baik = Decimal(str(quantity_kondisi_baik)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if quantity_kondisi_reject is not None:
            quantity_kondisi_reject = Decimal(str(quantity_kondisi_reject)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if quantity_kembali <= 0:
            raise ValidationError("Quantity kembali harus lebih dari 0")

        # Validate mandor exists
        mandor = self.mandor_repo.get(mandor_id, project_id=project_id)
        if not mandor:
            raise NotFoundError(f"Mandor dengan ID {mandor_id} tidak ditemukan")

        # VALIDASI: stock_out_id wajib ada
        if stock_out_id is None:
            raise ValidationError("Nomor Barang Keluar wajib diisi untuk melakukan barang kembali")

        # Validate stock_out exists dan tidak deleted
        # Wajib: stock_out harus memiliki project_id dan sesuai dengan project aktif
        stock_out = self.stock_out_repo.get(stock_out_id)
        if not stock_out:
            raise NotFoundError(f"Stock out dengan ID {stock_out_id} tidak ditemukan")

        if getattr(stock_out, "project_id", None) is None:
            raise ValidationError(
                f"Stock out {getattr(stock_out, 'nomor_barang_keluar', stock_out_id)} tidak memiliki project_id"
            )
        if project_id is not None and stock_out.project_id != project_id:
            raise ValidationError(
                f"Stock out {stock_out.nomor_barang_keluar} bukan milik project ini"
            )
        
        if stock_out.is_deleted == 1:
            raise ValidationError(f"Stock out dengan nomor {stock_out.nomor_barang_keluar} sudah dihapus")

        # VALIDASI: Validasi consistency material dan mandor
        if stock_out.material_id != material_id:
            raise ValidationError(
                f"Material tidak sesuai. Stock out {stock_out.nomor_barang_keluar} "
                f"menggunakan material berbeda."
            )
        
        if stock_out.mandor_id != mandor_id:
            raise ValidationError(
                f"Mandor tidak sesuai. Stock out {stock_out.nomor_barang_keluar} "
                f"menggunakan mandor berbeda."
            )

        # VALIDASI: Hitung batas maksimal barang kembali berbasis
        # Sisa Barang Kembali = Barang Keluar - Terpasang
        total_installed_for_stock_out = self.installed_repo.get_total_quantity_by_stock_out(stock_out_id)
        max_return_allowed = max(0, (stock_out.quantity or 0) - (total_installed_for_stock_out or 0))

        # Hitung total quantity_kembali yang sudah ada untuk stock_out_id ini
        total_quantity_kembali_existing = self.return_repo.get_total_quantity_by_stock_out(stock_out_id)
        total_quantity_kembali_new = total_quantity_kembali_existing + quantity_kembali

        # Validasi: total kembali tidak boleh melebihi Sisa Barang Kembali
        if total_quantity_kembali_new > max_return_allowed:
            available_quantity = max_return_allowed - total_quantity_kembali_existing
            raise ValidationError(
                f"Quantity kembali melebihi sisa barang kembali. "
                f"Stock out {stock_out.nomor_barang_keluar} qty keluar: {stock_out.quantity}. "
                f"Total terpasang: {total_installed_for_stock_out}. "
                f"Maksimal bisa dikembalikan: {max_return_allowed}. "
                f"Sudah dikembalikan: {total_quantity_kembali_existing}. "
                f"Sisa yang bisa dikembalikan: {max(0, available_quantity)}. "
                f"Anda mencoba mengembalikan: {quantity_kembali}."
            )
        
        # Validate kondisi fields
        if quantity_kondisi_baik is not None and quantity_kondisi_baik < 0:
            raise ValidationError("Quantity kondisi baik tidak boleh negatif")
        
        if quantity_kondisi_reject is not None and quantity_kondisi_reject < 0:
            raise ValidationError("Quantity kondisi reject tidak boleh negatif")
        
        # Validasi: quantity_kondisi_baik + quantity_kondisi_reject tidak boleh melebihi quantity_kembali
        if quantity_kondisi_baik and quantity_kondisi_reject:
            total_kondisi = quantity_kondisi_baik + quantity_kondisi_reject
            if total_kondisi > quantity_kembali:
                raise ValidationError(
                    f"Total kondisi (baik + reject) tidak boleh melebihi quantity kembali. "
                    f"Quantity kembali: {quantity_kembali}, Total kondisi: {total_kondisi}"
                )
        
        # Create return
        return_data = {
            "mandor_id": mandor_id,
            "material_id": material_id,
            "quantity_kembali": quantity_kembali,
            "quantity_kondisi_baik": quantity_kondisi_baik or 0,
            "quantity_kondisi_reject": quantity_kondisi_reject or 0,
            "stock_out_id": stock_out_id,
            "tanggal_kembali": tanggal_kembali,
            # Hindari konversi ganda; route akan update evidence_paths setelah ID diketahui
            "evidence_paths": None,
            "created_by": created_by,
            "is_deleted": 0
        }
        
        if project_id is not None:
            return_data["project_id"] = project_id
        
        return_item = self.return_repo.create(return_data)
        if not return_item:
            raise ValidationError("Gagal membuat data barang pengembalian")
        
        return return_item

    def get_stock_balance(self, material_id: Optional[int] = None, search: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, project_id: Optional[int] = None) -> dict:
        """Calculate current stock balance per material dengan optional date filter dan project filter"""
        if material_id:
            materials = [self.material_repo.get(material_id, project_id=project_id)]
            if not materials[0]:
                raise NotFoundError(f"Material dengan ID {material_id} tidak ditemukan")
        elif search:
            materials = self.material_repo.search_by_name_or_code(search_term=search, skip=0, limit=10000, project_id=project_id)
        else:
            materials = self.material_repo.get_active_materials(skip=0, limit=10000, project_id=project_id)
        
        balance_data = []
        
        for material in materials:
            # Get stock ins dengan date filter dan project filter jika ada
            if start_date or end_date:
                if start_date and end_date:
                    stock_ins = self.stock_in_repo.get_by_date_range(start_date, end_date, skip=0, limit=10000)
                    stock_ins = self._filter_by_material_and_not_deleted(stock_ins, material.id)
                else:
                    stock_ins = self.stock_in_repo.get_by_material(material.id, skip=0, limit=10000)
                    stock_ins = self._filter_not_deleted(stock_ins)
                    if start_date:
                        stock_ins = [si for si in stock_ins if si.tanggal_masuk >= start_date]
                    if end_date:
                        stock_ins = [si for si in stock_ins if si.tanggal_masuk <= end_date]
            else:
                stock_ins = self.stock_in_repo.get_by_material(material.id, skip=0, limit=10000)
                stock_ins = self._filter_not_deleted(stock_ins)
            
            # Get stock outs dengan date filter
            # TIDAK filter project_id karena data lama mungkin punya project_id NULL
            # Filter hanya berdasarkan material_id (material sudah terfilter project_id)
            if start_date or end_date:
                if start_date and end_date:
                    stock_outs = self.stock_out_repo.get_by_date_range(start_date, end_date, skip=0, limit=10000)
                    stock_outs = self._filter_by_material_and_not_deleted(stock_outs, material.id)
                else:
                    stock_outs = self.stock_out_repo.get_all_by_material(material.id, skip=0, limit=10000)
                    if start_date:
                        stock_outs = [so for so in stock_outs if so.tanggal_keluar >= start_date]
                    if end_date:
                        stock_outs = [so for so in stock_outs if so.tanggal_keluar <= end_date]
            else:
                stock_outs = self.stock_out_repo.get_all_by_material(material.id, skip=0, limit=10000)
            
            # Get returns dengan date filter
            # TIDAK filter project_id karena data lama mungkin punya project_id NULL
            # Filter hanya berdasarkan material_id (material sudah terfilter project_id)
            if start_date or end_date:
                if start_date and end_date:
                    returns = self.return_repo.get_by_date_range(start_date, end_date, skip=0, limit=10000, project_id=None)
                    returns = self._filter_by_material_and_not_deleted(returns, material.id)
                else:
                    returns = self.return_repo.get_all_by_material(material.id, skip=0, limit=10000)
                    if start_date:
                        returns = [r for r in returns if r.tanggal_kembali >= start_date]
                    if end_date:
                        returns = [r for r in returns if r.tanggal_kembali <= end_date]
            else:
                returns = self.return_repo.get_all_by_material(material.id, skip=0, limit=10000)
            
            # Get installed items dengan date filter dan project filter jika ada
            # Filter selalu menggunakan project_id melalui material.project_id
            if start_date or end_date:
                if start_date and end_date:
                    installed_items = self.installed_repo.get_by_date_range(start_date, end_date, skip=0, limit=10000, project_id=project_id)
                    installed_items = self._filter_by_material_and_not_deleted(installed_items, material.id)
                else:
                    installed_items = self.installed_repo.get_all_by_project(skip=0, limit=10000, project_id=project_id)
                    installed_items = self._filter_by_material_and_not_deleted(installed_items, material.id)
                    if start_date:
                        installed_items = [i for i in installed_items if i.tanggal_pasang >= start_date]
                    if end_date:
                        installed_items = [i for i in installed_items if i.tanggal_pasang <= end_date]
            else:
                installed_items = self.installed_repo.get_all_by_project(skip=0, limit=10000, project_id=project_id)
                installed_items = self._filter_by_material_and_not_deleted(installed_items, material.id)
            
            # Get returns yang sudah dikeluarkan kembali (is_released = 1) untuk retur keluar
            # Filter dari returns yang sudah diambil sebelumnya
            returns_released = [r for r in returns if getattr(r, 'is_released', 0) == 1]
            
            total_in = sum(si.quantity for si in stock_ins)
            total_out = sum(so.quantity for so in stock_outs)
            total_return = sum(r.quantity_kembali for r in returns)
            total_retur_keluar = sum(r.quantity_kembali for r in returns_released)
            total_terpasang = sum(i.quantity for i in installed_items)
            total_kondisi_baik = sum((r.quantity_kondisi_baik or 0) for r in returns)
            total_kondisi_reject = sum((r.quantity_kondisi_reject or 0) for r in returns)
            
            # Rumus Stock Balance yang Dinamis & Best Practice
            # Keluar Efektif = Keluar - Retur Keluar (retur keluar mengurangi efek keluar karena sudah kembali ke gudang)
            keluar_efektif = total_out - total_retur_keluar
            # Stock Saat Ini = Masuk - Keluar Efektif + Kembali
            current_stock = total_in - keluar_efektif + total_return
            # Stok Ready = Stock Saat Ini - Kondisi Reject (barang reject tidak bisa dikeluarkan)
            stock_ready = max(0, current_stock - total_kondisi_reject)
            
            balance_data.append({
                "material_id": material.id,
                "kode_barang": material.kode_barang,
                "nama_barang": material.nama_barang,
                "satuan": material.satuan,
                "total_masuk": total_in,
                "total_keluar": total_out,
                "total_terpasang": total_terpasang,
                "total_kembali": total_return,
                "total_retur_keluar": total_retur_keluar,
                "total_kondisi_baik": total_kondisi_baik,
                "total_kondisi_reject": total_kondisi_reject,
                "stock_ready": stock_ready,
                "stock_saat_ini": current_stock
            })
        
        return balance_data if material_id is None else balance_data[0]

    def _create_stock_out_with_retry(
        self,
        stock_out_data: Dict[str, Any],
        tanggal_keluar: date,
        max_retries: int = 5
    ):
        """Create stock out with retry mechanism to handle race condition in number generation.
        
        Jika terjadi duplicate nomor_barang_keluar, akan generate nomor baru dan retry.
        """
        for attempt in range(max_retries):
            try:
                stock_out = self.stock_out_repo.create(stock_out_data)
                if not stock_out:
                    raise ValidationError("Gagal membuat data barang keluar")
                return stock_out
            except IntegrityError as e:
                error_str = str(e).lower()
                # Cek jika error karena duplicate nomor_barang_keluar
                is_duplicate_nomor = (
                    "duplicate entry" in error_str and "uq_stock_out_number" in error_str
                ) or (
                    "duplicate" in error_str and ("nomor_barang_keluar" in error_str or "stock_out_number" in error_str)
                )
                if is_duplicate_nomor:
                    if attempt < max_retries - 1:
                        # Generate nomor baru
                        old_nomor = stock_out_data.get('nomor_barang_keluar')
                        self.logger.warning(
                            f"Duplicate nomor_barang_keluar detected: {old_nomor}. "
                            f"Retrying with new number (attempt {attempt + 1}/{max_retries})"
                        )
                        self.db.rollback()
                        # Expire all objects to ensure fresh query
                        self.db.expire_all()
                        # Generate nomor baru - query akan fresh setelah expire_all
                        # Get project_id from stock_out_data if available
                        retry_project_id = stock_out_data.get("project_id")
                        next_num = self.stock_out_repo.get_next_number_for_date(tanggal_keluar, project_id=retry_project_id)
                        date_str = tanggal_keluar.strftime("%Y%m%d")
                        new_nomor = f"JRGS-KDL-{date_str}-{next_num:04d}"
                        stock_out_data["nomor_barang_keluar"] = new_nomor
                        self.logger.info(f"Generated new nomor: {new_nomor} (was {old_nomor})")
                        # Small delay to avoid tight loop and allow DB to sync
                        time.sleep(0.2)
                        continue
                    else:
                        # Max retries reached
                        self.logger.error(
                            f"Failed to create stock_out after {max_retries} attempts. "
                            f"Last nomor: {stock_out_data.get('nomor_barang_keluar')}"
                        )
                        raise ValidationError(
                            f"Gagal membuat data barang keluar: nomor duplikat setelah {max_retries} percobaan. "
                            f"Silakan coba lagi."
                        )
                else:
                    # Other integrity error, re-raise
                    self.logger.error(f"Integrity error creating stock_out: {str(e)}")
                    self.db.rollback()
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error creating stock_out: {str(e)}")
                self.db.rollback()
                raise ValidationError(f"Gagal membuat data barang keluar: {str(e)}")
        
        # Should not reach here
        raise ValidationError("Gagal membuat data barang keluar setelah beberapa percobaan")

    def release_return_to_stock_out(
        self,
        return_id: int,
        tanggal_keluar: date,
        evidence_paths: List[str],
        created_by: int,
        project_id: Optional[int] = None
    ):
        """Create stock out from an existing return and mark it released.

        Uses the full quantity_kembali, same mandor_id and material_id.
        """
        # Get return
        ret = self.return_repo.get(return_id, project_id=project_id)
        if not ret or ret.is_deleted == 1:
            raise NotFoundError(f"Return dengan ID {return_id} tidak ditemukan")

        if getattr(ret, 'is_released', 0) == 1:
            raise ValidationError("Return ini sudah dikeluarkan kembali")

        # Validate material exists
        material = self.material_repo.get(ret.material_id, project_id=project_id)
        if not material:
            raise NotFoundError(f"Material dengan ID {ret.material_id} tidak ditemukan")

        if ret.quantity_kembali <= 0:
            raise ValidationError("Quantity kembali pada return tidak valid")

        # Use project_id from return if not provided
        if project_id is None:
            project_id = ret.project_id

        # Generate nomor barang keluar
        next_num = self.stock_out_repo.get_next_number_for_date(tanggal_keluar, project_id=project_id)
        date_str = tanggal_keluar.strftime("%Y%m%d")
        nomor_barang_keluar = f"JRGS-KDL-{date_str}-{next_num:04d}"

        # Create stock out from return with retry mechanism
        stock_out_data = {
            "project_id": project_id,
            "nomor_barang_keluar": nomor_barang_keluar,
            "mandor_id": ret.mandor_id,
            "material_id": ret.material_id,
            "quantity": ret.quantity_kembali,
            "tanggal_keluar": tanggal_keluar,
            "evidence_paths": save_evidence_paths_to_db(evidence_paths),
            "created_by": created_by,
            "is_deleted": 0
        }

        stock_out = self._create_stock_out_with_retry(stock_out_data, tanggal_keluar)

        # Update return: set stock_out_id and is_released=1
        self.return_repo.update(ret.id, {
            "stock_out_id": stock_out.id,
            "is_released": 1
        })

        return stock_out

    def create_stock_in_bulk(
        self,
        nomor_invoice: str,
        tanggal_masuk: date,
        items: List[dict],
        evidence_paths: List[str],
        created_by: int,
        surat_jalan_paths: List[str] = None,
        material_datang_paths: List[str] = None,
        project_id: Optional[int] = None
    ):
        """Create multiple stock in records under one invoice.

        items: List of { "material_id": int, "quantity": int }
        Evidence paths, surat_jalan_paths, dan material_datang_paths applied to all records.
        """
        self.logger.info(f"create_stock_in_bulk: Starting for invoice {nomor_invoice}, {len(items)} items, created_by={created_by}")
        
        if not items:
            self.logger.warning("create_stock_in_bulk: Empty items list")
            raise ValidationError("Items wajib diisi minimal 1")

        # Normalize and validate structure
        normalized = []
        for idx, it in enumerate(items):
            try:
                # DEBUG: Log raw item sebelum konversi
                raw_quantity = it.get("quantity")
                raw_material_id = it.get("material_id")
                self.logger.info(f"[DEBUG create_stock_in_bulk] Item {idx+1} BEFORE conversion: material_id={raw_material_id} (type: {type(raw_material_id)}), quantity={raw_quantity} (type: {type(raw_quantity)})")
                
                material_id = int(it.get("material_id"))
                # Gunakan Decimal untuk presisi dan kuantisasi ke 2 desimal
                quantity = Decimal(str(it.get("quantity"))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                
                # DEBUG: Log setelah konversi
                self.logger.info(f"[DEBUG create_stock_in_bulk] Item {idx+1} AFTER conversion: material_id={material_id}, quantity={quantity}")
                
                # Validasi quantity tidak berubah setelah konversi (dengan toleransi untuk float)
                if isinstance(raw_quantity, (int, float)):
                    if abs(float(raw_quantity) - float(quantity)) > 0.001:
                        self.logger.error(f"[ERROR create_stock_in_bulk] Quantity changed after conversion! Original: {raw_quantity}, Converted: {quantity}")
                        raise ValidationError(f"Quantity pada item ke-{idx+1} berubah setelah konversi: {raw_quantity} -> {quantity}")
                elif isinstance(raw_quantity, str):
                    parsed_from_str = float(raw_quantity)
                    if abs(parsed_from_str - float(quantity)) > 0.001:
                        self.logger.error(f"[ERROR create_stock_in_bulk] Quantity mismatch! String: '{raw_quantity}', Parsed: {parsed_from_str}, Final: {quantity}")
                        raise ValidationError(f"Quantity pada item ke-{idx+1} tidak konsisten: '{raw_quantity}' -> {quantity}")
                
                self.logger.debug(f"Item {idx+1}: material_id={material_id}, quantity={quantity}")
            except (ValueError, TypeError) as e:
                self.logger.error(f"Item {idx+1} validation error: {str(e)}, item={it}")
                raise ValidationError(f"Item ke-{idx+1} tidak valid: material_id/quantity bukan angka")
            except Exception as e:
                self.logger.error(f"Item {idx+1} unexpected error: {str(e)}", exc_info=True)
                raise ValidationError(f"Item ke-{idx+1} tidak valid: material_id/quantity bukan angka")

            if quantity <= 0:
                self.logger.warning(f"Item {idx+1}: Invalid quantity {quantity}")
                raise ValidationError(f"Quantity pada item ke-{idx+1} harus lebih dari 0")
            normalized.append({"material_id": material_id, "quantity": quantity})

        # Check duplicate materials
        material_ids = [it["material_id"] for it in normalized]
        unique_material_ids = set(material_ids)
        if len(material_ids) != len(unique_material_ids):
            duplicates = [mid for mid in material_ids if material_ids.count(mid) > 1]
            self.logger.warning(f"Duplicate materials detected: {duplicates}")
            raise ValidationError("Terdapat duplikat material pada items. Mohon gabungkan atau hilangkan duplikat.")

        # Validate all materials exist
        self.logger.info(f"Validating {len(unique_material_ids)} unique materials")
        for mid in unique_material_ids:
            material = self.material_repo.get(mid, project_id=project_id)
            if not material:
                self.logger.error(f"Material ID {mid} not found in database")
                raise NotFoundError(f"Material dengan ID {mid} tidak ditemukan")
            if material.is_active == 0:
                self.logger.warning(f"Material ID {mid} is inactive")
                raise ValidationError(f"Material dengan ID {mid} tidak aktif")

        # Prepare file paths JSON
        evidence_paths_json = save_evidence_paths_to_db(evidence_paths)
        surat_jalan_paths_json = save_evidence_paths_to_db(surat_jalan_paths) if surat_jalan_paths else None
        material_datang_paths_json = save_evidence_paths_to_db(material_datang_paths) if material_datang_paths else None
        self.logger.debug(f"Evidence paths JSON: {evidence_paths_json}")
        self.logger.debug(f"Surat jalan paths JSON: {surat_jalan_paths_json}")
        self.logger.debug(f"Material datang paths JSON: {material_datang_paths_json}")

        created_records = []
        failed_items = []
        
        # Commit per item to avoid nested transaction issues
        for idx, it in enumerate(normalized):
            try:
                self.logger.info(f"Creating stock_in record {idx+1}/{len(normalized)}: material_id={it['material_id']}, quantity={it['quantity']}")
                
                # DEBUG: Log data sebelum create
                self.logger.info(f"[DEBUG] Creating stock_in for item {idx+1}: quantity={it['quantity']} (type: {type(it['quantity'])})")
                
                stock_in_data = {
                    "nomor_invoice": nomor_invoice,
                    "material_id": it["material_id"],
                    "quantity": it["quantity"],
                    "tanggal_masuk": tanggal_masuk,
                    "evidence_paths": evidence_paths_json,
                    "surat_jalan_paths": surat_jalan_paths_json,
                    "material_datang_paths": material_datang_paths_json,
                    "created_by": created_by,
                    "is_deleted": 0
                }
                
                if project_id is not None:
                    stock_in_data["project_id"] = project_id
                
                try:
                    stock_in = self.stock_in_repo.create(stock_in_data)
                    if not stock_in:
                        self.logger.error(f"Failed to create stock_in for item {idx+1}: repository.create returned None")
                        raise ValidationError(f"Gagal membuat data barang masuk untuk item ke-{idx+1}")
                    
                    # DEBUG: Log quantity setelah create (dari database)
                    self.logger.info(f"[DEBUG] Successfully created stock_in record ID: {stock_in.id}, quantity in DB: {stock_in.quantity} (type: {type(stock_in.quantity)})")
                    
                    # Validasi quantity di database sama dengan yang dikirim
                    if stock_in.quantity != it["quantity"]:
                        self.logger.error(f"[ERROR] Quantity mismatch after DB save! Sent: {it['quantity']}, Saved in DB: {stock_in.quantity}")
                    
                    created_records.append(stock_in)
                    
                except IntegrityError as e:
                    self.logger.error(f"Integrity error creating stock_in for item {idx+1}: {str(e)}", exc_info=True)
                    self.db.rollback()
                    error_msg = str(e).lower()
                    if "foreign key constraint" in error_msg:
                        if "materials" in error_msg:
                            raise ValidationError(f"Material dengan ID {it['material_id']} tidak ditemukan atau tidak valid")
                        elif "users" in error_msg:
                            raise ValidationError(f"User dengan ID {created_by} tidak ditemukan atau tidak valid")
                        else:
                            raise ValidationError(f"Data referensi tidak valid untuk item ke-{idx+1}")
                    elif "duplicate" in error_msg or "unique" in error_msg:
                        raise ValidationError(f"Data duplikat untuk item ke-{idx+1}. Periksa nomor invoice atau data lain.")
                    else:
                        raise ValidationError(f"Gagal menyimpan item ke-{idx+1}: {str(e)}")
                        
                except SQLAlchemyError as e:
                    self.logger.error(f"SQLAlchemy error creating stock_in for item {idx+1}: {str(e)}", exc_info=True)
                    self.db.rollback()
                    raise ValidationError(f"Gagal membuat data barang masuk untuk item ke-{idx+1}: {str(e)}")
                    
            except (ValidationError, NotFoundError):
                # Re-raise validation and not found errors as-is
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error creating stock_in for item {idx+1}: {str(e)}", exc_info=True)
                self.db.rollback()
                failed_items.append(idx+1)
                # Don't raise here, continue with other items but log the failure
                # In a more robust implementation, we might want to rollback all or continue partial
                # For now, we'll raise on first error
                raise ValidationError(f"Gagal membuat data barang masuk untuk item ke-{idx+1}: {str(e)}")

        if failed_items:
            self.logger.warning(f"Some items failed: {failed_items}")
            
        self.logger.info(f"Successfully created {len(created_records)}/{len(normalized)} stock_in records")
        return created_records

    def create_stock_out_bulk(
        self,
        mandor_id: int,
        tanggal_keluar: date,
        items: List[dict],
        evidence_paths: List[str],
        created_by: int,
        surat_permohonan_paths: List[str] = None,
        surat_serah_terima_paths: List[str] = None,
        nomor_surat_permintaan: Optional[str] = None,
        project_id: Optional[int] = None
    ):
        """Create multiple stock out records for one mandor on one date.

        items: List of { "material_id": int, "quantity": int }
        Evidence paths, surat_permohonan_paths, dan surat_serah_terima_paths applied to all records.
        Jika nomor_surat_permintaan diisi, semua item akan menggunakan nomor tersebut dengan suffix -1, -2, dst.
        Jika tidak, setiap item gets its own auto-generated nomor_barang_keluar.
        """
        self.logger.info(f"create_stock_out_bulk: Starting for mandor {mandor_id}, {len(items)} items, created_by={created_by}, nomor_surat_permintaan={nomor_surat_permintaan}")
        
        if not items:
            self.logger.warning("create_stock_out_bulk: Empty items list")
            raise ValidationError("Items wajib diisi minimal 1")

        # Validate mandor exists
        mandor = self.mandor_repo.get(mandor_id, project_id=project_id)
        if not mandor:
            raise NotFoundError(f"Mandor dengan ID {mandor_id} tidak ditemukan")
        if mandor.is_active == 0:
            raise ValidationError(f"Mandor dengan ID {mandor_id} tidak aktif")
        
        # Jika nomor_surat_permintaan diisi, validasi terlebih dahulu
        if nomor_surat_permintaan:
            surat_permintaan = self.surat_permintaan_repo.get_by_nomor_surat(nomor_surat_permintaan, project_id=project_id)
            if not surat_permintaan:
                raise NotFoundError(f"Surat permintaan dengan nomor {nomor_surat_permintaan} tidak ditemukan")
            if surat_permintaan.is_deleted == 1:
                raise ValidationError(f"Surat permintaan dengan nomor {nomor_surat_permintaan} sudah dihapus")

        # Normalize and validate structure
        normalized = []
        for idx, it in enumerate(items):
            try:
                material_id = int(it.get("material_id"))
                quantity = Decimal(str(it.get("quantity"))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                self.logger.debug(f"Item {idx+1}: material_id={material_id}, quantity={quantity}")
            except (ValueError, TypeError) as e:
                self.logger.error(f"Item {idx+1} validation error: {str(e)}, item={it}")
                raise ValidationError(f"Item ke-{idx+1} tidak valid: material_id/quantity bukan angka")
            except Exception as e:
                self.logger.error(f"Item {idx+1} unexpected error: {str(e)}", exc_info=True)
                raise ValidationError(f"Item ke-{idx+1} tidak valid: material_id/quantity bukan angka")

            if quantity <= 0:
                self.logger.warning(f"Item {idx+1}: Invalid quantity {quantity}")
                raise ValidationError(f"Quantity pada item ke-{idx+1} harus lebih dari 0")
            normalized.append({"material_id": material_id, "quantity": quantity})

        # Check duplicate materials
        material_ids = [it["material_id"] for it in normalized]
        unique_material_ids = set(material_ids)
        if len(material_ids) != len(unique_material_ids):
            duplicates = [mid for mid in material_ids if material_ids.count(mid) > 1]
            self.logger.warning(f"Duplicate materials detected: {duplicates}")
            raise ValidationError("Terdapat duplikat material pada items. Mohon gabungkan atau hilangkan duplikat.")

        # Validate all materials exist and get stock balances
        self.logger.info(f"Validating {len(unique_material_ids)} unique materials and checking stock")
        material_stocks = {}
        for mid in unique_material_ids:
            material = self.material_repo.get(mid)
            if not material:
                self.logger.error(f"Material ID {mid} not found in database")
                raise NotFoundError(f"Material dengan ID {mid} tidak ditemukan")
            if material.is_active == 0:
                self.logger.warning(f"Material ID {mid} is inactive")
                raise ValidationError(f"Material dengan ID {mid} tidak aktif")
            
            # Get current stock for this material
            balance = self.get_stock_balance(material_id=mid)
            current_stock = balance.get("stock_saat_ini", 0) if isinstance(balance, dict) else 0
            material_stocks[mid] = current_stock
            self.logger.debug(f"Material ID {mid}: current stock = {current_stock}")

        # Validate stock availability for each item
        for idx, it in enumerate(normalized):
            material_id = it["material_id"]
            quantity = it["quantity"]
            current_stock = material_stocks.get(material_id, 0)
            
            if current_stock < quantity:
                material_info = self.material_repo.get(material_id)
                material_name = f"{material_info.kode_barang} - {material_info.nama_barang}" if material_info else f"ID {material_id}"
                self.logger.warning(f"Item {idx+1}: Insufficient stock. Required: {quantity}, Available: {current_stock}")
                raise ValidationError(
                    f"Stok tidak cukup untuk material {material_name} pada item ke-{idx+1}. "
                    f"Stok tersedia: {current_stock}, dibutuhkan: {quantity}"
                )

        # Prepare file paths JSON
        evidence_paths_json = save_evidence_paths_to_db(evidence_paths)
        surat_permohonan_paths_json = save_evidence_paths_to_db(surat_permohonan_paths) if surat_permohonan_paths else None
        surat_serah_terima_paths_json = save_evidence_paths_to_db(surat_serah_terima_paths) if surat_serah_terima_paths else None
        self.logger.debug(f"Evidence paths JSON: {evidence_paths_json}")
        self.logger.debug(f"Surat permohonan paths JSON: {surat_permohonan_paths_json}")
        self.logger.debug(f"Surat serah terima paths JSON: {surat_serah_terima_paths_json}")

        created_records = []
        failed_items = []
        
        # Commit per item to avoid nested transaction issues
        for idx, it in enumerate(normalized):
            try:
                self.logger.info(f"Creating stock_out record {idx+1}/{len(normalized)}: material_id={it['material_id']}, quantity={it['quantity']}")
                
                # Generate nomor barang keluar for this item
                if nomor_surat_permintaan:
                    # Jika menggunakan nomor surat permintaan, tambahkan suffix untuk multiple items
                    if len(normalized) > 1:
                        nomor_barang_keluar = f"{nomor_surat_permintaan}-{idx+1}"
                    else:
                        nomor_barang_keluar = nomor_surat_permintaan
                    
                    # Cek apakah nomor sudah digunakan
                    existing_stock_out = self.stock_out_repo.get_by_nomor(nomor_barang_keluar)
                    if existing_stock_out and existing_stock_out.is_deleted == 0:
                        raise ValidationError(f"Nomor {nomor_barang_keluar} sudah digunakan untuk stock out lain")
                else:
                    # Generate nomor barang keluar otomatis
                    next_num = self.stock_out_repo.get_next_number_for_date(tanggal_keluar, project_id=project_id)
                    date_str = tanggal_keluar.strftime("%Y%m%d")
                    nomor_barang_keluar = f"JRGS-KDL-{date_str}-{next_num:04d}"
                
                stock_out_data = {
                    "nomor_barang_keluar": nomor_barang_keluar,
                    "mandor_id": mandor_id,
                    "material_id": it["material_id"],
                    "quantity": it["quantity"],
                    "tanggal_keluar": tanggal_keluar,
                    "evidence_paths": evidence_paths_json,
                    "surat_permohonan_paths": surat_permohonan_paths_json,
                    "surat_serah_terima_paths": surat_serah_terima_paths_json,
                    "created_by": created_by,
                    "is_deleted": 0
                }
                
                if project_id is not None:
                    stock_out_data["project_id"] = project_id
                
                try:
                    # Use retry mechanism for creating stock_out to handle race conditions
                    stock_out = self._create_stock_out_with_retry(stock_out_data, tanggal_keluar)
                    self.logger.info(f"Successfully created stock_out record ID: {stock_out.id}, Nomor: {stock_out.nomor_barang_keluar}")
                    created_records.append(stock_out)
                    
                except IntegrityError as e:
                    # This should rarely happen now due to retry mechanism, but keep for other integrity errors
                    self.logger.error(f"Integrity error creating stock_out for item {idx+1}: {str(e)}", exc_info=True)
                    self.db.rollback()
                    error_msg = str(e).lower()
                    if "foreign key constraint" in error_msg:
                        if "materials" in error_msg:
                            raise ValidationError(f"Material dengan ID {it['material_id']} tidak ditemukan atau tidak valid")
                        elif "mandors" in error_msg:
                            raise ValidationError(f"Mandor dengan ID {mandor_id} tidak ditemukan atau tidak valid")
                        elif "users" in error_msg:
                            raise ValidationError(f"User dengan ID {created_by} tidak ditemukan atau tidak valid")
                        else:
                            raise ValidationError(f"Data referensi tidak valid untuk item ke-{idx+1}")
                    else:
                        raise ValidationError(f"Gagal menyimpan item ke-{idx+1}: {str(e)}")
                        
                except SQLAlchemyError as e:
                    self.logger.error(f"SQLAlchemy error creating stock_out for item {idx+1}: {str(e)}", exc_info=True)
                    self.db.rollback()
                    raise ValidationError(f"Gagal membuat data barang keluar untuk item ke-{idx+1}: {str(e)}")
                    
            except (ValidationError, NotFoundError):
                # Re-raise validation and not found errors as-is
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error creating stock_out for item {idx+1}: {str(e)}", exc_info=True)
                self.db.rollback()
                failed_items.append(idx+1)
                raise ValidationError(f"Gagal membuat data barang keluar untuk item ke-{idx+1}: {str(e)}")

        if failed_items:
            self.logger.warning(f"Some items failed: {failed_items}")
            
        self.logger.info(f"Successfully created {len(created_records)}/{len(normalized)} stock_out records")
        return created_records