from sqlalchemy.exc import SQLAlchemyError

from human_evaluation_tool import db


def _request(client, method: str, url: str, **kwargs):
    return getattr(client, method)(url, **kwargs)


def test_document_crud_flow(auth_client, create_document):
    client, _ = auth_client
    create_document(name="Existing Doc")

    list_response = _request(client, "get", "/api/documents")
    assert list_response.status_code == 200
    assert len(list_response.get_json()) == 1

    create_response = _request(
        client,
        "post",
        "/api/documents",
        json={"name": "New Doc"},
    )
    assert create_response.status_code == 201
    document_id = create_response.get_json()["id"]

    read_response = _request(client, "get", f"/api/documents/{document_id}")
    assert read_response.status_code == 200

    update_response = _request(
        client,
        "put",
        f"/api/documents/{document_id}",
        json={"name": "Updated", "documentId": document_id},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["name"] == "Updated"

    delete_response = _request(client, "delete", f"/api/documents/{document_id}")
    assert delete_response.status_code == 204


def test_document_create_missing_field(auth_client):
    client, _ = auth_client
    response = _request(client, "post", "/api/documents", json={})
    assert response.status_code == 422


def test_document_read_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "get", "/api/documents/123")
    assert response.status_code == 404


def test_document_update_not_found(auth_client):
    client, _ = auth_client
    response = _request(
        client,
        "put",
        "/api/documents/123",
        json={"name": "Updated", "documentId": 123},
    )
    assert response.status_code == 404


def test_document_update_missing_field(auth_client, create_document):
    client, _ = auth_client
    document = create_document(name="Needs Update")
    response = _request(
        client,
        "put",
        f"/api/documents/{document.id}",
        json={},
    )
    assert response.status_code == 422


def test_document_update_invalid_document_id(auth_client, create_document):
    client, _ = auth_client
    document = create_document(name="Has Bitexts")
    response = _request(
        client,
        "put",
        f"/api/documents/{document.id}",
        json={"name": "Bad", "documentId": 999},
    )
    assert response.status_code == 422


def test_document_delete_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "delete", "/api/documents/999")
    assert response.status_code == 404


def test_document_bitexts_listing(auth_client, create_document, create_bitext):
    client, _ = auth_client
    document = create_document(name="Doc with Bitexts")
    create_bitext(document=document, source="One", target="Uno")
    response = _request(client, "get", f"/api/documents/{document.id}/bitexts")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_document_bitexts_document_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "get", "/api/documents/999/bitexts")
    assert response.status_code == 404


def test_document_create_database_error(auth_client, monkeypatch):
    client, _ = auth_client

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(client, "post", "/api/documents", json={"name": "Fail"})
    assert response.status_code == 500


def test_document_update_database_error(auth_client, create_document, monkeypatch):
    client, _ = auth_client
    document = create_document(name="Doc to Fail")

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "put",
        f"/api/documents/{document.id}",
        json={"name": "Doc to Fail", "documentId": document.id},
    )
    assert response.status_code == 500


def test_document_delete_database_error(auth_client, create_document, monkeypatch):
    client, _ = auth_client
    document = create_document(name="Doc to Delete")

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(client, "delete", f"/api/documents/{document.id}")
    assert response.status_code == 500
