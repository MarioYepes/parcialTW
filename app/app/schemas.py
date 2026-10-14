"""Esquemas Pydantic para solicitudes y respuestas de la API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Datos necesarios para registrar una cuenta."""

    email: EmailStr = Field(examples=["persona@example.com"])
    password: str = Field(min_length=12, max_length=128, examples=["UnaFraseSegura2026!"])
    full_name: str = Field(min_length=1, max_length=200, examples=["Nombre Apellido"])


class UserLogin(BaseModel):
    """Credenciales para iniciar el proceso de autenticacion."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class OTPVerification(BaseModel):
    """Codigo OTP enviado al correo del usuario."""

    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$", examples=["123456"])


class OTPResend(BaseModel):
    """Correo al que se reenviara el codigo OTP."""

    email: EmailStr


class UserProfileUpdate(BaseModel):
    """Campos editables del perfil del usuario."""

    full_name: str = Field(min_length=1, max_length=200)


class UserResponse(BaseModel):
    """Informacion publica del usuario."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Respuesta generica para tokens de acceso."""

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
