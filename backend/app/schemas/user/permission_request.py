from pydantic import BaseModel, Field
from typing import Optional


class PageCreateRequest(BaseModel):
    """Schema untuk create page"""
    name: str = Field(..., min_length=3, max_length=100)
    path: str = Field(..., min_length=1, max_length=255)
    icon: Optional[str] = Field(None, max_length=100)
    display_name: str = Field(..., min_length=3, max_length=255)
    order: Optional[int] = Field(0, ge=0)


class PageUpdateRequest(BaseModel):
    """Schema untuk update page"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    path: Optional[str] = Field(None, min_length=1, max_length=255)
    icon: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, min_length=3, max_length=255)
    order: Optional[int] = Field(None, ge=0)


class PermissionCreateRequest(BaseModel):
    """Schema untuk create permission"""
    page_id: int
    can_create: bool = False
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False


class PermissionUpdateRequest(BaseModel):
    """Schema untuk update permission"""
    can_create: Optional[bool] = None
    can_read: Optional[bool] = None
    can_update: Optional[bool] = None
    can_delete: Optional[bool] = None


class AssignUserPermissionsRequest(BaseModel):
    """Schema untuk assign permissions ke user (override)"""
    permission_ids: list[int] = Field(..., min_items=0)

