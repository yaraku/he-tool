"""System management endpoints."""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .. import db
from ..models import Annotation, AnnotationSystem, System

bp = Blueprint("systems", __name__)


def _current_time() -> datetime:
    return datetime.now()


def _get_annotation_system(annotation_id: int, system_id: int) -> AnnotationSystem | None:
    return db.session.execute(
        select(AnnotationSystem).filter_by(annotationId=annotation_id, systemId=system_id)
    ).scalar_one_or_none()


@bp.get("/api/systems")
@jwt_required()
def read_systems() -> ResponseReturnValue:
    """Return all systems."""

    systems = db.session.execute(select(System)).scalars().all()
    return jsonify([system.to_dict() for system in systems]), 200


@bp.post("/api/systems")
@jwt_required()
def create_system() -> ResponseReturnValue:
    """Create a new system."""

    data = request.get_json(silent=True) or {}
    if "name" not in data:
        return {"message": "Missing required field"}, 422

    existing = db.session.execute(
        select(System).filter_by(name=data["name"])
    ).scalar_one_or_none()
    if existing is not None:
        return {"message": "System already exists"}, 409

    try:
        now = _current_time()
        system = System(name=data["name"], createdAt=now, updatedAt=now)
        db.session.add(system)
        db.session.commit()
        return jsonify(system.to_dict()), 201
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.get("/api/systems/<int:system_id>")
@jwt_required()
def read_system(system_id: int) -> ResponseReturnValue:
    """Return a specific system."""

    system = db.session.get(System, system_id)
    if system is None:
        return {"message": "System not found"}, 404
    return jsonify(system.to_dict()), 200


@bp.put("/api/systems/<int:system_id>")
@jwt_required()
def update_system(system_id: int) -> ResponseReturnValue:
    """Update a system."""

    system = db.session.get(System, system_id)
    if system is None:
        return {"message": "System not found"}, 404

    data = request.get_json(silent=True) or {}
    if "name" not in data:
        return {"message": "Missing required field"}, 422

    conflict = db.session.execute(
        select(System).filter(System.id != system_id, System.name == data["name"])
    ).scalar_one_or_none()
    if conflict is not None:
        return {"message": "System already exists"}, 409

    try:
        system.name = data["name"]
        system.updatedAt = _current_time()
        db.session.commit()
        return jsonify(system.to_dict()), 200
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.delete("/api/systems/<int:system_id>")
@jwt_required()
def delete_system(system_id: int) -> ResponseReturnValue:
    """Delete a system."""

    system = db.session.get(System, system_id)
    if system is None:
        return {"message": "System not found"}, 404

    try:
        db.session.delete(system)
        db.session.commit()
        return jsonify({}), 204
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.get("/api/annotations/<int:annotation_id>/systems")
@jwt_required()
def read_annotation_systems(annotation_id: int) -> ResponseReturnValue:
    """Return systems linked to an annotation."""

    if db.session.get(Annotation, annotation_id) is None:
        return {"message": "Annotation not found"}, 404

    systems = db.session.execute(
        select(AnnotationSystem).filter_by(annotationId=annotation_id)
    ).scalars().all()
    return jsonify([system.to_dict() for system in systems]), 200


@bp.post("/api/annotations/<int:annotation_id>/systems")
@jwt_required()
def create_annotation_system(annotation_id: int) -> ResponseReturnValue:
    """Add a new system record for an annotation."""

    if db.session.get(Annotation, annotation_id) is None:
        return {"message": "Annotation not found"}, 404

    data = request.get_json(silent=True) or {}
    required_fields = ["systemId", "translation"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    if db.session.get(System, data["systemId"]) is None:
        return {"message": "Invalid systemId"}, 422

    if _get_annotation_system(annotation_id, data["systemId"]) is not None:
        return {"message": "System already exists"}, 409

    try:
        now = _current_time()
        annotation_system = AnnotationSystem(
            annotationId=annotation_id,
            systemId=data["systemId"],
            translation=data["translation"],
            createdAt=now,
            updatedAt=now,
        )
        db.session.add(annotation_system)
        db.session.commit()
        return jsonify(annotation_system.to_dict()), 201
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.get("/api/annotations/<int:annotation_id>/systems/<int:system_id>")
@jwt_required()
def read_annotation_system(annotation_id: int, system_id: int) -> ResponseReturnValue:
    """Return a specific annotation system entry."""

    annotation_system = _get_annotation_system(annotation_id, system_id)
    if annotation_system is None:
        return {"message": "System not found"}, 404
    return jsonify(annotation_system.to_dict()), 200


@bp.put("/api/annotations/<int:annotation_id>/systems/<int:system_id>")
@jwt_required()
def update_annotation_system(annotation_id: int, system_id: int) -> ResponseReturnValue:
    """Update a specific annotation system."""

    annotation_system = _get_annotation_system(annotation_id, system_id)
    if annotation_system is None:
        return {"message": "System not found"}, 404

    data = request.get_json(silent=True) or {}
    if "translation" not in data:
        return {"message": "Missing required field"}, 422

    try:
        annotation_system.translation = data["translation"]
        annotation_system.updatedAt = _current_time()
        db.session.commit()
        return jsonify(annotation_system.to_dict()), 200
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500


@bp.delete("/api/annotations/<int:annotation_id>/systems/<int:system_id>")
@jwt_required()
def delete_annotation_system(annotation_id: int, system_id: int) -> ResponseReturnValue:
    """Delete a specific annotation system entry."""

    annotation_system = _get_annotation_system(annotation_id, system_id)
    if annotation_system is None:
        return {"message": "System not found"}, 404

    try:
        db.session.delete(annotation_system)
        db.session.commit()
        return jsonify({}), 204
    except SQLAlchemyError as exc:
        db.session.rollback()
        return {"message": str(exc)}, 500

