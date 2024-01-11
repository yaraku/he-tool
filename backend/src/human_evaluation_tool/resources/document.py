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


@app.route("/api/documents", methods=["GET"])
@jwt_required()
def read_documents():
    """
    Reads all documents.
    """
    documents = db.session.query(Document).all()
    return jsonify([d.to_dict() for d in documents]), 200


@app.route("/api/documents", methods=["POST"])
@jwt_required()
def create_document():
    """
    Creates a new document.
    """
    data = request.get_json()

    # Confirm that all required fields are present
    if "name" not in data:
        return {"message": "Missing required field"}, 422

    try:
        # Create the document and save it to the database
        document = Document(
            name=data["name"], createdAt=datetime.now(), updatedAt=datetime.now()
        )
        db.session.add(document)
        db.session.commit()

        return jsonify(document.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/documents/<int:id>", methods=["GET"])
@jwt_required()
def read_document(id):
    """
    Reads a document.
    """
    document = db.session.query(Document).get(id)
    if not document:
        return {"message": "Document not found"}, 404

    return jsonify(document.to_dict()), 200


@app.route("/api/documents/<int:id>/bitexts", methods=["GET"])
@jwt_required()
def read_document_bitexts(id):
    """
    Reads all bitexts for a document.
    """
    document = db.session.query(Document).get(id)
    if not document:
        return {"message": "Document not found"}, 404

    bitexts = db.session.query(Bitext).filter_by(documentId=id).all()
    return jsonify([b.to_dict() for b in bitexts]), 200


@app.route("/api/documents/<int:id>", methods=["PUT"])
@jwt_required()
def update_document(id):
    """
    Updates a document.
    """
    document = db.session.query(Document).get(id)
    if not document:
        return {"message": "Document not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    if "name" not in data:
        return {"message": "Missing required field"}, 422

    # Verify if provided documentId is valid
    if not db.session.query(Document).get(data["documentId"]):
        return {"message": "Invalid documentId"}, 422

    try:
        # Update the document and save it to the database
        document.name = data["name"]
        document.updatedAt = datetime.now()
        db.session.commit()

        return jsonify(document.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/documents/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_document(id):
    """
    Deletes a document.
    """
    document = db.session.query(Document).get(id)
    if not document:
        return {"message": "Document not found"}, 404

    try:
        # Delete the document from the database
        db.session.delete(document)
        db.session.commit()

        return jsonify({}), 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500
