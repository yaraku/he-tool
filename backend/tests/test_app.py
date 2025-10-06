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
