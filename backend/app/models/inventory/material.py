from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Material(BaseModel):
    __tablename__ = "materials"
    __table_args__ = (
        UniqueConstraint('project_id', 'kode_barang', name='uq_material_project_kode'),
    )

    kode_barang = Column(String(100), index=True, nullable=True)
    nama_barang = Column(String(255), nullable=False, index=True)
    satuan = Column(String(50), nullable=False)  # pcs, kg, m, dll
    kategori = Column(String(100), nullable=True, index=True)
    harga = Column(Numeric(15, 2), nullable=True)  # Harga material (opsional)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = aktif, 0 = tidak aktif
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="materials")
    stock_ins = relationship("StockIn", back_populates="material")
    stock_outs = relationship("StockOut", back_populates="material")
    installed_items = relationship("Installed", back_populates="material")
    returns = relationship("Return", back_populates="material")
    surat_permintaan_items = relationship("SuratPermintaanItem", back_populates="material")

