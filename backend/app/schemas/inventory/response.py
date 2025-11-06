from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


# Material Response
class MaterialResponse(BaseModel):
    id: int
    kode_barang: Optional[str]
    nama_barang: str
    satuan: str
    kategori: Optional[str]
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Mandor Response
class MandorResponse(BaseModel):
    id: int
    nama: str
    nomor_kontak: Optional[str]
    alamat: Optional[str]
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Stock In Response
class MaterialBasicResponse(BaseModel):
    id: int
    kode_barang: Optional[str]
    nama_barang: str
    satuan: str

    class Config:
        from_attributes = True


class MandorBasicResponse(BaseModel):
    id: int
    nama: str

    class Config:
        from_attributes = True


class StockInResponse(BaseModel):
    id: int
    nomor_invoice: str
    material_id: int
    material: Optional[MaterialBasicResponse] = None
    quantity: float
    tanggal_masuk: date
    evidence_paths: Optional[str] = None
    surat_jalan_paths: Optional[str] = None
    material_datang_paths: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Stock Out Response
class StockOutResponse(BaseModel):
    id: int
    nomor_barang_keluar: str
    mandor_id: int
    mandor: Optional[MandorBasicResponse] = None
    material_id: int
    material: Optional[MaterialBasicResponse] = None
    quantity: float
    tanggal_keluar: date
    evidence_paths: Optional[str] = None
    surat_permohonan_paths: Optional[str] = None
    surat_serah_terima_paths: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Installed Response
class InstalledResponse(BaseModel):
    id: int
    material_id: int
    material: Optional[MaterialBasicResponse] = None
    quantity: float
    tanggal_pasang: date
    mandor_id: int
    mandor: Optional[MandorBasicResponse] = None
    stock_out_id: Optional[int]
    stock_out: Optional["StockOutBasicResponse"] = None
    evidence_paths: Optional[str] = None
    no_register: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Return Response
class StockOutBasicResponse(BaseModel):
    id: int
    nomor_barang_keluar: str

    class Config:
        from_attributes = True


class ReturnResponse(BaseModel):
    id: int
    mandor_id: int
    mandor: Optional[MandorBasicResponse] = None
    material_id: int
    material: Optional[MaterialBasicResponse] = None
    quantity_kembali: float
    quantity_kondisi_baik: Optional[float] = None
    quantity_kondisi_reject: Optional[float] = None
    stock_out_id: Optional[int] = None
    stock_out: Optional[StockOutBasicResponse] = None
    tanggal_kembali: date
    evidence_paths: Optional[str] = None
    is_released: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Stock Balance Response
class StockBalanceResponse(BaseModel):
    material_id: int
    kode_barang: str
    nama_barang: str
    satuan: str
    total_masuk: float
    total_keluar: float
    total_terpasang: float
    total_kembali: float
    total_kondisi_baik: float
    total_kondisi_reject: float
    stock_ready: float
    stock_saat_ini: float


# Discrepancy Response
class DiscrepancyResponse(BaseModel):
    mandor_id: int
    mandor_nama: str
    material_id: int
    material_kode: str
    material_nama: str
    barang_keluar: float
    barang_terpasang: float
    barang_kembali_dicatat: float
    selisih_seharusnya: float
    selisih_aktual: float
    status: str


# Notification Response
class NotificationResponse(BaseModel):
    id: int
    mandor_id: int
    mandor_nama: Optional[str] = None
    material_id: int
    material_nama: Optional[str] = None
    title: str
    message: str
    barang_keluar: float
    barang_terpasang: float
    selisih: float
    status: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# List Response with Pagination
class PaginatedResponse(BaseModel):
    items: List[BaseModel]
    total: int
    page: int
    size: int
    pages: int

