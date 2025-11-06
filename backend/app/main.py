from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.config.settings import settings
from app.api.v1.router import api_router
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError
)
from app.utils.response import error_response
import logging
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return error_response(
        message=exc.detail if hasattr(exc, 'detail') else "Data tidak ditemukan",
        status_code=status.HTTP_404_NOT_FOUND
    )


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return error_response(
        message=exc.detail,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return error_response(
        message=exc.detail,
        status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return error_response(
        message=exc.detail,
        status_code=status.HTTP_403_FORBIDDEN
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    error_details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors[field] = error["msg"]
        error_details.append({
            "field": field,
            "location": list(error["loc"]),
            "message": error["msg"],
            "type": error.get("type", "unknown")
        })
    
    logger.error(f"Validation Error on {request.method} {request.url.path}: {error_details}")
    
    return error_response(
        message="Validasi data gagal",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=errors
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Integrity Error: {str(exc)}")
    return error_response(
        message="Data yang dimasukkan melanggar aturan database",
        status_code=status.HTTP_400_BAD_REQUEST
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database Error: {str(exc)}")
    return error_response(
        message="Terjadi kesalahan pada database",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected Error: {str(exc)}", exc_info=True)
    return error_response(
        message="Terjadi kesalahan pada server",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


# Include API router
app.include_router(api_router, prefix="/api/v1")

# Static files for evidence uploads
app.mount("/api/v1/evidence", StaticFiles(directory="uploads/evidence"), name="evidence")


@app.on_event("startup")
async def startup_event():
    """
    Lifecycle hook untuk startup tasks:
    1. Auto-migrate database (jika diaktifkan)
    2. Auto-generate pages dan permissions
    """
    # 1. Auto-migrate database (Best Practice: Controlled via environment variable)
    if settings.AUTO_MIGRATE:
        try:
            from app.utils.migration import auto_migrate_safe
            logger.info("Auto-migrate diaktifkan, memeriksa migration status...")
            
            result = auto_migrate_safe(only_if_pending=settings.AUTO_MIGRATE_ONLY_IF_PENDING)
            
            if result["success"]:
                if result["migrated"]:
                    logger.info(f"✅ Auto-migration berhasil: {result['message']}")
                else:
                    logger.info(f"ℹ️ {result['message']}")
            else:
                logger.warning(f"⚠️ Auto-migration gagal: {result.get('message', 'Unknown error')}")
                logger.warning("Aplikasi akan tetap berjalan, namun sebaiknya periksa migration secara manual")
        except Exception as e:
            # Jangan crash aplikasi jika auto-migrate gagal
            logger.error(f"Error during auto-migrate: {str(e)}", exc_info=True)
            logger.warning("Application will continue despite auto-migrate error")
            logger.warning("⚠️ PERHATIAN: Periksa status migration database secara manual!")
    else:
        logger.info("Auto-migrate tidak diaktifkan (AUTO_MIGRATE=False). Gunakan script manual untuk migration.")
    
    # 2. Auto-generate pages dan permissions
    try:
        from scripts.auto_generate_pages import auto_generate_pages
        logger.info("Running auto-generate pages and permissions...")
        auto_generate_pages()
    except Exception as e:
        # Jangan crash aplikasi jika auto-generate gagal
        logger.error(f"Error during auto-generate pages: {str(e)}", exc_info=True)
        logger.warning("Application will continue despite auto-generate error")


@app.get("/")
async def root():
    return {
        "message": "Jargas APBN API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
