from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class StockIn(BaseModel):
    __tablename__ = "stock_ins"

    nomor_invoice = Column(String(255), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    tanggal_masuk = Column(Date, nullable=False, index=True)
    evidence_paths = Column(Text, nullable=True)  # JSON array untuk multiple files
    surat_jalan_paths = Column(Text, nullable=True)  # JSON array untuk multiple files surat jalan
    material_datang_paths = Column(Text, nullable=True)  # JSON array untuk multiple files material datang
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)  # Nullable untuk backward compatibility
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_deleted = Column(Integer, default=0, nullable=False, index=True)  # 0 = tidak dihapus, 1 = dihapus
    
    # Relationships
    project = relationship("Project", back_populates="stock_ins")
    material = relationship("Material", back_populates="stock_ins")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_stock_ins")

