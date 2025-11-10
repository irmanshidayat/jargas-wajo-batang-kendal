from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import date
import json


# Surat Permintaan Item Schemas
class SuratPermintaanItemRequest(BaseModel):
    material_id: Optional[int] = Field(None, gt=0)  # Nullable jika input manual
    kode_barang: Optional[str] = Field(None, max_length=100)
    nama_barang: str = Field(..., min_length=1, max_length=255)
    qty: Decimal = Field(..., gt=0)
    satuan: str = Field(..., min_length=1, max_length=50)
    sumber_barang: Optional[dict] = None  # JSON untuk checkbox dan values
    peruntukan: Optional[dict] = None  # JSON untuk checkbox dan values


class SuratPermintaanItemResponse(BaseModel):
    id: int
    material_id: Optional[int]
    kode_barang: Optional[str]
    nama_barang: str
    qty: Decimal
    satuan: str
    sumber_barang: Optional[dict]
    peruntukan: Optional[dict]
    material: Optional[dict] = None  # Material object jika ada

    class Config:
        from_attributes = True


# Surat Permintaan Schemas
class SuratPermintaanCreateRequest(BaseModel):
    tanggal: date
    items: List[SuratPermintaanItemRequest] = Field(..., min_items=1)
    signatures: Optional[dict] = None  # JSON untuk semua signature data


class SuratPermintaanUpdateRequest(BaseModel):
    tanggal: Optional[date] = None
    items: Optional[List[SuratPermintaanItemRequest]] = None
    signatures: Optional[dict] = None


class SuratPermintaanResponse(BaseModel):
    id: int
    nomor_surat: str
    tanggal: date
    project_id: int
    status: str = "Draft"  # Draft, Barang Keluar Dibuat, Selesai
    signatures: Optional[dict] = None
    created_by: int
    created_at: str
    updated_at: str
    items: List[SuratPermintaanItemResponse] = []
    project: Optional[dict] = None
    creator: Optional[dict] = None

    class Config:
        from_attributes = True

