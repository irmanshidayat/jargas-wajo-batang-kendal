from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreateRequest(BaseModel):
    """Schema untuk create user"""
    email: EmailStr
    name: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=100)
    role_id: Optional[int] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserUpdateRequest(BaseModel):
    """Schema untuk update user (full update)"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserPatchRequest(BaseModel):
    """Schema untuk partial update user"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserPasswordUpdateRequest(BaseModel):
    """Schema untuk update password user"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)

