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
import sys
from fastapi.staticfiles import StaticFiles

# Konfigurasi logging - hanya tampilkan yang penting
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set level untuk SQLAlchemy - hanya ERROR dan WARNING
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.orm').setLevel(logging.ERROR)

# Set level untuk uvicorn - hanya tampilkan yang penting
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
logging.getLogger('uvicorn.error').setLevel(logging.INFO)

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
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": request.url.path,
        "method": request.method,
    }
    logger.error(f"Database Error: {error_detail}", exc_info=settings.DEBUG)
    
    error_message = "Terjadi kesalahan pada database"
    if settings.DEBUG:
        error_message = f"{error_message}: {str(exc)}"
    
    return error_response(
        message=error_message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc) if settings.DEBUG else None
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log error dengan detail lengkap untuk debugging
    error_detail = {
        "error": str(exc),
        "type": type(exc).__name__,
        "path": request.url.path,
        "method": request.method,
    }
    logger.error(f"Unexpected Error: {error_detail}", exc_info=settings.DEBUG)
    
    # Return error response dengan detail jika DEBUG mode
    error_message = "Terjadi kesalahan pada server"
    if settings.DEBUG:
        error_message = f"{error_message}: {str(exc)}"
    
    return error_response(
        message=error_message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc) if settings.DEBUG else None
    )


# Include API router
app.include_router(api_router, prefix="/api/v1")

# Static files for evidence uploads
app.mount("/api/v1/evidence", StaticFiles(directory="uploads/evidence"), name="evidence")


@app.on_event("startup")
async def startup_event():
    """
    Lifecycle hook untuk startup tasks:
    1. Auto-migrate database (jika diaktifkan) dengan retry logic
    2. Auto-generate pages dan permissions
    """
    # 1. Auto-migrate database (Best Practice: Controlled via environment variable)
    if settings.AUTO_MIGRATE:
        import asyncio
        from sqlalchemy.exc import OperationalError
        
        max_retries = 3
        retry_delay = 5  # detik
        
        for attempt in range(1, max_retries + 1):
            try:
                from app.utils.migration import auto_migrate_safe
                migration_mode = settings.MIGRATION_MODE or "sequential"
                
                if attempt == 1:
                    logger.info(f"Auto-migrate diaktifkan (mode: {migration_mode}), memeriksa migration status...")
                else:
                    logger.info(f"Retry auto-migrate (attempt {attempt}/{max_retries})...")
                
                result = auto_migrate_safe(only_if_pending=settings.AUTO_MIGRATE_ONLY_IF_PENDING)
                
                if result["success"]:
                    if result["migrated"]:
                        mode_info = f" (mode: {result.get('mode', migration_mode)})" if result.get('mode') else ""
                        if result.get("is_database_empty"):
                            logger.info(f"✅ Initial migration berhasil{mode_info}: {result['message']}")
                        else:
                            logger.info(f"✅ Auto-migration berhasil{mode_info}: {result['message']}")
                    else:
                        logger.info(f"ℹ️ {result['message']}")
                    break  # Berhasil, keluar dari retry loop
                else:
                    # Cek apakah error karena database belum ready
                    error_msg = result.get('error', '').lower() if result.get('error') else ''
                    is_connection_error = any(keyword in error_msg for keyword in [
                        'connection', 'connect', 'operational', 'timeout', 
                        'refused', 'unreachable', 'unknown database'
                    ])
                    
                    if is_connection_error and attempt < max_retries:
                        logger.warning(f"⚠️ Database belum ready (attempt {attempt}/{max_retries}), retry dalam {retry_delay} detik...")
                        logger.warning(f"   Error: {result.get('error', 'Unknown error')}")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.warning(f"⚠️ Auto-migration gagal: {result.get('message', 'Unknown error')}")
                        if result.get('error'):
                            logger.warning(f"   Error detail: {result['error']}")
                        logger.warning("Aplikasi akan tetap berjalan, namun sebaiknya periksa migration secara manual")
                        logger.warning("💡 Gunakan: python -m scripts.smart_migrate --status untuk cek status")
                        break  # Keluar dari retry loop
                    
            except (OperationalError, ConnectionError) as e:
                # Error koneksi database - retry
                if attempt < max_retries:
                    logger.warning(f"⚠️ Database connection error (attempt {attempt}/{max_retries}): {str(e)}")
                    logger.warning(f"   Retry dalam {retry_delay} detik...")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"❌ Database connection error setelah {max_retries} attempts: {str(e)}")
                    logger.warning("Application will continue despite auto-migrate error")
                    logger.warning("⚠️ PERHATIAN: Periksa status migration database secara manual!")
                    logger.warning("💡 Gunakan: python -m scripts.smart_migrate --status untuk cek status")
                    break
            except Exception as e:
                # Jangan crash aplikasi jika auto-migrate gagal
                logger.error(f"Error during auto-migrate: {str(e)}", exc_info=True)
                logger.warning("Application will continue despite auto-migrate error")
                logger.warning("⚠️ PERHATIAN: Periksa status migration database secara manual!")
                logger.warning("💡 Gunakan: python -m scripts.smart_migrate --status untuk cek status")
                break
    else:
        logger.info("Auto-migrate tidak diaktifkan (AUTO_MIGRATE=False). Gunakan script manual untuk migration.")
        logger.info("💡 Gunakan: python -m scripts.smart_migrate untuk migration manual")
    
    # 2. Auto-generate pages dan permissions
    try:
        from scripts.auto_generate_pages import auto_generate_pages
        logger.info("Running auto-generate pages and permissions...")
        auto_generate_pages()
    except ConnectionError as e:
        # Error koneksi database - tampilkan pesan yang jelas
        logger.error(f"❌ Database connection error: {str(e)}")
        logger.warning("⚠️  Application will continue, but pages may not be auto-generated")
        logger.warning("⚠️  Periksa konfigurasi database di file .env dan pastikan MySQL/XAMPP berjalan")
    except Exception as e:
        # Jangan crash aplikasi jika auto-generate gagal
        error_msg = str(e)
        # Tampilkan traceback hanya jika DEBUG mode
        if settings.DEBUG:
            logger.error(f"Error during auto-generate pages: {error_msg}", exc_info=True)
        else:
            logger.error(f"Error during auto-generate pages: {error_msg}")
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
