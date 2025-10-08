"""Copyright (C) 2023 Yaraku, Inc.

This file is part of Human Evaluation Tool.

Human Evaluation Tool is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

Human Evaluation Tool is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
Human Evaluation Tool. If not, see <https://www.gnu.org/licenses/>.

Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, August 2023
"""

from datetime import datetime, timedelta, timezone

from flask.testing import FlaskClient
from flask_jwt_extended import decode_token

from human_evaluation_tool import auth


def _extract_token_from_set_cookie(header_value: str) -> str:
    for segment in header_value.split(";"):
        segment = segment.strip()
        if segment.startswith("access_token_cookie="):
            return segment.split("=", 1)[1]
    raise AssertionError("access_token_cookie not found in header")


def _get_cookie_value(client: FlaskClient, name: str) -> str:
    cookie = client.get_cookie(name)
    if cookie is None:
        raise AssertionError(f"Cookie {name} not found")
    return str(cookie.value)


def test_login_success_sets_cookie(client, create_user):
    user = create_user(email="login-success@example.com")
    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password", "remember": False},
    )
    assert response.status_code == 200
    cookies = response.headers.getlist("Set-Cookie")
    assert any("access_token_cookie" in cookie for cookie in cookies)


def test_login_failure_returns_401(client, create_user):
    user = create_user(email="login-failure@example.com")
    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "wrong", "remember": False},
    )
    assert response.status_code == 401
    assert response.get_json()["success"] is False


def test_login_missing_fields_returns_401(client):
    response = client.post("/api/auth/login", json={"email": "missing@example.com"})
    assert response.status_code == 401


def test_logout_clears_cookie(auth_client):
    client, _ = auth_client
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    cookies = response.headers.getlist("Set-Cookie")
    assert any("access_token_cookie=;" in cookie for cookie in cookies)


def test_validate_requires_authentication(client):
    response = client.get("/api/auth/validate")
    assert response.status_code == 401


def test_validate_returns_success(auth_client):
    client, _ = auth_client
    response = client.get("/api/auth/validate")
    assert response.status_code == 200
    assert response.get_json() == {"success": False}


def test_refresh_expiring_jwt_sets_new_cookie(auth_client, monkeypatch):
    client, _ = auth_client
    original_token = _get_cookie_value(client, "access_token_cookie")
    decoded = decode_token(original_token)
    exp_timestamp = decoded["exp"]

    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz: timezone | None = None) -> datetime:  # type: ignore[override]
            return datetime.fromtimestamp(exp_timestamp, tz) - timedelta(minutes=10)

    monkeypatch.setattr(auth, "datetime", MockDateTime)
    response = client.get("/api/users")
    assert response.status_code in {200, 401}
    cookies = response.headers.getlist("Set-Cookie")
    refreshed = [cookie for cookie in cookies if "access_token_cookie" in cookie]
    assert refreshed, "Expected refreshed access token cookie"
    new_token = _extract_token_from_set_cookie(refreshed[-1])
    decoded_new = decode_token(new_token)
    assert decoded_new["exp"] != exp_timestamp


def test_refresh_without_token_returns_response(client):
    response = client.get("/api/users")
    assert response.status_code == 401


def test_refresh_does_not_refresh_when_token_far_from_expiry(auth_client, monkeypatch):
    client, _ = auth_client
    original_token = _get_cookie_value(client, "access_token_cookie")
    decoded = decode_token(original_token)
    exp_timestamp = decoded["exp"]

    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz: timezone | None = None) -> datetime:  # type: ignore[override]
            return datetime.fromtimestamp(exp_timestamp, tz) - timedelta(hours=2)

    monkeypatch.setattr(auth, "datetime", MockDateTime)
    response = client.get("/api/users")
    assert response.status_code in {200, 401}
    cookies = response.headers.getlist("Set-Cookie")
    refreshed = [cookie for cookie in cookies if "access_token_cookie" in cookie]
    assert not refreshed


def test_refresh_with_missing_identity_returns_response(auth_client, monkeypatch):
    client, _ = auth_client
    original_token = _get_cookie_value(client, "access_token_cookie")
    decoded = decode_token(original_token)
    exp_timestamp = decoded["exp"]

    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz: timezone | None = None) -> datetime:  # type: ignore[override]
            return datetime.fromtimestamp(exp_timestamp, tz) - timedelta(minutes=10)

    monkeypatch.setattr(auth, "datetime", MockDateTime)
    monkeypatch.setattr("human_evaluation_tool.auth.get_jwt_identity", lambda: None)
    response = client.get("/api/users")
    assert response.status_code in {200, 401}
    cookies = response.headers.getlist("Set-Cookie")
    refreshed = [cookie for cookie in cookies if "access_token_cookie" in cookie]
    assert not refreshed
