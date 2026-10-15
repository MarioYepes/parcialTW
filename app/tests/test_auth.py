"""Pruebas de integracion de autenticacion."""

from __future__ import annotations

import pytest


def _register_and_login(client, monkeypatch, email="auth@example.com", password="Secreta2026!!"):
    client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Auth User"},
    )
    captured = {}

    def fake_send(recipient, code):
        captured["code"] = code

    monkeypatch.setattr("app.routes.auth.send_otp_email", fake_send)
    client.post("/auth/login", json={"email": email, "password": password})
    return captured["code"]


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "Secreta2026!!", "full_name": "New User"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"


def test_register_duplicate_email_returns_conflict(client):
    payload = {"email": "dup@example.com", "password": "Secreta2026!!", "full_name": "Dup"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_login_and_verify_otp_returns_token(client, monkeypatch):
    code = _register_and_login(client, monkeypatch, email="otp@example.com")
    response = client.post("/auth/verify-otp", json={"email": "otp@example.com", "code": code})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_verify_otp_rejects_invalid_code(client, monkeypatch):
    _register_and_login(client, monkeypatch, email="badotp@example.com")
    response = client.post(
        "/auth/verify-otp", json={"email": "badotp@example.com", "code": "000000"}
    )
    assert response.status_code == 400


def test_logout_revokes_token(client, monkeypatch):
    code = _register_and_login(client, monkeypatch, email="logout@example.com")
    verify = client.post("/auth/verify-otp", json={"email": "logout@example.com", "code": code})
    token = verify.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.get("/users/profile", headers=headers).status_code == 401


def test_profile_requires_authentication(client):
    assert client.get("/users/profile").status_code == 401
