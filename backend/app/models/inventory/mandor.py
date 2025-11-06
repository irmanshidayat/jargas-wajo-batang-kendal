from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Mandor(BaseModel):
    __tablename__ = "mandors"

    nama = Column(String(255), nullable=False, index=True)
    nomor_kontak = Column(String(50), nullable=True)
    alamat = Column(String(500), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = aktif, 0 = tidak aktif
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)  # Nullable untuk backward compatibility
    
    # Relationships
    project = relationship("Project", back_populates="mandors")
    stock_outs = relationship("StockOut", back_populates="mandor")
    installed_items = relationship("Installed", back_populates="mandor")
    returns = relationship("Return", back_populates="mandor")

