"""Rutas para consultar y actualizar el perfil del usuario."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware import get_current_user
from app.models import User
from app.schemas import UserProfileUpdate, UserResponse

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Retorna el perfil del usuario autenticado."""
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza el nombre completo del usuario autenticado."""
    current_user.full_name = payload.full_name
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
