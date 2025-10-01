import os
from flask.testing import FlaskClient


def test_index_route_serves_index_html(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"<!DOCTYPE" in response.data


def test_index_route_serves_static_file(client: FlaskClient) -> None:
    static_path = "vite.svg"
    static_root = client.application.static_folder
    assert static_root is not None
    full_path = os.path.join(static_root, static_path)
    assert os.path.exists(full_path)
    response = client.get(f"/{static_path}")
    assert response.status_code == 200
