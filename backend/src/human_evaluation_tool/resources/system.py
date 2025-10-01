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

from .. import app, db
from ..models import Annotation, AnnotationSystem, System
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError


@app.route("/api/systems", methods=["GET"])
@jwt_required()
def read_systems():
    """
    Reads all systems.
    """
    systems = db.session.query(System).all()
    return jsonify([s.to_dict() for s in systems]), 200


@app.route("/api/systems", methods=["POST"])
@jwt_required()
def create_system():
    """
    Creates a new system.
    """
    data = request.get_json()

    # Confirm that all required fields are present
    if "name" not in data:
        return {"message": "Missing required field"}, 422

    # Check if a system with the same name already exists
    if db.session.query(System).filter_by(name=data["name"]).first():
        return {"message": "System already exists"}, 409

    try:
        # Create the system and save it to the database
        system = System(
            name=data["name"], createdAt=datetime.now(), updatedAt=datetime.now()
        )
        db.session.add(system)
        db.session.commit()

        return jsonify(system.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/systems/<int:id>", methods=["GET"])
@jwt_required()
def read_system(id):
    """
    Reads a specific system.
    """
    system = db.session.query(System).get(id)
    if not system:
        return {"message": "System not found"}, 404

    return jsonify(system.to_dict()), 200


@app.route("/api/systems/<int:id>", methods=["PUT"])
@jwt_required()
def update_system(id):
    """
    Updates a specific system.
    """
    system = db.session.query(System).get(id)
    if not system:
        return {"message": "System not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    if "name" not in data:
        return {"message": "Missing required field"}, 422

    # Check if a system with the requested name already exists
    if (
        db.session.query(System)
        .filter(System.id != id, System.name == data["name"])
        .first()
    ):
        return {"message": "System already exists"}, 409

    try:
        # Update the system and save it to the database
        system.name = data["name"]
        system.updatedAt = datetime.now()
        db.session.commit()

        return jsonify(system.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/systems/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_system(id):
    """
    Deletes a specific system.
    """
    system = db.session.query(System).get(id)
    if not system:
        return {"message": "System not found"}, 404

    try:
        # Delete the system from the database
        db.session.delete(system)
        db.session.commit()

        return jsonify({}), 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/annotations/<int:a_id>/systems", methods=["GET"])
@jwt_required()
def read_annotation_systems(a_id):
    """
    Reads the systems of an annotation.
    """
    if not db.session.query(Annotation).get(a_id):
        return {"message": "Annotation not found"}, 404

    systems = db.session.query(AnnotationSystem).filter_by(annotationId=a_id).all()
    return jsonify([s.to_dict() for s in systems]), 200


@app.route("/api/annotations/<int:a_id>/systems", methods=["POST"])
@jwt_required()
def create_annotation_system(a_id):
    """
    Add a new system for an annotation.
    """
    if not db.session.query(Annotation).get(a_id):
        return {"message": "Annotation not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = ["systemId", "translation"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    # Verify if provided systemId is valid
    if not db.session.query(System).get(data["systemId"]):
        return {"message": "Invalid systemId"}, 422

    # Check if the system already exists
    if (
        db.session.query(AnnotationSystem)
        .filter_by(annotationId=a_id, systemId=data["systemId"])
        .first()
    ):
        return {"message": "System already exists"}, 409

    try:
        # Create the system and save it to the database
        system = AnnotationSystem(
            annotationId=a_id,
            systemId=data["systemId"],
            translation=data["translation"],
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        db.session.add(system)
        db.session.commit()

        return jsonify(system.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/annotations/<int:a_id>/systems/<int:s_id>", methods=["GET"])
@jwt_required()
def read_annotation_system(a_id, s_id):
    """
    Reads a specific system of an annotation.
    """
    system = (
        db.session.query(AnnotationSystem)
        .filter_by(annotationId=a_id, systemId=s_id)
        .first()
    )
    if not system:
        return {"message": "System not found"}, 404

    return jsonify(system.to_dict()), 200


@app.route("/api/annotations/<int:a_id>/systems/<int:s_id>", methods=["PUT"])
@jwt_required()
def update_annotation_system(a_id, s_id):
    """
    Updates a specific system of an annotation.
    """
    system = (
        db.session.query(AnnotationSystem)
        .filter_by(annotationId=a_id, systemId=s_id)
        .first()
    )
    if not system:
        return {"message": "System not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    if "translation" not in data:
        return {"message": "Missing required field"}, 422

    try:
        # Update the system and save it to the database
        system.translation = data["translation"]
        system.updatedAt = datetime.now()
        db.session.commit()

        return jsonify(system.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/annotations/<int:a_id>/systems/<int:s_id>", methods=["DELETE"])
@jwt_required()
def delete_annotation_system(a_id, s_id):
    """
    Deletes a specific system of an annotation.
    """
    system = (
        db.session.query(AnnotationSystem)
        .filter_by(annotationId=a_id, systemId=s_id)
        .first()
    )
    if not system:
        return {"message": "System not found"}, 404

    try:
        # Delete the system from the database
        db.session.delete(system)
        db.session.commit()

        return jsonify({}), 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500
