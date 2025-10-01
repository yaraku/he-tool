from sqlalchemy.exc import SQLAlchemyError

from human_evaluation_tool import db


def _request(client, method: str, url: str, **kwargs):
    return getattr(client, method)(url, **kwargs)


def test_system_crud_flow(auth_client, create_system):
    client, _ = auth_client
    system = create_system(name="Existing System")

    list_response = _request(client, "get", "/api/systems")
    assert list_response.status_code == 200
    assert len(list_response.get_json()) == 1

    create_response = _request(
        client,
        "post",
        "/api/systems",
        json={"name": "New System"},
    )
    assert create_response.status_code == 201
    system_id = create_response.get_json()["id"]

    read_response = _request(client, "get", f"/api/systems/{system_id}")
    assert read_response.status_code == 200

    update_response = _request(
        client,
        "put",
        f"/api/systems/{system_id}",
        json={"name": "Updated System"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["name"] == "Updated System"

    delete_response = _request(client, "delete", f"/api/systems/{system_id}")
    assert delete_response.status_code == 204


def test_system_create_missing_field(auth_client):
    client, _ = auth_client
    response = _request(client, "post", "/api/systems", json={})
    assert response.status_code == 422


def test_system_create_duplicate(auth_client, create_system):
    client, _ = auth_client
    system = create_system(name="Duplicate System")
    response = _request(
        client,
        "post",
        "/api/systems",
        json={"name": system.name},
    )
    assert response.status_code == 409


def test_system_read_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "get", "/api/systems/999")
    assert response.status_code == 404


def test_system_update_missing_field(auth_client, create_system):
    client, _ = auth_client
    system = create_system(name="Needs Update")
    response = _request(client, "put", f"/api/systems/{system.id}", json={})
    assert response.status_code == 422


def test_system_update_duplicate(auth_client, create_system):
    client, _ = auth_client
    first = create_system(name="First System")
    second = create_system(name="Second System")
    response = _request(
        client,
        "put",
        f"/api/systems/{first.id}",
        json={"name": second.name},
    )
    assert response.status_code == 409


def test_system_update_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "put", "/api/systems/999", json={"name": "Missing"})
    assert response.status_code == 404


def test_system_delete_not_found(auth_client):
    client, _ = auth_client
    response = _request(client, "delete", "/api/systems/999")
    assert response.status_code == 404


def test_system_create_database_error(auth_client, monkeypatch):
    client, _ = auth_client

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(client, "post", "/api/systems", json={"name": "Error"})
    assert response.status_code == 500


def test_system_update_database_error(auth_client, create_system, monkeypatch):
    client, _ = auth_client
    system = create_system(name="To Update")

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "put",
        f"/api/systems/{system.id}",
        json={"name": "To Update"},
    )
    assert response.status_code == 500


def test_system_delete_database_error(auth_client, create_system, monkeypatch):
    client, _ = auth_client
    system = create_system(name="To Delete")

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(client, "delete", f"/api/systems/{system.id}")
    assert response.status_code == 500


def test_annotation_system_endpoints(
    auth_client,
    create_annotation,
    create_system,
):
    client, _ = auth_client
    annotation = create_annotation()
    system = create_system(name="Annotation System")

    list_response = _request(
        client,
        "get",
        f"/api/annotations/{annotation.id}/systems",
    )
    assert list_response.status_code == 200
    assert list_response.get_json() == []

    create_response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems",
        json={"systemId": system.id, "translation": "Translated"},
    )
    assert create_response.status_code == 201
    annotation_system_id = create_response.get_json()["id"]

    duplicate_response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems",
        json={"systemId": system.id, "translation": "Translated"},
    )
    assert duplicate_response.status_code == 409

    read_response = _request(
        client,
        "get",
        f"/api/annotations/{annotation.id}/systems/{system.id}",
    )
    assert read_response.status_code == 200

    missing_field_response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/{system.id}",
        json={},
    )
    assert missing_field_response.status_code == 422

    update_response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/{system.id}",
        json={"translation": "Updated"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["translation"] == "Updated"

    delete_response = _request(
        client,
        "delete",
        f"/api/annotations/{annotation.id}/systems/{system.id}",
    )
    assert delete_response.status_code == 204

    not_found_response = _request(
        client,
        "get",
        f"/api/annotations/{annotation.id}/systems/{system.id}",
    )
    assert not_found_response.status_code == 404

    update_after_delete = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/{system.id}",
        json={"translation": "Another"},
    )
    assert update_after_delete.status_code == 404

    delete_again = _request(
        client,
        "delete",
        f"/api/annotations/{annotation.id}/systems/{system.id}",
    )
    assert delete_again.status_code == 404


def test_annotation_system_validation(auth_client, create_annotation, create_system):
    client, _ = auth_client
    annotation = create_annotation()
    system = create_system(name="Extra System")

    missing_field = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems",
        json={"systemId": system.id},
    )
    assert missing_field.status_code == 422

    invalid_system = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems",
        json={"systemId": 999, "translation": "T"},
    )
    assert invalid_system.status_code == 422

    annotation_not_found = _request(
        client,
        "get",
        "/api/annotations/999/systems",
    )
    assert annotation_not_found.status_code == 404

    create_missing_annotation = _request(
        client,
        "post",
        "/api/annotations/999/systems",
        json={"systemId": system.id, "translation": "T"},
    )
    assert create_missing_annotation.status_code == 404


def test_annotation_system_database_errors(
    auth_client, create_annotation, create_system, monkeypatch
):
    client, _ = auth_client
    annotation = create_annotation()
    system = create_system(name="DB Error System")

    def _raise_error():
        raise SQLAlchemyError("boom")

    original_commit = db.session.commit
    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems",
        json={"systemId": system.id, "translation": "T"},
    )
    assert response.status_code == 500

    monkeypatch.setattr(db.session, "commit", original_commit)
    _request(
        client,
        "post",
        f"/api/annotations/{annotation.id}/systems",
        json={"systemId": system.id, "translation": "T"},
    )
    monkeypatch.setattr(db.session, "commit", _raise_error)
    update_response = _request(
        client,
        "put",
        f"/api/annotations/{annotation.id}/systems/{system.id}",
        json={"translation": "Updated"},
    )
    assert update_response.status_code == 500

    delete_response = _request(
        client,
        "delete",
        f"/api/annotations/{annotation.id}/systems/{system.id}",
    )
    assert delete_response.status_code == 500
