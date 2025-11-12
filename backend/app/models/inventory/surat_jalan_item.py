from sqlalchemy import Column, String, Integer, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SuratJalanItem(BaseModel):
    __tablename__ = "surat_jalan_items"

    surat_jalan_id = Column(Integer, ForeignKey("surat_jalans.id"), nullable=False, index=True)
    nama_barang = Column(String(255), nullable=False)
    qty = Column(Numeric(10, 1), nullable=False)
    keterangan = Column(Text, nullable=True)  # KET column
    
    # Relationships
    surat_jalan = relationship("SuratJalan", back_populates="items")

