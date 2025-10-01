from sqlalchemy.exc import SQLAlchemyError

from human_evaluation_tool import db


def _request(client, method: str, url: str, **kwargs):
    return getattr(client, method)(url, **kwargs)


def test_bitext_crud_flow(auth_client, create_bitext, create_document):
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


def test_bitext_create_missing_field(auth_client, create_document):
    client, _ = auth_client
    document = create_document()
    response = _request(
        client,
        "post",
        "/api/bitexts",
        json={"documentId": document.id, "source": "Only source"},
    )
    assert response.status_code == 422


def test_bitext_create_invalid_document(auth_client):
    client, _ = auth_client
    response = _request(
        client,
        "post",
        "/api/bitexts",
        json={"documentId": 999, "source": "src", "target": "tgt"},
    )
    assert response.status_code == 422


def test_bitext_read_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "get", "/api/bitexts/999")
    assert response.status_code == 404


def test_bitext_update_missing_field(auth_client, create_bitext):
    client, _ = auth_client
    bitext = create_bitext()
    response = _request(client, "put", f"/api/bitexts/{bitext.id}", json={})
    assert response.status_code == 422


def test_bitext_update_not_found(auth_client):
    client, _ = auth_client
    response = _request(
        client,
        "put",
        "/api/bitexts/999",
        json={"documentId": 1, "source": "s", "target": "t"},
    )
    assert response.status_code == 404


def test_bitext_delete_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "delete", "/api/bitexts/999")
    assert response.status_code == 404


def test_bitext_create_database_error(auth_client, create_document, monkeypatch):
    client, _ = auth_client
    document = create_document()

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "post",
        "/api/bitexts",
        json={"documentId": document.id, "source": "s", "target": "t"},
    )
    assert response.status_code == 500


def test_bitext_update_database_error(auth_client, create_bitext, monkeypatch):
    client, _ = auth_client
    bitext = create_bitext()

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "put",
        f"/api/bitexts/{bitext.id}",
        json={"documentId": bitext.documentId, "source": "s", "target": "t"},
    )
    assert response.status_code == 500


def test_bitext_delete_database_error(auth_client, create_bitext, monkeypatch):
    client, _ = auth_client
    bitext = create_bitext()

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(client, "delete", f"/api/bitexts/{bitext.id}")
    assert response.status_code == 500
