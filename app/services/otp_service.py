"""Generacion y validacion de codigos OTP temporales."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app import models
from app.config import settings

OTP_DIGITS = 6


def _utc_now() -> datetime:
    """Retorna la fecha/hora actual en UTC (naive, apta para SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generate_otp_code() -> str:
    """Genera un codigo OTP numerico de 6 digitos."""
    return f"{secrets.randbelow(10**OTP_DIGITS):0{OTP_DIGITS}d}"


def hash_otp(code: str) -> str:
    """Hashea un codigo OTP para almacenamiento seguro."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def verify_otp_hash(stored_hash: str, code: str) -> bool:
    """Compara un codigo contra su hash de forma resistente a timing attacks."""
    return hmac.compare_digest(stored_hash, hash_otp(code))


def otp_expires_at() -> datetime:
    """Calcula la fecha de expiracion de un OTP segun la configuracion."""
    return _utc_now() + timedelta(minutes=settings.otp_expire_minutes)


def create_otp_entry(db: Session, user_id: int) -> tuple[models.OTPCode, str]:
    """Crea y persiste un nuevo codigo OTP para el usuario.

    Retorna la entidad creada y el codigo en texto plano (para enviarlo por correo).
    """
    code = generate_otp_code()
    entry = models.OTPCode(
        user_id=user_id,
        code=hash_otp(code),
        expires_at=otp_expires_at(),
        used=False,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry, code


def find_valid_otp(db: Session, user_id: int) -> models.OTPCode | None:
    """Obtiene el OTP valido (no usado y no expirado) mas reciente del usuario."""
    return (
        db.query(models.OTPCode)
        .filter(
            models.OTPCode.user_id == user_id,
            models.OTPCode.used.is_(False),
            models.OTPCode.expires_at > _utc_now(),
        )
        .order_by(models.OTPCode.created_at.desc())
        .first()
    )


def consume_otp(db: Session, user_id: int, code: str) -> models.OTPCode | None:
    """Valida y marca como usado un codigo OTP. Retorna la entidad si es valido."""
    entry = find_valid_otp(db, user_id)
    if entry is None:
        return None
    if not verify_otp_hash(entry.code, code):
        return None
    entry.used = True
    db.commit()
    db.refresh(entry)
    return entry
