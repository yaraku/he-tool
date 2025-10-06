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

from sqlalchemy.exc import SQLAlchemyError

from human_evaluation_tool import db


def _request(client, method: str, url: str, **kwargs):
    return getattr(client, method)(url, **kwargs)


def test_annotation_crud_flow(
    auth_client,
    create_annotation,
    create_evaluation,
    create_bitext,
    create_user,
):
    client, login_user = auth_client
    evaluation = create_evaluation(name="Evaluation CRUD")
    bitext = create_bitext()

    list_response = _request(client, "get", "/api/annotations")
    assert list_response.status_code == 200

    create_response = _request(
        client,
        "post",
        "/api/annotations",
        json={
            "userId": login_user.id,
            "evaluationId": evaluation.id,
            "bitextId": bitext.id,
            "isAnnotated": True,
            "comment": "Great",
        },
    )
    assert create_response.status_code == 201
    annotation_id = create_response.get_json()["id"]

    read_response = _request(client, "get", f"/api/annotations/{annotation_id}")
    assert read_response.status_code == 200

    update_response = _request(
        client,
        "put",
        f"/api/annotations/{annotation_id}",
        json={
            "userId": login_user.id,
            "evaluationId": evaluation.id,
            "bitextId": bitext.id,
            "isAnnotated": False,
            "comment": "Updated",
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["isAnnotated"] is False

    delete_response = _request(client, "delete", f"/api/annotations/{annotation_id}")
    assert delete_response.status_code == 204


def test_annotation_create_missing_field(auth_client, create_evaluation, create_bitext):
    client, login_user = auth_client
    evaluation = create_evaluation(name="Missing Field Eval")
    bitext = create_bitext()
    response = _request(
        client,
        "post",
        "/api/annotations",
        json={"userId": login_user.id, "evaluationId": evaluation.id},
    )
    assert response.status_code == 422


def test_annotation_create_invalid_ids(auth_client):
    client, login_user = auth_client
    response = _request(
        client,
        "post",
        "/api/annotations",
        json={"userId": login_user.id, "evaluationId": 999, "bitextId": 999},
    )
    assert response.status_code == 422


def test_annotation_create_invalid_user(auth_client, create_evaluation, create_bitext):
    client, _ = auth_client
    evaluation = create_evaluation(name="Invalid User Eval")
    bitext = create_bitext()
    response = _request(
        client,
        "post",
        "/api/annotations",
        json={"userId": 999, "evaluationId": evaluation.id, "bitextId": bitext.id},
    )
    assert response.status_code == 422


def test_annotation_create_invalid_evaluation(auth_client, create_bitext):
    client, login_user = auth_client
    bitext = create_bitext()
    response = _request(
        client,
        "post",
        "/api/annotations",
        json={"userId": login_user.id, "evaluationId": 999, "bitextId": bitext.id},
    )
    assert response.status_code == 422


def test_annotation_create_invalid_bitext(auth_client, create_evaluation):
    client, login_user = auth_client
    evaluation = create_evaluation(name="Invalid Bitext Eval")
    response = _request(
        client,
        "post",
        "/api/annotations",
        json={"userId": login_user.id, "evaluationId": evaluation.id, "bitextId": 999},
    )
    assert response.status_code == 422


def test_annotation_read_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "get", "/api/annotations/999")
    assert response.status_code == 404


def test_annotation_update_missing_field(auth_client, create_annotation):
    client, _ = auth_client
    annotation = create_annotation()
    response = _request(client, "put", f"/api/annotations/{annotation.id}", json={})
    assert response.status_code == 422


def test_annotation_update_invalid_ids(auth_client, create_annotation):
    client, _ = auth_client
    annotation = create_annotation()
    response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}",
        json={"userId": 999, "evaluationId": 999, "bitextId": 999},
    )
    assert response.status_code == 422


def test_annotation_update_invalid_evaluation(auth_client, create_annotation):
    client, _ = auth_client
    annotation = create_annotation()
    response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}",
        json={
            "userId": annotation.userId,
            "evaluationId": 999,
            "bitextId": annotation.bitextId,
        },
    )
    assert response.status_code == 422


def test_annotation_update_invalid_bitext(auth_client, create_annotation):
    client, _ = auth_client
    annotation = create_annotation()
    response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}",
        json={
            "userId": annotation.userId,
            "evaluationId": annotation.evaluationId,
            "bitextId": 999,
        },
    )
    assert response.status_code == 422


def test_annotation_update_not_found(auth_client, create_evaluation, create_bitext, create_user):
    client, login_user = auth_client
    evaluation = create_evaluation(name="Update Missing Eval")
    bitext = create_bitext()
    response = _request(
        client,
        "put",
        "/api/annotations/999",
        json={
            "userId": login_user.id,
            "evaluationId": evaluation.id,
            "bitextId": bitext.id,
        },
    )
    assert response.status_code == 404


def test_annotation_delete_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "delete", "/api/annotations/999")
    assert response.status_code == 404


def test_read_annotations_missing_identity(auth_client, monkeypatch):
    client, _ = auth_client

    monkeypatch.setattr(
        "human_evaluation_tool.resources.annotation.get_jwt_identity", lambda: None
    )
    response = _request(client, "get", "/api/annotations")
    assert response.status_code == 401


def test_annotation_create_database_error(
    auth_client, create_evaluation, create_bitext, monkeypatch
):
    client, login_user = auth_client
    evaluation = create_evaluation(name="Error Eval")
    bitext = create_bitext()

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "post",
        "/api/annotations",
        json={
            "userId": login_user.id,
            "evaluationId": evaluation.id,
            "bitextId": bitext.id,
        },
    )
    assert response.status_code == 500


def test_annotation_update_database_error(auth_client, create_annotation, monkeypatch):
    client, _ = auth_client
    annotation = create_annotation()

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}",
        json={
            "userId": annotation.userId,
            "evaluationId": annotation.evaluationId,
            "bitextId": annotation.bitextId,
        },
    )
    assert response.status_code == 500


def test_annotation_delete_database_error(auth_client, create_annotation, monkeypatch):
    client, _ = auth_client
    annotation = create_annotation()

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(client, "delete", f"/api/annotations/{annotation.id}")
    assert response.status_code == 500
