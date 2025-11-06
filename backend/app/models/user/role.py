from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Role(BaseModel):
    """Model untuk Role"""
    __tablename__ = "roles"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    users = relationship("User", back_populates="role_obj")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

