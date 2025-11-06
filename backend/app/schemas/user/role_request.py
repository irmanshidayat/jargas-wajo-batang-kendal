from pydantic import BaseModel, Field
from typing import Optional, List


class RoleCreateRequest(BaseModel):
    """Schema untuk create role"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None


class RoleUpdateRequest(BaseModel):
    """Schema untuk update role (full update)"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None


class RolePatchRequest(BaseModel):
    """Schema untuk partial update role"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None


class AssignPermissionsRequest(BaseModel):
    """Schema untuk assign permissions ke role"""
    permission_ids: list[int] = Field(..., min_items=0)


class PageCRUDPermission(BaseModel):
    """Schema untuk CRUD permission per page"""
    page_id: int = Field(..., gt=0)
    can_create: bool = False
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False


class AssignRolePermissionsCRUDRequest(BaseModel):
    """Schema untuk assign CRUD permissions per page ke role"""
    page_permissions: List[PageCRUDPermission] = Field(..., min_items=0)

