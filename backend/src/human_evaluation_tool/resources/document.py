"""Copyright (C) 2023 Yaraku, Inc.

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

# Document endpoints.

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .. import db
from ..models import Bitext, Document

bp = Blueprint("documents", __name__)


def _current_time() -> datetime:
    return datetime.now()


@bp.get("/api/documents")
@jwt_required()
def read_documents() -> ResponseReturnValue:
    """Return all documents."""

    documents = db.session.execute(select(Document)).scalars().all()
    return jsonify([document.to_dict() for document in documents]), 200


@bp.post("/api/documents")
@jwt_required()
def create_document() -> ResponseReturnValue:
    """Create a new document."""

    data = request.get_json(silent=True) or {}
    if "name" not in data:
        return {"message": "Missing required field"}, 422

    try:
        now = _current_time()
        document = Document(name=data["name"], createdAt=now, updatedAt=now)
        db.session.add(document)
        db.session.commit()
        return jsonify(document.to_dict()), 201
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.get("/api/documents/<int:document_id>")
@jwt_required()
def read_document(document_id: int) -> ResponseReturnValue:
    """Return a single document."""

    document = db.session.get(Document, document_id)
    if document is None:
        return {"message": "Document not found"}, 404
    return jsonify(document.to_dict()), 200


@bp.get("/api/documents/<int:document_id>/bitexts")
@jwt_required()
def read_document_bitexts(document_id: int) -> ResponseReturnValue:
    """Return all bitexts for a document."""

    if db.session.get(Document, document_id) is None:
        return {"message": "Document not found"}, 404

    bitexts = db.session.execute(
        select(Bitext).filter_by(documentId=document_id)
    ).scalars().all()
    return jsonify([bitext.to_dict() for bitext in bitexts]), 200


@bp.put("/api/documents/<int:document_id>")
@jwt_required()
def update_document(document_id: int) -> ResponseReturnValue:
    """Update a document."""

    document = db.session.get(Document, document_id)
    if document is None:
        return {"message": "Document not found"}, 404

    data = request.get_json(silent=True) or {}
    if "name" not in data:
        return {"message": "Missing required field"}, 422
    if db.session.get(Document, data.get("documentId")) is None:
        return {"message": "Invalid documentId"}, 422

    try:
        document.name = data["name"]
        document.updatedAt = _current_time()
        db.session.commit()
        return jsonify(document.to_dict()), 200
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.delete("/api/documents/<int:document_id>")
@jwt_required()
def delete_document(document_id: int) -> ResponseReturnValue:
    """Delete a document."""

    document = db.session.get(Document, document_id)
    if document is None:
        return {"message": "Document not found"}, 404

    try:
        db.session.delete(document)
        db.session.commit()
        return jsonify({}), 204
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500

