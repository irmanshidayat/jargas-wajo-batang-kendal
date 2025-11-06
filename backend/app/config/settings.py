from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator


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
    # Support localhost dan IP lokal untuk development
    # Default untuk Docker: http://localhost:8080 (frontend via Nginx)
    # Default untuk development: http://localhost:3000,http://localhost:5173
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:8080,http://localhost:3000,http://localhost:5173"
    
    # File Upload
    UPLOAD_DIR: str = "uploads/evidence"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
    
    # Database Migration
    AUTO_MIGRATE: bool = False  # Default False untuk safety, aktifkan via .env jika diperlukan
    AUTO_MIGRATE_ONLY_IF_PENDING: bool = True  # Hanya migrate jika ada pending migration

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        if isinstance(v, list):
            return v
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in str(self.CORS_ORIGINS).split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
