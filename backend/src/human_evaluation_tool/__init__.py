"""Application factory for the Human Evaluation Tool backend."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from dotenv import load_dotenv
from flask import Flask, Response, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Load environment variables from .env files once during import so the factory can
# rely on ``os.environ`` when configuring the application.
load_dotenv()

# Lazily initialised Flask extensions.


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
bcrypt = Bcrypt()
jwt_manager = JWTManager()
migrate = Migrate()


def _configure_database(app: Flask) -> None:
    """Configure the SQLAlchemy database URI for the application."""

    if "SQLALCHEMY_DATABASE_URI" in app.config and app.config["SQLALCHEMY_DATABASE_URI"]:
        return

    if "SQLALCHEMY_DATABASE_URI" in os.environ:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
        return

    required_variables = ["DB_HOST", "DB_NAME", "DB_PASSWORD", "DB_PORT", "DB_USER"]
    missing = [key for key in required_variables if key not in os.environ]
    if missing:
        missing_values = ", ".join(missing)
        raise RuntimeError(
            "Missing required database environment variables: " f"{missing_values}"
        )

    from urllib.parse import quote_plus

    user = os.environ["DB_USER"]
    password = quote_plus(os.environ["DB_PASSWORD"])
    host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    name = os.environ["DB_NAME"]
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{user}:{password}@{host}:{port}/{name}"
    )


def create_app(config_override: Mapping[str, Any] | None = None) -> Flask:
    """Create and configure the Flask application instance."""

    package_root = Path(__file__).resolve().parent
    src_root = package_root.parent
    backend_root = src_root.parent
    project_root = backend_root.parent
    static_folder_path = project_root / "public"
    static_folder_str = str(static_folder_path)

    app = Flask(
        __name__,
        static_folder=static_folder_str,
    )

    config_path = backend_root / "flask.config.json"
    if config_path.exists():
        app.config.from_file(str(config_path), load=json.load)

    if config_override:
        app.config.update(dict(config_override))

    secret_key = app.config.get("JWT_SECRET_KEY") or os.environ.get("JWT_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY environment variable must be set")
    app.config["JWT_SECRET_KEY"] = secret_key
    app.config["JSON_SORT_KEYS"] = False

    _configure_database(app)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt_manager.init_app(app)
    migrate.init_app(app, db)

    from . import auth
    from .resources import register_resources

    auth.register_auth_blueprint(app)
    register_resources(app)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def index(path: str) -> Response:
        if path and (static_folder_path / path).exists():
            return send_from_directory(static_folder_str, path)
        return send_from_directory(static_folder_str, "index.html")

    return app


def _create_default_app() -> Flask:
    """Create the production application used by WSGI servers."""

    default_config: dict[str, Any] = {}
    if "JWT_SECRET_KEY" not in os.environ:
        default_config["JWT_SECRET_KEY"] = "development-secret-key"
    if "SQLALCHEMY_DATABASE_URI" not in os.environ:
        default_config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    return create_app(default_config)


app = _create_default_app()

__all__ = ["Base", "app", "bcrypt", "create_app", "db", "jwt_manager", "migrate"]
