from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Project(BaseModel):
    """Model untuk Project"""
    __tablename__ = "projects"

    name = Column(String(255), nullable=False, index=True)
    code = Column(String(100), unique=True, nullable=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    user_projects = relationship("UserProject", back_populates="project", cascade="all, delete-orphan")
    materials = relationship("Material", back_populates="project")
    mandors = relationship("Mandor", back_populates="project")
    stock_ins = relationship("StockIn", back_populates="project")
    stock_outs = relationship("StockOut", back_populates="project")
    # installed_items = relationship("Installed", back_populates="project")  # Comment sementara karena project_id di Installed di-comment
    returns = relationship("Return", back_populates="project")
    audit_logs = relationship("AuditLog", back_populates="project")
    surat_permintaans = relationship("SuratPermintaan", back_populates="project")
    surat_jalans = relationship("SuratJalan", back_populates="project")

