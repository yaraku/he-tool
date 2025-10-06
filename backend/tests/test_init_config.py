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

from pathlib import Path

import pytest

from human_evaluation_tool import create_app


def test_database_uri_constructed_when_override_missing(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URI", raising=False)
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_NAME", "db")
    monkeypatch.setenv("DB_PASSWORD", "pw")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "user")

    app = create_app({})
    assert app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql://")


def test_database_uri_override_used(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)

    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite://"})
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite://"


def test_missing_secret_raises(monkeypatch):
    for key in [
        "JWT_SECRET_KEY",
        "SQLALCHEMY_DATABASE_URI",
        "DB_HOST",
        "DB_NAME",
        "DB_PASSWORD",
        "DB_PORT",
        "DB_USER",
    ]:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeError):
        create_app({})


def test_missing_database_variables_raise(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")
    for key in ["DB_HOST", "DB_NAME", "DB_PASSWORD", "DB_PORT", "DB_USER", "SQLALCHEMY_DATABASE_URI"]:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeError):
        create_app({})


def test_config_file_missing_is_tolerated(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", "sqlite://")

    monkeypatch.setattr(Path, "exists", lambda self: False)
    app = create_app({})
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite://"


def test_default_app_uses_fallback_configuration(monkeypatch):
    for key in [
        "JWT_SECRET_KEY",
        "SQLALCHEMY_DATABASE_URI",
        "DB_HOST",
        "DB_NAME",
        "DB_PASSWORD",
        "DB_PORT",
        "DB_USER",
    ]:
        monkeypatch.delenv(key, raising=False)

    from human_evaluation_tool import _create_default_app

    app = _create_default_app()
    assert app.config["JWT_SECRET_KEY"] == "development-secret-key"
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite://"
