from typing import Any, Optional, Dict
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(
    data: Any = None,
    message: str = "Operasi berhasil",
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Format response untuk operasi sukses"""
    content = {
        "success": True,
        "message": message,
    }
    
    if data is not None:
        content["data"] = data
    
    if meta:
        content["meta"] = meta
    
    return JSONResponse(status_code=status_code, content=jsonable_encoder(content))


def error_response(
    message: str = "Terjadi kesalahan",
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[Dict[str, Any]] = None,
    detail: Optional[str] = None
) -> JSONResponse:
    """Format response untuk operasi error"""
    content = {
        "success": False,
        "message": message,
    }
    
    if errors:
        content["errors"] = errors
    
    if detail:
        content["detail"] = detail
    
    return JSONResponse(status_code=status_code, content=jsonable_encoder(content))


def paginated_response(
    data: list,
    total: int,
    page: int = 1,
    limit: int = 100,
    message: str = "Data berhasil diambil"
) -> JSONResponse:
    """Format response untuk data paginated"""
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    content = {
        "success": True,
        "message": message,
        "data": data,
        "meta": {
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    }
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(content))

