from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserProject(BaseModel):
    """Model untuk relasi many-to-many User dan Project"""
    __tablename__ = "user_projects"
    __table_args__ = (
        UniqueConstraint('user_id', 'project_id', name='uq_user_project'),
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_owner = Column(Boolean, default=False, nullable=False)  # Owner bisa manage project dan user lain

    # Relationships
    user = relationship("User", back_populates="user_projects")
    project = relationship("Project", back_populates="user_projects")

