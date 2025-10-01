import os


def test_index_route_serves_index_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<!DOCTYPE" in response.data


def test_index_route_serves_static_file(client):
    static_path = "vite.svg"
    full_path = os.path.join(client.application.static_folder, static_path)
    assert os.path.exists(full_path)
    response = client.get(f"/{static_path}")
    assert response.status_code == 200
