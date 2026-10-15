"""Pruebas de endpoints de usuario."""

from __future__ import annotations

import pytest


def test_update_profile(client, monkeypatch):
    client.post(
        "/auth/register",
        json={"email": "profile@example.com", "password": "Secreta2026!!", "full_name": "Original"},
    )
    captured = {}

    def fake_send(recipient, code):
        captured["code"] = code

    monkeypatch.setattr("app.routes.auth.send_otp_email", fake_send)
    client.post("/auth/login", json={"email": "profile@example.com", "password": "Secreta2026!!"})
    verify = client.post(
        "/auth/verify-otp", json={"email": "profile@example.com", "code": captured["code"]}
    )
    token = verify.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put("/users/profile", json={"full_name": "Actualizado"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Actualizado"

    profile = client.get("/users/profile", headers=headers)
    assert profile.json()["full_name"] == "Actualizado"
