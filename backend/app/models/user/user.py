from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    GUDANG = "gudang"
    MANDOR = "mandor"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.GUDANG, nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Relationships
    role_obj = relationship("Role", foreign_keys=[role_id], back_populates="users")
    parent_user = relationship("User", remote_side="User.id", foreign_keys=[created_by], backref="child_users")
    user_permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")
    user_projects = relationship("UserProject", back_populates="user", cascade="all, delete-orphan")
    menu_preferences = relationship("UserMenuPreference", back_populates="user", cascade="all, delete-orphan")
    created_stock_ins = relationship("StockIn", foreign_keys="StockIn.created_by", back_populates="creator")
    created_stock_outs = relationship("StockOut", foreign_keys="StockOut.created_by", back_populates="creator")
    created_installed = relationship("Installed", foreign_keys="Installed.created_by", back_populates="creator")
    created_returns = relationship("Return", foreign_keys="Return.created_by", back_populates="creator")
    audit_logs = relationship("AuditLog", foreign_keys="AuditLog.user_id", back_populates="user")
    created_surat_permintaans = relationship("SuratPermintaan", foreign_keys="SuratPermintaan.created_by", back_populates="creator")
    created_surat_jalans = relationship("SuratJalan", foreign_keys="SuratJalan.created_by", back_populates="creator")
