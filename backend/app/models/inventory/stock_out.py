from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class StockOut(BaseModel):
    __tablename__ = "stock_outs"
    __table_args__ = (
        UniqueConstraint('nomor_barang_keluar', name='uq_stock_out_number'),
    )

    nomor_barang_keluar = Column(String(255), unique=True, nullable=False, index=True)  # JRGS-KDL-YYYYMMDD-XXXX
    mandor_id = Column(Integer, ForeignKey("mandors.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    tanggal_keluar = Column(Date, nullable=False, index=True)
    evidence_paths = Column(Text, nullable=True)  # JSON array untuk multiple files
    surat_permohonan_paths = Column(Text, nullable=True)  # JSON array untuk multiple files surat permohonan dari mandor
    surat_serah_terima_paths = Column(Text, nullable=True)  # JSON array untuk multiple files surat serah terima gudang
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)  # Nullable untuk backward compatibility
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_deleted = Column(Integer, default=0, nullable=False, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="stock_outs")
    mandor = relationship("Mandor", back_populates="stock_outs")
    material = relationship("Material", back_populates="stock_outs")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_stock_outs")
    installed_items = relationship("Installed", back_populates="stock_out")
    returns = relationship("Return", back_populates="stock_out")

