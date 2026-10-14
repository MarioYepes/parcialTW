"""Dependencias de autenticacion y proteccion de rutas."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LoginSession, User
from app.security import decode_access_token, hash_token


security_scheme = HTTPBearer(auto_error=False)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Obtiene el usuario autenticado a partir del token Bearer."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido o expirado")

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    session = (
        db.query(LoginSession)
        .filter(LoginSession.token == hash_token(token), LoginSession.user_id == user_id)
        .first()
    )
    if session is None or session.expires_at <= _utc_now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion invalida o expirada")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    return user


def get_current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> str:
    """Retorna el token Bearer recibido (sin validarlo por si solo)."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    return credentials.credentials
