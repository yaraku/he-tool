"""
Copyright (C) 2023 Yaraku, Inc.

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
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from . import app, bcrypt
from .models import User


@app.after_request
def refresh_expiring_jwts(response):
    """
    Set the JWT cookie to refresh the token.
    """
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=15))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route("/api/auth/login", methods=["POST"])
def login():
    """
    Login endpoint. Returns a JWT token to be used in subsequent requests.
    """
    data = request.get_json()

    # Retrieve user from the database if it exists
    user = User.query.filter_by(email=data["email"]).first()
    if user and bcrypt.check_password_hash(
        pw_hash=user.password, password=data["password"]
    ):
        response = jsonify({"success": True})
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7) if data["remember"] else timedelta(hours=1),
        )
        set_access_cookies(response, access_token)
        return response, 200

    return jsonify({"success": False, "message": "Invalid username and password"}), 401


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """
    Logout endpoint. Invalidates the JWT token.
    """
    response = jsonify({"success": True})
    unset_jwt_cookies(response)
    return response, 200


@app.route("/api/auth/validate", methods=["GET"])
@jwt_required()
def validate():
    """
    Validate endpoint. Returns 200 if the JWT token is still valid.
    """
    return jsonify({"success": False}), 200
