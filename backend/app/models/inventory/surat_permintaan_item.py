from sqlalchemy import Column, String, Integer, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SuratPermintaanItem(BaseModel):
    __tablename__ = "surat_permintaan_items"

    surat_permintaan_id = Column(Integer, ForeignKey("surat_permintaans.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=True, index=True)  # Nullable jika input manual
    kode_barang = Column(String(100), nullable=True)  # Backup/audit trail
    nama_barang = Column(String(255), nullable=False)
    qty = Column(Numeric(10, 2), nullable=False)
    satuan = Column(String(50), nullable=False)
    sumber_barang = Column(Text, nullable=True)  # JSON untuk menyimpan checkbox dan values
    peruntukan = Column(Text, nullable=True)  # JSON untuk menyimpan checkbox dan values
    
    # Relationships
    surat_permintaan = relationship("SuratPermintaan", back_populates="items")
    material = relationship("Material", back_populates="surat_permintaan_items")

