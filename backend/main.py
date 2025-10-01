"""Development entry point for the Human Evaluation Tool backend server."""

from __future__ import annotations

import os
from typing import Any

from human_evaluation_tool import create_app


def _development_config() -> dict[str, Any]:
    """Compose configuration defaults suitable for local development."""

    config: dict[str, Any] = {}
    if "JWT_SECRET_KEY" not in os.environ:
        config["JWT_SECRET_KEY"] = "development-secret-key"
    if "SQLALCHEMY_DATABASE_URI" not in os.environ:
        config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development.db"
    return config


if __name__ == "__main__":
    app = create_app(_development_config())
    app.run(
        host="0.0.0.0",  # Listen on all network interfaces
        port=5000,
        debug=True,
        load_dotenv=True,
    )
