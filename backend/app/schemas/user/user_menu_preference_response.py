from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user.permission_response import PageResponse


class UserMenuPreferenceResponse(BaseModel):
    """Schema untuk response user menu preference"""
    id: int
    user_id: int
    page_id: int
    show_in_menu: bool
    created_at: datetime
    updated_at: datetime
    page: Optional[PageResponse] = None

    class Config:
        from_attributes = True


class UserMenuPreferenceListResponse(BaseModel):
    """Schema untuk list user menu preference response"""
    id: int
    user_id: int
    page_id: int
    show_in_menu: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

