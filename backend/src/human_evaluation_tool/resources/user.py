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

from datetime import datetime

from .. import app, bcrypt, db
from ..models import User
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError


@app.route("/api/users", methods=["GET"])
@jwt_required()
def read_users():
    """
    Reads all users.
    """
    users = db.session.query(User).all()
    return jsonify([u.to_dict() for u in users]), 200


@app.route("/api/users", methods=["POST"])
@jwt_required()
def create_user():
    """
    Creates a new user.
    """
    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = ["email", "password", "nativeLanguage"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    # Check if a user with the same email already exists
    if db.session.query(User).filter_by(email=data["email"]).first():
        return {"message": "User already exists"}, 409

    try:
        # Create the user and save it to the database
        user = User(
            email=data["email"],
            password=bcrypt.generate_password_hash(data["password"]).decode("utf-8"),
            nativeLanguage=data["nativeLanguage"],
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        db.session.add(user)
        db.session.commit()

        return {"user": user.to_dict()}, 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/users/<int:id>", methods=["GET"])
@jwt_required()
def read_user(id):
    """
    Reads a specific user.
    """
    user = db.session.query(User).get(id)
    if not user:
        return {"message": "User not found"}, 404

    return jsonify(user.to_dict()), 200


@app.route("/api/users/<int:id>", methods=["PUT"])
@jwt_required()
def update_user(id):
    """
    Updates a specific user.
    """
    user = db.session.query(User).get(id)
    if not user:
        return {"message": "User not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = ["email", "password", "nativeLanguage"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    # Check if a user with the requested email already exists
    if (
        db.session.query(User)
        .filter(User.id != id, User.email == data["email"])
        .first()
    ):
        return {"message": "User already exists"}, 409

    try:
        # Update the user and save it to the database
        user.email = data["email"]
        user.password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
        user.nativeLanguage = data["nativeLanguage"]
        user.updatedAt = datetime.now()
        db.session.commit()

        return {"user": user.to_dict()}, 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/users/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    """
    Deletes a specific user.
    """
    user = db.session.query(User).get(id)
    if not user:
        return {"message": "User not found"}, 404

    try:
        # Delete the user from the database
        db.session.delete(user)
        db.session.commit()

        return jsonify({}), 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500
