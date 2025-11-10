from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import date


# Surat Jalan Item Schemas
class SuratJalanItemRequest(BaseModel):
    nama_barang: str = Field(..., min_length=1, max_length=255)
    qty: Decimal = Field(..., ge=0)
    keterangan: Optional[str] = Field(None, max_length=500)


class SuratJalanItemResponse(BaseModel):
    id: int
    nama_barang: str
    qty: Decimal
    keterangan: Optional[str] = None

    class Config:
        from_attributes = True


# Surat Jalan Schemas
class SuratJalanCreateRequest(BaseModel):
    kepada: str = Field(..., min_length=1, max_length=255)
    tanggal_pengiriman: date
    items: List[SuratJalanItemRequest] = Field(..., min_items=1)
    nama_pemberi: Optional[str] = Field(None, max_length=255)
    nama_penerima: Optional[str] = Field(None, max_length=255)
    tanggal_diterima: Optional[date] = None
    nomor_surat_permintaan: Optional[str] = Field(None, max_length=255)  # Relasi ke surat permintaan
    nomor_barang_keluar: Optional[str] = Field(None, max_length=255)  # Nomor barang keluar yang akan digunakan sebagai nomor_form


class SuratJalanUpdateRequest(BaseModel):
    kepada: Optional[str] = Field(None, min_length=1, max_length=255)
    tanggal_pengiriman: Optional[date] = None
    items: Optional[List[SuratJalanItemRequest]] = None
    nama_pemberi: Optional[str] = Field(None, max_length=255)
    nama_penerima: Optional[str] = Field(None, max_length=255)
    tanggal_diterima: Optional[date] = None


class SuratJalanResponse(BaseModel):
    id: int
    nomor_form: str
    kepada: str
    tanggal_pengiriman: date
    nama_pemberi: Optional[str] = None
    nama_penerima: Optional[str] = None
    tanggal_diterima: Optional[date] = None
    nomor_surat_permintaan: Optional[str] = None  # Relasi ke surat permintaan
    nomor_barang_keluar: Optional[str] = None  # Nomor barang keluar yang digunakan
    stock_out_id: Optional[int] = None  # Foreign key ke stock_out
    project_id: int
    created_by: int
    created_at: str
    updated_at: str
    items: List[SuratJalanItemResponse] = []
    project: Optional[dict] = None
    creator: Optional[dict] = None

    class Config:
        from_attributes = True

