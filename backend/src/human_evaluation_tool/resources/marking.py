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

# Marking endpoints.

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .. import db
from ..models import Annotation, Marking, System


MARKING_RESOURCE_PATH = (
    "/api/annotations/<int:annotation_id>/systems/"
    "<int:system_id>/markings/<int:marking_id>"
)


bp = Blueprint("markings", __name__)


def _current_time() -> datetime:
    return datetime.now()


def _require_annotation(annotation_id: int) -> Annotation | ResponseReturnValue:
    annotation = db.session.get(Annotation, annotation_id)
    if annotation is None:
        return {"message": "Annotation not found"}, 404

    identity = get_jwt_identity()
    if identity is None or annotation.userId != int(identity):
        return {"message": "Unauthorized"}, 401

    return annotation


def _require_system(system_id: int) -> ResponseReturnValue | None:
    if db.session.get(System, system_id) is None:
        return {"message": "System not found"}, 404
    return None


def _get_marking(annotation_id: int, system_id: int, marking_id: int) -> Marking | None:
    return db.session.execute(
        select(Marking).filter_by(
            id=marking_id, annotationId=annotation_id, systemId=system_id
        )
    ).scalar_one_or_none()


@bp.get("/api/annotations/<int:annotation_id>/markings")
@jwt_required()
def read_markings(annotation_id: int) -> ResponseReturnValue:
    """Return markings for an annotation."""

    annotation_or_error = _require_annotation(annotation_id)
    if not isinstance(annotation_or_error, Annotation):
        return annotation_or_error
    annotation = annotation_or_error

    markings = (
        db.session.execute(select(Marking).filter_by(annotationId=annotation.id))
        .scalars()
        .all()
    )
    return jsonify([marking.to_dict() for marking in markings]), 200


@bp.post("/api/annotations/<int:annotation_id>/systems/<int:system_id>/markings")
@jwt_required()
def create_marking(annotation_id: int, system_id: int) -> ResponseReturnValue:
    """Create a marking for an annotation."""

    annotation_or_error = _require_annotation(annotation_id)
    if not isinstance(annotation_or_error, Annotation):
        return annotation_or_error
    annotation = annotation_or_error

    system_error = _require_system(system_id)
    if system_error is not None:
        return system_error

    data = request.get_json(silent=True) or {}
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
        now = _current_time()
        marking = Marking(
            annotationId=annotation.id,
            systemId=system_id,
            errorStart=data["errorStart"],
            errorEnd=data["errorEnd"],
            errorCategory=data["errorCategory"],
            errorSeverity=data["errorSeverity"],
            isSource=bool(data["isSource"]),
            createdAt=now,
            updatedAt=now,
        )
        db.session.add(marking)
        db.session.commit()
        return jsonify(marking.to_dict()), 201
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.get(MARKING_RESOURCE_PATH)
@jwt_required()
def read_marking(
    annotation_id: int, system_id: int, marking_id: int
) -> ResponseReturnValue:
    """Return a single marking."""

    annotation_or_error = _require_annotation(annotation_id)
    if not isinstance(annotation_or_error, Annotation):
        return annotation_or_error
    annotation = annotation_or_error

    system_error = _require_system(system_id)
    if system_error is not None:
        return system_error

    marking = _get_marking(annotation.id, system_id, marking_id)
    if marking is None:
        return {"message": "Marking not found"}, 404
    return jsonify(marking.to_dict()), 200


@bp.put(MARKING_RESOURCE_PATH)
@jwt_required()
def update_marking(
    annotation_id: int, system_id: int, marking_id: int
) -> ResponseReturnValue:
    """Update a marking."""

    annotation_or_error = _require_annotation(annotation_id)
    if not isinstance(annotation_or_error, Annotation):
        return annotation_or_error
    annotation = annotation_or_error
    assert annotation is not None

    system_error = _require_system(system_id)
    if system_error is not None:
        return system_error

    marking = _get_marking(annotation.id, system_id, marking_id)
    if marking is None:
        return {"message": "Marking not found"}, 404

    data = request.get_json(silent=True) or {}
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
        marking.errorStart = data["errorStart"]
        marking.errorEnd = data["errorEnd"]
        marking.errorCategory = data["errorCategory"]
        marking.errorSeverity = data["errorSeverity"]
        marking.isSource = bool(data["isSource"])
        marking.updatedAt = _current_time()
        db.session.commit()
        return jsonify(marking.to_dict()), 200
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.delete(MARKING_RESOURCE_PATH)
@jwt_required()
def delete_marking(
    annotation_id: int, system_id: int, marking_id: int
) -> ResponseReturnValue:
    """Delete a marking."""

    annotation = _require_annotation(annotation_id)
    if not isinstance(annotation, Annotation):
        return annotation

    system_error = _require_system(system_id)
    if system_error is not None:
        return system_error

    marking = _get_marking(annotation.id, system_id, marking_id)
    if marking is None:
        return {"message": "Marking not found"}, 404

    try:
        db.session.delete(marking)
        db.session.commit()
        return jsonify({}), 204
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500
