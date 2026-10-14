"""Rutas para registro, inicio de sesion, OTP y tokens."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.limiter import limiter
from app.middleware import get_current_token, get_current_user
from app.models import LoginSession, User
from app.schemas import OTPResend, OTPVerification, TokenResponse, UserCreate, UserLogin
from app.security import create_access_token, hash_password, hash_token, verify_password
from app.services.email_service import send_otp_email
from app.services.otp_service import consume_otp, create_otp_entry

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario con contrasena hasheada."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya esta registrado")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "full_name": user.full_name}


@router.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    """Valida credenciales y envia un codigo OTP al correo del usuario."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")

    _entry, code = create_otp_entry(db, user.id)
    send_otp_email(user.email, code)
    return {"message": "Se ha enviado un codigo OTP a tu correo"}


@router.post("/verify-otp", response_model=TokenResponse)
@limiter.limit("10/minute")
def verify_otp(request: Request, payload: OTPVerification, db: Session = Depends(get_db)):
    """Verifica el codigo OTP y retorna un JWT de acceso."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    entry = consume_otp(db, user.id, payload.code)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Codigo OTP invalido o expirado")

    token, expires = create_access_token(user.id)
    session = LoginSession(
        user_id=user.id,
        token=hash_token(token),
        expires_at=expires.replace(tzinfo=None),
    )
    db.add(session)
    db.commit()

    return TokenResponse(access_token=token, token_type="bearer", expires_at=expires)


@router.post("/resend-otp", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def resend_otp(request: Request, payload: OTPResend, db: Session = Depends(get_db)):
    """Reenvia un nuevo codigo OTP al correo indicado."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    _entry, code = create_otp_entry(db, user.id)
    send_otp_email(user.email, code)
    return {"message": "Se ha reenviado el codigo OTP"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    current_user: User = Depends(get_current_user),
    current_token: str = Depends(get_current_token),
    db: Session = Depends(get_db),
):
    """Emite un nuevo JWT revocando el token anterior."""
    token, expires = create_access_token(current_user.id)

    db.query(LoginSession).filter(LoginSession.token == hash_token(current_token)).delete()
    session = LoginSession(
        user_id=current_user.id,
        token=hash_token(token),
        expires_at=expires.replace(tzinfo=None),
    )
    db.add(session)
    db.commit()

    return TokenResponse(access_token=token, token_type="bearer", expires_at=expires)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    _current_user: User = Depends(get_current_user),
    current_token: str = Depends(get_current_token),
    db: Session = Depends(get_db),
):
    """Cierra la sesion revocando el token actual."""
    deleted = db.query(LoginSession).filter(LoginSession.token == hash_token(current_token)).delete()
    db.commit()
    if not deleted:
        return {"message": "No habia sesion activa"}
    return {"message": "Sesion cerrada correctamente"}
