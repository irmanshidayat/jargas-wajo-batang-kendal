from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Return(BaseModel):
    __tablename__ = "returns"

    mandor_id = Column(Integer, ForeignKey("mandors.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True)
    quantity_kembali = Column(Numeric(10, 2), nullable=False)
    quantity_kondisi_baik = Column(Numeric(10, 2), nullable=True, default=0)
    quantity_kondisi_reject = Column(Numeric(10, 2), nullable=True, default=0)
    stock_out_id = Column(Integer, ForeignKey("stock_outs.id"), nullable=True, index=True)
    tanggal_kembali = Column(Date, nullable=False, index=True)
    evidence_paths = Column(Text, nullable=True)  # JSON array untuk multiple files
    is_released = Column(Integer, default=0, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_deleted = Column(Integer, default=0, nullable=False, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="returns")
    mandor = relationship("Mandor", back_populates="returns")
    material = relationship("Material", back_populates="returns")
    stock_out = relationship("StockOut", back_populates="returns")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_returns")

