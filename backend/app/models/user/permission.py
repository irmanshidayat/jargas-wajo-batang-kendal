from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Page(BaseModel):
    """Model untuk halaman/menu"""
    __tablename__ = "pages"

    name = Column(String(100), unique=True, nullable=False, index=True)
    path = Column(String(255), nullable=False, unique=True, index=True)
    icon = Column(String(100), nullable=True)
    display_name = Column(String(255), nullable=False)
    order = Column(Integer, default=0, nullable=False)

    # Relationships
    permissions = relationship("Permission", back_populates="page", cascade="all, delete-orphan")
    user_menu_preferences = relationship("UserMenuPreference", back_populates="page", cascade="all, delete-orphan")


class Permission(BaseModel):
    """Model untuk Permission dengan CRUD flags"""
    __tablename__ = "permissions"

    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False, index=True)
    can_create = Column(Boolean, default=False, nullable=False)
    can_read = Column(Boolean, default=False, nullable=False)
    can_update = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)

    # Relationships
    page = relationship("Page", back_populates="permissions")
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    user_permissions = relationship("UserPermission", back_populates="permission", cascade="all, delete-orphan")

