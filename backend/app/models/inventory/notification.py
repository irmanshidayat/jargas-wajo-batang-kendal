from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"

    mandor_id = Column(Integer, ForeignKey("mandors.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    barang_keluar = Column(Integer, nullable=False)
    barang_terpasang = Column(Integer, nullable=False)
    selisih = Column(Integer, nullable=False)
    status = Column(String(50), default="warning", nullable=False)  # warning, info, error
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Relationships
    mandor = relationship("Mandor")
    material = relationship("Material")

