from pydantic import BaseModel
from typing import Optional, List


class PermissionInfo(BaseModel):
    """Permission info untuk response"""
    id: int
    page_id: int
    page_name: Optional[str] = None
    page_path: Optional[str] = None
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool

    class Config:
        from_attributes = True


class RoleInfo(BaseModel):
    """Role info untuk response"""
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    is_superuser: bool = False
    role: Optional[RoleInfo] = None
    permissions: List[PermissionInfo] = []

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
