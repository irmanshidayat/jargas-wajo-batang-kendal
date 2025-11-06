from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectResponse(BaseModel):
    """Response schema untuk Project"""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProjectResponse(BaseModel):
    """Response schema untuk UserProject"""
    id: int
    user_id: int
    project_id: int
    is_active: bool
    is_owner: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectWithUserResponse(BaseModel):
    """Response schema untuk Project dengan info user"""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    is_active: bool
    is_owner: bool = False  # Apakah current user adalah owner
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

