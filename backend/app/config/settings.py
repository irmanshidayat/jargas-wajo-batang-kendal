from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import field_validator
import os
import logging

logger = logging.getLogger(__name__)


def _get_env_file() -> str | None:
    """
    Auto-detect environment file berdasarkan priority:
    1. Jika di Docker, tidak perlu file .env (semua dari environment variables)
    2. ENV_FILE environment variable (jika di-set manual)
    3. .env.dev di root project (untuk development lokal)
    4. .env di root project (untuk production/default lokal)
    
    Note: Di Docker, semua environment variables di-pass dari docker-compose,
    jadi tidak perlu membaca file .env di backend.
    """
    # Priority 1: Jika di Docker, tidak perlu file .env
    if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true":
        return None
    
    # Priority 2: Check ENV_FILE environment variable
    env_file_from_env = os.getenv("ENV_FILE")
    if env_file_from_env:
        return env_file_from_env
    
    # Priority 3: Check .env.dev di root project (untuk development lokal)
    # Path relatif dari backend/ ke root: ../.env.dev
    root_env_dev = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.dev")
    if os.path.exists(root_env_dev):
        return root_env_dev
    
    # Priority 4: Default to .env di root project (untuk production/default lokal)
    # Path relatif dari backend/ ke root: ../.env
    root_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(root_env):
        return root_env
    
    # Jika tidak ada file .env, return None (akan menggunakan environment variables atau defaults)
    return None


class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "jargas_apbn"

    # Application
    APP_NAME: str = "Jargas APBN API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS - parse dari env string ke list
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:8080,http://localhost:3000,http://localhost:5173"
    
    # File Upload
    UPLOAD_DIR: str = "uploads/evidence"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    # Ubah tipe menjadi Union agar tidak di-parse sebagai JSON
    ALLOWED_FILE_TYPES: Union[str, List[str]] = "image/jpeg,image/jpg,image/png,application/pdf"
    
    # Database Migration
    AUTO_MIGRATE: bool = False
    AUTO_MIGRATE_ONLY_IF_PENDING: bool = True
    # Migration Mode: "sequential" (default, recommended), "head" (fallback), "auto" (smart selection)
    MIGRATION_MODE: str = "sequential"
    # Validasi migration chain sebelum upgrade (best practice: True)
    MIGRATION_VALIDATE_BEFORE_UPGRADE: bool = True
    # Stop migration jika ada error (best practice: True untuk safety)
    MIGRATION_STOP_ON_ERROR: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        if isinstance(v, list):
            return v
        return v

    @field_validator("ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, v):
        """Parse ALLOWED_FILE_TYPES dari string comma-separated ke list"""
        if isinstance(v, str):
            # Jika string kosong, return default
            if not v.strip():
                return ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
            # Split by comma dan strip whitespace
            return [ftype.strip() for ftype in v.split(",") if ftype.strip()]
        if isinstance(v, list):
            return v
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in str(self.CORS_ORIGINS).split(",")]

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get ALLOWED_FILE_TYPES as list"""
        if isinstance(self.ALLOWED_FILE_TYPES, list):
            return self.ALLOWED_FILE_TYPES
        return [ftype.strip() for ftype in str(self.ALLOWED_FILE_TYPES).split(",") if ftype.strip()]

    # Auto-detect Docker environment
    @property
    def is_docker(self) -> bool:
        """Detect if running in Docker container"""
        return os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"

    # Auto-adjust settings based on environment
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Validasi format file .env (hanya warning, tidak crash)
        # Hanya validasi jika tidak di Docker dan file .env ada
        if not self.is_docker:
            try:
                from app.utils.env_validator import validate_env_file
                env_file_path = _get_env_file()
                if env_file_path and os.path.exists(env_file_path):
                    is_valid, errors = validate_env_file(env_path=env_file_path)
                    if not is_valid and errors:
                        logger.warning(f"⚠️  Ditemukan masalah format di file {env_file_path}:")
                        for error in errors[:3]:  # Tampilkan maksimal 3 error pertama
                            logger.warning(f"   {error}")
                        if len(errors) > 3:
                            logger.warning(f"   ... dan {len(errors) - 3} error lainnya")
                        logger.warning(f"💡 Periksa file {env_file_path} dan pastikan format: KEY=value (tanpa spasi di sekitar =)")
            except Exception:
                # Ignore error validasi, jangan crash aplikasi
                pass
        
        # Auto-adjust untuk Docker jika terdeteksi
        if self.is_docker and self.DB_HOST == "localhost":
            # Jika di Docker tapi masih pakai localhost, ubah ke mysql (service name)
            self.DB_HOST = "mysql"
        # Auto-adjust untuk Development
        if not self.is_docker and self.DB_HOST == "mysql":
            # Jika di Development tapi masih pakai mysql, ubah ke localhost
            self.DB_HOST = "localhost"

    model_config = SettingsConfigDict(
        env_file=_get_env_file(),  # None jika di Docker, path ke root .env jika lokal
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_ignore_empty=False,
        extra="ignore",
    )


settings = Settings()
