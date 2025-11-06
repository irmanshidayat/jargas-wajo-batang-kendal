from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Data tidak ditemukan"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ValidationError(HTTPException):
    def __init__(self, detail: str = "Data tidak valid"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Tidak diizinkan"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Akses ditolak"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
