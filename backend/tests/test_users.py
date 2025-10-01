from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from human_evaluation_tool import db


def _auth_request(client, method: str, url: str, **kwargs):
    http_method = getattr(client, method.lower())
    return http_method(url, **kwargs)


def test_read_users_returns_list(auth_client, create_user):
    client, _ = auth_client
    create_user(email="second@example.com")
    response = _auth_request(client, "get", "/api/users")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_create_user_success(auth_client):
    client, _ = auth_client
    response = _auth_request(
        client,
        "post",
        "/api/users",
        json={
            "email": "new@example.com",
            "password": "secret",
            "nativeLanguage": "ja",
        },
    )
    assert response.status_code == 201
    payload = response.get_json()["user"]
    assert payload["email"] == "new@example.com"


def test_create_user_missing_field_returns_422(auth_client):
    client, _ = auth_client
    response = _auth_request(
        client,
        "post",
        "/api/users",
        json={"email": "missing@example.com"},
    )
    assert response.status_code == 422


def test_create_user_duplicate_returns_409(auth_client, create_user):
    client, _ = auth_client
    create_user(email="duplicate@example.com")
    response = _auth_request(
        client,
        "post",
        "/api/users",
        json={
            "email": "duplicate@example.com",
            "password": "secret",
            "nativeLanguage": "en",
        },
    )
    assert response.status_code == 409


def test_create_user_handles_database_error(auth_client, monkeypatch):
    client, _ = auth_client
    original_commit = db.session.commit

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _auth_request(
        client,
        "post",
        "/api/users",
        json={
            "email": "error@example.com",
            "password": "secret",
            "nativeLanguage": "en",
        },
    )
    monkeypatch.setattr(db.session, "commit", original_commit)
    assert response.status_code == 500


def test_read_user_success(auth_client, create_user):
    client, _ = auth_client
    user = create_user(email="read@example.com")
    response = _auth_request(client, "get", f"/api/users/{user.id}")
    assert response.status_code == 200
    assert response.get_json()["email"] == "read@example.com"


def test_read_user_not_found_returns_404(auth_client):
    client, _ = auth_client
    response = _auth_request(client, "get", "/api/users/999")
    assert response.status_code == 404


def test_update_user_success(auth_client, create_user):
    client, _ = auth_client
    user = create_user(email="update@example.com")
    response = _auth_request(
        client,
        "put",
        f"/api/users/{user.id}",
        json={
            "email": "updated@example.com",
            "password": "newpass",
            "nativeLanguage": "fr",
        },
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["email"] == "updated@example.com"


def test_update_user_missing_field_returns_422(auth_client, create_user):
    client, _ = auth_client
    user = create_user(email="missing-update@example.com")
    response = _auth_request(
        client,
        "put",
        f"/api/users/{user.id}",
        json={"email": "missing-update@example.com"},
    )
    assert response.status_code == 422


def test_update_user_duplicate_email_returns_409(auth_client, create_user):
    client, _ = auth_client
    first = create_user(email="first@example.com")
    second = create_user(email="seconddup@example.com")
    response = _auth_request(
        client,
        "put",
        f"/api/users/{first.id}",
        json={
            "email": second.email,
            "password": "secret",
            "nativeLanguage": "en",
        },
    )
    assert response.status_code == 409


def test_update_user_not_found_returns_404(auth_client):
    client, _ = auth_client
    response = _auth_request(
        client,
        "put",
        "/api/users/999",
        json={
            "email": "missing@example.com",
            "password": "secret",
            "nativeLanguage": "en",
        },
    )
    assert response.status_code == 404


def test_update_user_handles_database_error(auth_client, create_user, monkeypatch):
    client, _ = auth_client
    user = create_user(email="error-update@example.com")

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _auth_request(
        client,
        "put",
        f"/api/users/{user.id}",
        json={
            "email": "error-update@example.com",
            "password": "secret",
            "nativeLanguage": "en",
        },
    )
    assert response.status_code == 500


def test_delete_user_success(auth_client, create_user):
    client, _ = auth_client
    user = create_user(email="delete@example.com")
    response = _auth_request(client, "delete", f"/api/users/{user.id}")
    assert response.status_code == 204


def test_delete_user_not_found_returns_404(auth_client):
    client, _ = auth_client
    response = _auth_request(client, "delete", "/api/users/999")
    assert response.status_code == 404


def test_delete_user_handles_database_error(auth_client, create_user, monkeypatch):
    client, _ = auth_client
    user = create_user(email="error-delete@example.com")

    def _raise_error():
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(db.session, "commit", _raise_error)
    response = _auth_request(client, "delete", f"/api/users/{user.id}")
    assert response.status_code == 500
