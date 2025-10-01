"""Annotation CRUD endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .. import db
from ..models import Annotation, Bitext, Evaluation, User

bp = Blueprint("annotations", __name__)


def _current_time() -> datetime:
    return datetime.now()


def _validate_required_fields(data: dict[str, Any], fields: list[str]) -> bool:
    return all(field in data for field in fields)


def _validate_foreign_keys(data: dict[str, Any]) -> tuple[bool, str | None]:
    if db.session.get(User, data["userId"]) is None:
        return False, "Invalid userId"
    if db.session.get(Evaluation, data["evaluationId"]) is None:
        return False, "Invalid evaluationId"
    if db.session.get(Bitext, data["bitextId"]) is None:
        return False, "Invalid bitextId"
    return True, None


@bp.get("/api/annotations")
@jwt_required()
def read_annotations() -> ResponseReturnValue:
    """Return all annotations for the authenticated user."""

    identity = get_jwt_identity()
    if identity is None:
        return {"message": "Missing user identity"}, 401

    annotations = db.session.execute(
        select(Annotation).filter_by(userId=int(identity))
    ).scalars().all()
    return jsonify([annotation.to_dict() for annotation in annotations]), 200


@bp.post("/api/annotations")
@jwt_required()
def create_annotation() -> ResponseReturnValue:
    """Create a new annotation."""

    data = request.get_json(silent=True) or {}
    required_fields = ["userId", "evaluationId", "bitextId"]
    if not _validate_required_fields(data, required_fields):
        return {"message": "Missing required field"}, 422

    valid, error_message = _validate_foreign_keys(data)
    if not valid:
        return {"message": error_message}, 422

    try:
        now = _current_time()
        annotation = Annotation(
            userId=data["userId"],
            evaluationId=data["evaluationId"],
            bitextId=data["bitextId"],
            isAnnotated=bool(data.get("isAnnotated", False)),
            comment=data.get("comment"),
            createdAt=now,
            updatedAt=now,
        )
        db.session.add(annotation)
        db.session.commit()
        return jsonify(annotation.to_dict()), 201
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.get("/api/annotations/<int:annotation_id>")
@jwt_required()
def read_annotation(annotation_id: int) -> ResponseReturnValue:
    """Return a single annotation."""

    annotation = db.session.get(Annotation, annotation_id)
    if annotation is None:
        return {"message": "Annotation not found"}, 404
    return jsonify(annotation.to_dict()), 200


@bp.put("/api/annotations/<int:annotation_id>")
@jwt_required()
def update_annotation(annotation_id: int) -> ResponseReturnValue:
    """Update an annotation."""

    annotation = db.session.get(Annotation, annotation_id)
    if annotation is None:
        return {"message": "Annotation not found"}, 404

    data = request.get_json(silent=True) or {}
    required_fields = ["userId", "evaluationId", "bitextId"]
    if not _validate_required_fields(data, required_fields):
        return {"message": "Missing required field"}, 422

    valid, error_message = _validate_foreign_keys(data)
    if not valid:
        return {"message": error_message}, 422

    try:
        annotation.userId = data["userId"]
        annotation.evaluationId = data["evaluationId"]
        annotation.bitextId = data["bitextId"]
        if "isAnnotated" in data:
            annotation.isAnnotated = bool(data["isAnnotated"])
        if "comment" in data:
            annotation.comment = data["comment"]
        annotation.updatedAt = _current_time()
        db.session.commit()
        return jsonify(annotation.to_dict()), 200
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.delete("/api/annotations/<int:annotation_id>")
@jwt_required()
def delete_annotation(annotation_id: int) -> ResponseReturnValue:
    """Delete an annotation."""

    annotation = db.session.get(Annotation, annotation_id)
    if annotation is None:
        return {"message": "Annotation not found"}, 404

    try:
        db.session.delete(annotation)
        db.session.commit()
        return jsonify({}), 204
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500

