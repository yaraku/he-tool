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
from ..models import Annotation, AnnotationSystem, Bitext, Document, \
    Evaluation, Marking, System, User
from ..utils import CATEGORY_NAME, SEVERITY_NAME
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError


@app.route("/api/evaluations", methods=["GET"])
@jwt_required()
def read_evaluations():
    """
    Reads all evaluations.
    """
    evaluations = db.session.query(Evaluation).all()
    return jsonify([e.to_dict() for e in evaluations]), 200


@app.route("/api/evaluations", methods=["POST"])
@jwt_required()
def create_evaluation():
    """
    Creates a new evaluation.
    """
    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = ["name", "type"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    # Check if an evaluation with the same name already exists
    if db.session.query(Evaluation).filter_by(name=data["name"]).first():
        return {"message": "Evaluation already exists"}, 409

    try:
        # Create the evaluation and save it to the database
        evaluation = Evaluation(
            name=data["name"],
            type=data["type"],
            isFinished=data.get("isFinished", False),
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        db.session.add(evaluation)
        db.session.commit()

        return jsonify(evaluation.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/evaluations/<int:id>", methods=["GET"])
@jwt_required()
def read_evaluation(id):
    """
    Reads a specific evaluation.
    """
    evaluation = db.session.query(Evaluation).get(id)
    if not evaluation:
        return {"message": "Evaluation not found"}, 404

    return jsonify(evaluation.to_dict()), 200


@app.route("/api/evaluations/<int:id>/annotations", methods=["GET"])
@jwt_required()
def read_evaluation_annotations(id):
    """
    Reads all annotations for a specific evaluation.
    """
    evaluation = db.session.query(Evaluation).get(id)
    if not evaluation:
        return {"message": "Evaluation not found"}, 404

    annotations = db.session.query(Annotation)\
        .filter_by(userId=get_jwt_identity(), evaluationId=id)\
        .all()

    return jsonify([a.to_dict() for a in annotations]), 200


@app.route("/api/evaluations/<int:id>/results", methods=["GET"])
@jwt_required()
def read_evaluation_results(id):
    """
    Reads all results for a specific evaluation.
    """
    if not db.session.query(Evaluation).get(id):
        return {"message": "Evaluation not found"}, 404

    annotations = db.session.query(Annotation)\
        .filter_by(evaluationId=id)\
        .all()

    results = []
    for annotation in annotations:
        bitext = db.session.query(Bitext).get(annotation.bitextId)
        user = db.session.query(User).get(annotation.userId)
        document = db.session.query(Document).get(bitext.documentId)
        markings = db.session.query(Marking)\
            .filter_by(annotationId=annotation.id)\
            .all()

        for marking in markings:
            row = []

            # Get required information for building the row
            annotation_system = db.session.query(AnnotationSystem)\
                .filter_by(annotationId=annotation.id,
                           systemId=marking.systemId)\
                .first()
            system = db.session.query(System).get(marking.systemId)

            # Add marking information to the row
            row.append(system.name)
            row.append(document.name)
            row.append(str(bitext.id))
            row.append(str(bitext.id))
            row.append(user.email.split("@")[0])

            if marking.isSource:
                source = bitext.source.replace("\n", "<NEWLINE>").split(" ")
                source.insert(marking.errorStart, "<v>")
                source.insert(marking.errorEnd + 2, "</v>")

                row.append(" ".join(source))
                row.append(annotation_system.translation.replace("\n", "<NEWLINE>"))
            else:
                translation = annotation_system.translation.replace("\n", "<NEWLINE>").split(" ")
                translation.insert(marking.errorStart, "<v>")
                translation.insert(marking.errorEnd + 2, "</v>")

                row.append(bitext.source.replace("\n", "<NEWLINE>"))
                row.append(" ".join(translation))

            row.append(CATEGORY_NAME[marking.errorCategory])
            row.append(SEVERITY_NAME[marking.errorSeverity])
            row.append(annotation.comment)

            # Add the row to the results
            results.append("\t".join(row) + "\n")

    return jsonify(results), 200


@app.route("/api/evaluations/<int:id>", methods=["PUT"])
@jwt_required()
def update_evaluation(id):
    """
    Updates a specific evaluation.
    """
    evaluation = db.session.query(Evaluation).get(id)
    if not evaluation:
        return {"message": "Evaluation not found"}, 404

    data = request.get_json()

    # Confirm that all required fields are present
    required_fields = ["name", "type"]
    if any(field not in data for field in required_fields):
        return {"message": "Missing required field"}, 422

    # Check if an evaluation with the same name already exists
    if db.session.query(Evaluation).filter(
            Evaluation.id != id,
            Evaluation.name == data["name"]
    ).first():
        return {"message": "Evaluation already exists"}, 409

    try:
        # Update the evaluation and save it to the database
        evaluation.name = data["name"]
        evaluation.type = data["type"]
        if "isFinished" in data:
            evaluation.isFinished = data["isFinished"]
        evaluation.updatedAt = datetime.now()
        db.session.commit()

        return jsonify(evaluation.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500


@app.route("/api/evaluations/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_evaluation(id):
    """
    Deletes a specific evaluation.
    """
    evaluation = db.session.query(Evaluation).get(id)
    if not evaluation:
        return {"message": "Evaluation not found"}, 404

    try:
        # Delete the evaluation and save it to the database
        db.session.delete(evaluation)
        db.session.commit()

        return jsonify({}), 204
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": str(e)}, 500
