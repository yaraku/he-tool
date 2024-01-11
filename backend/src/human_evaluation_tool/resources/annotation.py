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
from ..models import Annotation, Bitext, Evaluation, User
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError


@app.route("/api/annotations", methods=["GET"])
@jwt_required()
def read_annotations():
    """
    Reads all annotations.
    """
    annotations = (
        db.session.query(Annotation).filter_by(userId=get_jwt_identity()).all()
    )
    return jsonify([a.to_dict() for a in annotations]), 200


@app.route("/api/annotations", methods=["POST"])
@jwt_required()
def create_annotation():
    """
    Creates a new annotation.
    """
    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = ["userId", "evaluationId", "bitextId"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    # Verify if provided userId, evaluationId and bitextId are valid
    if not db.session.query(User).get(data["userId"]):
        return {"message": "Invalid userId"}, 422
    if not db.session.query(Evaluation).get(data["evaluationId"]):
        return {"message": "Invalid evaluationId"}, 422
    if not db.session.query(Bitext).get(data["bitextId"]):
        return {"message": "Invalid bitextId"}, 422

    try:
        # Create the annotation and save it to the database
        annotation = Annotation(
            userId=data["userId"],
            evaluationId=data["evaluationId"],
            bitextId=data["bitextId"],
            isAnnotated=data.get("isAnnotated", False),
            comment=data.get("comment", None),
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        db.session.add(annotation)
        db.session.commit()

        return jsonify(annotation.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/annotations/<int:id>", methods=["GET"])
@jwt_required()
def read_annotation(id):
    """
    Reads an annotation.
    """
    annotation = db.session.query(Annotation).get(id)
    if not annotation:
        return {"message": "Annotation not found"}, 404

    return jsonify(annotation.to_dict()), 200


@app.route("/api/annotations/<int:id>", methods=["PUT"])
@jwt_required()
def update_annotation(id):
    """
    Updates an annotation.
    """
    annotation = db.session.query(Annotation).get(id)
    if not annotation:
        return {"message": "Annotation not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = ["userId", "evaluationId", "bitextId"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    # Verify if provided userId, evaluationId and bitextId are valid
    if not db.session.query(User).get(data["userId"]):
        return {"message": "Invalid userId"}, 422
    if not db.session.query(Evaluation).get(data["evaluationId"]):
        return {"message": "Invalid evaluationId"}, 422
    if not db.session.query(Bitext).get(data["bitextId"]):
        return {"message": "Invalid bitextId"}, 422

    try:
        # Update the annotation and save it to the database
        annotation.userId = data["userId"]
        annotation.evaluationId = data["evaluationId"]
        annotation.bitextId = data["bitextId"]
        if "isAnnotated" in data:
            annotation.isAnnotated = data["isAnnotated"]
        if "comment" in data:
            annotation.comment = data["comment"]
        annotation.updatedAt = datetime.now()
        db.session.commit()

        return jsonify(annotation.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/annotations/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_annotation(id):
    """
    Deletes an annotation.
    """
    annotation = db.session.query(Annotation).get(id)
    if not annotation:
        return {"message": "Annotation not found"}, 404

    try:
        # Delete the annotation from the database
        db.session.delete(annotation)
        db.session.commit()

        return jsonify({}), 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500
