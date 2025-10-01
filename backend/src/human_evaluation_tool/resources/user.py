"""User CRUD endpoints."""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError

from .. import bcrypt, db
from ..models import User

bp = Blueprint("users", __name__)


def _current_time() -> datetime:
    return datetime.now()


def _select_all_users() -> Select[tuple[User]]:
    return select(User)


@bp.get("/api/users")
@jwt_required()
def read_users() -> ResponseReturnValue:
    """Return all users."""

    users = db.session.execute(_select_all_users()).scalars().all()
    return jsonify([user.to_dict() for user in users]), 200


@bp.post("/api/users")
@jwt_required()
def create_user() -> ResponseReturnValue:
    """Create a new user."""

    data = request.get_json(silent=True) or {}
    required_fields = ["email", "password", "nativeLanguage"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    existing = db.session.execute(
        select(User).filter_by(email=data["email"])
    ).scalar_one_or_none()
    if existing is not None:
        return {"message": "User already exists"}, 409

    try:
        now = _current_time()
        user = User(
            email=data["email"],
            password=bcrypt.generate_password_hash(data["password"]).decode("utf-8"),
            nativeLanguage=data["nativeLanguage"],
            createdAt=now,
            updatedAt=now,
        )
        db.session.add(user)
        db.session.commit()
        return {"user": user.to_dict()}, 201
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.get("/api/users/<int:user_id>")
@jwt_required()
def read_user(user_id: int) -> ResponseReturnValue:
    """Return a specific user."""

    user = db.session.get(User, user_id)
    if user is None:
        return {"message": "User not found"}, 404
    return jsonify(user.to_dict()), 200


@bp.put("/api/users/<int:user_id>")
@jwt_required()
def update_user(user_id: int) -> ResponseReturnValue:
    """Update the details of a user."""

    user = db.session.get(User, user_id)
    if user is None:
        return {"message": "User not found"}, 404

    data = request.get_json(silent=True) or {}
    required_fields = ["email", "password", "nativeLanguage"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    conflict = db.session.execute(
        select(User).filter(User.id != user_id, User.email == data["email"])
    ).scalar_one_or_none()
    if conflict is not None:
        return {"message": "User already exists"}, 409

    try:
        user.email = data["email"]
        user.password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
        user.nativeLanguage = data["nativeLanguage"]
        user.updatedAt = _current_time()
        db.session.commit()
        return {"user": user.to_dict()}, 200
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.delete("/api/users/<int:user_id>")
@jwt_required()
def delete_user(user_id: int) -> ResponseReturnValue:
    """Delete a user."""

    user = db.session.get(User, user_id)
    if user is None:
        return {"message": "User not found"}, 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({}), 204
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


