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


def _create_annotation_for_user(create_annotation, user, evaluation=None, bitext=None):
    return create_annotation(user=user, evaluation=evaluation, bitext=bitext)


def test_marking_flow(
    auth_client,
    create_annotation,
    create_system,
    create_evaluation,
    create_bitext,
):
    client, user = auth_client
    evaluation = create_evaluation(name="Mark Eval")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, user, evaluation, bitext)
    system = create_system(name="Mark System")

    list_empty = _request(client, "get", f"/api/annotations/{annotation.id}/markings")
    assert list_empty.status_code == 200
    assert list_empty.get_json() == []

    create_response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert create_response.status_code == 201
    marking_id = create_response.get_json()["id"]

    list_response = _request(client, "get", f"/api/annotations/{annotation.id}/markings")
    assert list_response.status_code == 200
    assert len(list_response.get_json()) == 1

    read_response = _request(
        client,
        "get",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/{marking_id}",
    )
    assert read_response.status_code == 200

    update_response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/{marking_id}",
        json={
            "errorStart": 1,
            "errorEnd": 2,
            "errorCategory": "A02",
            "errorSeverity": "minor",
            "isSource": False,
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["errorCategory"] == "A02"

    delete_response = _request(
        client,
        "delete",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/{marking_id}",
    )
    assert delete_response.status_code == 204

    not_found_response = _request(
        client,
        "get",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/{marking_id}",
    )
    assert not_found_response.status_code == 404


def test_marking_requires_valid_annotation(auth_client, create_system):
    client, _ = auth_client
    system = create_system(name="Other System")
    response = _request(client, "get", f"/api/annotations/999/systems/{system.id}/markings/1")
    assert response.status_code == 404


def test_read_markings_annotation_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "get", "/api/annotations/999/markings")
    assert response.status_code == 404


def test_marking_checks_authorization(
    auth_client, create_annotation, create_system, create_evaluation, create_bitext, create_user
):
    client, user = auth_client
    other_user = create_user(email="other@example.com")
    evaluation = create_evaluation(name="Other Eval")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, other_user, evaluation, bitext)
    system = create_system(name="System Auth")

    response = _request(client, "get", f"/api/annotations/{annotation.id}/markings")
    assert response.status_code == 401

    response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert response.status_code == 401

    response_read = _request(
        client,
        "get",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/1",
    )
    assert response_read.status_code == 401

    response_update = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/1",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert response_update.status_code == 401

    response_delete = _request(
        client,
        "delete",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/1",
    )
    assert response_delete.status_code == 401


def test_marking_requires_existing_system(
    auth_client, create_annotation, create_evaluation, create_bitext
):
    client, user = auth_client
    evaluation = create_evaluation(name="System Missing Eval")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, user, evaluation, bitext)
    response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems/999/markings",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert response.status_code == 404


def test_marking_create_annotation_not_found(auth_client, create_system):
    client, _ = auth_client
    system = create_system(name="Missing Annotation System")
    response = _request(
        client,
        "post",
        f"/api/annotations/999/systems/{system.id}/markings",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert response.status_code == 404


def test_marking_update_annotation_not_found(auth_client, create_system):
    client, _ = auth_client
    system = create_system(name="Update Missing Annotation System")
    response = _request(
        client,
        "put",
        f"/api/annotations/999/systems/{system.id}/markings/1",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert response.status_code == 404


def test_marking_delete_annotation_not_found(auth_client, create_system):
    client, _ = auth_client
    system = create_system(name="Delete Missing Annotation System")
    response = _request(
        client,
        "delete",
        f"/api/annotations/999/systems/{system.id}/markings/1",
    )
    assert response.status_code == 404


def test_marking_system_not_found_for_operations(
    auth_client, create_annotation, create_evaluation, create_bitext
):
    client, user = auth_client
    evaluation = create_evaluation(name="System Missing Eval 2")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, user, evaluation, bitext)
    response_read = _request(
        client,
        "get",
        f"/api/annotations/{annotation.id}/systems/999/markings/1",
    )
    assert response_read.status_code == 404

    response_update = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/999/markings/1",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert response_update.status_code == 404

    response_delete = _request(
        client,
        "delete",
        f"/api/annotations/{annotation.id}/systems/999/markings/1",
    )
    assert response_delete.status_code == 404


def test_marking_create_missing_fields(
    auth_client,
    create_annotation,
    create_system,
    create_evaluation,
    create_bitext,
):
    client, user = auth_client
    evaluation = create_evaluation(name="Missing Fields Eval")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, user, evaluation, bitext)
    system = create_system(name="System Missing Fields")

    response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings",
        json={"errorStart": 0},
    )
    assert response.status_code == 422


def test_marking_update_missing_fields(
    auth_client,
    create_annotation,
    create_system,
    create_evaluation,
    create_bitext,
):
    client, user = auth_client
    evaluation = create_evaluation(name="Update Missing Eval")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, user, evaluation, bitext)
    system = create_system(name="Update Missing System")
    create_response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    marking_id = create_response.get_json()["id"]

    response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/{marking_id}",
        json={"errorStart": 0},
    )
    assert response.status_code == 422


def test_marking_update_not_found(
    auth_client,
    create_annotation,
    create_system,
    create_evaluation,
    create_bitext,
):
    client, user = auth_client
    evaluation = create_evaluation(name="Update Missing Eval 2")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, user, evaluation, bitext)
    system = create_system(name="Update Missing System 2")

    response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/999",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert response.status_code == 404


def test_marking_delete_not_found(
    auth_client,
    create_annotation,
    create_system,
    create_evaluation,
    create_bitext,
):
    client, user = auth_client
    evaluation = create_evaluation(name="Delete Missing Eval")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, user, evaluation, bitext)
    system = create_system(name="Delete Missing System")

    response = _request(
        client,
        "delete",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/999",
    )
    assert response.status_code == 404


def test_marking_database_errors(
    auth_client,
    create_annotation,
    create_system,
    create_evaluation,
    create_bitext,
    monkeypatch,
):
    client, user = auth_client
    evaluation = create_evaluation(name="DB Eval")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, user, evaluation, bitext)
    system = create_system(name="DB System")

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert response.status_code == 500


def test_marking_update_delete_database_errors(
    auth_client,
    create_annotation,
    create_system,
    create_evaluation,
    create_bitext,
    monkeypatch,
):
    client, user = auth_client
    evaluation = create_evaluation(name="DB Eval 2")
    bitext = create_bitext()
    annotation = _create_annotation_for_user(create_annotation, user, evaluation, bitext)
    system = create_system(name="DB System 2")
    create_response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    marking_id = create_response.get_json()["id"]

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    update_response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/{marking_id}",
        json={
            "errorStart": 0,
            "errorEnd": 1,
            "errorCategory": "A01",
            "errorSeverity": "critical",
            "isSource": True,
        },
    )
    assert update_response.status_code == 500

    delete_response = _request(
        client,
        "delete",
        f"/api/annotations/{annotation.id}/systems/{system.id}/markings/{marking_id}",
    )
    assert delete_response.status_code == 500
