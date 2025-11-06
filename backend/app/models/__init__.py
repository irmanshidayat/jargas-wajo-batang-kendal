from app.models.base import Base
from app.config.database import engine

# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user.user import User
from app.models.user.role import Role
from app.models.user.permission import Page, Permission
from app.models.user.role_permission import RolePermission
from app.models.user.user_permission import UserPermission
from app.models.user.user_menu_preference import UserMenuPreference
from app.models.project import Project, UserProject
from app.models.inventory import (
    Material,
    Mandor,
    StockIn,
    StockOut,
    Installed,
    Return,
    Notification,
    AuditLog,
)

# Create tables
Base.metadata.create_all(bind=engine)
