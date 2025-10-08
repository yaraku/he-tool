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

Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, August 2023
"""

# Authentication routes and JWT helpers.

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, TypeVar, cast

from flask import Blueprint, Flask, Response, jsonify, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)
from sqlalchemy import select

from . import bcrypt, db
from .models import User


bp = Blueprint("auth", __name__)


_F = TypeVar("_F", bound=Callable[..., ResponseReturnValue])


def _typed_jwt_required(*args: Any, **kwargs: Any) -> Callable[[_F], _F]:
    """Typed wrapper around :func:`flask_jwt_extended.jwt_required`."""

    return cast("Callable[[_F], _F]", jwt_required(*args, **kwargs))


@bp.after_app_request
def refresh_expiring_jwts(response: Response) -> Response:
    """Refresh the JWT cookie if the token is about to expire."""

    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=15))
        if target_timestamp > exp_timestamp:
            identity = get_jwt_identity()
            if identity is None:
                return response
            access_token = create_access_token(identity=identity)
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # No valid JWT present – return the original response unchanged.
        return response


@bp.post("/api/auth/login")
def login() -> ResponseReturnValue:
    """Login endpoint that issues a JWT cookie."""

    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")
    remember = bool(data.get("remember"))

    if not email or not password:
        return {"success": False, "message": "Invalid username and password"}, 401

    user = db.session.execute(select(User).filter_by(email=email)).scalar_one_or_none()
    if user and bcrypt.check_password_hash(pw_hash=user.password, password=password):
        response = jsonify({"success": True})
        expires = timedelta(days=7) if remember else timedelta(hours=1)
        access_token = create_access_token(identity=user.id, expires_delta=expires)
        set_access_cookies(response, access_token)
        return response, 200

    return {"success": False, "message": "Invalid username and password"}, 401


@bp.post("/api/auth/logout")
def logout() -> ResponseReturnValue:
    """Logout endpoint that clears the JWT cookies."""

    response = jsonify({"success": True})
    unset_jwt_cookies(response)
    return response, 200


@bp.get("/api/auth/validate")
@_typed_jwt_required()
def validate() -> ResponseReturnValue:
    """Validate that the JWT token stored in cookies is still valid."""

    return jsonify({"success": False}), 200


def register_auth_blueprint(app: Flask) -> None:
    """Attach the authentication blueprint to the Flask app."""

    app.register_blueprint(bp)
