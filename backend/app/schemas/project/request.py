from pydantic import BaseModel, Field
from typing import Optional


class ProjectCreateRequest(BaseModel):
    """Request schema untuk create project"""
    name: str = Field(..., min_length=1, max_length=255, description="Nama project")
    code: Optional[str] = Field(None, max_length=100, description="Kode project (optional)")
    description: Optional[str] = Field(None, description="Deskripsi project")


class ProjectUpdateRequest(BaseModel):
    """Request schema untuk update project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nama project")
    code: Optional[str] = Field(None, max_length=100, description="Kode project")
    description: Optional[str] = Field(None, description="Deskripsi project")
    is_active: Optional[bool] = Field(None, description="Status aktif project")


class UserProjectCreateRequest(BaseModel):
    """Request schema untuk assign user ke project"""
    user_id: int = Field(..., description="ID user")
    project_id: int = Field(..., description="ID project")
    is_owner: Optional[bool] = Field(False, description="Apakah user adalah owner project")


class ProjectSelectRequest(BaseModel):
    """Request schema untuk select project setelah login"""
    project_id: int = Field(..., description="ID project yang dipilih")

