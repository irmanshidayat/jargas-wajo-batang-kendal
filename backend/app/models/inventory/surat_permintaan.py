from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SuratPermintaan(BaseModel):
    __tablename__ = "surat_permintaans"
    __table_args__ = (
        UniqueConstraint('nomor_surat', name='uq_surat_permintaan_number'),
    )

    nomor_surat = Column(String(255), unique=True, nullable=False, index=True)  # JRGS-KDL-YYYYMMDD-XXXX
    tanggal = Column(Date, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    signatures = Column(Text, nullable=True)  # JSON untuk menyimpan semua signature data
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_deleted = Column(Integer, default=0, nullable=False, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="surat_permintaans")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_surat_permintaans")
    items = relationship("SuratPermintaanItem", back_populates="surat_permintaan", cascade="all, delete-orphan")

