from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date


# Material Schemas
class MaterialCreateRequest(BaseModel):
    kode_barang: Optional[str] = Field(None, min_length=1, max_length=100)
    nama_barang: str = Field(..., min_length=1, max_length=255)
    satuan: str = Field(..., min_length=1, max_length=50)
    kategori: Optional[str] = Field(None, max_length=100)


class MaterialUpdateRequest(BaseModel):
    kode_barang: Optional[str] = Field(None, min_length=1, max_length=100)
    nama_barang: Optional[str] = Field(None, min_length=1, max_length=255)
    satuan: Optional[str] = Field(None, min_length=1, max_length=50)
    kategori: Optional[str] = Field(None, max_length=100)
    is_active: Optional[int] = Field(None, ge=0, le=1)


# Mandor Schemas
class MandorCreateRequest(BaseModel):
    nama: str = Field(..., min_length=1, max_length=255)
    nomor_kontak: Optional[str] = Field(None, max_length=50)
    alamat: Optional[str] = Field(None, max_length=500)


class MandorUpdateRequest(BaseModel):
    nama: Optional[str] = Field(None, min_length=1, max_length=255)
    nomor_kontak: Optional[str] = Field(None, max_length=50)
    alamat: Optional[str] = Field(None, max_length=500)
    is_active: Optional[int] = Field(None, ge=0, le=1)


# Stock In Schemas
class StockInCreateRequest(BaseModel):
    nomor_invoice: str = Field(..., min_length=1, max_length=255)
    material_id: int = Field(..., gt=0)
    quantity: Decimal = Field(..., gt=0)
    tanggal_masuk: date


class StockInUpdateRequest(BaseModel):
    nomor_invoice: Optional[str] = Field(None, min_length=1, max_length=255)
    material_id: Optional[int] = Field(None, gt=0)
    quantity: Optional[Decimal] = Field(None, gt=0)
    tanggal_masuk: Optional[date] = None


# Stock Out Schemas
class StockOutCreateRequest(BaseModel):
    mandor_id: int = Field(..., gt=0)
    material_id: int = Field(..., gt=0)
    quantity: Decimal = Field(..., gt=0)
    tanggal_keluar: date


class StockOutUpdateRequest(BaseModel):
    mandor_id: Optional[int] = Field(None, gt=0)
    material_id: Optional[int] = Field(None, gt=0)
    quantity: Optional[Decimal] = Field(None, gt=0)
    tanggal_keluar: Optional[date] = None


# Installed Schemas
class InstalledCreateRequest(BaseModel):
    material_id: int = Field(..., gt=0)
    quantity: Decimal = Field(..., gt=0)
    tanggal_pasang: date
    mandor_id: int = Field(..., gt=0)
    stock_out_id: Optional[int] = Field(None, gt=0)
    no_register: Optional[str] = Field(None, max_length=255)


class InstalledUpdateRequest(BaseModel):
    material_id: Optional[int] = Field(None, gt=0)
    quantity: Optional[Decimal] = Field(None, gt=0)
    tanggal_pasang: Optional[date] = None
    mandor_id: Optional[int] = Field(None, gt=0)
    stock_out_id: Optional[int] = Field(None, gt=0)
    no_register: Optional[str] = Field(None, max_length=255)


# Return Schemas
class ReturnCreateRequest(BaseModel):
    mandor_id: int = Field(..., gt=0)
    material_id: int = Field(..., gt=0)
    quantity_kembali: Decimal = Field(..., gt=0)
    quantity_kondisi_baik: Optional[Decimal] = Field(None, ge=0)
    quantity_kondisi_reject: Optional[Decimal] = Field(None, ge=0)
    stock_out_id: Optional[int] = Field(None, gt=0)
    tanggal_kembali: date


class ReturnUpdateRequest(BaseModel):
    mandor_id: Optional[int] = Field(None, gt=0)
    material_id: Optional[int] = Field(None, gt=0)
    quantity_kembali: Optional[Decimal] = Field(None, gt=0)
    quantity_kondisi_baik: Optional[Decimal] = Field(None, ge=0)
    quantity_kondisi_reject: Optional[Decimal] = Field(None, ge=0)
    stock_out_id: Optional[int] = Field(None, gt=0)
    tanggal_kembali: Optional[date] = None


# Export Excel Request
class ExportExcelRequest(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    mandor_id: Optional[int] = None
    material_id: Optional[int] = None
    # Opsional: filter pencarian untuk menyamakan dengan tampilan stock balance
    search: Optional[str] = None

