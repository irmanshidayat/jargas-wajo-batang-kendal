from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserMenuPreference(BaseModel):
    """Model untuk menyimpan preferensi visibility menu per user"""
    __tablename__ = "user_menu_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False, index=True)
    show_in_menu = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="menu_preferences")
    page = relationship("Page", back_populates="user_menu_preferences")

    # Unique constraint: satu user tidak boleh punya preference yang sama untuk page yang sama
    __table_args__ = (
        UniqueConstraint('user_id', 'page_id', name='uq_user_menu_preference'),
    )

