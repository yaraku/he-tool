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

Written by Giovanni G. De Giacomo <giovanni@yaraku.com>, October 2025
"""

from collections.abc import Callable
from typing import Any

from flask.testing import FlaskClient
from pytest import MonkeyPatch
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.test import TestResponse

from human_evaluation_tool import db
from human_evaluation_tool.models import Bitext, Document, User


def _request(client: FlaskClient, method: str, url: str, **kwargs: Any) -> TestResponse:
    request_callable: Callable[..., TestResponse] = getattr(client, method)
    return request_callable(url, **kwargs)


def test_bitext_crud_flow(
    auth_client: tuple[FlaskClient, User],
    create_bitext: Callable[..., Bitext],
    create_document: Callable[..., Document],
) -> None:
    client, _ = auth_client
    document = create_document(name="Doc for Bitext")
    bitext = create_bitext(document=document)

    list_response = _request(client, "get", "/api/bitexts")
    assert list_response.status_code == 200
    assert len(list_response.get_json()) == 1

    create_response = _request(
        client,
        "post",
        "/api/bitexts",
        json={
            "documentId": document.id,
            "source": "New source",
            "target": "New target",
        },
    )
    assert create_response.status_code == 201
    bitext_id = create_response.get_json()["id"]

    read_response = _request(client, "get", f"/api/bitexts/{bitext_id}")
    assert read_response.status_code == 200

    update_response = _request(
        client,
        "put",
        f"/api/bitexts/{bitext_id}",
        json={
            "documentId": document.id,
            "source": "Updated",
            "target": "Updated target",
        },
    )
    assert update_response.status_code == 200

    delete_response = _request(client, "delete", f"/api/bitexts/{bitext_id}")
    assert delete_response.status_code == 204

    not_found_response = _request(client, "get", f"/api/bitexts/{bitext.id}")
    assert not_found_response.status_code == 200


def test_bitext_create_missing_field(
    auth_client: tuple[FlaskClient, User],
    create_document: Callable[..., Document],
) -> None:
    client, _ = auth_client
    document = create_document()
    response = _request(
        client,
        "post",
        "/api/bitexts",
        json={"documentId": document.id, "source": "Only source"},
    )
    assert response.status_code == 422


def test_bitext_create_invalid_document(auth_client: tuple[FlaskClient, User]) -> None:
    client, _ = auth_client
    response = _request(
        client,
        "post",
        "/api/bitexts",
        json={"documentId": 999, "source": "src", "target": "tgt"},
    )
    assert response.status_code == 422


def test_bitext_read_not_found(auth_client: tuple[FlaskClient, User]) -> None:
    client, _ = auth_client
    response = _request(client, "get", "/api/bitexts/999")
    assert response.status_code == 404


def test_bitext_update_missing_field(
    auth_client: tuple[FlaskClient, User],
    create_bitext: Callable[..., Bitext],
) -> None:
    client, _ = auth_client
    bitext = create_bitext()
    response = _request(client, "put", f"/api/bitexts/{bitext.id}", json={})
    assert response.status_code == 422


def test_bitext_update_not_found(auth_client: tuple[FlaskClient, User]) -> None:
    client, _ = auth_client
    response = _request(
        client,
        "put",
        "/api/bitexts/999",
        json={"documentId": 1, "source": "s", "target": "t"},
    )
    assert response.status_code == 404


def test_bitext_delete_not_found(auth_client: tuple[FlaskClient, User]) -> None:
    client, _ = auth_client
    response = _request(client, "delete", "/api/bitexts/999")
    assert response.status_code == 404


def test_bitext_create_database_error(
    auth_client: tuple[FlaskClient, User],
    create_document: Callable[..., Document],
    monkeypatch: MonkeyPatch,
) -> None:
    client, _ = auth_client
    document = create_document()

    def _raise_error() -> None:
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "post",
        "/api/bitexts",
        json={"documentId": document.id, "source": "s", "target": "t"},
    )
    assert response.status_code == 500


def test_bitext_update_database_error(
    auth_client: tuple[FlaskClient, User],
    create_bitext: Callable[..., Bitext],
    monkeypatch: MonkeyPatch,
) -> None:
    client, _ = auth_client
    bitext = create_bitext()

    def _raise_error() -> None:
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "put",
        f"/api/bitexts/{bitext.id}",
        json={"documentId": bitext.documentId, "source": "s", "target": "t"},
    )
    assert response.status_code == 500


def test_bitext_delete_database_error(
    auth_client: tuple[FlaskClient, User],
    create_bitext: Callable[..., Bitext],
    monkeypatch: MonkeyPatch,
) -> None:
    client, _ = auth_client
    bitext = create_bitext()

    def _raise_error() -> None:
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(client, "delete", f"/api/bitexts/{bitext.id}")
    assert response.status_code == 500
