"""Utilidades de seguridad: hashing de contrasenas y (mas adelante) JWT."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings

from pwdlib import PasswordHash

_password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hashea una contrasena usando Argon2 (recomendado por pwdlib)."""
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contrasena en texto plano contra su hash."""
    try:
        return _password_hasher.verify(plain_password, hashed_password)
    except Exception:
        return False


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(subject: str | int) -> tuple[str, datetime]:
    """Crea un JWT de acceso con expiracion configurada.

    Retorna (token, fecha_de_expiracion_en_UTC).
    """
    expires = _now_utc() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(subject),
        "iat": _now_utc(),
        "exp": expires,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires


def decode_access_token(token: str) -> dict:
    """Decodifica y valida un JWT. Lanza jwt.PyJWTError si es invalido o expiro."""
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def hash_token(token: str) -> str:
    """Hashea un token JWT para almacenarlo/revocarlo en la base de datos."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token_hash(stored_hash: str, token: str) -> bool:
    """Compara un token contra su hash almacenado."""
    return hmac.compare_digest(stored_hash, hash_token(token))
