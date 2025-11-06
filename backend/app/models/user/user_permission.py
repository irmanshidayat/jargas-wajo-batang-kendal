from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserPermission(BaseModel):
    """Junction table untuk User-Permission (override permissions)"""
    __tablename__ = "user_permissions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="user_permissions")
    permission = relationship("Permission", back_populates="user_permissions")

    # Unique constraint: satu user tidak boleh punya permission yang sama dua kali
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id', name='uq_user_permission'),
    )

