from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PermissionDetail(BaseModel):
    """Detail permission dalam role"""
    id: int
    page_id: int
    page_name: str
    page_path: str
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """Schema untuk response role"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleDetailResponse(BaseModel):
    """Schema untuk response role dengan permissions"""
    id: int
    name: str
    description: Optional[str]
    permissions: List[PermissionDetail] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleListResponse(BaseModel):
    """Schema untuk list role response"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

