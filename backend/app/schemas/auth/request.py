from pydantic import BaseModel, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterAdminRequest(BaseModel):
    """Schema untuk register admin dengan validasi lengkap"""
    email: EmailStr
    name: str = Field(..., min_length=3, max_length=255, description="Nama lengkap admin")
    password: str = Field(..., min_length=6, max_length=100, description="Password minimal 6 karakter")
    confirm_password: str = Field(..., min_length=6, max_length=100, description="Konfirmasi password")
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Validasi bahwa password dan confirm_password sama"""
        if self.password != self.confirm_password:
            raise ValueError('Password dan konfirmasi password tidak sama')
        return self
