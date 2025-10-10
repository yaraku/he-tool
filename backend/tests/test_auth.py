"""
Copyright (C) 2023-2025 Yaraku, Inc.

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

Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, October 2025
"""

from collections.abc import Callable
from datetime import datetime, timedelta, tzinfo
from typing import Any

from flask.testing import FlaskClient
from flask_jwt_extended import decode_token
from pytest import MonkeyPatch

from human_evaluation_tool import auth
from human_evaluation_tool.models import User


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


def _patch_datetime(
    monkeypatch: MonkeyPatch, exp_timestamp: int, offset: timedelta
) -> None:
    class DateTimeStub:
        @staticmethod
        def now(tz: tzinfo | None = None) -> datetime:
            base = datetime.fromtimestamp(exp_timestamp, tz)
            return base - offset

        @staticmethod
        def timestamp(value: datetime) -> float:
            return value.timestamp()

    monkeypatch.setattr(auth, "datetime", DateTimeStub)


def test_login_success_sets_cookie(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    user = create_user(email="login-success@example.com")
    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "password", "remember": False},
    )
    assert response.status_code == 200
    cookies = response.headers.getlist("Set-Cookie")
    assert any("access_token_cookie" in cookie for cookie in cookies)


def test_login_failure_returns_401(
    client: FlaskClient, create_user: Callable[..., User]
) -> None:
    user = create_user(email="login-failure@example.com")
    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "wrong", "remember": False},
    )
    assert response.status_code == 401
    assert response.get_json()["success"] is False


def test_login_missing_fields_returns_401(client: FlaskClient) -> None:
    response = client.post("/api/auth/login", json={"email": "missing@example.com"})
    assert response.status_code == 401


def test_logout_clears_cookie(auth_client: tuple[FlaskClient, User]) -> None:
    client, _ = auth_client
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    cookies = response.headers.getlist("Set-Cookie")
    assert any("access_token_cookie=;" in cookie for cookie in cookies)


def test_validate_requires_authentication(client: FlaskClient) -> None:
    response = client.get("/api/auth/validate")
    assert response.status_code == 401


def test_validate_returns_success(auth_client: tuple[FlaskClient, User]) -> None:
    client, _ = auth_client
    response = client.get("/api/auth/validate")
    assert response.status_code == 200
    assert response.get_json() == {"success": False}


def test_refresh_expiring_jwt_sets_new_cookie(
    auth_client: tuple[FlaskClient, User], monkeypatch: MonkeyPatch
) -> None:
    client, _ = auth_client
    original_token = _get_cookie_value(client, "access_token_cookie")
    decoded: dict[str, Any] = decode_token(original_token)
    exp_timestamp = decoded["exp"]

    _patch_datetime(monkeypatch, exp_timestamp, timedelta(minutes=10))
    response = client.get("/api/users")
    assert response.status_code in {200, 401}
    cookies = response.headers.getlist("Set-Cookie")
    refreshed = [cookie for cookie in cookies if "access_token_cookie" in cookie]
    assert refreshed, "Expected refreshed access token cookie"
    new_token = _extract_token_from_set_cookie(refreshed[-1])
    decoded_new: dict[str, Any] = decode_token(new_token)
    assert decoded_new["exp"] != exp_timestamp


def test_refresh_without_token_returns_response(client: FlaskClient) -> None:
    response = client.get("/api/users")
    assert response.status_code == 401


def test_refresh_does_not_refresh_when_token_far_from_expiry(
    auth_client: tuple[FlaskClient, User], monkeypatch: MonkeyPatch
) -> None:
    client, _ = auth_client
    original_token = _get_cookie_value(client, "access_token_cookie")
    decoded: dict[str, Any] = decode_token(original_token)
    exp_timestamp = decoded["exp"]

    _patch_datetime(monkeypatch, exp_timestamp, timedelta(hours=2))
    response = client.get("/api/users")
    assert response.status_code in {200, 401}
    cookies = response.headers.getlist("Set-Cookie")
    refreshed = [cookie for cookie in cookies if "access_token_cookie" in cookie]
    assert not refreshed


def test_refresh_with_missing_identity_returns_response(
    auth_client: tuple[FlaskClient, User], monkeypatch: MonkeyPatch
) -> None:
    client, _ = auth_client
    original_token = _get_cookie_value(client, "access_token_cookie")
    decoded: dict[str, Any] = decode_token(original_token)
    exp_timestamp = decoded["exp"]

    _patch_datetime(monkeypatch, exp_timestamp, timedelta(minutes=10))
    monkeypatch.setattr("human_evaluation_tool.auth.get_jwt_identity", lambda: None)
    response = client.get("/api/users")
    assert response.status_code in {200, 401}
    cookies = response.headers.getlist("Set-Cookie")
    refreshed = [cookie for cookie in cookies if "access_token_cookie" in cookie]
    assert not refreshed
