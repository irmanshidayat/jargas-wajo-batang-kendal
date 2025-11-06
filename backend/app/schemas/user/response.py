from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RoleBasicInfo(BaseModel):
    """Basic role info"""
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """Schema untuk response user"""
    id: int
    email: str
    name: str
    is_active: bool
    is_superuser: bool
    role_id: Optional[int] = None
    role: Optional[RoleBasicInfo] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema untuk list user response"""
    id: int
    email: str
    name: str
    is_active: bool
    is_superuser: bool
    role_id: Optional[int] = None
    role: Optional[RoleBasicInfo] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

