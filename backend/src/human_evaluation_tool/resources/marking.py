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
from ..models import Annotation, Marking, System
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError


@app.route("/api/annotations/<int:a_id>/markings", methods=["GET"])
@jwt_required()
def read_markings(a_id):
    """
    Reads all markings for an annotation.
    """
    if not db.session.query(Annotation).get(a_id):
        return {"message": "Annotation not found"}, 404
    if db.session.query(Annotation).get(a_id).userId != get_jwt_identity():
        return {"message": "Unauthorized"}, 401

    markings = db.session.query(Marking).filter_by(annotationId=a_id).all()
    return jsonify([m.to_dict() for m in markings]), 200


@app.route("/api/annotations/<int:a_id>/systems/<int:s_id>/markings", methods=["POST"])
@jwt_required()
def create_marking(a_id, s_id):
    """
    Creates a new marking for an annotation.
    """
    if not db.session.query(Annotation).get(a_id):
        return {"message": "Annotation not found"}, 404
    if db.session.query(Annotation).get(a_id).userId != get_jwt_identity():
        return {"message": "Unauthorized"}, 401
    if not db.session.query(System).get(s_id):
        return {"message": "System not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = [
        "errorStart",
        "errorEnd",
        "errorCategory",
        "errorSeverity",
        "isSource",
    ]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    try:
        # Create the marking and save it to the database
        marking = Marking(
            annotationId=a_id,
            systemId=s_id,
            errorStart=data["errorStart"],
            errorEnd=data["errorEnd"],
            errorCategory=data["errorCategory"],
            errorSeverity=data["errorSeverity"],
            isSource=data["isSource"],
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        db.session.add(marking)
        db.session.commit()

        return jsonify(marking.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route(
    "/api/annotations/<int:a_id>/systems/<int:s_id>/markings/<int:m_id>",
    methods=["GET"],
)
@jwt_required()
def read_marking(a_id, s_id, m_id):
    """
    Reads a marking for an annotation.
    """
    if not db.session.query(Annotation).get(a_id):
        return {"message": "Annotation not found"}, 404
    if db.session.query(Annotation).get(a_id).userId != get_jwt_identity():
        return {"message": "Unauthorized"}, 401
    if not db.session.query(System).get(s_id):
        return {"message": "System not found"}, 404

    marking = (
        db.session.query(Marking)
        .filter_by(id=m_id, annotationId=a_id, systemId=s_id)
        .first()
    )
    if not marking:
        return {"message": "Marking not found"}, 404
    return jsonify(marking.to_dict()), 200


@app.route(
    "/api/annotations/<int:a_id>/systems/<int:s_id>/markings/<int:m_id>",
    methods=["PUT"],
)
@jwt_required()
def update_marking(a_id, s_id, m_id):
    """
    Updates a marking for an annotation.
    """
    if not db.session.query(Annotation).get(a_id):
        return {"message": "Annotation not found"}, 404
    if db.session.query(Annotation).get(a_id).userId != get_jwt_identity():
        return {"message": "Unauthorized"}, 401
    if not db.session.query(System).get(s_id):
        return {"message": "System not found"}, 404

    marking = (
        db.session.query(Marking)
        .filter_by(id=m_id, annotationId=a_id, systemId=s_id)
        .first()
    )
    if not marking:
        return {"message": "Marking not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = [
        "errorStart",
        "errorEnd",
        "errorCategory",
        "errorSeverity",
        "isSource",
    ]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    try:
        # Update the marking and save it to the database
        marking.errorStart = data["errorStart"]
        marking.errorEnd = data["errorEnd"]
        marking.errorCategory = data["errorCategory"]
        marking.errorSeverity = data["errorSeverity"]
        marking.isSource = data["isSource"]
        marking.updatedAt = datetime.now()
        db.session.commit()

        return jsonify(marking.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route(
    "/api/annotations/<int:a_id>/systems/<int:s_id>/markings/<int:m_id>",
    methods=["DELETE"],
)
@jwt_required()
def delete_marking(a_id, s_id, m_id):
    """
    Deletes a marking for an annotation.
    """
    if not db.session.query(Annotation).get(a_id):
        return {"message": "Annotation not found"}, 404
    if db.session.query(Annotation).get(a_id).userId != get_jwt_identity():
        return {"message": "Unauthorized"}, 401
    if not db.session.query(System).get(s_id):
        return {"message": "System not found"}, 404

    marking = (
        db.session.query(Marking)
        .filter_by(id=m_id, annotationId=a_id, systemId=s_id)
        .first()
    )
    if not marking:
        return {"message": "Marking not found"}, 404

    try:
        # Delete the marking from the database
        db.session.delete(marking)
        db.session.commit()

        return {}, 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500
