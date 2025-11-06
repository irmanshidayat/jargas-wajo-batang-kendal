from pydantic import BaseModel, Field
from typing import Optional


class UserMenuPreferenceCreateRequest(BaseModel):
    """Schema untuk create user menu preference"""
    page_id: int
    show_in_menu: bool = Field(True)


class UserMenuPreferenceUpdateRequest(BaseModel):
    """Schema untuk update user menu preference"""
    show_in_menu: bool


class UserMenuPreferenceBulkRequest(BaseModel):
    """Schema untuk bulk update user menu preferences"""
    preferences: list[dict] = Field(..., description="List of {page_id: int, show_in_menu: bool}")

