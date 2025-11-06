from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class ActionType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(SQLEnum(ActionType), nullable=False, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(Integer, nullable=True)
    old_values = Column(Text, nullable=True)  # JSON untuk nilai lama
    new_values = Column(Text, nullable=True)  # JSON untuk nilai baru
    description = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)  # Nullable untuk backward compatibility
    
    # Relationships
    project = relationship("Project", back_populates="audit_logs")
    user = relationship("User", foreign_keys=[user_id], back_populates="audit_logs")

