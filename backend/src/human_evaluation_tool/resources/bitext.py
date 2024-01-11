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
from ..models import Bitext, Document
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError


@app.route("/api/bitexts", methods=["GET"])
@jwt_required()
def read_bitexts():
    """
    Reads all bitexts.
    """
    bitexts = db.session.query(Bitext).all()
    return jsonify([b.to_dict() for b in bitexts]), 200


@app.route("/api/bitexts", methods=["POST"])
@jwt_required()
def create_bitext():
    """
    Creates a new bitext.
    """
    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = ["documentId", "source", "target"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    # Verify if provided documentId is valid
    if not db.session.query(Document).get(data["documentId"]):
        return {"message": "Invalid documentId"}, 422

    try:
        # Create the bitext and save it to the database
        bitext = Bitext(
            documentId=data["documentId"],
            source=data["source"],
            target=data["target"],
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        db.session.add(bitext)
        db.session.commit()

        return jsonify(bitext.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/bitexts/<int:id>", methods=["GET"])
@jwt_required()
def read_bitext(id):
    """
    Reads a bitext.
    """
    bitext = db.session.query(Bitext).get(id)
    if not bitext:
        return {"message": "Bitext not found"}, 404

    return jsonify(bitext.to_dict()), 200


@app.route("/api/bitexts/<int:id>", methods=["PUT"])
@jwt_required()
def update_bitext(id):
    """
    Updates a bitext.
    """
    bitext = db.session.query(Bitext).get(id)
    if not bitext:
        return {"message": "Bitext not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = ["documentId", "source", "target"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    try:
        # Update the bitext and save it to the database
        bitext.documentId = data["documentId"]
        bitext.source = data["source"]
        bitext.target = data["target"]
        bitext.updatedAt = datetime.now()
        db.session.commit()

        return jsonify(bitext.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/bitexts/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_bitext(id):
    """
    Deletes a bitext.
    """
    bitext = db.session.query(Bitext).get(id)
    if not bitext:
        return {"message": "Bitext not found"}, 404

    try:
        # Delete the bitext and save it to the database
        db.session.delete(bitext)
        db.session.commit()

        return jsonify({}), 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500
