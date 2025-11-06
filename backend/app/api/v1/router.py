from fastapi import APIRouter
from app.api.v1.routes import auth, dashboard, users, inventory, roles, permissions, project

api_router = APIRouter()

# Include feature routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(project.router, prefix="/projects", tags=["Projects"])
