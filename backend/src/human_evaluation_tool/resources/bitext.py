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

# Bitext endpoints.

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .. import db
from ..models import Bitext, Document


bp = Blueprint("bitexts", __name__)


def _current_time() -> datetime:
    return datetime.now()


@bp.get("/api/bitexts")
@jwt_required()
def read_bitexts() -> ResponseReturnValue:
    """Return all bitexts."""

    bitexts = db.session.execute(select(Bitext)).scalars().all()
    return jsonify([bitext.to_dict() for bitext in bitexts]), 200


@bp.post("/api/bitexts")
@jwt_required()
def create_bitext() -> ResponseReturnValue:
    """Create a new bitext."""

    data = request.get_json(silent=True) or {}
    required_fields = ["documentId", "source", "target"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    if db.session.get(Document, data["documentId"]) is None:
        return {"message": "Invalid documentId"}, 422

    try:
        now = _current_time()
        bitext = Bitext(
            documentId=data["documentId"],
            source=data["source"],
            target=data["target"],
            createdAt=now,
            updatedAt=now,
        )
        db.session.add(bitext)
        db.session.commit()
        return jsonify(bitext.to_dict()), 201
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.get("/api/bitexts/<int:bitext_id>")
@jwt_required()
def read_bitext(bitext_id: int) -> ResponseReturnValue:
    """Return a single bitext."""

    bitext = db.session.get(Bitext, bitext_id)
    if bitext is None:
        return {"message": "Bitext not found"}, 404
    return jsonify(bitext.to_dict()), 200


@bp.put("/api/bitexts/<int:bitext_id>")
@jwt_required()
def update_bitext(bitext_id: int) -> ResponseReturnValue:
    """Update a bitext."""

    bitext = db.session.get(Bitext, bitext_id)
    if bitext is None:
        return {"message": "Bitext not found"}, 404

    data = request.get_json(silent=True) or {}
    required_fields = ["documentId", "source", "target"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    try:
        bitext.documentId = data["documentId"]
        bitext.source = data["source"]
        bitext.target = data["target"]
        bitext.updatedAt = _current_time()
        db.session.commit()
        return jsonify(bitext.to_dict()), 200
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.delete("/api/bitexts/<int:bitext_id>")
@jwt_required()
def delete_bitext(bitext_id: int) -> ResponseReturnValue:
    """Delete a bitext."""

    bitext = db.session.get(Bitext, bitext_id)
    if bitext is None:
        return {"message": "Bitext not found"}, 404

    try:
        db.session.delete(bitext)
        db.session.commit()
        return jsonify({}), 204
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500
