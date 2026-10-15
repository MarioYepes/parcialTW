"""Pruebas unitarias de servicios y utilidades de seguridad."""

from __future__ import annotations

from app.models import User
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.services.otp_service import consume_otp, create_otp_entry, generate_otp_code
from app.database import Base


def _create_user(db_session) -> User:
    user = User(email="unit@example.com", password_hash=hash_password("Secreta2026!!"), full_name="Unit")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_hash_password_is_not_plain():
    plain = "Secreta2026!!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$argon2")


def test_verify_password_accepts_valid_and_rejects_invalid():
    plain = "Secreta2026!!"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True
    assert verify_password("otra", hashed) is False


def test_create_and_consume_otp(db_session):
    user = _create_user(db_session)
    entry, code = create_otp_entry(db_session, user.id)
    assert len(code) == 6
    assert code.isdigit()
    assert entry.used is False

    consumed = consume_otp(db_session, user.id, code)
    assert consumed is not None
    assert consumed.used is True

    # No se puede reutilizar.
    assert consume_otp(db_session, user.id, code) is None


def test_consume_otp_rejects_wrong_code(db_session):
    user = _create_user(db_session)
    create_otp_entry(db_session, user.id)
    assert consume_otp(db_session, user.id, "000000") is None


def test_create_and_decode_jwt():
    token, expires = create_access_token(42)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert expires is not None


def test_hash_token_is_deterministic():
    token = "abc.def.ghi"
    assert hash_token(token) == hash_token(token)
    assert len(hash_token(token)) == 64
