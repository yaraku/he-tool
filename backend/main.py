"""
Copyright (C) 2023-2025 Yaraku, Inc.

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

from __future__ import annotations

import os
from typing import Any

from human_evaluation_tool import DB_ENV_VARIABLES, create_app


def _development_config() -> dict[str, Any]:
    """Compose configuration defaults suitable for local development."""

    config: dict[str, Any] = {}
    if "JWT_SECRET_KEY" not in os.environ:
        config["JWT_SECRET_KEY"] = "development-secret-key"

    if "SQLALCHEMY_DATABASE_URI" in os.environ:
        return config

    # If any explicit database configuration is present, let the factory assemble
    # the SQLAlchemy URI instead of forcing a SQLite fallback.
    if any(key in os.environ for key in DB_ENV_VARIABLES):
        return config

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
