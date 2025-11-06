from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PageResponse(BaseModel):
    """Schema untuk response page"""
    id: int
    name: str
    path: str
    icon: Optional[str]
    display_name: str
    order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PageListResponse(BaseModel):
    """Schema untuk list page response"""
    id: int
    name: str
    path: str
    icon: Optional[str]
    display_name: str
    order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    """Schema untuk response permission"""
    id: int
    page_id: int
    page_name: Optional[str] = None
    page_path: Optional[str] = None
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionDetailResponse(BaseModel):
    """Schema untuk response permission dengan detail page"""
    id: int
    page_id: int
    page: Optional[PageResponse] = None
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

