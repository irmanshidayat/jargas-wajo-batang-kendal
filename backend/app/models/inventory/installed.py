from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Installed(BaseModel):
    __tablename__ = "installed"

    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True)
    quantity = Column(Numeric(10, 1), nullable=False)
    tanggal_pasang = Column(Date, nullable=False, index=True)
    mandor_id = Column(Integer, ForeignKey("mandors.id"), nullable=False, index=True)
    stock_out_id = Column(Integer, ForeignKey("stock_outs.id"), nullable=True, index=True)
    evidence_paths = Column(Text, nullable=True)  # JSON array untuk multiple files
    no_register = Column(String(255), nullable=True)
    # project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)  # Comment sementara karena kolom belum ada di database. Uncomment setelah migration dijalankan
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_deleted = Column(Integer, default=0, nullable=False, index=True)
    
    # Relationships
    # project = relationship("Project", back_populates="installed_items")  # Comment sementara karena project_id di-comment
    material = relationship("Material", back_populates="installed_items")
    mandor = relationship("Mandor", back_populates="installed_items")
    stock_out = relationship("StockOut", back_populates="installed_items")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_installed")

