from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SuratJalan(BaseModel):
    __tablename__ = "surat_jalans"
    __table_args__ = (
        UniqueConstraint('nomor_form', name='uq_surat_jalan_number'),
    )

    nomor_form = Column(String(255), unique=True, nullable=False, index=True)  # Auto-generated nomor form atau nomor barang keluar
    kepada = Column(String(255), nullable=False)  # Penerima/Kepada
    tanggal_pengiriman = Column(Date, nullable=False, index=True)
    nama_pemberi = Column(String(255), nullable=True)  # Nama pemberi/sender
    nama_penerima = Column(String(255), nullable=True)  # Nama penerima/receiver
    tanggal_diterima = Column(Date, nullable=True)  # Tanggal diterima
    nomor_surat_permintaan = Column(String(255), nullable=True, index=True)  # Relasi ke surat permintaan
    nomor_barang_keluar = Column(String(255), nullable=True, index=True)  # Nomor barang keluar yang digunakan sebagai nomor_form
    stock_out_id = Column(Integer, ForeignKey("stock_outs.id"), nullable=True, index=True)  # Foreign key ke stock_out untuk referential integrity
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_deleted = Column(Integer, default=0, nullable=False, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="surat_jalans")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_surat_jalans")
    items = relationship("SuratJalanItem", back_populates="surat_jalan", cascade="all, delete-orphan")
    stock_out = relationship("StockOut", foreign_keys=[stock_out_id], backref="surat_jalans")

